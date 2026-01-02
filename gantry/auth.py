import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import User

# Configuration
SECRET_KEY = os.getenv("CHAINLIT_AUTH_SECRET", "supersecret-dev-key-change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(
    db: Session, full_name: str, email: str, password: str, role: str = "user"
):
    hashed_password = get_password_hash(password)
    db_user = User(
        username=email,  # Enforce email as username
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_count(db: Session) -> int:
    return db.query(User).count()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
