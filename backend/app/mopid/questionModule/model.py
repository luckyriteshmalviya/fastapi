from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from app.server.database import Base 

class Questions(Base):
    __tablename__ = "questions"
    id = Column(Integer,  primary_key=True, nullable=False, autoincrement=True) 
    uid= Column(String, nullable=False, unique=True)
    content = Column(String, nullable=False)
    tags = Column(JSON, default={
        "tags": ""
        })
    type = Column(String)
    status = Column(String, default="active")
    image =  Column(String, default=None)
    is_reported = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    
class QuestionsOptions(Base): 
    __tablename__ = "questions_options"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    uid = Column(String, nullable=False, unique=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    content = Column(String, nullable=False)
    image =  Column(String, default=None)
    status = Column(String, default="active")
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    
class QuestionsSolution(Base): 
    __tablename__ = "questions_solution"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    uid = Column(String, nullable=False, unique=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    image =  Column(String, default=None)
    option_id = Column(Integer, ForeignKey("questions_options.id"))
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    
