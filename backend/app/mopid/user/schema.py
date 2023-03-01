from pydantic import BaseModel, Field
from fastapi import Form
from enum import Enum
from typing import List, Optional
# import json

class authType(str, Enum):
   MOBILE = 'MOBILE'
   FACEBOOK = 'FACEBOOK'
   GOOGLE = 'GOOGLE'
   TEST = 'TEST'
   
class employeeOtpSchema(BaseModel):
    phone: int = Field(..., example=9876543219)
    isLogin: bool = Field(..., example=False)
    
class employeeSignupSchema(BaseModel):
    name: str = Field(...,example='John Doe')
    email: str = Field(...,example='johndoe@gmail.com')
    authType: authType
    phone: str = Field(...,min_length=10,max_length=10,example=8847264356)
    otp: int = Field(..., gt=999, example='1234')
    type: str = Field('Jobseeker')

class employeeExperienceSchema(BaseModel):    
    companyName: Optional[str]
    startingDate: Optional[str]
    endingDate: Optional[str]
    projectDescription: Optional[str]
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return value
        return value
    
class employeeDetailsSchema(BaseModel):
    type: str = Field(..., example='Jobseeker')
    resume: Optional[str]
    domain: Optional[str]
    role: Optional[str]
    jobType: Optional[str]
    immediateJoiner: Optional[str]
    authType: authType
    availableAfter: Optional[int]
    modeOfAvailability: Optional[str]
    preferredLocation: Optional[str]
    currentlyEmployed: Optional[str]
    currentSalary: Optional[int]
    expectedSalary: Optional[int]
    experience:Optional[List[employeeExperienceSchema]]

class employerSignupSchema(BaseModel):
    name: str = Field(...,example='John Doe')
    email: str = Field(...,example='johndoe@gmail.com')
    type: str = Field(..., example='Recruiter')
    companyName: str = Field(..., example='Examarly.com')
    companySize: int = Field(..., example=12)
    message:str = Field(..., example='THis is my project')
    domain: str = Field(..., example='Designer')
    designation: str = Field(..., example='Frontend Developer')

class employeeLoginSchema(BaseModel):
    phone: int = Field(..., example=7415077577)
    otp: int = Field(..., gt=999, example=1234)
    authType: authType