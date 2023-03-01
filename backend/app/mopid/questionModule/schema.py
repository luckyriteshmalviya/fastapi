from pydantic import BaseModel
from enum import Enum

class ImageUploadType(str, Enum): 
    question = "question"
    solution = "solution"
    option = "option"