# Feature: Token Usage & Cost Tracking

## 1. Overview
**Branch**: `feat/token-tracking`

Monitor and display token usage (input/output) and estimated costs for models, especially relevant if using paid API providers.

## 2. Requirements
List specific, testable requirements:
- [x] **Data Collection**:
    - [x] Capture token counts from LLM responses (Ollama/OpenAI provide this).
    - [x] Log usage per user/session.
- [x] **UI Display**:
    - [x] Show "Tokens: 154" in message footer.
    - [x] Dashboard visualization of usage over time.
- [x] **Cost Calculation**:
    - [x] Configurable cost-per-token map.

## 3. Technical Implementation
- **Modules**: `gantry/metrics/usage.py`, `gantry/ui/usage.py`
- **Dependencies**: N/A
- **Data**: Usage logs table.

## 4. Verification Plan
**Automated Tests**:
- [x] Script: `pytest tests/metrics/test_usage.py`
- [x] Logic Verified: Metrics are parsed and stored.

**Manual Verification**:
- [x] Step 1: Send a message.
- [x] Step 2: Check message footer for token count.
- [x] Step 3: Check usage dashboard for increment.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/token-tracking` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
