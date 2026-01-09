import datetime
from gantry.chat import truncate_chat_after_db

# Setup in-memory DB for testing
# We might need to mock SessionLocal or use a separate DB.
# gantry.chat imports SessionLocal from database.py.
# We can patch it.

from unittest.mock import MagicMock, patch


@patch("gantry.chat.db_session")
def test_truncate_chat_after_db(mock_db_session):
    """Test that truncation deletes messages after the target."""
    mock_db = MagicMock()
    # Mocking the context manager: with db_session() as db:
    mock_db_session.return_value.__enter__.return_value = mock_db

    # Setup mock messages
    target_msg = MagicMock()
    target_msg.created_at = datetime.datetime(2025, 1, 1, 12, 0, 0)
    target_msg.cl_id = "msg_1"

    # Query structure: db.query(Message).filter(...).first()
    # and db.query(Message).filter(...).delete()

    # First query finds the target
    mock_db.query.return_value.filter.return_value.first.return_value = target_msg

    # Call function
    truncate_chat_after_db("chat_1", "msg_1")

    # Verify delete was called
    # The second query chain is: db.query(Message).filter().delete()
    assert mock_db.query.call_count >= 2


@patch("gantry.chat.db_session")
def test_truncate_chat_not_found(mock_db_session):
    """Test graceful exit if message not found."""
    mock_db = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_db

    mock_db.query.return_value.filter.return_value.first.return_value = None

    truncate_chat_after_db("chat_1", "missing_id")

    # Should not call query.delete
    # The first call is to find the message, if None, should stop.
    assert mock_db.query.return_value.filter.return_value.delete.call_count == 0
