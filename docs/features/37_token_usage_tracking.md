# Feature: Token Usage & Cost Tracking

## 1. Overview
**Branch**: `feat/token-tracking`

Monitor and display token usage (input/output) and estimated costs for models, especially relevant if using paid API providers.

## 2. Requirements
List specific, testable requirements:
- [ ] **Data Collection**:
    - [ ] Capture token counts from LLM responses (Ollama/OpenAI provide this).
    - [ ] Log usage per user/session.
- [ ] **UI Display**:
    - [ ] Show "Tokens: 154" in message footer.
    - [ ] Dashboard visualization of usage over time.
- [ ] **Cost Calculation**:
    - [ ] Configurable cost-per-token map.

## 3. Technical Implementation
- **Modules**: `gantry/metrics/usage.py`, `gantry/ui/usage.py`
- **Dependencies**: N/A
- **Data**: Usage logs table.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/metrics/test_usage.py`
- [ ] Logic Verified: Metrics are parsed and stored.

**Manual Verification**:
- [ ] Step 1: Send a message.
- [ ] Step 2: Check message footer for token count.
- [ ] Step 3: Check usage dashboard for increment.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/token-tracking` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
