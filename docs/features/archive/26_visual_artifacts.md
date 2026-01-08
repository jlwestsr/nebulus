# Feature: Visual Artifacts

## 1. Overview
**Branch**: `feat/visual-artifacts`

Enhance the chat rendering to support specialized visual artifacts, specifically code blocks and internal "thinking" states.

## 2. Requirements
List specific, testable requirements:
- [ ] **Code Rendering**:
    - [ ] Detect markdown code blocks (```python ... ```).
    - [ ] Apply syntax highlighting based on language.
    - [ ] Header prompt with "Copy Code" button.
- [ ] **Thinking Process**:
    - [ ] Detect `<think>` tags or specific chain-of-thought metadata from models (like DeepSeek R1).
    - [ ] Render as a collapsible "Thinking..." section, default collapsed.
    - [ ] Animate the "Thinking..." state if streaming.

## 3. Technical Implementation
- **Modules**: `gantry/ui/renderer.py`, `gantry/utils/markdown.py`
- **Dependencies**: `pygments` or JS-based highlighter (Prism/Highlight.js).
- **Data**: CSS styles for syntax themes.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/ui/test_rendering.py`
- [ ] Logic Verified: Markdown parsing of code blocks, extraction of thinking tags.

**Manual Verification**:
- [ ] Step 1: Ask model for Python code. Verify highlighting and Copy button.
- [ ] Step 2: Use a reasoning model (or mock response). Verify "Thinking" section is collapsible.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/visual-artifacts` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
