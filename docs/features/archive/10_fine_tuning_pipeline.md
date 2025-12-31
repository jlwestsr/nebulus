# Feature: Fine-tuning Pipeline

## 1. Overview
**Branch**: `feat/finetune-pipeline`

Create a standardized workflow and set of scripts to prepare usage data (chats, codebase) for Fine-Tuning (LoRA). This is the first step towards a self-improving agent that learns from the user's specific coding style and project context.

## 2. Requirements
List specific, testable requirements:
- [x] Implement `scripts/export_chat_logs.py`: Export Open WebUI chat history to JSONL.
- [x] Implement `scripts/prepare_dataset.py`: Format data for Unsloth or similar trainers.
- [x] **Format**: Output standard ShareGPT or Alpaca format JSONL.

## 3. Technical Implementation
- **Modules**: Create `scripts/finetune/`.
- **Dependencies**: `pandas`, `sqlitedict` (to read WebUI DB if needed).
- **Data**: Output datasets in `data/datasets/`.

## 4. Verification Plan
**Automated Tests**:
- [x] Script/Test: Run export script, verify JSONL validity.

**Manual Verification**:
- [x] Step 1: Accumulate some chat history.
- [x] Step 2: Run export script.
- [x] Step 3: Inspect output JSONL for correctness.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/finetune-pipeline` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass?
- [x] **Doc**: Updated `README.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
