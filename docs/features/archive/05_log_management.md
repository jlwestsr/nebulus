# Feature: Log Management (Dozzle)

## 1. Overview
**Branch**: `feat/log-management`

Integrate [Dozzle](https://dozzle.com) into the Docker Compose stack. This provides a lightweight, real-time web interface for monitoring logs from all containers, which is essential for debugging and monitoring long-running agent tasks.

## 2. Requirements
List specific, testable requirements:
- [x] Add `dozzle` service to `docker-compose.yml`.
- [x] **Configuration**: Mount `/var/run/docker.sock`.
- [x] **Access**: Expose on port `8888` (or similar).
- [x] **Security**: Limit access (basic auth if possible, or note for local use only).

## 3. Technical Implementation
- **Modules**: Update `docker-compose.yml`.
- **Dependencies**: `amir20/dozzle:latest` image.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [x] Docker Healtcheck: Verify container starts.

**Manual Verification**:
- [x] Step 1: Run `docker compose up -d`.
- [x] Step 2: Open `http://localhost:8888`.
- [x] Step 3: Verify logs from `blackbox-ollama` and `blackbox-mcp` are visible.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/log-management` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: Verified UI?
- [x] **Doc**: Updated `README.md` with URL?
- [x] **Data**: `git add .`, `git commit`, `git push`?
