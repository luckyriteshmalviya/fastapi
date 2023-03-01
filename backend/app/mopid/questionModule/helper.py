from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from ...utils.functions import CSVToDict, responseBody
from ...utils.classes import Logger, error_format, error_file, timing_format, timing_file
from .model import *
import traceback
from google.cloud import storage
import os
from .schema import ImageUploadType
from ..user.GcpUpload import set_blob_cache_control

logger = Logger(__name__, error_file, error_format)
timingLogger = Logger('Timer:' + __name__, timing_file, timing_format)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json" 
client = storage.Client.from_service_account_json(json_credentials_path='creds.json') 


def find_correct_option(row):
    '''
    Description - This helper method identify the correct option for the given question
    
    Parameters  - row{question with multiple options}
    
    Returns     - correct option
    '''
    if row['status_1'] == '1': 
        return 1
    elif row['status_2'] == '1': 
        return 2 
    elif row['status_3'] == '1': 
        return 3 
    return 4


def add_questions(file: UploadFile, db: Session): 
    '''
    Description - This method convert csv file into dict then add questions and their details in QUESTIONS table and their options in
                  QUESTIONOPTION table with their solution in QUESTIONSOLUTION table in database.
                  
    Parameters  - file: UploadFile {file which needs to be added}, db: Session
    
    Returns     - message after successful run:- "File uploaded successfully",
                  message after unsuccessful run:- "Something went wrong in add_question api"
    '''
    try: 
        data = CSVToDict(file)

        for row in data: 
            questionUid = str(row['question_id'])
            content = row['question'] 
            tags = row['tags']
            solutionDescription = row['description']
            questionType = row['type']
            questionImage = row['question_image'] if row['question_image'] != "" else None
            

            question = Questions(uid=questionUid, type = questionType, image = questionImage, content=content, tags = { 'tags': tags})
            db.add(question)
            db.flush()
            # questions.append(question)
            
            correctOptionId = find_correct_option(row)
            correctOption = None
            for i in range(4):
                optionId=str(i+1)
                optionImage = row['option_image_'+optionId] if row['option_image_'+optionId] != "" else None
                option = QuestionsOptions(uid=questionUid+'-option-'+optionId, question_id=question.id, image = optionImage, content=row['option_'+optionId])
                db.add(option)
                if i+1 == correctOptionId: 
                    # print(correctOptionId)
                    db.flush()
                    correctOption = option
                # options.append(option)
    
            solutionImage = row['description_image'] if row['description_image'] != "" else None
            solution = QuestionsSolution(uid=questionUid+'-solution', question_id=question.id, image = solutionImage, option_id=correctOption.id, content=solutionDescription)
            # solutions.append(solution)
            db.add(solution)

        db.commit()
        return responseBody(204, "Questions added successfully")
    except: 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail= "Something went wrong in add_question api")




def add_images(type: ImageUploadType, file: UploadFile): 
    '''
    Description - This method upload images files in GCP in jpeg format in mopid-questions bucket and set its cache_control as no-store.
                  The file should be of jpeg format and should not be exceeded size of 5 mb.
                  It saves the image in this paths:-
                  
                  question images in "mopid/questions/questionImages" path.
                  
                  option images in "mopid/questions/optionImages" path.
                  
                  solution images in "mopid/questions/solutionImages" path.   
                  
                           
    Parameters  - db: Session, file {The file which needs to be uploaded}
    
    Returns     - "File uploaded successfully"
    '''
    try: 
        if len(file.file.read()) > 5000000:
            return responseBody(406, "File size too large! max file size: 5mb")

        if file.content_type != "image/jpeg":
            return responseBody(406, "Invalid file format")
        
        filename = file.filename.split(".")[0]
        
        path = "questions/"

        if type == ImageUploadType.question: 
            path += "questionImages/"
        elif type == ImageUploadType.option: 
            path += "optionImages/"
        else:
            path += "solutionImages/"

        filename = path + filename

        # Creating bucket object 
        
        bucket = client.get_bucket('mopid') 

        object_name_in_gcs_bucket = bucket.blob(f"{filename}")   

        # Name of the object in local file system
        object_name_in_gcs_bucket.upload_from_file(file.file, content_type='image/jpeg', rewind=True)
       
        logMsg = logger.return_log_msg(200,"File uploaded successfully")
        logger.logger.info(logMsg)
        return responseBody(200,"File uploaded successfully")
    except Exception as e: 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Something went wrong!")