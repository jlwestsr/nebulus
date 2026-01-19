# Feature: Bulk Delete Chats

## 1. Overview
**Branch**: `feat/bulk-delete-chats`

This feature enables users to bulk delete their chat history in Nebulus Gantry via a conversational command (e.g., `/clear_all`). This provides a quick way to sanitize the workspace and remove outdated discussions without manual deletion of individual chats.

## 2. Requirements
- [x] Users can trigger bulk deletion by sending a specific command (e.g., `/clear_all` or `/prune_history`).
- [x] The command must delete all chat records associated with the current user from the database.
- [x] The command should delete associated messages and feedback (cascading delete).
- [x] The UI should ideally reflect the cleared history immediately.
- [x] A confirmation message should be displayed to the user.

## 3. Technical Implementation
- **Modules**: `gantry/public/script.js` (Frontend), `gantry/routers/chat_routes.py` (Backend API).
- **Backend API**: `DELETE /api/chats` deletes all chats for the authenticated user using `delete_all_chats_for_user_db`.
- **Frontend Interception**:
    - `script.js` implements a **Document-level Event Delegation** strategy to intercept the `/clear_all` command.
    - It listens for `keydown` (Enter key) on inputs and `click` on submit buttons.
    - When detected, it prevents the default form submission (blocking the message from hitting Chainlit).
    - It triggers a `Nebulus.Modal.confirm` dialog.
- **Confirmation Flow**:
    - If user confirms, `fetch('/api/chats', { method: 'DELETE' })` is called.
    - On success, the sidebar (`#recent-chats-list`) is cleared via DOM manipulation.
    - A toast notification is displayed.
    - If the user was in a specific chat, they are redirected to the home page.

## 4. Verification Plan
**Automated Tests**:
- [x] Verification of DB state before/after API call.
- [x] Browser automated verification of modal trigger and interaction.

**Manual Verification**:
- [x] Login to Gantry.
- [x] Create multiple chats.
- [x] Type `/clear_all` and press Enter OR click Send.
- [x] Verify confirmation modal appears.
- [x] Click "Delete" and verify modal closes, sidebar clears, and toast appears.

## 5. Workflow Checklist
- [x] **Branch**: Created `feat/bulk-delete-chats`?
- [x] **Work**: Implemented `/clear_all` handler?
- [x] **Test**: Verified DB operations?
- [x] **Doc**: Updated walkthrough?
- [x] **Data**: Merged to develop?
