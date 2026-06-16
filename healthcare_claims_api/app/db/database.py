from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Engine = DB sanga connection
engine = create_engine(DATABASE_URL)

# SessionLocal = har request ko lagi ek DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = sabai models inherit garchhan (Django ko models.Model jastai)
Base = declarative_base()

# Dependency — FastAPI route ma DB session inject garchha
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()