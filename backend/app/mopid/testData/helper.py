from .schema import submitTestSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..questionModule.model import Questions, QuestionsSolution, QuestionsOptions
from .model import *
from ..user.model import Employees
from ...utils.classes import Logger, Timer, error_format, error_file, timing_format, timing_file
from ...utils.functions import responseBody, dbCommit, getUniqueId
import requests
from sqlalchemy import any_
import json
import random
from sqlalchemy import func
import traceback
from sqlalchemy.sql.expression import func

logger = Logger(__name__, error_file, error_format)
timingLogger = Logger('Timer:' + __name__, timing_file, timing_format)


@Timer(timingLogger)
def get_tags(domain: str, role: str):
    '''
    Description - This helper method returns tags for a particular user with the help of domain and role of that user.
    
    Parameters  - domain: str, role: str
    
    Returns     - Tags with their respective question counts in an array,
                   
                  Example:- [{'html5': 5}, {'css': 5}, {'javascript': 5}, {'jquery': 5}, {'quants': 10}, {'reasoning': 10}]            
    '''
    tags = json.load(open("tagsConfig.json","r"))
    quants_and_reasoning = tags.get("quants_and_reasoning").get("quants_and_reasoning")
    roles = tags.get(domain)  
    if roles is None: 
        return quants_and_reasoning
    
    skills = roles.get(role, [])
    skills += quants_and_reasoning
    return skills



@Timer(timingLogger)
def create_req_options_list(options):
    '''
    Description - This helper method merge all options together who have same question id.
    
    Parameters  - options
    
    Returns     - Example:- 
                  {"question_id1":[{"option1.1": option1.1Content, "uid": option1.1id}, {"option1.2": option1.2Content, "uid": option1.2id},
                                   {"option1.3": option1.3Content, "uid": option1.3id}, {"option1.4": option1.4Content, "uid": option1.4id}],
                                   
                   "question_id2":[{"option2.1": option2.1Content, "uid": option2.1id}, {"option2.2": option2.2Content, "uid": option2.2id},
                                   {"option2.3": option2.3Content, "uid": option2.3id}, {"option2.4": option2.4Content, "uid": option2.4id}],
                                   
                   "question_id3":[{}, {}, {}, {}], "question_id4":[{},{},{},{}], ......                                                   
                  }          
    '''
    jsonD = {}
    for i in range(0,len(options)):
        question_id = options[i].get("question_id")
        opt = options[i].get("options")
        options_id = options[i].get("options_id")
        if question_id in jsonD:
            optionL = jsonD.get(question_id,[])
            optionL.append({"option":opt,"uid":options_id})
            jsonD[question_id] = optionL
        else:
            jsonD[question_id] = [{"option":opt,"uid":options_id}]
    return jsonD


 
@Timer(timingLogger) 
def merge_questions_and_options(questions,options):
    '''
    Description - This helper method merge all option's array with their respective questions.
    
    Parameters  - questions, options
    
    Returns     - [{"uid": question1id, "question": question1content, "options":[{"option1.1": option1.1Content, "uid": option1.1id},
                   {"option1.2": option1.2Content, "uid": option1.2id}, {"option1.3": option1.3Content, "uid": option1.3id},
                   {"option1.4": option1.4Content, "uid": option1.4id}]},
                   
                   {"uid": question2id, "question": question2content, "options":[{"option2.1": option2.1Content, "uid": option2.1id},
                   {"option2.2": option2.2Content, "uid": option2.2id}, {"option2.3": option2.3Content, "uid": option2.3id},
                   {"option2.4": option2.4Content, "uid": option2.4id}]},
                   
                   {"uid": question3id, "question": question3content, "options":[{"option3.1": option3.1Content, "uid": option3.1id},
                   {"option3.2": option3.2Content, "uid": option3.2id}, {"option3.3": option3.3Content, "uid": option3.3id},
                   {"option3.4": option3.4Content, "uid": option3.4id}]},                   
                   {},{}, ......... ]         
    '''
    finalList = []
    for i in range(0,len(questions)):
        question_id = questions[i].get("question_id","")
        content = questions[i].get("content","")
        option = options.get(question_id)
        jsonF = {"uid":question_id,"question":content,"options":option}
        finalList.append(jsonF)
    return finalList
         
     
