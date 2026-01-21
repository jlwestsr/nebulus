# Feature: Web Search & Browsing

## 1. Overview

**Branch**: `develop` (Merged from `feat/web-search`)

Implement web search capabilities (e.g., SearXNG, Tavily) and URL browsing to allow the LLM to access real-time information.

## 2. Requirements

List specific, testable requirements:

- [x] **Search Tool**:
  - [x] Integrate a search provider (SearXNG/Google/DuckDuckGo).
  - [x] Enable `#` or similar trigger to insert search results.
- [x] **URL Browsing**:
  - [x] Ability to read and parse content from a given URL.
  - [x] Inject parsed content into context.
- [x] **Citations**:
  - [x] Display source URLs for retrieved information.

## 3. Technical Implementation

- **Modules**: [server.py](file:///home/jlwestsr/projects/west_ai_labs/nebulus/mcp_server/server.py) (MCP Tools: `web_search`, `scrape_url`)
- **Dependencies**: `beautifulsoup4`, `httpx`, `duckduckgo_search`.
- **Data**: N/A

## 4. Verification Plan

**Automated Tests**:

- [x] Script: `pytest tests/test_mcp_tools.py`
- [x] Logic Verified: Search returns expected results, URL parser extracts text.

**Manual Verification**:

- [x] Step 1: Ask "What is the latest news on X?". Verify search tool is triggered.
- [x] Step 2: Paste a URL. Ask for summary. Verify content is read.

## 5. Workflow Checklist

Follow the AI Behavior strict workflow:

- [x] **Branch**: Created `feat/web-search` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass (`pytest`)?
- [x] **Doc**: Updated `README.md` and `walkthrough.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
