import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Chat, Message, UsageLog
from metrics.usage import log_usage, calculate_cost

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Create mock data
        user = User(id=1, email="test@example.com", username="testuser")
        chat = Chat(id="test-chat", user_id=1)
        db.add(user)
        db.add(chat)
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_calculate_cost():
    # Test unknown model uses default (0 cost)
    assert calculate_cost("unknown", 100, 100) == 0

    # Test specific model (currently all free, but logic should work)
    assert calculate_cost("llama3.1:latest", 500, 500) == 0


def test_log_usage(db):
    # Create a message first
    msg = Message(
        id=1, chat_id="test-chat", author="assistant", content="Hello", cl_id="cl-1"
    )
    db.add(msg)
    db.commit()

    entry = log_usage(db, 1, "test-chat", 1, "llama3.1:latest", 10, 20)

    assert entry.total_tokens == 30
    assert entry.prompt_tokens == 10
    assert entry.completion_tokens == 20
    assert entry.model == "llama3.1:latest"

    # Verify in DB
    db_entry = db.query(UsageLog).first()
    assert db_entry is not None
    assert db_entry.total_tokens == 30
