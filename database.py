from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String, Boolean, Float
from typing import Optional


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fastapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# host='localhost',
#             database='fastapi',
#             user='postgres',
#             password='postgres',
#             cursor_factory=RealDictCursor


# TO TALK TO THE DB YOU NEED TO CREATE A SESSION
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base= declarative_base()

