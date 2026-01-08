# Feature: Response Controls

## 1. Overview
**Branch**: `feat/response-controls`

Implement a standard set of interaction controls for chat messages to allow users to manage the conversation flow and provide feedback.

## 2. Requirements
List specific, testable requirements:
- [x] **Message Actions**:
    - [x] **Regenerate**: specific button on the latest assistant message to re-run the prompt.
    - [x] **Edit**: specific button on user messages to edit the text and re-submit (truncating subsequent history).
    - [x] **Copy**: One-click copy button for raw markdown content of any message.
    - [x] **Feedback**: Thumbs up/down icons on assistant messages to log quality.

## 3. Technical Implementation
- **Modules**: `gantry/ui/actions.py`, `gantry/api/chat.py`
- **Dependencies**: Clipboard API for copy.
- **Data**: Feedback table (message_id, rating, optional_comment).

## 4. Verification Plan
**Automated Tests**:
- [x] Script: `pytest tests/ui/test_actions.py`
- [x] Logic Verified: Edit triggers branch/truncate in history, Regenerate calls LLM again.

**Manual Verification**:
- [x] Step 1: Send a message. Click "Copy" and check clipboard.
- [x] Step 2: Edit the message. Verify old response is removed and new one generates.
- [x] Step 3: Rate a response. Check database/logs for feedback entry.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/response-controls` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
