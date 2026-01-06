# Feature: Global Theme Toggle

## 1. Overview
**Branch**: `feat/theme-toggle` (merged)

Implement a global Light/Dark theme toggle that persists across sessions and eliminates "Flash of Incorrect Theme" (FOIT) on reload.

## 2. Requirements
- [x] **UI Control**:
    - [x] Fixed position toggle button (sun/moon icon).
    - [x] Smooth transition between states.
- [x] **Persistence**:
    - [x] Save preference to `localStorage` (`vite-ui-theme`).
    - [x] Respect system preference if no manual override (optional, currently defaults to storage).
- [x] **Performance**:
    - [x] Zero-flicker on reload (Critical).
    - [x] Instant application of critical CSS variables.

## 3. Technical Implementation
- **Frontend**:
    - `script.js`: `injectThemeToggle()` appends the button and handles click events.
    - `style.css`: Defines `.dark` class overrides for CSS variables.
- **Backend/Template**:
    - `gantry/main.py`: Injected a **blocking script** in `<head>` to read `localStorage` and apply `.dark` class to `<html>` before body render. This prevents the white flash.

## 4. Verification Plan
**Automated Tests**:
- [x] Browser Test: Script provided to toggle local storage and reload, verifying class application and computed styles.

**Manual Verification**:
- [x] Verified manual toggle works.
- [x] Verified page reload maintains theme.
- [x] Verified no white flash when reloading in Dark mode.

## 5. Workflow Checklist
- [x] **Work**: Implemented toggle, persistence, and flicker fix.
- [x] **Test**: Verified in browser.
- [x] **Doc**: Updated roadmap.
