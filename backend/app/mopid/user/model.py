from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from app.server.database import Base 

class User(Base): 
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True) 
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(Integer, nullable=True)
    type = Column(String, default="jobseeker")
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)

class Employees(Base): 
    __tablename__ = "employees"
    id = Column(Integer,  primary_key=True,  nullable=False) 
    userId= Column(Integer, ForeignKey("user.id"), unique=True)
    resume = Column(String)
    resumeLink= Column(String)
    domain = Column(String, nullable=True)
    role = Column(String, nullable=True)
    jobType = Column(String, nullable=True, default="Full Time Role")
    immediateJoiner = Column(String, default="Yes" , nullable=True)
    availableAfter = Column(Integer, nullable=True)
    modeOfAvailability = Column(String, default="Work From Home", nullable=True)
    preferredLocation = Column(String, nullable=True)
    currentlyEmployed = Column(String,nullable=True)
    currentSalary = Column(Integer, nullable=True)
    expectedSalary = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)


class Employers(Base): 
    __tablename__ = "employers"
    id = Column(Integer,  primary_key=True, nullable=False) 
    userId= Column(Integer, ForeignKey("user.id"), unique=True)
    companyName = Column(String, nullable=False)
    companySize = Column(Integer, nullable=False)
    domain = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    message = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)


class EmployeeExperience(Base):
    __tablename__ = "employeeExperience"
    id = Column(Integer,  primary_key=True, nullable=False) 
    userId= Column(Integer, ForeignKey("user.id"))
    companyName = Column(String)
    startingDate = Column(String, nullable=True)
    endingDate = Column(String, nullable=True)
    projectDescription = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)