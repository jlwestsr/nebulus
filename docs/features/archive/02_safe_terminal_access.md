# Feature: Safe Terminal Access

## 1. Overview
**Branch**: `feat/safe-terminal`

Give the agent a restricted `run_command` tool. This allows it to explore the environment (`ls`, `find`), check statuses (`git status`), and run tests (`pytest`), but prevents destructive actions.

## 2. Requirements
List specific, testable requirements:
- [x] Implement `run_command` tool: Accepts `command` string.
- [x] **Allowlist**: Only execute commands starting with allowed binaries (e.g., `ls`, `grep`, `cat`, `find`, `pytest`, `git`, `echo`).
- [x] **Blocklist**: Explicitly reject `rm`, `mv`, `chmod`, `chown`, `sudo`, `>`.
- [x] **Timeout**: Kill commands taking longer than X seconds.

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py`.
- **Dependencies**: `subprocess` (standard lib).
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [x] Script/Test: `test_terminal.py`.
- [x] Logic Verified: Test allowed command returns output. Test blocked command returns permission error.

**Manual Verification**:
- [x] Step 1: Ask agent to "List files in current directory". -> Success.
- [x] Step 2: Ask agent to "Delete all files". -> Failure/Refusal.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/safe-terminal` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
