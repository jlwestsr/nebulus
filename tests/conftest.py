import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True, scope="session")
def mock_scheduler():
    """Globally mock the task scheduler to prevent database writes during tests."""
    with patch("mcp_server.scheduler.BackgroundScheduler") as mock_bg:
        mock_instance = MagicMock()
        mock_bg.return_value = mock_instance
        yield mock_instance
