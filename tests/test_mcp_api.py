import os
import sys
import importlib
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch

# Add mcp_server to path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../mcp_server"))
)


def dummy_wrapper():
    def decorator(func):
        return func

    return decorator


# Mock FastMCP to return a real FastAPI app and pass-through decorator
with patch("mcp.server.fastmcp.FastMCP") as MockFastMCP:
    mock_instance = MockFastMCP.return_value
    mock_instance.sse_app.return_value = FastAPI()
    mock_instance.tool.side_effect = dummy_wrapper

    import server

    importlib.reload(server)
    from server import app


client = TestClient(app)


def test_health_check():
    """Verify health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("server.scheduler")
def test_list_tasks_api(mock_scheduler):
    """Verify list tasks endpoint."""
    mock_scheduler.get_tasks.return_value = [{"id": "1", "name": "Task 1"}]

    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "name": "Task 1"}]


@patch("server.scheduler")
def test_add_task_api(mock_scheduler):
    """Verify add task endpoint."""
    mock_scheduler.add_task.return_value = "Task scheduled"

    payload = {"title": "New Task", "prompt": "Do something", "schedule": "0 8 * * *"}

    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Task scheduled"}

    # Test missing fields
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400


@patch("server.scheduler")
def test_delete_task_api(mock_scheduler):
    """Verify delete task endpoint."""
    mock_scheduler.delete_task.return_value = "Deleted"

    response = client.delete("/api/tasks/job123")
    assert response.status_code == 200
    assert response.json() == {"message": "Deleted"}
    mock_scheduler.delete_task.assert_called_with("job123")


@patch("server.scheduler")
def test_run_task_api(mock_scheduler):
    """Verify run task endpoint."""
    mock_scheduler.run_task.return_value = "Executed"

    response = client.post("/api/tasks/job123/run")
    assert response.status_code == 200
    assert response.json() == {"message": "Executed"}
    mock_scheduler.run_task.assert_called_with("job123")

    # Test failure
    mock_scheduler.run_task.return_value = "Error: Not found"
    response = client.post("/api/tasks/invalid/run")
    assert response.status_code == 404
