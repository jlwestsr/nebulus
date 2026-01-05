# Feature: Workspace Management UI

## 1. Overview
**Branch**: `feat/workspace-ui`

Create a dedicated "Workspace" management area in the UI to manage the tools and knowledge available to the AI.

## 2. Requirements
List specific, testable requirements:
- [ ] **Model Management**:
    - [ ] UI to list available LLMs.
    - [ ] Interface to Pull new models (via Ollama) and Delete old ones.
- [ ] **Knowledge Management**:
    - [ ] Interface to view/manage RAG collections.
    - [ ] Upload/Indexing status for documents.
- [ ] **Tool Configuration**:
    - [ ] UI to toggle enabled MCP tools.
    - [ ] Configuration forms for tool parameters if needed.

## 3. Technical Implementation
- **Modules**: `gantry/ui/workspace.py`, `gantry/api/management.py`
- **Dependencies**: None.
- **Data**: API endpoints to interface with Ollama, ChromaDB, and MCP config.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/api/test_management_endpoints.py`
- [ ] Logic Verified: Model pull/delete actions, RAG collection listing.

**Manual Verification**:
- [ ] Step 1: Go to Workspace -> Models.
- [ ] Step 2: Trigger a model pull and observe progress.
- [ ] Step 3: Verify tool toggle enables/disables tool availability in chat.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/workspace-ui` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
