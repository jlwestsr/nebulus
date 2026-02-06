# Project Context & Coding Standards

> **[IMPORTANCE: CRITICAL] AI AGENT DIRECTIVE**:
> You MUST read and adhere to the following documents at the start of every session. They contain strict operational guardrails, "Ansible-First" policies, and Git branching rules that supersede general instructions.
>
> - [AI_DIRECTIVES.md](AI_DIRECTIVES.md) — Agent role, operational guardrails, coding style, and testing standards.
> - [WORKFLOW.md](WORKFLOW.md) — Git branching, commit workflows, verification, and parallel development.

## 1. Project Overview

**Nebulus Prime** is a production-grade, containerized local AI ecosystem for Linux. It integrates **TabbyAPI/ExLlamaV2** (inference), **Open WebUI** (frontend), and **ChromaDB** (RAG) with a custom **MCP Server** to provide a secure, extensible platform for AI engineering.

**Key Philosophy**:

- **Linux Native**: Exclusively designed for the Linux kernel.
- **Privacy-First**: All data and inference remain local.
- **Ansible-First**: All infrastructure changes are automated and version-controlled.
- **Documentation-First**: Feature development starts with documentation in the [Wiki](https://github.com/jlwestsr/nebulus.wiki).

## 2. Technology Stack

### Core Infrastructure

- **Runtime**: Docker & Docker Compose
- **Language**: Python 3.12+ (managed via `uv`)
- **Automation**: Ansible (System setup & verification)

### Services

- **Inference**: [TabbyAPI](https://github.com/theroyallab/tabbyAPI) (ExLlamaV2 GPU Runtime)
- **Frontend**: [Open WebUI](https://openwebui.com/) (Chat & UI Interface)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/) (Knowledge retrieval)
- **Tools**: Custom MCP Server (FastMCP/FastAPI)
- **Monitoring**: [Dozzle](https://dozzle.com/) (Real-time logs)

### CLI & Utilities

- **CLI Framework**: `click` + `rich`
- **Testing**: `pytest`
- **Linting**: `black`, `flake8`, `pre-commit`

## 3. Project Structure

---

nebulus/
├── AI_DIRECTIVES.md     # Agent role, guardrails, coding style
├── WORKFLOW.md          # Git branching, commit workflows, verification
├── ansible/             # Infrastructure automation
│   ├── setup.yml        # Main setup playbook
│   └── verify.yml       # System verification
├── backups/             # Automated volume backups
├── docker-compose.yml   # Specialized service orchestration
├── docs/                # Feature specifications
├── models/              # Local LLM weights (git-ignored)
├── scripts/             # Shell & Python utilities
│   ├── backup.sh        # Backup logic
│   ├── bootstrap.sh     # Bootstrap script
│   ├── create_worktree.sh # Git Worktree helper
│   └── docker_maintain.sh # Docker cleanup script
├── src/                 # Application Source Code (MANDATORY)
│   ├── cli.py           # CLI Entry Point
│   ├── core/            # Core Logic (Memory, Utils)
│   └── mcp_server/      # Custom Tool Server
│       ├── benchmark.py # Performance testing
│       ├── db.py        # Database client
│       ├── scheduler.py # Task scheduler
│       ├── server.py    # MCP Tool definitions
│       └── static/      # Dashboard UI
├── terraform/           # GCP Infrastructure
├── tests/               # Unit and Integration tests
├── nebulus.py           # CLI Entry Script
└── requirements.txt     # Python Dependencies

---

## 4. Development Workflow

We follow a strict **Git-Ops** & **Fork-Branch-PR** workflow.

### Git Rules

1. **Fork First**: Do not clone the main repo directly. Fork it to your account.
2. **Branch off `develop`**: Create feature branches from `develop`.
    - `feat/new-feature`
    - `fix/bug-fix`
    - `docs/update-readme`
3. **Pull Request**: Open PRs from your fork to `jlwestsr/nebulus:develop`.
4. **No Direct Commits**: `main` is protected.

### Parallel Development (Git Worktree)

For concurrent tasks (e.g. multiple AI agents), use the **Git Worktree** workflow to save disk space.

- **Helper**: `scripts/create_worktree.sh` (Shared `venv` strategy).
- **Docs**: [docs/workflows/git_worktree.md](docs/workflows/git_worktree.md).

### Operational Maintenance

Prevent "daemon death spirals" by running periodic Docker cleanup.

- **Script**: `scripts/docker_maintain.sh`.
- **Docs**: [docs/operations/docker_maintenance.md](docs/operations/docker_maintenance.md).

### Automation Rules

1. **Ansible-First**: Do not manually configure the server. Update `ansible/setup.yml`.
2. **Push Approval**: `git push origin` requires explicit, just-in-time user approval.
3. **Verify**: Always run `scripts/run_tests.sh` before pushing.

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

1. **Path Validation**: All file operations must use `_validate_path()` to prevent traversal attacks.
2. **Command Execution**: Use explicit allowlists for `subprocess`. Never use `shell=True` with user input.
3. **Secrets**: Never commit secrets. Use `.env` file (template in `.env.example`).

## 6. Resources & Documentation

- **[Nebulus Wiki](https://github.com/jlwestsr/nebulus.wiki)**: Complete documentation.
- **Development Guide**: See [Wiki/Development-Guide](https://github.com/jlwestsr/nebulus.wiki/blob/master/Development-Guide.md).
- **Bug Reports**: Use the [Issue Template](.github/ISSUE_TEMPLATE/bug_report.md).
