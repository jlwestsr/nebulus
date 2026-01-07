# Feature: Web Search & Browsing

## 1. Overview
**Branch**: `feat/web-search`

Implement web search capabilities (e.g., SearXNG, Tavily) and URL browsing to allow the LLM to access real-time information.

## 2. Requirements
List specific, testable requirements:
- [ ] **Search Tool**:
    - [ ] Integrate a search provider (SearXNG/Google/DuckDuckGo).
    - [ ] Enable `#` or similar trigger to insert search results.
- [ ] **URL Browsing**:
    - [ ] Ability to read and parse content from a given URL.
    - [ ] Inject parsed content into context.
- [ ] **Citations**:
    - [ ] Display source URLs for retrieved information.

## 3. Technical Implementation
- **Modules**: `gantry/tools/search.py`, `gantry/tools/browser.py`
- **Dependencies**: `beautifulsoup4`, `requests`, `googlesearch-python` (or API client).
- **Data**: N/A

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/tools/test_search.py`
- [ ] Logic Verified: Search returns expected results, URL parser extracts text.

**Manual Verification**:
- [ ] Step 1: Ask "What is the latest news on X?". Verify search tool is triggered.
- [ ] Step 2: Paste a URL. Ask for summary. Verify content is read.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/web-search` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
