import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, User, Chat, Message, get_db
from main import app
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


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)
client.cookies = {"access_token": "valid_token"}


@pytest.fixture(autouse=True)
def mock_auth_checks():
    # Patch verify_token and get_user_count to bypass auth middleware redirects
    with (
        patch("middleware.verify_token", return_value=True),
        patch("middleware.get_user_count", return_value=1),
    ):
        yield


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test user if not exists
    if not db.query(User).filter_by(id=1).first():
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="user",
        )
        db.add(user)
        db.commit()

    yield db
    Base.metadata.drop_all(bind=engine)


def test_bulk_delete_api(test_db):
    # 1. Seed Data
    # Create chats
    chat1 = Chat(id="chat_1", user_id=1, title="Chat 1")
    chat2 = Chat(id="chat_2", user_id=1, title="Chat 2")
    test_db.add_all([chat1, chat2])
    test_db.commit()

    # Create messages
    msg1 = Message(chat_id="chat_1", author="user", content="Hello", cl_id="msg_1")
    msg2 = Message(chat_id="chat_1", author="assistant", content="Hi", cl_id="msg_2")
    msg3 = Message(chat_id="chat_2", author="user", content="Test", cl_id="msg_3")
    test_db.add_all([msg1, msg2, msg3])
    test_db.commit()

    # Verify Seed
    assert test_db.query(Chat).filter(Chat.user_id == 1).count() == 2
    assert test_db.query(Message).count() == 3

    # Debug: Print all routes and Remove Root Mount
    # (Cleaned up as the issue was AuthMiddleware redirect)

    # 2. Call Bulk Delete Endpoint
    res = client.delete("/api/chats")
    assert res.status_code == 200
    assert res.json() == {"status": "success"}

    # 3. Verify Deletion
    # Use a new session or expire all to ensure we get fresh data
    test_db.expire_all()

    assert test_db.query(Chat).filter(Chat.user_id == 1).count() == 0
    # Messages should be cascaded or explicitly deleted
    assert test_db.query(Message).count() == 0
