# Feature: Automated Backups

## 1. Overview
**Branch**: `feat/automated-backups`

Create a robust backup solution for the persistent data in Ollama, ChromaDB, and Open WebUI. This ensures that user chats, downloaded models, and vector embeddings are safe.

## 2. Requirements
List specific, testable requirements:
- [ ] Implement `scripts/backup.sh`: usage `./scripts/backup.sh [output_dir]`.
- [ ] **Strategy**: Use a temporary alpine container to mount the volumes and create a compressed tarball (`.tar.gz`).
- [ ] **Volumes**: Backup `ollama_data`, `chroma_data`, `webui_data`.
- [ ] **Retention**: (Optional) Simple rotation to keep last N backups.

## 3. Technical Implementation
- **Modules**: Create `scripts/backup.sh` and `scripts/restore.sh`.
- **Dependencies**: `docker` (CLI).
- **Data**: New backup artifacts in `backups/` directory.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `test_backup_restore.sh`. Run backup, delete volume, run restore, verify data exists.

**Manual Verification**:
- [ ] Step 1: Run `scripts/backup.sh`.
- [ ] Step 2: Stop containers and `docker volume rm ...`.
- [ ] Step 3: Run `scripts/restore.sh`.
- [ ] Step 4: Start containers and verify chat history/models are present.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/automated-backups` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass?
- [ ] **Doc**: Updated `README.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
