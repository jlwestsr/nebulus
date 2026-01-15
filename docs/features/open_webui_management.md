# Feature: Open WebUI Management Restore

## 1. Overview
**Branch**: `feat/open-webui-mgmt`

This feature restores the ability to manage the `open-webui` container via the `nebulus` CLI. Although previously removed in favor of "Gantry", `open-webui` remains a core component for legacy support and original functionality as described in `CONTEXT.md`. This task involves re-integrating it into Docker Compose, Ansible, and the CLI management tools.

## 2. Requirements
List specific, testable requirements:
- [ ] `open-webui` service added to `docker-compose.yml`.
- [ ] `nebulus up` displays `open-webui` access point at `http://localhost:3000`.
- [ ] `nebulus status` reports `open-webui` as `ONLINE`.
- [ ] `scripts/health.sh` includes a health check for `open-webui`.
- [ ] Ansible setup ensures `open-webui` is deployed.

## 3. Technical Implementation
- **Modules**:
    - `nebulus.py` (CLI update)
    - `docker-compose.yml` (Service restoration)
    - `scripts/health.sh` (Health check update)
    - `ansible/setup.yml` (Infrastructure sync)
- **Dependencies**: No new Python dependencies.
- **Data**: New Docker volume `webui_data`.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `pytest tests/test_nebulus_cli.py` (Ensure CLI logic is sound)
- [ ] Script/Test: `./scripts/health.sh` (Verify service accessibility)

**Manual Verification**:
- [ ] Step 1: Run `nebulus up`
- [ ] Step 2: Run `nebulus status`
- [ ] Step 3: Access `http://localhost:3000` in browser

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/...` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
