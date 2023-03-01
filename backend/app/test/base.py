from fastapi.testclient import TestClient
from .temp_app import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from app.server.database import get_db, Base
from app.utils.functions import dbCommit

import pytest
from httpx import AsyncClient

import os
import csv

from localStoragePy import localStoragePy

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
