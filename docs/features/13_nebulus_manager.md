# Feature: Nebulus Manager CLI

## 1. Overview
**Branch**: `feat/nebulus-manager`

Build a unified "Nebulus Manager" CLI to manage containers, check logs, and monitor the AI instance from a terminal. This tool consolidates existing utility scripts and provides a rich, user-friendly interface for ecosystem management.

## 2. Requirements
- [ ] **Service Management**: Start (`up`), Stop (`down`), and Restart services via Docker Compose.
- [ ] **Status Dashboard**: A rich visual display of current service health (replacing/enhancing `scripts/health.sh`).
- [ ] **Log Streaming**: Stream aggregated or service-specific logs.
- [ ] **Maintenance**: Quick commands for `backup` and `restore` (wrappers for existing scripts).
- [ ] **Monitoring**: Command to launch Dozzle (log viewer) in the default browser.
- [ ] **Interactive Shell**: Capability to drop into a container's shell.
- [ ] **Testing**: Full unit test coverage for CLI logic.

## 3. Technical Implementation
- **Modules**: `nebulus` (Main CLI script), `mcp_server/scheduler.py` (referenced).
- **Dependencies**: `click`, `rich`.
- **Data**: None (stateless CLI).

## 4. Verification Plan
**Automated Tests**:
- [ ] `pytest tests/test_nebulus_cli.py`: Verify command parsing and subprocess execution logic.
- [ ] `flake8 nebulus`: Ensure linting compliance.

**Manual Verification**:
- [ ] Run `./nebulus status` and verify the table displays correctly.
- [ ] Run `./nebulus monitor` and verify the browser opens to the correct port.
- [ ] Run `./nebulus up` and verify containers start.

## 5. Workflow Checklist
- [ ] **Branch**: Created `feat/nebulus-manager` branch?
- [ ] **Work**: Implemented changes (code, type hints, docstrings)?
- [ ] **Test**: All tests pass (`pytest`, `flake8`)?
- [ ] **Doc**: Updated `README.md` and created `walkthrough.md`?
- [ ] **Data**: Committed and pushed to origin?
