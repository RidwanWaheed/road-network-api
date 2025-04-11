"""
Manual database session setup - use this if automatic configuration is not working
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Direct database URL without using settings - for troubleshooting
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/roadnetworkdb"

# Create engine directly
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

