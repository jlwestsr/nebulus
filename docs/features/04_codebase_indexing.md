# Feature: Codebase Indexing

## 1. Overview
**Branch**: `feat/codebase-indexing`

Empower the agent to search the codebase using regular expressions and semantic search logic. The current vector store provides semantic chunk retrieval, but exact keyword search (`grep`) is often more precise for engineering tasks.

## 2. Requirements
List specific, testable requirements:
- [x] Implement `search_code` tool: Accepts `query` and `path`.
- [x] **Engine**: Use `grep` or `ripgrep` (if installed) via subprocess.
- [x] **Output**: Return file paths and matching lines with context.
- [x] **Integration**: Ensure it respects `.gitignore` to avoid searching artifacts/dependencies.

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py`.
- **Dependencies**: None (uses system `grep`) or `ripgrep` binary in Dockerfile.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [x] Script/Test: `test_search.py`. Search for unique string in a test file.

**Manual Verification**:
- [x] Step 1: Ask agent "Find all TODOs in the codebase".
- [x] Step 2: Verify it returns a list of files and lines containing "TODO".

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/codebase-indexing` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass?
- [x] **Doc**: Updated `README.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
