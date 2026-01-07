# Feature: Model Builder UI

## 1. Overview
**Branch**: `feat/model-builder`

Provide a graphical interface to create custom Modelfiles for Ollama (System Prompt, Parameters, Base Model).

## 2. Requirements
List specific, testable requirements:
- [ ] **Builder Interface**:
    - [ ] Form to input: Name, Base Model, System Prompt, Parameters (Temperature, etc.).
    - [ ] "Create" button to push to Ollama.
- [ ] **Save Management**:
    - [ ] Save definition to `models/` directory.
    - [ ] Refresh model list.

## 3. Technical Implementation
- **Modules**: `gantry/ui/model_builder.py`, `gantry/ops/ollama.py`
- **Dependencies**: N/A
- **Data**: Filesystem write access to `models/`.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/ops/test_model_builder.py`
- [ ] Logic Verified: Modelfile generation is valid, Ollama `create` API is called.

**Manual Verification**:
- [ ] Step 1: Fill out form "My Pirate Bot".
- [ ] Step 2: Click Create.
- [ ] Step 3: Select "My Pirate Bot" from model dropdown and chat.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/model-builder` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
