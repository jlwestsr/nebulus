# Feature: Fine-tuning Pipeline

## 1. Overview
**Branch**: `feat/finetune-pipeline`

Create a standardized workflow and set of scripts to prepare usage data (chats, codebase) for Fine-Tuning (LoRA). This is the first step towards a self-improving agent that learns from the user's specific coding style and project context.

## 2. Requirements
List specific, testable requirements:
- [ ] Implement `scripts/export_chat_logs.py`: Export Open WebUI chat history to JSONL.
- [ ] Implement `scripts/prepare_dataset.py`: Format data for Unsloth or similar trainers.
- [ ] **Format**: Output standard ShareGPT or Alpaca format JSONL.

## 3. Technical Implementation
- **Modules**: Create `scripts/finetune/`.
- **Dependencies**: `pandas`, `sqlitedict` (to read WebUI DB if needed).
- **Data**: Output datasets in `data/datasets/`.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: Run export script, verify JSONL validity.

**Manual Verification**:
- [ ] Step 1: Accumulate some chat history.
- [ ] Step 2: Run export script.
- [ ] Step 3: Inspect output JSONL for correctness.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/finetune-pipeline` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass?
- [ ] **Doc**: Updated `README.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
