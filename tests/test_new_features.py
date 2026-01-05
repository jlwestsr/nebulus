import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, User, Chat, Message, get_db
from routers import chat_routes
from routers.auth_routes import get_current_user


# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter_by(id=1).first()
        if not user:
            user = User(
                id=1,
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                role="user",
                current_model="Llama 3.1",
            )
            db.add(user)
            db.commit()
        return user
    finally:
        db.close()


# Create isolated app for testing
test_app = FastAPI()
test_app.include_router(chat_routes.router)
test_app.dependency_overrides[get_db] = override_get_db
test_app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(test_app)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test user
    if not db.query(User).filter_by(id=1).first():
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            role="user",
            current_model="Llama 3.1",
        )
        db.add(user)
        db.commit()

    yield db
    Base.metadata.drop_all(bind=engine)


def test_history_empty_filtering(test_db):
    # 1. Create an empty chat (should be hidden)
    empty_chat = Chat(id="empty_chat", user_id=1, title="Empty Chat")
    test_db.add(empty_chat)
    test_db.commit()

    # 2. Create a chat with messages (should be shown)
    active_chat = Chat(id="active_chat", user_id=1, title="Active Chat")
    msg = Message(chat_id="active_chat", author="user", content="Hello")
    test_db.add(active_chat)
    test_db.add(msg)
    test_db.commit()

    # Query API
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.json()

    # Verify
    ids = [c["id"] for c in data]
    assert "active_chat" in ids
    assert "empty_chat" not in ids


def test_model_switching(test_db):
    # Initial state
    user = test_db.query(User).filter_by(id=1).first()
    assert user.current_model == "Llama 3.1"

    # Switch model
    new_model = "Llama 3.2 Vision"
    res = client.post("/api/model", json={"model": new_model})
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    assert res.json()["model"] == new_model

    # Verify persistence in DB
    test_db.refresh(user)
    assert user.current_model == new_model
