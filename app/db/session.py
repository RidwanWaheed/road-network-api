# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import settings

# Use environment variable with fallback to settings
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Create engine using settings from config
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()