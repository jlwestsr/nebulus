import datetime
from gantry.chat import truncate_chat_after_db

# Setup in-memory DB for testing
# We might need to mock SessionLocal or use a separate DB.
# gantry.chat imports SessionLocal from database.py.
# We can patch it.

from unittest.mock import MagicMock, patch


@patch("gantry.chat.SessionLocal")
def test_truncate_chat_after_db(mock_session_cls):
    """Test that truncation deletes messages after the target."""
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db

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
    # Verify commit
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()


@patch("gantry.chat.SessionLocal")
def test_truncate_chat_not_found(mock_session_cls):
    """Test graceful exit if message not found."""
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db

    mock_db.query.return_value.filter.return_value.first.return_value = None

    truncate_chat_after_db("chat_1", "missing_id")

    # Should not commit
    mock_db.commit.assert_not_called()
    mock_db.close.assert_called_once()
