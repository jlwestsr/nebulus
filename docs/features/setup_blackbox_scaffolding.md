# Feature: Black Box System Scaffolding

## 1. Overview
**Branch**: `develop`

Scaffold the initial "Black Box" AI system using Docker. This setup integrates Ollama (backend), Open WebUI (frontend), ChromaDB (RAG), and a custom MCP Server (tools) into a unified local stack.

## 2. Requirements
- [x] Create `docker-compose.yml` orchestrating Ollama, WebUI, ChromaDB, and MCP.
- [x] Configure internal Docker network `ai-network`.
- [x] Implement custom MCP server in Python with file system and web search tools.
- [x] Enable persistent storage for vector DB and model files.
- [x] Document setup instructions in `README.md`.

## 3. Technical Implementation
- **Modules**:
    - `docker-compose.yml`: Main orchestration file.
    - `mcp_server/`: New directory for the MCP tool service.
    - `mcp_server/server.py`: FastAPI/FastMCP implementation.
    - `mcp_server/Dockerfile`: Container definition.
- **Dependencies**:
    - `fastapi`, `uvicorn`, `mcp`, `duckduckgo-search` (inside MCP container).
- **Configuration**:
    - `.env.example`: Template for secrets and URLs.

## 4. Verification Plan
**Automated Tests**:
- [x] Docker Config: `docker-compose config` passed.

**Manual Verification**:
- [x] Verified `docker-compose.yml` structure matches requirements.
- [x] Verified MCP server code (`server.py`) contains requested tools (`list_directory`, `web_search`).

## 5. Workflow Checklist
- [x] **Branch**: Working on `develop`.
- [x] **Work**: Implemented Docker and Python files.
- [x] **Test**: Configuration validated.
- [x] **Doc**: Updated `README.md` and created `walkthrough.md`.
- [ ] **Data**: `git add .`, `git commit`, `git push`.
