# Feature: Document Parsers

## 1. Overview
**Branch**: `feat/document-parsers`

Expand the MCP server's file reading capabilities to support binary document formats like PDF and DOCX. This allows the agent to ingest requirements, research papers, and legacy documentation directly.

## 2. Requirements
List specific, testable requirements:
- [x] Implement `read_pdf` tool.
- [x] Implement `read_docx` tool.
- [x] **Library**: Use `pypdf` (or `pdfminer.six`) and `python-docx`.
- [x] **Output**: Return extracted text content.

## 3. Technical Implementation
- **Modules**: Modify `mcp_server/server.py`.
- **Dependencies**: Add `pypdf`, `python-docx` to `mcp_server/requirements.txt`.
- **Data**: None.

## 4. Verification Plan
**Automated Tests**:
- [x] Script/Test: `test_parsers.py`. Test against sample PDF/DOCX files.

**Manual Verification**:
- [x] Step 1: Upload a PDF to the workspace.
- [x] Step 2: Ask agent to "Summarize resume.pdf".
- [x] Step 3: Verify it reads and understands the content.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [x] **Branch**: Created `feat/document-parsers` branch?
- [x] **Work**: Implemented changes?
- [x] **Test**: All tests pass?
- [x] **Doc**: Updated `README.md`?
- [x] **Data**: `git add .`, `git commit`, `git push`?
