# Feature: Image Generation

## 1. Overview

**Branch**: `feat/image-generation`

Integrate image generation capabilities (Stable Diffusion, DALL-E) into the chat interface.

## 2. Requirements

List specific, testable requirements:

- [ ] **Generation Interface**:
  - [ ] Command or UI trigger (e.g., `/image "a cat floating in space"`)
  - [ ] Display generated image in chat stream.
- [ ] **Backend Integration**:
  - [ ] Connect to local Stable Diffusion (WebUI) or OpenAI DALL-E API.
  - [ ] Handle asynchronous generation time.
  - [ ] Save generated images to `static` or artifact store.

## 3. Technical Implementation

- **Modules**: `gantry/tools/image.py`, `mcp_server/tools/image_gen.py`
- **Dependencies**: `openai` (for DALL-E), `requests` (for SD WebUI).
- **Data**: Storage for generated images.

## 4. Verification Plan

**Automated Tests**:

- [ ] Script: `pytest tests/tools/test_image_gen.py`
- [ ] Logic Verified: API call structure, file saving logic.

**Manual Verification**:

- [ ] Step 1: Request an image generation.
- [ ] Step 2: Verify image appears in chat and is saved locally.

## 5. Workflow Checklist

Follow the AI Behavior strict workflow:

- [ ] **Branch**: Created `feat/image-generation` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
