# Feature: CLI Dashboard URL Display

**Status**: Draft
**Owner**: AI Agent
**Created**: 2024-12-30

## 1. Context & Problem Statement
Currently, when a user runs `nebulus up`, the services start, but the user is left guessing which local ports to access for the various interfaces (WebUI, Logs, API docs). This friction reduces usability.

## 2. Goals
- Display a clear, clickable list of URLs for all active services immediately after `nebulus up` completes successfully.
- Improve the "first run" experience for new users.

## 3. Scope
- **In Scope**:
  - Modify `nebulus up` command.
  - List URLs for: Open WebUI, Dozzle, MCP Server, Ollama, ChromaDB.
- **Out of Scope**:
  - dynamic port detection (we assume standard ports from docker-compose).

## 4. Technical Approach
- Update `nebulus.py`:
  - Enhance `up()` function.
  - Use `rich.table` or `rich.panel` to present links attractively.
  - URLs:
    - Web Interface: `http://localhost:3000`
    - Logs (Dozzle): `http://localhost:8888`
    - MCP API: `http://localhost:8000/docs`
    - ChromaDB: `http://localhost:8001`
    - Ollama: `http://localhost:11435`

## 5. Security Implications
None. Displays localhost links only.

## 6. Verification Plan
- **Automated**: Update `tests/test_nebulus.py` (if exists) or create a test to verify stdout captures the URLs.
- **Manual**: Run `nebulus up` and click the links.
