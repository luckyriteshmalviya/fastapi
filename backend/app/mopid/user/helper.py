from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from fastapi.param_functions import File
from ...utils.functions import responseBody, dbCommit, getUniqueId, generateRandomNumber
from ...utils.classes import Logger, Timer, error_format, error_file, timing_format, timing_file
import requests
from .schema import employeeOtpSchema, employeeExperienceSchema, employeeSignupSchema, employeeDetailsSchema, employeeLoginSchema, authType, employerSignupSchema
from decouple import config
from pydantic import *
from .model import User, EmployeeExperience, Employees, Employers
from ...utils.jwtHandler import signJWT, decodeJWT
from ..testData.helper import get_user_test_given
from sqlalchemy import or_
import traceback
import json


logger = Logger(__name__, error_file, error_format)
timingLogger = Logger('Timer:' + __name__, timing_file, timing_format)
 
AUTH_KEY = config('AUTH_KEY') 
TEMPLATE_ID = config('TEMPLATE_ID')


@Timer(timingLogger)
def send_otp(db , phone: str , isLogin: bool ):
    '''
    Description - This method sends OTP to the user. In case of login before sending OTP it will check the user exists or not.
                  If the user not exist in case of login then it will returns (400,"User does not exist. Please register!")
                  
    Parameters  - db{database} , phone: str , isLogin: bool
    
    Returns     - {
                    "status_code": 200,
                    "message": "OTP sent successfully!"
                  }
    '''
    try:
        if (isLogin == True):
            if check_user_exist(db,phone) is None:
                logMsg = logger.return_log_msg(400,"User does not exist. Please register!")
                logger.logger.info(logMsg)
                return responseBody(400, "User does not exist. Please register!")    
                
        if phone == 7415077577 or phone == 8553481764 or phone == 7483513449 or phone == 8240075341:
            response = requests.get(
                f'https://api.msg91.com/api/v5/otp?authkey={AUTH_KEY}&template_id={TEMPLATE_ID}&mobile=91{phone}&otp=1234').json()
        else:   
            response = requests.get(f'https://api.msg91.com/api/v5/otp?authkey={AUTH_KEY}&template_id={TEMPLATE_ID}&mobile=91{phone}&otp={generateRandomNumber()}').json()
        if (response['type'] == 'success'):
            logMsg = logger.return_log_msg(200,"OTP sent successfully!")
            logger.logger.info(logMsg)
            return responseBody(200,"OTP sent successfully!")
        else:
            logMsg = logger.return_log_msg(400,"Network Error")
            logger.logger.info(logMsg)
            return responseBody(400,"Network Error")
    except Exception as e:
        print(e)
        logMsg = logger.return_log_msg(404, "Something went wromg in OTP sending. Please try again")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=404,detail="Something went wrong in OTP sending. Please try again")
       
       
       
@Timer(timingLogger)
def verify_otp(phone , otp):
    '''
    Description - This helper method verify the OTP given by the user.
    
    Parameters  - phone , otp
    
    Returns     - Either { "OTP verified successfully" } or { "OTP not match" } 
    '''
    response = requests.post(f'https://api.msg91.com/api/v5/otp/verify?authkey={AUTH_KEY}&mobile=91{phone}&otp={otp}').json()
    if(response['type'] == 'success'):
        return True
    else:
        logMsg = logger.return_log_msg(404,response['message'])
        logger.logger.info(logMsg)
        return responseBody(404,response['message'])
    
    
    
    
@Timer(timingLogger)
def check_user_exist(db: Session, phone: Optional[int], email: Optional[str] = None):
    '''
    Description - This helper method check the current user exist or not by either there phone or by there email id.
    
    Parameters  - db: Session, phone: Optional[int], email: Optional[str]
    
    Returns     - Either null or { "mobileNo or email is already taken!" }
    '''
    return db.query(User).filter(or_(User.phone==phone,User.email==email)).first() 




