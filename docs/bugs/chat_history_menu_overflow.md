# Bug: Chat History Menu Overflow

**Status**: Fixed
**Date**: 2026-01-08
**Context**: Chat sidebar history items

## Issue Description
When a chat title is very long in the sidebar history list, it pushes the "options" button (vertical ellipsis `⋮`) out of the visible area or causes layout issues, making it impossible to access the context menu (Share, Rename, Delete).

## Root Cause
The flexbox container for the history item does not properly handle text overflow for the title label.
- `.nav-label` lacks `min-width: 0` and flex sizing properties to force truncation.
- `.chat-options-btn` is not prevented from shrinking.

## Solution Plan
Apply CSS fixes to `gantry/public/style.css`:
1.  **Truncate Title**: Force `.nav-label` to take available space but truncate with ellipsis if too long.
2.  **Preserve Button**: Prevent `.chat-options-btn` from shrinking so it remains visible.

### CSS Changes
```css
.nav-label {
    /* ... */
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-options-btn {
    /* ... */
    flex-shrink: 0;
}
```

## Verification
- Create a chat with a long title.
- Verify the title truncates (`...`).
- Verify the options button is visible and clickable.
