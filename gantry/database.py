import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database Setup
DB_PATH = os.getenv("DB_PATH", "sqlite:///./data/gantry.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    # Create data directory if it doesn't exist
    if "sqlite" in DB_PATH:
        db_file = DB_PATH.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    Base.metadata.create_all(bind=engine)
