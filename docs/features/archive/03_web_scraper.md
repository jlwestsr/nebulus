# Feature: Web Scraper

## 1. Overview
**Branch**: `feat/web-scraper`

Add a `scrape_url` tool to the MCP server. While the search tool finds links, this tool allows the agent to read the full content of a page, enabling deep research and documentation analysis.

## 2. Requirements
List specific, testable requirements:
- [x] Implement `scrape_url` tool: Accepts `url`.
- [x] **Parsing**: Extract main text content from HTML, removing ads/nav (using `beautifulsoup4` or `newspaper3k`).
- [x] **Formatting**: Return clean Markdown.
- [x] **Error Handling**: Gracefully handle 404s, timeouts, and unparseable content.

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py`.
- **Dependencies**: Add `beautifulsoup4` and `requests` (or `httpx`) to `mcp_server/requirements.txt`.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [x] Script/Test: `test_scraper.py` checking extraction against a known static HTML page.
- [x] Logic Verified: Ensure HTML tags are stripped and text is readable.

**Manual Verification**:
- [x] Step 1: Ask agent to "Read https://example.com".
- [x] Step 2: Verify it returns the full text content of the page.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/web-scraper` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