@Timer(timingLogger)         
def merge_questions(db: Session, questions: list): 
    '''
    Description -  This helper method extract options form QUESTIONSOPTIONS table by matching the questions id and then
                   return it by merge them with the help of create_req_options_list method and merge_questions_and_options mehtod
                   
    Parameters  -  db: Session, questions: list
    
    Returns     -  It returns an array of question with their options.....
                   Example : - 
                   [{'uid': 1371, 'question': 'Which of the following......Javascript?', 
                           'options': [{'option': 'variable', 'uid': 5481}, {'option': 'case', 'uid': 5482},
                                       {'option': 'Both', 'uid': 5483}, {'option': 'None', 'uid': 5484}]},
                               
                   {'uid': 1449, 'question': 'Which of the following.......array?',
                            'options': [{'option': 'unshift()', 'uid': 5793}, {'option': 'sort()', 'uid': 5794},
                                        {'option': 'splice()', 'uid': 5795}, {'option': 'toString()', 'uid': 5796}]},
                   {.....} ,{......}, {.....} ,{......}, {.....} ,{......}]          
    ''' 
    
    questionIds = list(map(lambda x: x.id, questions)) 
    questionOptions = db.query(QuestionsOptions).filter(QuestionsOptions.question_id.in_((questionIds))).all()  
    
    options = []
    questionList = []
    for  i in questions:
        jsonD = {"content":i.content,"question_id":i.id}
        questionList.append(jsonD)
    for item in questionOptions:
        options.append({"question_id" :item.question_id,"options": item.content,"options_id":item.id})  
    
    #for merge all options for a particular question 
    optionsList = create_req_options_list(options)
    
    finalList = merge_questions_and_options(questionList, optionsList)
    return finalList



@Timer(timingLogger)
def get_question(db: Session, tags: str, tagCount: int): 
    '''
    Description - This helper method extract random questions from the QUESTION table on the basis of
                  domain and role and extract their respective options by the help of merge_questions method.
                  
    Parameters  - db: Session, tags: str, tagCount: int
    
    Returns     - It returns an array of question with their options.....
                  Example : - 
                          [{'uid': 1371, 'question': 'Which of the following......Javascript?', 
                                         'options': [{'option': 'variable', 'uid': 5481}, {'option': 'case', 'uid': 5482},
                                                     {'option': 'Both', 'uid': 5483}, {'option': 'None', 'uid': 5484}]},
                                                     
                           {'uid': 1449, 'question': 'Which of the following.......array?',
                                         'options': [{'option': 'unshift()', 'uid': 5793}, {'option': 'sort()', 'uid': 5794},
                                                     {'option': 'splice()', 'uid': 5795}, {'option': 'toString()', 'uid': 5796}]},
                                                     
                  {.....} ,{......}, {.....} ,{......}, {.....} ,{......}]          
    ''' 
    questionList =[]
    questions = db.query(Questions).filter(Questions.tags["tags"].like("%"+tags+"%")).order_by(func.rand()).limit(tagCount).all()  
   
    
    questionList = merge_questions(db, questions)   

    return questionList

    
