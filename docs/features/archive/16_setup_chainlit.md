# Feature: Setup Chainlit (Gantry)

## 1. Overview
**Branch**: `feat/setup-chainlit`

We will implement Chainlit as the new "Gantry" interface for the Nebulus ecosystem. This replaces the recently removed Open WebUI. It will run as a separate Docker service, connecting to the existing Ollama and ChromaDB instances.

## 2. Requirements
- [x] Create a new service `gantry` running Chainlit.
- [x] Map port `8002` (reserved for UI) to container.
- [x] Connect to `ollama` (port 11434).
- [x] Connect to `chromadb` (port 8000).
- [x] Connect to `mcp-server` (port 8000).
- [x] Implement basic "Hello World" or chat interface to verify connectivity.

## 3. Technical Implementation
- **Directory**: `gantry/`
    - `Dockerfile`: Python 3.11-slim base.
    - `requirements.txt`: `chainlit`, `openai` (or `ollama` python lib), `chromadb`.
    - `app.py`: Main entry point.
- **Docker**:
    - Add `gantry` service to `docker-compose.yml`.
    - Dependencies: `ollama`, `chromadb`, `mcp-server`.
- **CLI**:
    - Update `nebulus.py` to track the new service.

## 4. Verification Plan
**Automated Tests**:
- [x] `pytest tests/test_nebulus_cli.py`: Update to expect the new service URL.
- [x] `scripts/health.sh`: Update to check the new port.

**Manual Verification**:
- [x] `nebulus up` -> Check if `localhost:8002` loads Chainlit UI.
