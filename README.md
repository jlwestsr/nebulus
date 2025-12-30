# Nebulus - Black Box AI System

A containerized, general-purpose local AI ecosystem with extended tool access and automation capabilities.

> [!WARNING]
> **Use at your own risk.** This project allows AI models to read local files and browse the internet. Ensure you review all code and run in a safe environment.

## 📚 Documentation

**Complete documentation available in the [Nebulus Wiki](https://github.com/jlwestsr/nebulus/wiki)**

### Quick Links
- **[Setup and Installation](https://github.com/jlwestsr/nebulus/wiki/Setup-and-Installation)** - Get started in minutes
- **[CLI Reference](https://github.com/jlwestsr/nebulus/wiki/CLI-Reference)** - Master the `nebulus` command
- **[Features](https://github.com/jlwestsr/nebulus/wiki/Features)** - Explore all capabilities
- **[Architecture](https://github.com/jlwestsr/nebulus/wiki/Architecture)** - Understand the system design
- **[Troubleshooting](https://github.com/jlwestsr/nebulus/wiki/Troubleshooting)** - Common issues and solutions

## Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Inference** | [Ollama](https://ollama.com/) | Local LLM runtime with GPU support |
| **Frontend** | [Open WebUI](https://docs.openwebui.com/) | Chat interface and RAG |
| **Vector DB** | ChromaDB | Persistent embeddings storage |
| **Tools** | Custom MCP Server | Extended AI capabilities |
| **Monitoring** | [Dozzle](https://dozzle.com) | Real-time log viewer |
| **Automation** | Ansible | Infrastructure as code |

## Default Models (Preinstalled)

- `llama3.1:latest` (General Purpose - **Default**)
- `llama3.2-vision:latest` (Vision Support)
- `qwen2.5-coder:latest` (Coding Specialist)
- `nomic-embed-text` (Embeddings for RAG)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Recommended) NVIDIA GPU with Container Toolkit

### Installation

Please refer to the **[Setup and Installation Guide](https://github.com/jlwestsr/nebulus/wiki/Setup-and-Installation)** for complete installation instructions.

### Access

- **Open WebUI**: [http://localhost:3000](http://localhost:3000)
- **MCP Server**: [http://localhost:8000](http://localhost:8000)
- **Dozzle (Logs)**: [http://localhost:8888](http://localhost:8888)

**First-time setup**: The first account created becomes the admin.

## Management CLI

Nebulus includes a unified command-line tool:

```bash
nebulus --help
```

**Common Commands:**
```bash
nebulus up          # Start all services
nebulus down        # Stop all services
nebulus status      # Service health dashboard
nebulus logs        # Stream logs
nebulus monitor     # Launch Dozzle
nebulus backup      # Backup data volumes
nebulus restore     # Restore from backup
```

See **[CLI Reference](https://github.com/jlwestsr/nebulus/wiki/CLI-Reference)** for complete documentation.

## Features

### 🛠️ MCP Tool Integration

The custom MCP server provides AI agents with extended capabilities:

**File Operations**
- Read, write, and edit files in the workspace
- List directories and search code

**Web Access**
- DuckDuckGo web search
- URL scraping and content extraction

**Terminal Access**
- Safe command execution (whitelisted commands only)
- Git operations, pytest, grep, find

**Document Parsing**
- PDF text extraction
- DOCX document reading

**Vision Support**
- Image analysis with `llama3.2-vision`

**Task Automation**
- Schedule recurring AI tasks with cron
- Email reports automatically
- Web dashboard for task management

**To connect in Open WebUI:**
1. Go to **Settings → Admin Settings → Tools**
2. Add a new tool connection
3. URL: `http://mcp-server:8000/sse`

See **[MCP Server](https://github.com/jlwestsr/nebulus/wiki/MCP-Server)** for complete tool documentation.

### 📊 RAG Pipeline

Documents uploaded to Open WebUI are automatically:
1. Chunked into segments
2. Embedded using `nomic-embed-text` (via Ollama)
3. Stored in ChromaDB for persistent retrieval
4. Available for semantic search in conversations

### 🔄 Automation

- **Ansible-driven setup** - Reproducible infrastructure
- **Scheduled tasks** - Recurring AI workflows with email delivery
- **Automated backups** - Data persistence and recovery
- **Health monitoring** - Service status checks

### 🧪 Development Features

- **Fine-tuning pipeline** - Export chat logs to ShareGPT format
- **Unit tests** - Comprehensive test coverage
- **Code formatting** - Black and Flake8 integration
- **Pre-commit hooks** - Automated quality checks

See **[Features](https://github.com/jlwestsr/nebulus/wiki/Features)** for the complete feature catalog.

## Documentation

| Topic | Link |
|-------|------|
| **Getting Started** | [Setup and Installation](https://github.com/jlwestsr/nebulus/wiki/Setup-and-Installation) |
| **System Design** | [Architecture](https://github.com/jlwestsr/nebulus/wiki/Architecture) |
| **CLI Tool** | [CLI Reference](https://github.com/jlwestsr/nebulus/wiki/CLI-Reference) |
| **All Features** | [Features](https://github.com/jlwestsr/nebulus/wiki/Features) |
| **Docker Config** | [Docker Services](https://github.com/jlwestsr/nebulus/wiki/Docker-Services) |
| **Tool Server** | [MCP Server](https://github.com/jlwestsr/nebulus/wiki/MCP-Server) |
| **Contributing** | [Development Guide](https://github.com/jlwestsr/nebulus/wiki/Development-Guide) |
| **Model Management** | [Models](https://github.com/jlwestsr/nebulus/wiki/Models) |
| **Infrastructure** | [Ansible Automation](https://github.com/jlwestsr/nebulus/wiki/Ansible-Automation) |
| **API Docs** | [API Reference](https://github.com/jlwestsr/nebulus/wiki/API-Reference) |
| **Support** | [Troubleshooting](https://github.com/jlwestsr/nebulus/wiki/Troubleshooting) |

## Contributing

Contributions are welcome! Please see the **[Development Guide](https://github.com/jlwestsr/nebulus/wiki/Development-Guide)** for:
- Coding standards (unit tests, type hints, documentation)
- Git workflow (Git Flow)
- Adding new MCP tools
- Testing practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Nebulus Wiki](https://github.com/jlwestsr/nebulus/wiki)
- **Issues**: [GitHub Issues](https://github.com/jlwestsr/nebulus/issues)
- **Troubleshooting**: [Common Issues](https://github.com/jlwestsr/nebulus/wiki/Troubleshooting)
