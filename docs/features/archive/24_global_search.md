# Feature: Global Search

## 1. Overview
**Branch**: `feat/global-search`

Implement a powerful global search capability within Gantry to allow users to instantly retrieve information across all their interactions and stored data.

## 2. Requirements
List specific, testable requirements:
- [x] **Unified Search Interface**:
    - [x] Prominent search bar accessible from the sidebar.
    - [x] Real-time or "enter-to-search" query execution.
- [x] **Scope**:
    - [x] **Chat History**: Search across all past message content.
    - [ ] **Notes**: Search within user-created notes (Deferred to `feat/notes-system`).
    - [ ] **Workspace Items**: (Optional) Search across model names or tool descriptions.
- [x] **Results Display**:
    - [x] Clear list of matching results with context snippets.
    - [x] Click-to-navigate: Clicking a result opens the relevant chat/note at the correct position.

## 3. Technical Implementation
- **Modules**:
    - `gantry/routers/chat_routes.py`: Implements `GET /api/search` endpoint.
    - `gantry/public/script.js`: Implements logic for Modal, API calls, and Result rendering.
    - `gantry/public/style.css`: Styles for the Search Modal and results.
- **Dependencies**: `SQLAlchemy` for SQL-based `LIKE` queries on `Message` content.
- **Data**: Uses direct SQL filters on `Message.content`.

### API Endpoint
`GET /api/search?q={query}`
- Performs case-insensitive `LIKE` search on `messages.content`.
- Groups results by `chat_id`.
- Returns earliest match snippet per chat to avoid clutter.

## 4. Verification Plan
**Automated Tests**:
- [x] Script: `pytest tests/test_search.py`
- [x] Logic Verified: Query matching, Result context extraction, clicking navigation links.

**Manual Verification**:
- [x] Step 1: Create a chat with unique keywords (e.g., "NebulusSearchTest").
- [x] Step 2: Use the sidebar search bar to query "NebulusSearchTest".
- [x] Step 3: Verify the chat appears in results.
- [x] Step 4: Click the result and verify it opens the chat.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/global-search` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?

## 6. Recordings
### Feature Test
![Search Test](/home/jlwestsr/.gemini/antigravity/brain/7aa24b0d-bf72-4ee2-aad2-3cebedd6a2a8/global_search_test_1767646251145.webp)
