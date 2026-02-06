# Feature: Model Builder UI

## 1. Overview

**Branch**: `develop` (Merged from `feat/model-builder`)

Provide a graphical interface to create custom Modelfiles for Ollama (System Prompt, Parameters, Base Model).

## 2. Requirements

List specific, testable requirements:

- [x] **Builder Interface**:
  - [x] Form to input: Name, Base Model, System Prompt, Parameters (Temperature, etc.).
  - [x] "Create" button to push to Ollama.
- [x] **Save Management**:
  - [x] Save definition to `models/` directory.
  - [x] Refresh model list.

## 3. Technical Implementation

- **Modules**: [ollama.py](file:///home/jlwestsr/projects/west_ai_labs/nebulus/gantry/ops/ollama.py), [model_builder.py](file:///home/jlwestsr/projects/west_ai_labs/nebulus/gantry/ui/model_builder.py)
- **Dependencies**: N/A
- **Data**: Filesystem write access to `models/`.

## 4. Verification Plan

**Automated Tests**:

- [x] Script: `pytest tests/ops/test_model_builder.py`
- [x] Logic Verified: Modelfile generation is valid, Ollama `create` API is called.

**Manual Verification**:

- [x] Step 1: Fill out form "My Pirate Bot".
- [x] Step 2: Click Create.
- [x] Step 3: Select "My Pirate Bot" from model dropdown and chat.

## 5. Workflow Checklist

Follow the AI Behavior strict workflow:

- [x] **Branch**: Created `feat/model-builder` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
