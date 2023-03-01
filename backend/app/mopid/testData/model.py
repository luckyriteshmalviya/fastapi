from app.server.database import Base 
from sqlalchemy import Column,Integer, String, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.sqltypes import Boolean
from datetime import datetime

class TestResult(Base):
    __tablename__ = "testResult"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(String, nullable=False, unique=True)
    questionCount = Column(Integer, nullable=False)
    isPass = Column(Boolean, default=False)
    score = Column(Integer, default=0,nullable=False)
    submit = Column(Boolean, default=False)
    userId = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)

class TestQuestions(Base):
    __tablename__ = "testQuestions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    testId = Column(String, ForeignKey("testResult.uid"))
    questionId = Column(String)
    isCorrect = Column(Boolean, default=False)
    timeTaken = Column(String, default='0')

class TestOptions(Base):
    __tablename__ = "testOptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    marksPerQuestion = Column(Integer, default=10)
    timePerQuestion = Column(Integer, default=1)
    cutoff = Column(Integer, default=60)
    
