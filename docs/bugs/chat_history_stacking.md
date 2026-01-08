# Bug: Chat History Stacking

**Status**: Fixed
**Date**: 2026-01-08
**Context**: Chat Interface / History Loading

## Issue Description
When switching between chats using the sidebar (soft navigation), the messages from the requested chat are appended to the current chat window instead of clearing the previous conversation first. This leads to a "stacking" effect where multiple conversations appear sequentially.

## Root Cause
The `handle_soft_navigation` function in `gantry/chat.py` emits `new_message` events for the loaded history but fails to trigger a "clear" or "reset" action on the frontend before doing so.

## Solution Plan
Investigate methods to clear the Chainlit UI.
1.  **Check for Native API**: Does `cl.user_session` or context have a reset?
2.  **Frontend Event**: If usage allows, emit a custom event (e.g., `clear_messages`) and handle it in `public/script.js` (if strictly necessary and supported).
    *   *Self-correction*: Chainlit doesn't natively support arbitrary custom JS event listeners easily without a custom frontend build or `cl.html`.
3.  **Removal Loop**: We might need to track message IDs in the user session and explicitly remove them? That sounds slow.

## Verification
- Load Chat A.
- Load Chat B.
- Verify Chat A's messages are gone and only Chat B's remain.
