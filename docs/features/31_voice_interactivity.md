# Feature: Advanced Voice & Video

## 1. Overview

**Branch**: `feat/voice-video`

Implement Speech-to-Text (STT) and Text-to-Speech (TTS) for full voice interactivity, and potentially video call capabilities.

## 2. Requirements

List specific, testable requirements:

- [ ] **Speech-to-Text (STT)**:
  - [ ] Expand on Feature 22 (Microphone Input) to use Whisper (Local/API).
- [ ] **Text-to-Speech (TTS)**:
  - [ ] Button to "Read Aloud" messages.
  - [ ] Option for automatic voice response.
  - [ ] Backend integration with ElevenLabs/OpenAI TTS/Local Coqui.
- [ ] **UI Controls**:
  - [ ] Mute/Unmute toggle.
  - [ ] Voice selection settings.

## 3. Technical Implementation

- **Modules**: `gantry/audio/stt.py`, `gantry/audio/tts.py`
- **Dependencies**: Audio processing libs (`pydub`), client-side JS for audio capture/playback.
- **Data**: Temporary audio file storage.

## 4. Verification Plan

**Automated Tests**:

- [ ] Script: `pytest tests/audio/test_audio.py`
- [ ] Logic Verified: Audio transcoding, API integration.

**Manual Verification**:

- [ ] Step 1: Speak into microphone. Verify text transcription appears (STT).
- [ ] Step 2: Click "Read Aloud". Verify audio playback (TTS).

## 5. Workflow Checklist

Follow the AI Behavior strict workflow:

- [ ] **Branch**: Created `feat/voice-video` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
