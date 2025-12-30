# Feature: File Write Support

## 1. Overview
**Branch**: `feat/file-write-support`

Enable the MCP agent to modify the codebase directly by adding file writing capabilities. This transforms the agent from a read-only advisor to an active engineer capable of implementing changes.

## 2. Requirements
List specific, testable requirements:
- [x] Implement `write_file` tool: Accepts `path` and `content`. Overwrites or creates new files.
- [x] Implement `edit_file` tool: Accepts `path`, `target_text`, and `replacement_text` for surgical edits.
- [x] **Security**: Ensure all paths are validated to be strictly within `/workspace`.
- [x] **Security**: Prevent traversal attacks (e.g., `../`).

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py` to add new `@mcp.tool()` functions.
- **Dependencies**: No new packages required (standard `os` and `io`).
- **Data**: No database changes.

## 4. Verification Plan
**Automated Tests**:
- [x] Script/Test: Create `tests/test_file_ops.py` to test `write_file` and `edit_file`.
- [x] Logic Verified: Verify file creation, content overwriting, and correct string replacement.

**Manual Verification**:
- [x] Step 1: Connect Open WebUI to MCP.
- [x] Step 2: Ask agent to "Create a file named hello.txt with content 'Hello World'".
- [x] Step 3: Verify file existence in `/workspace`.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/file-write-support` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