@Timer(timingLogger)    
def user_tags_with_count( db: Session, userId: str,): 
    '''
    Description - This helper method return tags and their count with the help of get_tags function on the basis of domain & role which is fetch from EMPLOYEES table 
                  on the basis of userId.
                  
    Parameters  - userId: str, db: Session
    
    Returns     - Example_1 :- {'project_management': 20, 'quants': 10, 'reasoning': 10}
                  Example_2 :- {'quants': 10, 'reasoning': 10}.....in case of no domain and role
                  Example_3 :- {'restful': 5, 'data_structures_and_algorithms': 5, 'design_pattern': 5, 'sql': 5, 'quants': 10, 'reasoning': 10}
    '''
    employeeDetail= db.query(Employees).filter(Employees.userId == userId).first()
    if employeeDetail==None:
        logMsg = logger.return_log_msg(400,"User doesn't exist")
        logger.logger.info(logMsg)
        return responseBody(400,"User doesn't exist")
    
    domain = employeeDetail.domain 
    role = employeeDetail.role 
   
    tags =get_tags(domain, role)
    if tags is None:
        logMsg = logger.return_log_msg(404,"Tags/Skills not found")
        logger.logger.info(logMsg)
        return responseBody(404, "Tags/Skills not found")
    
    tagsWithCount = {}
    for item in tags:
        tagsWithCount.update(item)   
        
    return tagsWithCount
    
    
    
@Timer(timingLogger)    
def get_user_test( userId: str, db: Session): 
    '''
    Description - This method gets tags and their count from a JSON file on the basis of domain & role and then extracts
                  the questions from the QUESTIONS table with the help of get_quesion method and returns it with their respective options.
                  which is fetching from QUESTIONOPTIONS table.
                  This method also generate the testId and also create a row for the given userId in TESTRESULT table.
                  
    Parameters  - userId: str, db: Session
    
    Returns     - 
                  message = "Test Created Successfully!",
                  response = {
                             'questions': questions,
                             'testDetails': {
                                            'marksPerQuestion': 10,
                                            'questions'       : len(questions),
                                            'testId'          : testId,
                                            'totalMarks'      : 10*len(questions),
                                            'totalTime'       : len(questions)
                                            }
                              }
    '''
    try: 
        tagsWithCount = user_tags_with_count(db, userId)   
        questions = []
        for key in tagsWithCount: 
            questions += get_question(db, key, tagsWithCount[key])       
        
        random.shuffle(questions)
        testId = getUniqueId()+str(userId)
        testResult = TestResult(uid=testId, questionCount=len(questions),userId=userId)
            
        testQuestions = list(map(lambda question: TestQuestions(testId=testId,questionId=question['uid']), questions))

        response = {
            'questions': questions,
            'testDetails': {
                'marksPerQuestion': 10,
                'questions': len(questions),
                'testId': testId,
                'totalMarks': 10*len(questions),
                'totalTime': len(questions)
            }
        }
        db.add(testResult)
        db.bulk_save_objects(testQuestions)
        db.commit()

        return responseBody(200, "Test Created Successfully!", response)
    except Exception as e: 
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




