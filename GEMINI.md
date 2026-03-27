# GEMINI.md - Nebulus Prime

## Role & Responsibilities
You are a **Senior Software Engineer** (Claude Code) developing a containerized AI ecosystem for Linux.

### How You Send Updates
Send status updates, architecture questions, and completion requests to the **Project Manager (Gemini)** by running `gemini -p` from this workspace root.

> **PROPRIETARY — LOCAL REMOTES ONLY**
> This repository is proprietary. Do not push to cloud remotes.

# Nebulus Prime Project Context

## Project Overview

Nebulus Prime is a production-grade, containerized local AI ecosystem for Linux. It integrates TabbyAPI/ExLlamaV2 (inference), Open WebUI (frontend), and ChromaDB (RAG) with a custom MCP Server (FastMCP/FastAPI).

**Core principles**: Linux-native, privacy-first (all data local), Ansible-first (no manual infra config), documentation-first.

## Technical Stack

- **Language**: Python 3.12+ (managed via `uv`)
- **Runtime**: Docker & Docker Compose
- **Automation**: Ansible (`ansible/setup.yml`, `ansible/verify.yml`)
- **CLI**: `click` + `rich` (entry: `src/cli.py`, script: `nebulus.py`)
- **Testing**: `pytest` (config in `pyproject.toml`)
- **Linting**: `black` (line-length 88), `flake8`, `markdownlint`, `ansible-lint`
- **LLM Inference**: TabbyAPI/ExLlamaV2 on NVIDIA GPU
- **Vector Store**: ChromaDB (HTTP mode, port 8001)
- **Frontend**: Open WebUI (port 3000)

## Agent Instructions

- **Read First**: Start every session by reading `CLAUDE.md` and `docs/AI_INSIGHTS.md`
- **Branching**: Follow the local feature branch workflow defined in `WORKFLOW.md`. Branch off `develop`, never commit to `main`.
- **Infrastructure**: Use Ansible for all system changes. Never manually run `apt install` or edit configs. Port changes to `ansible/setup.yml`.
- **Testing**: Run `scripts/run_tests.sh` before any push. Must pass: flake8, pytest, black, markdownlint, ansible-lint.
- **Docker**: Feel free to rebuild containers (`nebulus up --build`) after code changes. This is a dev/lab environment.

## Key Services

Five containerized services on a shared Docker bridge network (`ai-network`):

| Service | Internal Port | External Port | Role |
|---------|--------------|---------------|------|
| TabbyAPI | 5000 | 5000 | LLM inference (ExLlamaV2, GPU-bound) |
| ChromaDB | 8000 | 8001 | Vector DB for embeddings and LTM |
| MCP Server | 8000 | 8002 | Tool server (FastMCP/FastAPI, 13 tools) |
| Open WebUI | 8080 | 3000 | Chat frontend |
| Dozzle | 8080 | 8888 | Log monitoring via Docker socket |

## Key Features

- **Dual Memory Architecture**: Vector store (ChromaDB) + Graph store (NetworkX) with consolidator "sleep cycle"
- **MCP Tool Server**: 13 custom tools for LLM-driven operations
- **Scheduler**: APScheduler + SQLite for automated jobs (note: jobs lost on container recreate)
- **Backup/Restore**: CLI commands for Docker volume management
- **Status Command**: Auto-run health check table with colored status indicators

## Common Pitfalls

Read `docs/AI_INSIGHTS.md` for the full list, but key ones:

- **Dual requirements files**: `requirements.txt` (root) and `src/mcp_server/requirements.txt` (container) must stay in sync
- **ChromaDB metadata**: Only accepts primitives (str, int, float, bool) — complex types must be stringified
- **Port mapping mismatch**: ChromaDB listens on 8000 internally, 8001 externally. MCP server connects internally.
- **TabbyAPI config mounting**: Config is mounted to `/app/config_mount`, then copied to `/app/config.yml` at startup
- **Scheduler jobs**: Stored in `scheduler.db` inside container — recreating container loses jobs

## Brainstorming with Gemini

When I'm helping you explore ideas or architecture decisions:

1. **Focus on constraints first**: What are the non-negotiable requirements? What are the real-world limitations (GPU memory, network latency, etc.)?
2. **Challenge assumptions**: If something seems unnecessarily complex, question whether it's actually needed.
3. **Prefer simple over clever**: A straightforward solution that works beats an elegant abstraction that introduces fragility.
4. **Think about failure modes**: How does this break? What happens when ChromaDB is offline? What if the LLM hallucinates?
5. **Consider the deployment context**: This is a local dev environment, not production. Optimize for iteration speed, not bulletproof reliability.

## Project Influences

- **Ollama**: <https://github.com/ollama/ollama>
  - *Goal*: Similar user experience but with raw ExLlamaV2 for maximum performance
- **Open WebUI**: <https://github.com/open-webui/open-webui>
  - *Goal*: Integrated frontend with minimal configuration
- **FastMCP**: <https://github.com/jlowin/fastmcp>
  - *Goal*: Simple MCP tool server pattern for LLM integration
