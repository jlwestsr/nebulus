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

## 4. API Usage Examples

Base URL: `http://localhost:8002`

### Conversations

**Create a Conversation**
```bash
curl -X POST http://localhost:8002/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"topic": "Project Nebula", "user_id": "jlwestsr"}'
```

**Get Conversation**
```bash
curl http://localhost:8002/api/conversations/{conv_id}
```

**Update Conversation**
```bash
curl -X PUT http://localhost:8002/api/conversations/{conv_id} \
  -H "Content-Type: application/json" \
  -d '{"topic": "Project Nebula Phase 2"}'
```

**Delete Conversation**
```bash
curl -X DELETE http://localhost:8002/api/conversations/{conv_id}
```

### Messages

**Add Message**
```bash
curl -X POST http://localhost:8002/api/conversations/{conv_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Initialize phase 2 parameters.", "sender": "user", "receiver": "ai"}'
```

**List Messages**
```bash
curl http://localhost:8002/api/conversations/{conv_id}/messages
```

### User Preferences

**Set Preference**
```bash
curl -X POST http://localhost:8002/api/users/jlwestsr/preferences \
  -H "Content-Type: application/json" \
  -d '{"key": "editor_mode", "value": "vim"}'
```

**Get Preferences**
```bash
curl http://localhost:8002/api/users/jlwestsr/preferences
```

## 5. Verification Plan
**Automated Tests**:
- [x] Script: `python3 scripts/verify_ltm.py`
    - Creates conversation, adds message, sets preference, updates/deletes conversation.
    - Verifies all API responses match expected values.

## 6. Workflow Checklist
- [x] **Branch**: Created `feat/ltm-chromadb`? (Yes)
- [x] **Work**: Implemented changes? (Yes)
- [x] **Test**: All tests pass? (Yes, verified via script)
- [x] **Doc**: Updated `README.md` and feature docs? (Yes)
- [x] **Data**: `git add .`, `git commit`, `git push`? (Yes)
