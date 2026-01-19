# Feature: Bulk Delete Chats

## 1. Overview
**Branch**: `feat/bulk-delete-chats`

This feature enables users to bulk delete their chat history in Nebulus Gantry via a conversational command (e.g., `/clear_all`). This provides a quick way to sanitize the workspace and remove outdated discussions without manual deletion of individual chats.

## 2. Requirements
- [ ] Users can trigger bulk deletion by sending a specific command (e.g., `/clear_all` or `/prune_history`).
- [ ] The command must delete all chat records associated with the current user from the database.
- [ ] The command should delete associated messages and feedback (cascading delete).
- [ ] The UI should ideally reflect the cleared history (though a refresh might be needed due to Chainlit limitations).
- [ ] A confirmation message should be displayed to the user.

## 3. Technical Implementation
- **Modules**: `gantry/chat.py`
- **Dependencies**: None (uses existing SQLAlchemy session).
- **Data**: Deletes rows from `chats`, `messages`, and `feedback` tables.

## 4. Verification Plan
**Automated Tests**:
- [ ] verification of DB state before/after command.

**Manual Verification**:
- [ ] Login to Gantry.
- [ ] Create multiple chats.
- [ ] Type `/clear_all`.
- [ ] Verify chats are gone from DB and UI (after refresh).

## 5. Workflow Checklist
- [ ] **Branch**: Created `feat/bulk-delete-chats`?
- [ ] **Work**: Implemented `/clear_all` handler?
- [ ] **Test**: Verified DB operations?
- [ ] **Doc**: Updated walkthrough?
- [ ] **Data**: Merged to develop?
