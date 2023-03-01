from fastapi import APIRouter, Depends, UploadFile
from ...utils.jwtHandler import isAdminAccess
from fastapi.param_functions import File
from sqlalchemy.orm import Session
from ...server.database import get_db
from .helper import add_questions, add_images
from .schema import ImageUploadType

questionRouter = APIRouter()
 
@questionRouter.post('/questions')
def call(file: UploadFile = File(), key = Depends(isAdminAccess), db: Session = Depends(get_db)):
    return add_questions(file, db) 

@questionRouter.post('/images')
def call(type: ImageUploadType, file: UploadFile = File(), key = Depends(isAdminAccess)): 
    return add_images(type, file)