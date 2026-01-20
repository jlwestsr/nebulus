# Feature: Long Term Memory (LTM) with ChromaDB

## 1. Overview
**Branch**: `feat/ltm-chromadb`

Implement a persistent memory system for the AI using ChromaDB. This feature enables the storage and retrieval of conversations, messages, attachments, and user preferences, effectively giving the AI "Long Term Memory". This uses ChromaDB as a node-based document store to manage relationships between these entities.

## 2. Requirements
- [x] Use ChromaDB as the underlying storage mechanism.
- [x] Implement relationships: Conversation -> Messages (One-to-Many).
- [x] Implement relationships: User -> Preferences.
- [x] API: Create, Get, Update, Delete Conversations.
- [x] API: Add and List Messages.
- [x] API: Set and Get User Preferences.

## 3. Technical Implementation
- **Modules**:
    - `mcp_server/db.py` (New): ChromaDB client wrapper.
    - `mcp_server/server.py`: Added API endpoints and Pydantic models.
    - `mcp_server/requirements.txt`: Added `chromadb`.
- **Data**:
    - ChromaDB Collections: `conversations`, `messages`, `users`.

## 4. Verification Plan
**Automated Tests**:
- [x] Script: `python3 scripts/verify_ltm.py`
    - Creates conversation, adds message, sets preference, updates/deletes conversation.
    - Verifies all API responses match expected values.

## 5. Workflow Checklist
- [x] **Branch**: Created `feat/ltm-chromadb`? (Yes)
- [x] **Work**: Implemented changes? (Yes)
- [x] **Test**: All tests pass? (Yes, verified via script)
- [x] **Doc**: Updated `README.md` and feature docs? (Yes)
- [ ] **Data**: `git add .`, `git commit`, `git push`? (Pending)
