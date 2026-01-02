# Feature: Remove Open WebUI

## 1. Overview
**Branch**: `feat/remove-open-webui`

The goal is to determine the feasibility and steps required to remove Open WebUI from the Nebulus stack. The project is moving towards "Gantry" as the primary interface, making Open WebUI redundant. This feature involves analyzing dependencies, backing up configuration if necessary, and removing the Open WebUI service from Docker Compose and related documentation/scripts.

## 2. Requirements
- [x] Analyze `docker-compose.yml` for Open WebUI dependencies.
- [x] Analyze codebase for hardcoded references to Open WebUI (ports, URLs).
- [x] Determine impact on RAG pipeline.
    - **Critical**: Open WebUI handles document ingestion, chunking, and embedding. Removing it removes the ability to upload and process documents into ChromaDB unless Gantry implements this.
- [x] Define steps for removal.

## 3. Technical Implementation Plan
To remove Open WebUI, the following changes are required:

### Docker & Infrastructure
- **`docker-compose.yml`**:
    - Remove `open-webui` service block.
    - Remove `webui_data` volume definition.
    - Remove `depends_on` references in other services (none found, Open WebUI is the dependent).

### CLI (`nebulus.py`)
- **`up()`**: Remove Open WebUI from the "Access Points" table.
- **`status()`**: Remove `localhost:3000` health check.
- **`backup()`**: No code change needed, but `nebulus_webui_data` volume will no longer exist.
- **General**: Remove any logic assuming port 3000 is active.

### Scripts
- **`scripts/health.sh`**: Remove the curl check for port 3000.

### Documentation
- **`README.md`**: Remove "Frontend" section, "Access" links, and "RAG Pipeline" description (or note it is deprecated/waiting for Gantry).
- **Wiki/Docs**: Update Feature lists to remove Open WebUI references.

### Data
- **Volume**: The `webui_data` docker volume contains the SQLite database for chat history and users. This will be lost.
- **ChromaDB**: The vector content is in `chroma_data` and *will persist*, but without the Open WebUI frontend, there is no built-in way to search it until Gantry is connected.

## 4. Verification Plan
(For the actual removal phase)
**Automated Tests**:
- [ ] `pytest tests/test_nebulus_cli.py`: Verify CLI tests pass without Open WebUI checks.
- [ ] `scripts/health.sh`: Verify it passes without checking port 3000.

**Manual Verification**:
- [x] Run `nebulus up` and ensure no errors.
- [x] Run `nebulus status` and ensure all remaining services (Ollama, Chroma, MCP) are ONLINE.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/...` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