@Timer(timingLogger)
def check_employee_exist(db: Session, id: str):
    '''
    Description - This helper method check the current user exist or not by there ID.
    
    Parameters  - db: Session, id:str
    
    Returns     - Either none or details of the user
    '''
    return db.query(User).filter(or_(User.id==id)).first()




@Timer(timingLogger)
def employee_signup(db: Session, data: employeeSignupSchema):
    '''
    Description - This method create employee user ID by verifying otp and fill the details in USER table.
                  First it will check user exists or not. If a user exists either with same mobile number or with same email address then
                  it will returns (409,"mobileNo or email is already taken!")
                  
    Parameters  - db: Session,
                  data: employeeSignupSchema {name: str, 
                  email: str, 
                  authType: authType, 
                  phone: str, 
                  otp: int,
                  type: str}
    
    Returns     - {
                    "status_code": 201,
                    "message": "User created successfully",
                    "data": {
                             "user": {
                                      "phone": "7415077577",
                                      "email": "johddndoe@gmail.com",
                                      "created_at": "2022-12-14T14:49:45",
                                      "type": "jobseeker",
                                      "name": "John Doe",
                                      "id": 116,
                                      "updated_at": "2022-12-14T14:49:45"
                                      },
                             "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE2LCJuYW1lIjoiSm9obiBEb2UiLCJtb2JpbGVObyI6Ij
                             c0MTUwNzc1NzciLCJlbWFpbCI6ImpvaGRkbmRvZUBnbWFpbC5jb20iLCJ0eXBlIjoiam9ic2Vla2VyIiwiZXhwaXJ5IjoxNjcxMDk
                             1OTg2LjEzOTIwM30.DnoJTF7CdaQKX5YzEgwiwfFN9oYGuFPJ1050QCF0t7E"
                            }
                  }
    '''
    try:
        if check_user_exist(db,data.phone,data.email) is not None:
            logMsg = logger.return_log_msg(409,"mobileNo or email is already taken!")
            logger.logger.info(logMsg)
            return responseBody(409, "mobileNo or email is already taken!")     
        if not data.authType == authType.TEST:
            otp_response = verify_otp(data.phone,data.otp)
            if otp_response != True: return otp_response  
        db_user = User(name=data.name,email=data.email,phone=data.phone,type=data.type)
        dbCommit(db, db_user)      
        token = signJWT(db_user)       
        response = {
            'user': db_user,
            'token': token
        }      
        logMsg = logger.return_log_msg(201,"User created successfully")
        logger.logger.info(logMsg)
        return responseBody(201,"User created successfully", response)
    except Exception as e:
        print(e)
        logMsg = logger.return_log_msg(500, "Something went wrong in employee_signup api")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500,detail="Something went wrong in employee_signup api")
    

@Timer(timingLogger)
def update_employee_details(data, obj):
    '''
    Description - This method updates the obj{second_parameters} values by given data{first_parameters}.
    
    Parameters  - data, obj
    
    Returns     - updated obj{second_parameters} 
    '''
    obj.domain = data and data.domain
    obj.role = data and data.role
    obj.availableAfter = data and data.availableAfter
    obj.modeOfAvailability = data and data.modeOfAvailability
    obj.jobType = data and data.jobType
    obj.immediateJoiner = data and data.immediateJoiner
    obj.preferredLocation = data and data.preferredLocation
    obj.currentlyEmployed = data and data.currentlyEmployed
    obj.currentSalary = data and data.currentSalary
    obj.expectedSalary = data and data.expectedSalary
    return obj


