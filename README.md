# Black Box AI System

A containerized, general-purpose local AI ecosystem.

> [!WARNING]
> **Use at your own risk.** This project allows AI models to read local files and browse the internet. Ensure you review all code and run in a safe environment.

## Stack
- **Backend Inference**: [Ollama](https://ollama.com/)
- **Frontend**: [Open WebUI](https://docs.openwebui.com/)
- **RAG**: ChromaDB (Vector Store)
- **Tools**: Custom MCP Server (Python/FastAPI)
- **Backups**: `scripts/backup.sh` and `scripts/restore.sh` for data safety.
- **Document Parsers**: Support for reading PDF and DOCX files.
- **Vision Support**: `llama3.2-vision` model integrated for image analysis.
- **Fine-tuning**: `scripts/finetune/` pipeline to create ShareGPT datasets from chat logs.
- **Health Checks**: `scripts/health.sh` monitors all service statuses.
- **Monitoring**: [Dozzle](https://dozzle.com) (Log Viewer)

## Default Models
- `llama3.1:latest` (General Purpose)
- `qwen2.5-coder:latest` (Coding Specialist)
- `glm-4.7:cloud` (Advanced Cloud Model)
- `nomic-embed-text` (Embeddings)

## Prerequisites
- Docker & Docker Compose
- (Recommended) NVIDIA GPU with Container Toolkit (Enable by default in `docker-compose.yml`)

## Setup

1. **Run the Setup Script**
   This automated script checks for dependencies (uv, ansible) and runs the playbook to provision the system.
   ```bash
   ./scripts/setup.sh
   ```

2. **Access the Interface**
   - Open [http://localhost:3000](http://localhost:3000)
   - The first account created becomes the Admin.

## Features

### MCP Tool Integration
The system includes a custom MCP (Model Context Protocol) server running on the internal network at `http://mcp-server:8000/sse`.

**To connect in Open WebUI:**
1. Go to **Settings > Admin Settings > Tools**.
2. Add a new tool connection.
3. Use the URL: `http://mcp-server:8000/sse` (this hostname works inside the Docker network).

This enables the agent to:
- Read local files in this project directory (mounted at `/workspace`).
- Search the web via DuckDuckGo.

### RAG Pipeline
Documents uploaded to Open WebUI are automatically vectorized using `nomic-embed-text` (running on Ollama) and stored in ChromaDB for persistent retrieval.

## Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
