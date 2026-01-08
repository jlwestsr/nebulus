# Bug: Chat History Rendering Issues

**Status**: Planned
**Date**: 2026-01-08
**Context**: Chat Interface / History Loading

## Issue Description
When loading an old chat from the history sidebar, user messages are displayed with the AI styling (and potentially missing icons), and the message bubble orientation is incorrect (left instead of right).

## Root Cause
The `load_history` function in `gantry/chat.py` currently checks `if msg.author == "User"` to determine if a message is from the user. However, messages are stored in the database with the lowercase author string `"user"` (set in `save_user_message_db`). This case mismatch causes `load_history` to classify user messages as "assistant_message".

## Solution Plan
Update the author check in `chat.py` to be case-insensitive or strictly match the stored format.

### Backend Changes (`chat.py`)
Modify the message dictionary construction loop inside the `/load_history` command handler:

```python
# Before
"type": ("user_message" if msg.author == "User" else "assistant_message"),

# After
"type": ("user_message" if msg.author.lower() == "user" else "assistant_message"),
```

## Verification
- Reload the application.
- Open an existing chat from the sidebar.
- Verify that user messages are correctly styled (right-aligned, user color) and attributed.
