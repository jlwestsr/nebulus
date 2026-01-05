# Feature: Notes System

## 1. Overview
**Branch**: `feat/notes-system`

Create a dedicated "Notes" system within Gantry. This serves as a persistent "memory" or scratchpad for the user, independent of the ephemeral or linear nature of chat threads.

## 2. Requirements
List specific, testable requirements:
- [ ] **Notes Interface**:
    - [ ] Dedicated view in the Sidebar ("Notes").
    - [ ] List of existing notes.
    - [ ] Editor area for viewing/editing note content.
- [ ] **CRUD Operations**:
    - [ ] **Create**: Ability to start a new blank note.
    - [ ] **Read**: View note contents.
    - [ ] **Update**: Edit and save changes (auto-save preferred).
    - [ ] **Delete**: Remove unwanted notes.
- [ ] **Integration**:
    - [ ] (Future) Ability to reference notes in Chat.

## 3. Technical Implementation
- **Modules**: `gantry/ui/notes.py`, `gantry/api/notes.py`
- **Dependencies**: Markdown editor component (if rich text needed).
- **Data**: New `notes` table in database (id, user_id, title, content, created_at, updated_at).

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/api/test_notes.py`
- [ ] Logic Verified: Create, Read, Update, Delete flows.

**Manual Verification**:
- [ ] Step 1: Navigate to "Notes".
- [ ] Step 2: Click "New Note", type content "Test Note", and save.
- [ ] Step 3: Navigate away and return. Verify "Test Note" persists.
- [ ] Step 4: Delete the note and verify it disappears.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/notes-system` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
