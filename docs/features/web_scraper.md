# Feature: Web Scraper

## 1. Overview
**Branch**: `feat/web-scraper`

Add a `scrape_url` tool to the MCP server. While the search tool finds links, this tool allows the agent to read the full content of a page, enabling deep research and documentation analysis.

## 2. Requirements
List specific, testable requirements:
- [ ] Implement `scrape_url` tool: Accepts `url`.
- [ ] **Parsing**: Extract main text content from HTML, removing ads/nav (using `beautifulsoup4` or `newspaper3k`).
- [ ] **Formatting**: Return clean Markdown.
- [ ] **Error Handling**: Gracefully handle 404s, timeouts, and unparseable content.

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py`.
- **Dependencies**: Add `beautifulsoup4` and `requests` (or `httpx`) to `mcp_server/requirements.txt`.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `test_scraper.py` checking extraction against a known static HTML page.
- [ ] Logic Verified: Ensure HTML tags are stripped and text is readable.

**Manual Verification**:
- [ ] Step 1: Ask agent to "Read https://example.com".
- [ ] Step 2: Verify it returns the full text content of the page.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/web-scraper` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