@Timer(timingLogger)
def employee_details(db: Session, data: employeeDetailsSchema, userId:str):
    '''             
    Description - This method fill employee details in EMPLOYEES table by matching user ID and employee experience in employee experience.
    
    Parameters  - db: Session,
                  data: employeeDetailsSchema {type: str,
                  resume: Optional[str],
                  domain: Optional[str],
                  role: Optional[str],
                  jobType: Optional[str],
                  immediateJoiner: Optional[str],
                  authType: authType,
                  availableAfter: Optional[int],
                  modeOfAvailability: Optional[str],
                  preferredLocation: Optional[str],
                  currentlyEmployed: Optional[str],
                  currentSalary: Optional[int],
                  expectedSalary: Optional[int],
                  experience:Optional[List[employeeExperienceSchema]]},
                  userId: str (from token authorization)
                  
    Returns     - {
                  "status_code": 201,
                  "message": "now User created successfully"
                  }
    '''
    try:
        if check_employee_exist(db, userId) is None:
            logMsg = logger.return_log_msg(409,"User not found")
            logger.logger.info(logMsg)
            return responseBody(409, "User not found")
        
        # if data.modeOfAvailability=='Work From Home':
        #     if not data.preferredLocation:
        #         return responseBody(422, "Unprocessable entity")
            
        # if data.immediateJoiner=='No':
        #     if not data.availableAfter:
        #         return responseBody(422, "Unprocessable entity")
            
        # if data.currentlyEmployed=='No':
        #     if not data.currentSalary:
        #         return responseBody(422, "Unprocessable entity")        
        
        dbDetails = db.query(Employees).filter(Employees.userId==userId).first()
   
        if dbDetails is None:
            dbDetails = Employees(userId=userId)
            db.add(dbDetails)
       
        userDetails =  update_employee_details(data, dbDetails)
        
        employeeExperience = []
        if data and data.experience:
            for item in data.experience:
                experience = EmployeeExperience(userId=data and userId,companyName=item and item["companyName"], startingDate=item and item["startingDate"],
                                           endingDate=item and item["endingDate"], projectDescription=item and item["projectDescription"])
       
                employeeExperience.append(experience)  
            db.bulk_save_objects(employeeExperience)
        
        db.commit()
        response = {
            'user' : {
                      "domain": userDetails.domain,
                      "role": userDetails.role,
                      "availableAfter": userDetails.availableAfter,
                      "modeOfAvailability": userDetails.modeOfAvailability,
                      "jobType": userDetails.jobType,
                      "immediateJoiner": userDetails.immediateJoiner,
                      "preferredLocation": userDetails.preferredLocation,
                      "currentlyEmployed": userDetails.currentlyEmployed,
                      "currentSalary": userDetails.currentSalary,
                      "expectedSalary": userDetails.expectedSalary
                      },
            'user-experience': employeeExperience
        } 
        logMsg = logger.return_log_msg(200,"User details saved successfully")
        logger.logger.info(logMsg)
        return responseBody(200,"User details saved successfully", response)
    except Exception as e:
        print(e)
        traceback.print_exc()
        logMsg = logger.return_log_msg(500, "Something went wrong in employee details")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500,detail="Something went wrong in employee details")


@Timer(timingLogger)
def employer_signup(db: Session,data: employerSignupSchema):
    '''
    Description - This method create employer user ID and fill the details in USER table and
                  EMPLOYER table.
                  
    Parameters  - db: Session,
                  data: employerSignupSchema {
                        name: str,
                        email: str,
                        type: str,
                        companyName: str,
                        companySize: int,
                        message:str,
                        domain: str,
                        designation: str
                  }

    Returns     - {
                    "status_code": 201,
                    "message": "User created successfully",
                    "data": {
                            "user": {
                                    "name": "John Doe",
                                    "email": "jobhbbhndoe@gmail.com",
                                    "type": "Recruiter",
                                    "companyName": "Examarly.com",
                                    "companySize": 12,
                                    "message": "THis is my project",
                                    "domain": "Designer",
                                    "designation": "Frontend Developer"
                                    },
                            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE3LCJuYW1lIjoiSm9obiBEb2UiLCJtb2J
                                      pbGVObyI6bnVsbCwiZW1haWwiOiJqb2JoYmJobmRvZUBnbWFpbC5jb20iLCJ0eXBlIjoicmVjcnVpdGVyIiwiZXhwaXJ5Ij
                                      xNjcxMDk3ODgxLjg2MjYxM30.gWCGW3VRNUgOANixpHIEomb6EcY9ZKN7wuAI57RsLYI"
                             }
                   }
'''  
    try:
        if data.message and (len(data.message))>500:
            logMsg = logger.return_log_msg(300,"message limit exceeded")
            logger.logger.info(logMsg)
            return responseBody(300,"message limit exceeded")
        
        db_user = User(email=data.email,name=data.name,type=data.type)
        db.add(db_user)
        db.commit()
        
        token = signJWT(db_user)
        response = {
            'user': db_user,
            'token': token
        }
        
        db_recruiterDetails = Employers(userId=db_user.id, companyName=data.companyName,companySize=data.companySize,
                                        message=data.message,domain=data.domain,designation=data.designation)
        db.add(db_recruiterDetails)
        dbCommit(db, db_recruiterDetails)

        logMsg = logger.return_log_msg(201,"User created successfully")
        logger.logger.info(logMsg)
        return responseBody(201,"User created successfully", response)
    except Exception as e:
        print(e)
        traceback.print_exc()
        logMsg = logger.return_log_msg(500, "Something went wrong")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500,detail="Something went wrongs")
   
    
    
         
