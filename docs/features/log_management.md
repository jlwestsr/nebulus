# Feature: Log Management (Dozzle)

## 1. Overview
**Branch**: `feat/log-management`

Integrate [Dozzle](https://dozzle.com) into the Docker Compose stack. This provides a lightweight, real-time web interface for monitoring logs from all containers, which is essential for debugging and monitoring long-running agent tasks.

## 2. Requirements
List specific, testable requirements:
- [ ] Add `dozzle` service to `docker-compose.yml`.
- [ ] **Configuration**: Mount `/var/run/docker.sock`.
- [ ] **Access**: Expose on port `8888` (or similar).
- [ ] **Security**: Limit access (basic auth if possible, or note for local use only).

## 3. Technical Implementation
- **Modules**: Update `docker-compose.yml`.
- **Dependencies**: `amir20/dozzle:latest` image.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [ ] Docker Healtcheck: Verify container starts.

**Manual Verification**:
- [ ] Step 1: Run `docker compose up -d`.
- [ ] Step 2: Open `http://localhost:8888`.
- [ ] Step 3: Verify logs from `blackbox-ollama` and `blackbox-mcp` are visible.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/log-management` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: Verified UI?
- [ ] **Doc**: Updated `README.md` with URL?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
