from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

#Database connection string 
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stockx:stockx123@localhost:5432/stockx")
# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()