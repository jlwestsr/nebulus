# Feature: Enhanced Input & Dashboard

## 1. Overview

**Branch**: `feat/input-dashboard`

Improve the input methods to support multi-modal interactions (images, voice) and refine the empty state dashboard with proper branding and suggestions.

## 2. Requirements

List specific, testable requirements:

- [x] **Multi-Modal Support**:
  - [x] Allow file attachments (Images, PDFs) to prompt.
  - [x] Render uploaded images in chat.
- [x] **Voice Support**:
  - [x] Microphone input (Speech-to-Text) for prompting.
  - [x] **Personalized Greeting**: "Good Morning, [User]" or similar. (Resolved)
  - [x] **Suggested Prompts**: 3-4 clickable starter prompts. (Resolved)
  - [x] **Branding**: Display Nebulus logo and tagline when chat is empty. (Resolved)

## 3. Technical Implementation

- **Modules**: `gantry/ui/chat_input.py`, `gantry/ui/dashboard.py`
- **Dependencies**: Potential JS audio library for STT if not built-in.
- **Data**: Configure initial suggestions list.

## 4. Verification Plan

**Automated Tests**:

- [ ] Script: `pytest tests/ui/test_dashboard.py`
- [ ] Logic Verified: Greeting logic based on time, Suggestion rendering.

**Manual Verification**:

- [x] Step 1: Open fresh chat. Verify Greeting and Suggestions appear.
- [x] Step 2: Upload an image. Verify it appears in chat.
- [x] Step 3: Test microphone input (if environment supports media devices).

## 5. Workflow Checklist

Follow the AI Behavior strict workflow:

- [x] **Branch**: Created `feat/enhanced-input` branch.
- [x] **Work**: Implemented changes.
- [x] **Test**: All tests pass (`flake8`, manual browser verification).
- [x] **Doc**: Updated `README.md` and `walkthrough.md`.
- [x] **Data**: `git add .`, `git commit`, `git merge develop`.
