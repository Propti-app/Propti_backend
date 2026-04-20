# app/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# CONNECTION POOL SETTINGS
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using.
    pool_recycle=3600,   #Recycle connections every hour
    pool_size=5,         # Max 5 connections
    max_overflow=10,     # Allow 10 extra connections
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





















