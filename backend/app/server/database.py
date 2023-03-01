from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

SQL_HOST = config('SQL_HOST')
SQL_DB_NAME=config('SQL_DB_NAME')
SQL_USERNAME = config('SQL_USERNAME')
SQL_PASSWORD = config('SQL_PASSWORD')

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_HOST}/{SQL_DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
conn = engine.connect()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
