# Bug: Missing Edit Icon

**Status**: Planned
**Date**: 2026-01-08
**Context**: Chat Interface / Message Editing

## Issue Description
The "Edit" icon (pencil) does not appear when hovering over user messages in the chat interface, preventing users from modifying their previous prompts.

## Root Cause
Chainlit requires the `@cl.on_message_update` event handler to be defined in the backend (`chat.py`) to enable the edit functionality on the frontend. This handler is currently missing, so the frontend disables the feature even though `edit_message = true` is set in `config.toml`.

## Solution Plan
Implement the `on_message_update` handler in `gantry/chat.py`.

### Backend Changes (`chat.py`)
1.  **Define Handler**: Add `@cl.on_message_update`.
2.  **Update Database**: Update the message content in the database using `save_user_message_db` (or similar logic).
3.  **Truncate History**: Remove messages that occurred *after* the edited message to maintain conversation consistency.
4.  **Regenerate Response**: Trigger a new AI response for the modified context.

```python
@cl.on_message_update
async def on_update(message: cl.Message):
    # Logic to update DB, truncate future messages, and regenerate response
    pass
```

## Verification
- Restart the application.
- Send a message.
- Verify the Edit icon appears on hover.
- Edit the message and save.
- Verify the AI generates a new response based on the edit.
