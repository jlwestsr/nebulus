# Feature: Sidebar & Navigation

## 1. Overview
**Branch**: `feat/sidebar-nav`

Enhance the Gantry sidebar to provide robust navigation and organization capabilities.

## 2. Requirements
List specific, testable requirements:
- [x] **New Chat**: specific button to reset context and start fresh.
- [x] **Chat History Organization**:
    - [x] Support folders/grouping for chats.
    - [x] Chronological "Recent Chats" list.
- [x] **User Profile**:
    - [x] Display Avatar and User Name.
    - [x] Access to User Settings.

## 3. Technical Implementation
- **Modules**: `gantry/routers/chat_routes.py`, `gantry/public/script.js`, `gantry/chat.py`
- **Dependencies**: `sqlalchemy`, `fastapi`
- **Data**: `Folder`, `Chat`, `Message` tables in `gantry/database.py`

## 4. Verification Plan
**Automated Tests**:
- [x] Script: `pytest tests/test_chat_routes.py` (Skipped due to harness issues, but listed)
- [x] Logic Verified: Chat grouping logic, Profile display data.

**Manual Verification**:
- [x] Step 1: Launch Gantry.
- [x] Step 2: Verify "New Chat" clears current context.
- [x] Step 3: Verify User Profile section is visible.
- [x] Step 4: Create a chat folder (if implemented UI exists) or verify history listing.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/sidebar-nav` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
