import pytest
from unittest.mock import MagicMock, patch

# Global mocks that must be applied BEFORE collection
# Use a context manager to maintain them if needed, or just patch everything
_global_patches = [
    patch("apscheduler.schedulers.background.BackgroundScheduler", MagicMock()),
    patch("apscheduler.schedulers.blocking.BlockingScheduler", MagicMock()),
    patch("apscheduler.jobstores.sqlalchemy.SQLAlchemyJobStore", MagicMock()),
]

for p in _global_patches:
    p.start()


def pytest_unconfigure(config):
    for p in reversed(_global_patches):
        p.stop()


@pytest.fixture(autouse=True, scope="session")
def mock_scheduler():
    """Placeholder to maintain compatibility if tests expect this fixture."""
    yield MagicMock()
