import os
from contextlib import contextmanager
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database Setup
DB_PATH = os.getenv("DB_PATH", "sqlite:///./data/gantry.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="Untitled")
    content = Column(String, default="")
    category = Column(String, default="Uncategorized", nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="notes")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")
    current_model = Column(String, default="Llama 3.1")
    created_at = Column(DateTime, default=datetime.utcnow)
    chats = relationship("Chat", back_populates="user")
    folders = relationship("Folder", back_populates="user")
    notes = relationship("Note", back_populates="user")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="folders")
    chats = relationship("Chat", back_populates="folder")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, index=True)  # Chainlit Session ID
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    folder = relationship("Folder", back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    cl_id = Column(String, unique=True, nullable=True)  # Chainlit Message UUID
    chat_id = Column(String, ForeignKey("chats.id"))
    author = Column(String)  # User or Assistant
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", uselist=False)


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(String, ForeignKey("chats.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))
    model = Column(String)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Integer, default=0)  # Cost in micro-units
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    chat = relationship("Chat")
    message = relationship("Message")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    score = Column(Integer)  # 1 for up, -1 for down (or 0)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="feedback")


def init_db():
    # Create data directory if it doesn't exist
    if "sqlite" in DB_PATH:
        db_file = DB_PATH.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    Base.metadata.create_all(bind=engine)


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_db():
    """Simple migration to add missing columns or tables"""
    # Base.metadata.create_all handles table creation if they don't exist
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        try:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN current_model VARCHAR DEFAULT 'Llama 3.1'"
                )
            )
            print("Migration: Added current_model column.")
        except Exception:
            pass

        try:
            conn.execute(
                text(
                    "ALTER TABLE notes ADD COLUMN category VARCHAR DEFAULT 'Uncategorized'"
                )
            )
            print("Migration: Added category column to notes.")
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE messages ADD COLUMN cl_id VARCHAR"))
            print("Migration: Added cl_id column to messages.")
        except Exception as e:
            # cl_id likely exists or other error
            print(f"Migration cl_id check: {e}")
            pass
