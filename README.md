# Black Box AI System

A containerized, general-purpose local AI ecosystem.

## Stack
- **Backend Inference**: [Ollama](https://ollama.com/)
- **Frontend**: [Open WebUI](https://docs.openwebui.com/)
- **RAG**: ChromaDB (Vector Store)
- **Tools**: Custom MCP Server (Python/FastAPI)

## Prerequisites
- Docker & Docker Compose
- (Optional) NVIDIA GPU with Container Toolkit for acceleration

## Setup

1. **Run the Setup Playbook**
   This single command creates the environment, starts the services, and pulls the models.
   ```bash
   ansible-playbook -i ansible/inventory ansible/setup.yml
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
