# Bug: Dashboard Flash on Load

**Status**: Fixed
**Date**: 2026-01-08
**Context**: Frontend / Script.js

## Issue Description
When loading an old chat (which now triggers a full page reload with `?chat_id=...`), the custom "Dashboard" (Welcome screen) momentarily flashes on the screen before disappearing.

## Root Cause
Likely a race condition or logic error in `Nebulus.Dashboard.checkAndInject()`.
If `Nebulus.init()` runs before URL params are fully accessible (unlikely) or if `MutationObserver` triggers `inject()` erroneously.
Or specifically: The `checkAndInject` logic might be calling `inject()` in some edge case, or `hide()` is too slow?
Actually, if `inject()` is NOT called, the dashboard shouldn't exist. So `inject()` MUST be getting called.

## Solution Plan
1.  Debug `checkAndInject`. Add logging.
2.  Ensure `inject()` is strictly guarded by `!chat_id`.
3.  Maybe CSS "display: none" default?

## Verification
- Load a chat ID URL.
- Ensure no Dashboard flash.
