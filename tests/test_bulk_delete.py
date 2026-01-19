from unittest.mock import MagicMock, patch
from gantry.chat import delete_all_chats_for_user_db


@patch("gantry.chat.db_session")
def test_delete_all_chats_for_user_db(mock_db_session):
    """Verifies that the helper deletes messages and chats for the user."""
    # Setup Mock DB Session
    mock_db = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_db

    # Setup User ID
    user_id = 123

    # Setup Mock Chats Return
    mock_chat_1 = MagicMock()
    mock_chat_1.id = "chat_1"
    mock_chat_2 = MagicMock()
    mock_chat_2.id = "chat_2"

    # Mock chain for finding chats: db.query(Chat).filter(...).all()
    # 1. query(Chat) -> QueryObj
    # 2. filter(...) -> QueryObj
    # 3. all() -> [chat1, chat2]
    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_chat_1,
        mock_chat_2,
    ]

    # Setup Mock Delete Return
    # We expect two delete calls: one for messages, one for chats.
    # We can mock the return value of delete() to be a number.
    mock_db.query.return_value.filter.return_value.delete.return_value = 2

    # Execute
    deleted_count = delete_all_chats_for_user_db(user_id)

    # Assertions
    assert deleted_count == 2

    # Verify Logic
    # 1. Verify we queried for chats for this user
    # Note: Checking exact filter args with SQLAlchemy mocks is tricky,
    # but we can check call counts.
    assert (
        mock_db.query.call_count >= 3
    )  # Query Chats, Query Messages, Query Chats (Delete)

    # 2. Verify Delete Calls were made with synchronize_session=False
    delete_calls = mock_db.query.return_value.filter.return_value.delete.call_args_list
    assert len(delete_calls) == 2
    assert delete_calls[0].kwargs["synchronize_session"] is False  # Messages
    assert delete_calls[1].kwargs["synchronize_session"] is False  # Chats