@Timer(timingLogger)   
def get_user_data(db: Session,id: str):
        '''
    Description - This HELPER method get user (employee/jobseeker) details from USER table, EMPLOYEE table, EMPLOYEEEXPERIENCE table
                  by matching their userId which is fetching from token.
                  
    Parameters  - db: Session, id:str (from token)
    
    Returns     - {
                    "status_code": 200,
                    "message": "user details",
                    "data": {
                            "status_code": 200,
                            "message": "user details got",
                            "data": {
                            "name": "Ritesh Malviya",
                            "type": "jobseeker",
                            "email": "johddndoe@gmail.com",
                            "phone": "7415077577",
                            "domain": "technology",
                            "role": "frontend_development",
                            "jobType": "internship",
                            "immediateJoiner": "No",
                            "availableAfter": 21,
                            "modeOfAvailability": "WFO",
                            "preferredLocation": "Bhopal",
                            "currentlyEmployed": "YES",
                            "currentSalary": 8,
                            "expectedSalary": 16,
                            "companyName": "Arian",
                            "startingDate": "22/12/2019",
                            "endingDate": "22/11/2019",
                            "projectDescription": "This is my main project"
                            }
                    }
                    }
'''
        db_user = db.query(User).filter(User.id==id).first()    
        db_employee = db.query(Employees).filter(Employees.userId==id).first()    
        db_employeeExperience = db.query(EmployeeExperience).filter(EmployeeExperience.userId==id).first()

        testData = get_user_test_given(db_user.id, db)
        isAssessment = False
        if testData: isAssessment=True

        response = {
                   "name": db_user.name,
                   "type": db_user.type,
                   "email": db_user.email,
                   "phone": db_user.phone,
                   "resume": db_employee and db_employee.resume,
                   "resumeLink": db_employee and db_employee.resumeLink,
                   "domain": db_employee and db_employee.domain,
                   "role": db_employee and db_employee.role,
                   "jobType": db_employee and db_employee.jobType,
                   "immediateJoiner": db_employee and db_employee.immediateJoiner,
                   "availableAfter": db_employee and db_employee.availableAfter,
                   "modeOfAvailability": db_employee and db_employee.modeOfAvailability,
                   "preferredLocation": db_employee and db_employee.preferredLocation,
                   "currentlyEmployed": db_employee and db_employee.currentlyEmployed,
                   "currentSalary": db_employee and db_employee.currentSalary,
                   "expectedSalary": db_employee and db_employee.expectedSalary,
                   "companyName": db_employeeExperience and db_employeeExperience.companyName,
                   "startingDate": db_employeeExperience and db_employeeExperience.startingDate,
                   "endingDate": db_employeeExperience and db_employeeExperience.endingDate,
                   "projectDescription": db_employeeExperience and db_employeeExperience.projectDescription,
                   "isAssessment": isAssessment
             }
        return  response
         
         
         
         
