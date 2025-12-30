# Feature: Vision Support

## 1. Overview
**Branch**: `feat/vision-support`

Enable the system to process images by integrating a vision-language model (VLM) like `llava`. This allows users to upload screenshots, diagrams, or mockups for the AI to analyze.

## 2. Requirements
List specific, testable requirements:
- [x] **Model**: Add `llava:latest` (or `llama3.2-vision` if available) to the default model list.
- [x] **Config**: Ensure Open WebUI is configured to use this model for image inputs.
- [x] **Pull**: Update `ansible/setup.yml` to pull the vision model.

## 3. Technical Implementation
- **Modules**: Update `ansible/setup.yml` and `README.md`.
- **Dependencies**: None.
- **Data**: New model weight (large download).

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `ollama run llava "describe this image"`.

**Manual Verification**:
- [ ] Step 1: Open WebUI.
- [ ] Step 2: Upload an image.
- [ ] Step 3: Ask "What is in this image?".
- [ ] Step 4: Verify accurate description.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/vision-support` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: Verified manually?
- [x] **Doc**: Updated `README.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
