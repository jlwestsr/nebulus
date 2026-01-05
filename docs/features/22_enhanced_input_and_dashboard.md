# Feature: Enhanced Input & Dashboard

## 1. Overview
**Branch**: `feat/input-dashboard`

Improve the input methods to support multi-modal interactions (images, voice) and refine the empty state dashboard with proper branding and suggestions.

## 2. Requirements
List specific, testable requirements:
- [ ] **Multi-Modal Support**:
    - [ ] Allow file attachments (Images, PDFs) to prompt.
    - [ ] Render uploaded images in chat.
- [ ] **Voice Support**:
    - [ ] Microphone input (Speech-to-Text) for prompting.
- [ ] **Dashboard Experience**:
    - [ ] **Personalized Greeting**: "Good Morning, [User]" or similar.
    - [ ] **Suggested Prompts**: 3-4 clickable starter prompts (e.g., "Help me debug...", "Explain quantum computing").
    - [ ] **Branding**: Display Nebulus logo and tagline when chat is empty.

## 3. Technical Implementation
- **Modules**: `gantry/ui/chat_input.py`, `gantry/ui/dashboard.py`
- **Dependencies**: Potential JS audio library for STT if not built-in.
- **Data**: Configure initial suggestions list.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/ui/test_dashboard.py`
- [ ] Logic Verified: Greeting logic based on time, Suggestion rendering.

**Manual Verification**:
- [ ] Step 1: Open fresh chat. Verify Greeting and Suggestions appear.
- [ ] Step 2: Upload an image. Verify it appears in chat.
- [ ] Step 3: Test microphone input (if environment supports media devices).

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/input-dashboard` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
