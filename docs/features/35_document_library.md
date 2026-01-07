# Feature: Document Library & RAG UI

## 1. Overview
**Branch**: `feat/document-library`

Provide a comprehensive interface to manage uploaded documents, organize them into collections, and control RAG context.

## 2. Requirements
List specific, testable requirements:
- [ ] **Document Management**:
    - [ ] View list of all indexed documents.
    - [ ] Delete/Re-index documents.
    - [ ] View document metadata/chunks.
- [ ] **Collections (Tags)**:
    - [ ] Group documents by tag (e.g., #finance, #project-alpha).
    - [ ] Filter RAG retrieval by these tags.
- [ ] **Upload Interface**:
    - [ ] Drag-and-drop area to add files to specific collections.

## 3. Technical Implementation
- **Modules**: `gantry/rag/library.py`, `gantry/ui/library.py`
- **Dependencies**: N/A
- **Data**: ChromaDB metadata updates.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/rag/test_library.py`
- [ ] Logic Verified: Add/Delete operations sync with ChromaDB.

**Manual Verification**:
- [ ] Step 1: Upload "manual.pdf". Verify it appears in list.
- [ ] Step 2: Create tag "manuals". Add file to it.
- [ ] Step 3: Chat with context "manuals". Verify it retrieves info from manual.pdf.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/document-library` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
