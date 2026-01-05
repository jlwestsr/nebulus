# Feature: [Feature Name]

## 1. Overview
**Branch**: `feat/[feature-name]`

Briefly describe the feature, the problem it solves, and why it is being built.

## 2. Requirements
List specific, testable requirements:
- [ ] Requirement 1
- [ ] Requirement 2

## 3. Technical Implementation
- **Modules**: List modified/created files (e.g., `src/module.py`).
- **Dependencies**: List new packages (e.g., `rich`).
- **Data**: Database changes or new assets.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `pytest tests/test_feature.py`
- [ ] Logic Verified: [Describe what is tested]

**Manual Verification**:
- [ ] Step 1: Run `forge --flag`
- [ ] Step 2: Verify output in `dist/`

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/...` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
