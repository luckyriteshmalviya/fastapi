from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from typing import Optional, List
from sqlalchemy.orm import Session
from app.utils.jwtHandler import hasAccess, getToken
from .schema import *
from ...server.database import get_db
from .helper import employee_signup, employer_signup, employee_details, send_otp, get_user_details, user_login
from .GcpUpload import upload_file_in_gcp, download_file_from_gcp

userRouter = APIRouter()
   
@userRouter.post('/employeeOTP')
def call(data: employeeOtpSchema , db: Session = Depends(get_db)):
    return send_otp(db, data.phone, data.isLogin)   
   
@userRouter.post('/employeeSignup')
def call(data: employeeSignupSchema , db: Session = Depends(get_db)):
    return employee_signup(db, data)
  
@userRouter.post('/employeeDetails')
def call(data: employeeDetailsSchema , db: Session = Depends(get_db), key = Depends(hasAccess)):
    return employee_details(db, data, key['id'])

@userRouter.post('/employerSignup')
def call(data: employerSignupSchema , db: Session = Depends(get_db)):
    return employer_signup(db, data)

@userRouter.get('/userDetail')
def call(key = Depends(hasAccess), db: Session = Depends(get_db)):
    return get_user_details(db, key['id'])

@userRouter.post('/userLogin')
def call(data: employeeLoginSchema, db: Session = Depends(get_db)):
    return user_login(db, data)

@userRouter.post('/uploadResume')
def call(file: UploadFile, key = Depends(hasAccess), db: Session = Depends(get_db)):
    return upload_file_in_gcp(db, file, key['id'])

@userRouter.post('/checkGCPStorage')
def call():
    return download_file_from_gcp()
