# Project Context & Coding Standards

> **[IMPORTANCE: CRITICAL] AI AGENT DIRECTIVE**:
> You MUST read and adhere to [.agent/rules/ai_behavior.md](.agent/rules/ai_behavior.md) at the start of every session. It contains strict operational guardrails, "Ansible-First" policies, and Git branching rules that supersede general instructions.

## 1. Project Overview

**Nebulus** is a production-grade, containerized local AI ecosystem. It integrates **Ollama** (inference), **Open WebUI** (frontend), and **ChromaDB** (RAG) with a custom **MCP Server** to provide a secure, extensible platform for AI engineering.

**Key Philosophy**:
- **Privacy-First**: All data and inference remain local.
- **Ansible-First**: All infrastructure changes are automated and version-controlled.
- **Documentation-First**: Feature development starts with documentation in the [Wiki](https://github.com/jlwestsr/nebulus.wiki).

---

## 2. Technology Stack

### Core Infrastructure
- **Runtime**: Docker & Docker Compose
- **Language**: Python 3.12+ (managed via `uv`)
- **Automation**: Ansible (System setup & verification)

### Services
- **Inference**: [Ollama](https://ollama.com/) (Local LLMs)
- **Frontend**: [Open WebUI](https://docs.openwebui.com/) (ChatGPT-like interface)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/) (Knowledge retrieval)
- **Tools**: Custom MCP Server (FastMCP/FastAPI)
- **Monitoring**: [Dozzle](https://dozzle.com/) (Real-time logs)

### CLI & Utilities
- **CLI Framework**: `click` + `rich`
- **Testing**: `pytest`
- **Linting**: `black`, `flake8`, `pre-commit`

---

## 3. Project Structure

```
nebulus/
├── .agent/              # Antigravity AI Settings
│   ├── rules/           # AI Behavior Rules
│   └── workflows/       # On-demand Agent Tasks
├── ansible/              # Infrastructure automation
│   ├── setup.yml        # Main setup playbook
│   └── verify.yml       # System verification
├── backups/             # Automated volume backups
├── docker-compose.yml   # specialized service orchestration
├── docs/                # Feature specifications
├── mcp_server/          # Custom Tool Server
│   ├── server.py        # MCP Tool definitions
│   ├── scheduler.py     # Background task logic
│   └── static/          # Dashboard UI
├── models/              # Local LLM weights (git-ignored)
├── nebulus.py           # CLI Management Tool (`nebulus`)
├── scripts/             # Shell & Python utilities
│   ├── backup.sh        # Backup logic with retention
│   ├── restore.sh       # Restore logic
│   ├── setup.sh         # Bootstrap script
│   └── health.sh        # Service health checks
└── tests/               # Unit and Integration tests
```

---

## 4. Development Workflow

We follow a strict **Git-Ops** & **Fork-Branch-PR** workflow.

### Git Rules
1.  **Fork First**: Do not clone the main repo directly. Fork it to your account.
2.  **Branch off `develop`**: Create feature branches from `develop`.
    - `feat/new-feature`
    - `fix/bug-fix`
    - `docs/update-readme`
3.  **Pull Request**: Open PRs from your fork to `jlwestsr/nebulus:develop`.
4.  **No Direct Commits**: `main` is protected.

### Automation Rules
1.  **Ansible-First**: Do not manually configure the server. Update `ansible/setup.yml`.
2.  **Verify**: Always run `scripts/run_tests.sh` before pushing.

---

## 5. Coding Standards

### Python
- **Type Hints**: **MANDATORY** for all function signatures.
  ```python
  def execute(command: str, timeout: int = 30) -> str:
  ```
- **Docstrings**: **MANDATORY** for all public functions (Google Style).
  ```python
  """Executes a shell command safely.

  Args:
      command: The command line string.
      timeout: Max execution time in seconds.

  Returns:
      Stdout of the command.
  """
  ```
- **Formatting**: Code must pass `black` and `flake8` (max-line-length: 88).

### Security
1.  **Path Validation**: All file operations must use `_validate_path()` to prevent traversal attacks.
2.  **Command Execution**: Use explicit allowlists for `subprocess`. Never use `shell=True` with user input.
3.  **Secrets**: Never commit secrets. Use `.env` file (template in `.env.example`).

---

## 6. Resources documentation

- **[Nebulus Wiki](https://github.com/jlwestsr/nebulus.wiki)**: Complete documentation.
- **development Guide**: See [Wiki/Development-Guide](https://github.com/jlwestsr/nebulus.wiki/blob/master/Development-Guide.md).
- **Bug Reports**: Use the [Issue Template](.github/ISSUE_TEMPLATE/bug_report.md).
