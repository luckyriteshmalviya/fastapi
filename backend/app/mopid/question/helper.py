from .schema import addQuestionSchema, reportQuestionSchema, bookmarkQuestionSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .model import *
from ...utils.functions import responseBody, dbCommit, getUniqueId
import requests

def add_question(db: Session): 
    try:
    
        questions = requests.get('http://localhost:8000/api/question/test')
        questions = questions.json()

        testId = getUniqueId()

        return responseBody(200, "Test Created Successfully!", questions)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))