@Timer(timingLogger)
def submit_test(data: submitTestSchema, userId: str, db: Session):
    '''
    Description - This method submit the test given by the employee and update the result in TESTRESULT and TESTQUESTION data table.
                  It will takes user's questions from TestQuestion table and match theie answer from QUESTIONSOLUTION table.
    
    Parameters  - data: submitTestSchema{
                    testId: str,
                    options[list],
                    timeTaken[list]
                    },
                  userId: str, db: Session
    
    Returns     - 
                  {
                   "status_code": 200,
                   "message": "Test Submitted Successfully!",
                   "data": result = {
                                    'userId'     : userId,
                                    'totalMarks' : totalMarks,
                                    'marksScored': marksScored,
                                    'percentage' : percentage,
                                    'cutoff'     : testOptions.cutoff,
                                    'isPass'     : isPass,
                                    }
                   }                 
    '''
    try:
        result = {}
        questionResult = []
        testResult=[]
        correctQuestionCount = 0
        totalMarks = 0
        marksScored = 0
        percentage = 0
        isPass = False

        testQuestions = db.query(TestQuestions).filter(TestQuestions.testId==data.testId).all()
        
        # All attempted question ids
        questionIds = [question.questionId for question in testQuestions]
          
        userTestResult = db.query(TestResult).filter(TestResult.uid==data.testId).first()
        
        if userTestResult is None:
            logMsg = logger.return_log_msg(404, 'Test Result not found')
            logger.logger.info(logMsg)
            return responseBody(404, 'Test Result not found')
            
        testId = userTestResult.id
        
        solutions = db.query(QuestionsSolution).filter(QuestionsSolution.question_id.in_((questionIds))).all()
        
        answers = {}
        for i in solutions:
            answers[str(i.question_id)] = i.option_id
        
        testOptions = db.query(TestOptions).first()
        
        if testOptions is None:
            testOptions.marksPerQuestion = 10
            testOptions.cutoff = 60
      
        for question in testQuestions: 
            if data.response.__root__.get(question.questionId) != None:
                jsonT = {'id': question.id,'timeTaken': data.response.__root__[question.questionId].timeTaken}
                optionList = data.response.__root__[question.questionId].options  
                if len(optionList) != 0:
                    correctO = str(answers.get(str(question.questionId)))
                    attemptO = optionList[0]
                    if correctO == attemptO:
                        
                        jsonT["isCorrect"] = 1
                        correctQuestionCount += 1  
                questionResult.append(jsonT)   
            isPass = False
        
        totalMarks = len(testQuestions)*testOptions.marksPerQuestion
        marksScored = correctQuestionCount*testOptions.marksPerQuestion  
        percentage = round((marksScored/totalMarks)*100) 
        isPass = percentage >= testOptions.cutoff
            
        testResult.append({'id': testId,'isPass': isPass,'score': correctQuestionCount*testOptions.marksPerQuestion,'submit': True})
        db.bulk_update_mappings(TestQuestions, questionResult)
        db.bulk_update_mappings(TestResult, testResult)
        db.commit()   
        
        result = {
            'userId': userId,
            'totalMarks': totalMarks,
            'marksScored': marksScored,
            'percentage': percentage,
            'cutoff': testOptions.cutoff,
            'isPass': isPass,
        } 
        
        logMsg = logger.return_log_msg(200, 'Test Submitted Successfully!')
        logger.logger.info(logMsg)
        return responseBody(200, 'Test Submitted Successfully!', result)
    
    except Exception as e:
        print(e)
        traceback.print_exc()
        logMsg = logger.return_log_msg(500, "Something went wrong")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500, detail="Something went wrong")
    

@Timer(timingLogger)
def get_user_test_given(userId: str, db: Session): 
    '''
    Description - This helper method checks if the user has given a test or not.
    
    Parameters  - userId: str, db: Session
    
    Returns     - Either testData or not
    '''
    try:
        testData = db.query(TestResult).filter(TestResult.userId==userId).first()
        return testData
    except Exception as e: 
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@Timer(timingLogger)
def question_count(userId: str, db: Session): 
    '''
    Description - This method returns the total number of questions and time per question from test of the employees.
    
    Parameters  - userId: str, db: Session
    
    Returns     - {
                   "status_code": 200,
                   "message": "Question Count API run Successfully!",
                   "data": response = {
                                      'userId'         : userId,
                                      'domain'         : domain,
                                      'role'           : role,
                                      'totalQuestion'  : totalCount, example = 40
                                      'timePerQuestion': 1,
                                      }
                  }
    '''
    try:
        tagsWithCount = user_tags_with_count( db, userId)
        totalCount = 0
        for i in tagsWithCount.values():
            totalCount += i
            
        db_testDetails = db.query(TestOptions).first()
        
        if db_testDetails is None:
            db_testDetails.timePerQuestion = 1
            
        response = {
            'userId' : userId,
            'totalQuestion': totalCount,
            'timePerQuestion': db_testDetails.timePerQuestion,
        } 
        
        logMsg = logger.return_log_msg(200, 'Question Count API run Successfully!')
        logger.logger.info(logMsg)
        return responseBody(200, 'Question Count API run Successfully!', response)
        
    except Exception as e: 
        print(e)
        traceback.print_exc()
        logMsg = logger.return_log_msg(500, "Something went wrong in question count")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500, detail="Something went wrong in question count")   