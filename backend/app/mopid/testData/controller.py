from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.jwtHandler import hasAccess, getToken
from .schema import submitTestSchema
from ...server.database import get_db
from .helper import submit_test, get_user_test, question_count


testRouter = APIRouter()

@testRouter.post('/getTest')
def call(key = Depends(hasAccess), db: Session = Depends(get_db)):
    return get_user_test(key['id'], db)

@testRouter.post('/submit')
def call(data: submitTestSchema, key = Depends(hasAccess), db: Session = Depends(get_db)):
    return submit_test(data, key['id'], db)

@testRouter.post('/questionCount')
def call(key = Depends(hasAccess), db: Session = Depends(get_db)):
    return question_count(key['id'], db)
  