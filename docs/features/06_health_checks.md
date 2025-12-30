# Feature: Health Checks

## 1. Overview
**Branch**: `feat/health-checks`

Implement a comprehensive health check script. As the system grows with multiple services (Ollama, Chroma, WebUI, MCP), knowing the precise status of each and their connectivity is vital for debugging.

## 2. Requirements
List specific, testable requirements:
- [ ] Implement `scripts/health.sh`.
- [ ] **Ollama**: Check `/api/tags` to verify it's up and models are loaded.
- [ ] **ChromaDB**: Check `/api/v1/heartbeat`.
- [ ] **MCP**: Check `/health` or SSE connection (might need a new endpoint in server.py).
- [ ] **WebUI**: Check HTTP 200 on root.

## 3. Technical Implementation
- **Modules**: Create `scripts/health.sh`. Modify `mcp_server/server.py` to add a `/health` GET endpoint.
- **Dependencies**: `curl`.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: Run `scripts/health.sh` in CI/setup.

**Manual Verification**:
- [ ] Step 1: Run `./scripts/health.sh`.
- [ ] Step 2: Confirm it reports "OK" for all services when running.
- [ ] Step 3: Stop a service and confirm it reports "FAIL".

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/health-checks` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass?
- [ ] **Doc**: Updated `README.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
