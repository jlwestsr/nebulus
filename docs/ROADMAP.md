# Feature Roadmap

## 1. Enhanced Agent Capabilities (MCP Server)
Currently, the agent is read-only. To make it a true "Black Box" engineer, we should expand its toolset.
- [ ] **File Write Support**: Add `write_file` and `edit_file` tools to allow the agent to modify code directly.
- [ ] **Web Scraper**: Add a `scrape_url` tool (using `beautifulsoup` or `newspaper3k`) to fetch full page content, enabling deep research beyond search snippets.
- [ ] **Safe Terminal Access**: Add a `run_command` tool (allowlisted commands only, e.g., `ls`, `grep`, `pytest`) to let the agent explore and test the environment.

## 2. Operational Stability
- [ ] **Automated Backups**: Create a script/cron job to snapshot `ollama_data`, `chroma_data`, and `webui_data` volumes.
- [ ] **Log Management**: Add [Dozzle](https://dozzle.com/) to the Docker stack for real-time, web-based log monitoring of all containers.
- [ ] **Health Checks**: Implement a status dashboard (or just a healthcheck script) to verify all services are talking to each other correctly.

## 3. Knowledge & RAG
- [ ] **Codebase Indexing**: Implement a tool like `grep` or `ripgrep` in MCP to allow the agent to search the codebase semantically/regex-wise, complementing the vector store.
- [ ] **Document Parsers**: Add support for parsing PDF/Docx files within the MCP server for direct analysis.

## 4. Model & Performance
- [ ] **Vision Support**: Configure Llava or similar vision-capable models in Ollama by default.
- [ ] **Fine-tuning Pipeline**: A script to prepare local data for easy Lora fine-tuning (future scope).
