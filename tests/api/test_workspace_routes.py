from fastapi.testclient import TestClient
from gantry.main import app
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

client = TestClient(app)
# Bypass AuthMiddleware
client.cookies = {"access_token": "valid_token"}

# Mock Ollama Response
MOCK_MODELS_RESPONSE = MagicMock()
MOCK_MODELS_RESPONSE.data = [
    MagicMock(
        id="llama3:latest",
        size=4000000000,
        model_dump=lambda: {"name": "llama3:latest", "size": 4000000000},
    ),
    MagicMock(
        id="nomic-embed-text:latest",
        size=500000000,
        model_dump=lambda: {"name": "nomic-embed-text:latest", "size": 500000000},
    ),
]


@pytest.fixture(autouse=True)
def mock_auth():
    """Mock authentication for all tests."""
    with (
        patch("middleware.verify_token", return_value=True),
        patch("middleware.get_user_count", return_value=1),
    ):
        yield


@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_list_models(mock_get):
    """Test listing models via API."""
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "models": [
                {
                    "name": "llama3:latest",
                    "size": 4000000000,
                    "details": {"family": "llama"},
                },
                {
                    "name": "nomic-embed-text:latest",
                    "size": 500000000,
                    "details": {"family": "bert"},
                },
            ]
        },
    )

    response = client.get("/api/workspace/models")

    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) == 2
    assert data["models"][0]["name"] == "llama3:latest"
    assert data["models"][0]["size"] == 4000000000


@patch("httpx.post")
def test_pull_model(mock_post):
    """Test triggering a model pull."""
    mock_post.return_value = MagicMock(status_code=200, text="Success")

    response = client.post("/api/workspace/models/pull", json={"name": "tinyllama"})

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify call to external Ollama
    mock_post.assert_called_once()
    assert "api/pull" in mock_post.call_args[0][0]


def test_list_tools():
    """Test listing tools."""
    response = client.get("/api/workspace/tools")

    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 1
    assert data["tools"][0]["name"] == "web_search"


def test_list_knowledge():
    """Test listing knowledge (mock)."""
    response = client.get("/api/workspace/knowledge")

    assert response.status_code == 200
    data = response.json()
    assert "collections" in data
    assert data["collections"][0]["name"] == "default"
