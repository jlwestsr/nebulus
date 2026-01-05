# Feature: Global Search

## 1. Overview
**Branch**: `feat/global-search`

Implement a powerful global search capability within Gantry to allow users to instantly retrieve information across all their interactions and stored data.

## 2. Requirements
List specific, testable requirements:
- [ ] **Unified Search Interface**:
    - [ ] Prominent search bar accessible from the sidebar.
    - [ ] Real-time or "enter-to-search" query execution.
- [ ] **Scope**:
    - [ ] **Chat History**: Search across all past message content.
    - [ ] **Notes**: Search within user-created notes.
    - [ ] **Workspace Items**: (Optional) Search across model names or tool descriptions.
- [ ] **Results Display**:
    - [ ] Clear list of matching results with context snippets.
    - [ ] Click-to-navigate: Clicking a result opens the relevant chat/note at the correct position.

## 3. Technical Implementation
- **Modules**: `gantry/ui/search.py`, `gantry/api/search.py`
- **Dependencies**: Full-text search capability (SQLite FTS5, ChromaDB, or simple regex depending on scale).
- **Data**: Indexing mechanism for chat history and notes if standard DB query is insufficient.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/api/test_search.py`
- [ ] Logic Verified: Query matching, Result context extraction, clicking navigation links.

**Manual Verification**:
- [ ] Step 1: Create a chat with unique keywords (e.g., "NebulusSearchTest").
- [ ] Step 2: Use the sidebar search bar to query "NebulusSearchTest".
- [ ] Step 3: Verify the chat appears in results.
- [ ] Step 4: Click the result and verify it opens the chat.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/global-search` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