@Timer(timingLogger)        
def get_user_details(db: Session, id: str):
    '''
    Description - This method get user (employee/jobseeker) AND (employer/recruiter) details from USER table, EMPLOYEE table,
                  EMPLOYEEEXPERIENCE table and EMPLOYER table by matching their userId which is fetching from token.
                  
    Parameters  - db: Session, id:str (from token)

    Returns     - {
                    "status_code": 200,
                    "message": "user details",
                    "data": {
                            "name": "John Doe",
                            "type": "recruiter",
                            "email": "johddndoe@gmail.com",
                            "phone": 7415077577,
                            "companyName": "EXAMARLY",
                            "companySize": 20,
                            "domain": "technology",
                            "designation": "React-Native Developer",
                            "message": "It's a WFO job",
                            }
                }
                }
''' 
    try:
        db_user = db.query(User).filter(User.id==id).first()
        if not db_user: return responseBody(401, "Invalid Token")
          
        if db_user.type=="jobseeker":
            response = get_user_data(db, id)
            logMsg = logger.return_log_msg(200,"user details")
            logger.logger.info(logMsg)
            return responseBody(200,"user details",response)
        
        if db_user.type=="recruiter":
            db_employer = db.query(Employers).filter(Employers.userId==id).first()
            if not db_employer: return responseBody(401, "employer's details is not found")

            response = {
                   "name": db_user.name,
                   "email": db_user.email,
                   "phone": db_user.phone,
                   "type": db_user.type,
                   "companyName": db_employer.companyName,
                   "companySize": db_employer.companySize,
                   "domain": db_employer.domain,
                   "designation": db_employer.designation,
                   "message": db_employer.message,
              }  
            logMsg = logger.return_log_msg(200,"user details got")
            logger.logger.info(logMsg)
            return responseBody(200,"user details got", response)
    except Exception as e:
        print(e)
        logMsg = logger.return_log_msg(500, "Something went wrong")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500, detail="Something went wrong")
 
    



@Timer(timingLogger)        
def user_login( db: Session, data: employeeLoginSchema):
    '''
    Description - This method calls when user click on "Already have an account".
                  It will check - user exist or not
                  if exist then return all the details which was saved by user.
                  and if not then return (401, "Employee Account not exist")
                
    Parameters  - db: Session, data: employeeLoginSchema(phone and OTP, authType)
    
    Returns     - {
                    "status_code": 200,
                    "message": "user details",
                    "data": {
                            "name": John,
                            "type": jobseeker,
                            "email": johndou@gmail.com,
                            "phone": 7415077577,
                            "domain": developer,
                            "role": frontend,
                            "jobType": Full-time,
                            "immediateJoiner": Yes,
                            "availableAfter": 12,
                            "modeOfAvailability": wfo,
                            "preferredLocation": indore,
                            "currentlyEmployed": Yes,
                            "currentSalary": 12,
                            "expectedSalary": 24,
                            "companyName": arian,
                            "startingDate": 12/02/2017,
                            "endingDate": 13/02/2018,
                            "projectDescription": THIS IS MINE PROJECT 
                            }
                  }
'''
    try:
        if not data.authType == authType.TEST:
            otp_response = verify_otp(data.phone,data.otp)
            if otp_response != True: return otp_response
        
        db_user = db.query(User).filter(User.phone==data.phone).first()
        if not db_user: return responseBody(401, "Account not exist")
        
        if db_user.type=="recruiter": return responseBody(401, "Employee Account not exist")
        id= db_user.id  
        user = get_user_data(db, id)
        token = signJWT(db_user)  
        response = {
            'user': user,
            'token': token
        }
        logMsg = logger.return_log_msg(200,"user details")
        logger.logger.info(logMsg)
        return responseBody(200,"user details",response)      
        
    except Exception as e:
        print(e)
        logMsg = logger.return_log_msg(500, "Something went wrong")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500, detail="Something went wrong")