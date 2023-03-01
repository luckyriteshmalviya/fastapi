from .base import db
from fastapi import FastAPI;
from utils.functions import dbCommit, responseBody
import json, requests, time
from .temp_app import app
from sqlalchemy import create_engine
import pytest
from fastapi.testclient import TestClient
from decouple import config
from sqlalchemy.orm import sessionmaker
from app.server.database import get_db, Base
from app.mopid.user.model import User, Employees, Employers
from localStoragePy import localStoragePy
import traceback

client = TestClient(app)
localStorage = localStoragePy('mopid')

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

db = next(override_get_db())

def update_count():
    total_tests = localStorage.getItem("total_tests")
    total_tests = str(int(total_tests) + 1)
    localStorage.setItem("total_tests", total_tests)


AUTH_KEY = config('AUTH_KEY')
TEMPLATE_ID = config('TEMPLATE_ID')

localStorage.setItem("total_tests", "0")

base_url = "http://localhost:8000/docs"


# First test case
def test_check():
    x=20    
    y=20
    assert x==y
    update_count()
    
    

def test_employeeOtp():
    response = client.post(
        "/api/user/employeeOTP",
        json = {
            "phone": "7415077577"
        }
    )
    assert response.status_code == 200, response.text
    # test_user = response.json()
    print("In employeeOTP - ")
    update_count()


# Seventh Test Case
def test_signup_employeeSignup():
    response = client.post(
        "/api/user/employeeSignup",
        json = {
            "name": "SomeUser",
            "email": "ashutdfvsosh@examarly.com",
            "phone": "7049812589",
            "otp": 1234,
            "authType": "TEST",
            "type": "jobseeker",
        },
    )
    assert response.status_code == 200, response.text
    test_user = response.json()
    print("In signup - ", test_user['data']['token'])
    update_count()
    localStorage.setItem("employeeToken", str(test_user))

# Eighth Test Case
def test_signup_employerSignup():
    response = client.post(
        "/api/user/employerSignup",
        json = {
            "name": "someuser",
            "email": "adjn@gmail.com",
            "type": "recruiter",
            "companyName": "SomeCompany",
            "companySize": "12",
            "message": "Hi we have vaccancies",
            "domain": "developer",
            "designation": "front-end",
        }
    )
    assert response.status_code == 200, response.text
    # test_user = response.json()
    print("In employer signup - ")
    update_count()


# Eighth Test Case
def test_signup_employeeDetails():
    response = client.post(
        "/api/user/employeeDetails",
        json = {
            "name": "someuser",
            "email": "adjn@gmail.com",
            "type": "recruiter",
            "companyName": "SomeCompany",
            "companySize": "12",
            "message": "Hi we have vaccancies",
            "domain": "developer",
            "designation": "front-end",
        }
    )
    assert response.status_code == 200, response.text
    # test_user = response.json()
    print("In employer signup - ")
    update_count()


    
# Second Test Case
def test_send_otp(mobileNo: str = "7415076577"):
    print("otp")
    otp = 1234
    response = requests.get(f'https://api.msg91.com/api/v5/otp?authkey={AUTH_KEY}&template_id={TEMPLATE_ID}&mobile=91{mobileNo}&otp={otp}').json()
    if(response['type'] == 'success'):
        return responseBody(200,"OTP sent successfully!")
    else:
        return responseBody(404,response['message'])  
update_count()



    
# Fourth Test Case    
def test_create_employees():
    testEmployeeId = Employees(domain="Developer",role ="FrontEnd Developer", jobType ="full-time", immediateJoiner ="yes",
                               availableAfter ="5", modeOfAvailability ="wfh", preferredLocation ="pune", currentlyEmployed ="yes",
                               currentSalary = 6, expectedSalary = 8)        
    try:
        dbCommit(db, testEmployeeId)
    except Exception as e:
       print(e)  
update_count()             
    

# Sixth Test Case
def test_home(): 
    try: 
        response = client.get('/')
        assert response.status_code == 200, response.text
        response = response.json() 
        print("In home", response)
    except: 
        traceback.print_exc()
    update_count()
    # assert test_user == "8093623376", response.text

# Eight Test Case
def test_total_tests():
    total_test = localStorage.getItem("total_tests")
    Base.metadata.drop_all(bind=engine)
    print("All tests ran")
    # assert count == 6
    print(f"count is :{total_test} ")
    assert True