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

1. **Configure Environment**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to set your `WEBUI_SECRET_KEY` (optional for local dev).

2. **Start Services**
   ```bash
   docker-compose up -d
   ```
   *Note: The first run will pull large images (several GBs). Use `docker-compose logs -f` to monitor progress.*

3. **Pull Models**
   Once Ollama is running, pull the foundational models:
   ```bash
   # Enter the Ollama container
   docker exec -it blackbox-ollama ollama pull llama3.2
   docker exec -it blackbox-ollama ollama pull nomic-embed-text # For RAG
   ```

4. **Access the Interface**
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
