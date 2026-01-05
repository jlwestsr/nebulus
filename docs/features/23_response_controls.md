# Feature: Response Controls

## 1. Overview
**Branch**: `feat/response-controls`

Implement a standard set of interaction controls for chat messages to allow users to manage the conversation flow and provide feedback.

## 2. Requirements
List specific, testable requirements:
- [ ] **Message Actions**:
    - [ ] **Regenerate**: specific button on the latest assistant message to re-run the prompt.
    - [ ] **Edit**: specific button on user messages to edit the text and re-submit (truncating subsequent history).
    - [ ] **Copy**: One-click copy button for raw markdown content of any message.
    - [ ] **Feedback**: Thumbs up/down icons on assistant messages to log quality.

## 3. Technical Implementation
- **Modules**: `gantry/ui/actions.py`, `gantry/api/chat.py`
- **Dependencies**: Clipboard API for copy.
- **Data**: Feedback table (message_id, rating, optional_comment).

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/ui/test_actions.py`
- [ ] Logic Verified: Edit triggers branch/truncate in history, Regenerate calls LLM again.

**Manual Verification**:
- [ ] Step 1: Send a message. Click "Copy" and check clipboard.
- [ ] Step 2: Edit the message. Verify old response is removed and new one generates.
- [ ] Step 3: Rate a response. Check database/logs for feedback entry.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/response-controls` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
