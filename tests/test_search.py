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
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role="user",
    )


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
        user = User(id=1, username="testuser", email="test@example.com", role="user")
        db.add(user)

        # Create test chats and messages
        chat1 = Chat(id="chat1", user_id=1, title="Python Chat")
        msg1 = Message(
            chat_id="chat1", author="user", content="I love Python programming"
        )
        msg2 = Message(chat_id="chat1", author="assistant", content="Python is great")

        chat2 = Chat(id="chat2", user_id=1, title="Cooking Chat")
        msg3 = Message(chat_id="chat2", author="user", content="How to cook pasta?")

        db.add_all([chat1, msg1, msg2, chat2, msg3])
        db.commit()

    yield db
    Base.metadata.drop_all(bind=engine)


def test_search_api(test_db):
    # Search for "Python"
    res = client.get("/api/search?q=Python")
    assert res.status_code == 200, f"Response: {res.text}"
    data = res.json()
    assert len(data) >= 2
    assert any(d["chat_id"] == "chat1" for d in data)

    # Search for "pasta"
    res = client.get("/api/search?q=pasta")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["chat_id"] == "chat2"

    # Search for non-existent
    res = client.get("/api/search?q=xyz123")
    assert res.status_code == 200
    assert len(res.json()) == 0

    # Empty search
    res = client.get("/api/search?q=")
    assert res.json() == []
