# Feature: Codebase Indexing

## 1. Overview
**Branch**: `feat/codebase-indexing`

Empower the agent to search the codebase using regular expressions and semantic search logic. The current vector store provides semantic chunk retrieval, but exact keyword search (`grep`) is often more precise for engineering tasks.

## 2. Requirements
List specific, testable requirements:
- [ ] Implement `search_code` tool: Accepts `query` and `path`.
- [ ] **Engine**: Use `grep` or `ripgrep` (if installed) via subprocess.
- [ ] **Output**: Return file paths and matching lines with context.
- [ ] **Integration**: Ensure it respects `.gitignore` to avoid searching artifacts/dependencies.

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py`.
- **Dependencies**: None (uses system `grep`) or `ripgrep` binary in Dockerfile.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `test_search.py`. Search for unique string in a test file.

**Manual Verification**:
- [ ] Step 1: Ask agent "Find all TODOs in the codebase".
- [ ] Step 2: Verify it returns a list of files and lines containing "TODO".

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/codebase-indexing` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass?
- [ ] **Doc**: Updated `README.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
