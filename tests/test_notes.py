import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from gantry.database import Base, User, get_db
from gantry.routers import notes_routes
from gantry.routers.notes_routes import get_current_user_id

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


def override_get_current_user_id():
    return 1


# Create isolated app for testing
test_app = FastAPI()
test_app.include_router(notes_routes.router)
test_app.dependency_overrides[get_db] = override_get_db
test_app.dependency_overrides[get_current_user_id] = override_get_current_user_id

client = TestClient(test_app)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test user
    if not db.query(User).filter_by(id=1).first():
        user = User(id=1, username="testuser", email="test@example.com", role="user")
        db.add(user)
        db.commit()

    yield db
    Base.metadata.drop_all(bind=engine)


def test_create_note(test_db):
    response = client.post(
        "/api/notes", json={"title": "My Test Note", "content": "This is content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Test Note"
    assert data["content"] == "This is content"
    assert "id" in data


def test_get_notes(test_db):
    response = client.get("/api/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "My Test Note"


def test_update_note(test_db):
    # Get the note first
    notes = client.get("/api/notes").json()
    note_id = notes[0]["id"]

    response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"


def test_get_single_note(test_db):
    # Get note id
    notes = client.get("/api/notes").json()
    note_id = notes[0]["id"]

    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"


def test_delete_note(test_db):
    # Create a dummy note to delete
    res = client.post("/api/notes", json={"title": "To Delete", "content": "..."})
    note_id = res.json()["id"]

    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200

    # Verify it is gone
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 404
