# CLAUDE.md - Nebulus Prime

## Project Overview

Nebulus Prime is a production-grade, containerized local AI ecosystem for Linux. It integrates TabbyAPI/ExLlamaV2 (inference), Open WebUI (frontend), and ChromaDB (RAG) with a custom MCP Server (FastMCP/FastAPI).

**Core principles**: Linux-native, privacy-first (all data local), Ansible-first (no manual infra config), documentation-first.

**Required reading**:

- [AI_DIRECTIVES.md](AI_DIRECTIVES.md) — Agent role, operational guardrails, coding style, and testing standards.
- [WORKFLOW.md](WORKFLOW.md) — Git branching, commit workflows, verification, and parallel development.
- [docs/AI_INSIGHTS.md](docs/AI_INSIGHTS.md) — Long-term memory, recurring pitfalls, cross-project patterns. **Read at the start of every session.**

## Tech Stack

- **Language**: Python 3.10+ (venv)
- **Runtime**: Docker & Docker Compose
- **Automation**: Ansible (`ansible/setup.yml`, `ansible/verify.yml`)
- **CLI**: `click` + `rich` (entry: `src/cli.py`, script: `nebulus.py`)
- **Testing**: `pytest` (config in `pyproject.toml`)
- **Linting**: `black` (line-length 88), `flake8`, `markdownlint`, `ansible-lint`
- **Pre-commit**: `.pre-commit-config.yaml` (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, black, flake8, ansible-lint, markdownlint, pytest)

## Project Structure

```text
src/                    # All application source code
  cli.py                # CLI entry point
  core/                 # Core logic (memory, utils)
  mcp_server/           # Custom MCP tool server (server.py, db.py, scheduler.py, benchmark.py)
    static/             # Dashboard UI
tests/                  # Unit and integration tests
ansible/                # Infrastructure automation playbooks
scripts/                # Shell & Python utilities
  run_tests.sh          # Test runner - run before pushing
  create_worktree.sh    # Git worktree helper (shared venv)
  docker_maintain.sh    # Docker cleanup
docs/                   # Feature specifications
terraform/              # GCP infrastructure
```

## Coding Standards

### Python (Mandatory)

- **Type hints** on ALL function signatures: `def execute(command: str, timeout: int = 30) -> str:`
- **Google-style docstrings** on all public functions with Args, Returns, Raises sections
- **Formatting**: must pass `black` (line-length 88) and `flake8`
- **Security**: use `_validate_path()` for all file operations; use explicit allowlists for `subprocess`; never use `shell=True` with user input; never commit secrets

### When Editing Existing Files

- Small readability improvements (unused imports, etc.) in the file being edited are encouraged
- Search `src/` before creating new utility functions — reuse existing implementations
- Check `requirements.txt` before adding new dependencies

## Git Workflow

### Branching

- **Branch off `develop`** — never commit directly to `main`
- Branch naming: `feat/`, `fix/`, `docs/`, `chore/` prefixes
- Feature/fix/docs/chore branches are **local only** — never push them to origin
- Only `develop` and `main` exist on the remote
- Merge feature branches into `develop`, then push `develop`

### Commits

- **Conventional commits**: `feat:`, `fix:`, `docs:`, `chore:` prefixes
- `git push origin` requires explicit user approval — always ask first

### Verification Before Push

Run `scripts/run_tests.sh` (or `pre-commit run --all-files`) before pushing. This runs: trailing-whitespace, end-of-file-fixer, check-yaml, black, flake8, ansible-lint, markdownlint, pytest.

### Parallel Development

Use `scripts/create_worktree.sh <branch> <path>` for git worktrees (shares venv, zero disk overhead). Never run bare `git worktree add`.

## Running Tests

```bash
# Activate venv first
source venv/bin/activate

# Run pytest
pytest

# Run full pre-commit suite
pre-commit run --all-files

# Or use the project script
./scripts/run_tests.sh
```

Pytest config: `pyproject.toml` — test paths: `tests/`, python paths: `.`, `src`, `mcp_server`.

## Key Commands

```bash
nebulus              # CLI entry point (installed via pyproject.toml)
python nebulus.py    # Alternative CLI entry
```

## Infrastructure Rules

- **Ansible-first**: do not manually run `apt install`, `pip install`, or config edits. Port changes to `ansible/setup.yml`
- After applying Ansible roles, verify with: `ansible-playbook ansible/verify.yml`
- Run `scripts/docker_maintain.sh` for periodic Docker cleanup

## Multi-File Changes

For changes affecting more than 2 files or introducing new architecture, create an implementation plan and get approval before proceeding.

## Long-Term Memory

**CRITICAL**: Read [docs/AI_INSIGHTS.md](docs/AI_INSIGHTS.md) at the start of **every session** before doing any work. This file contains:

- **Architectural Patterns**: Service topology, inter-service communication, storage locations, dual memory architecture
- **Recurring Pitfalls**: Dependency traps, configuration gotchas, environment-specific quirks, testing issues
- **Workflow Nuances**: Pre-commit pipeline behavior, Docker Compose patterns, backup/restore procedures
- **Cross-Project Learnings**: Successful implementation patterns from Nebulus Atom and other projects
- **Recommendations**: Session start checklist, development best practices, merge verification steps

Update AI_INSIGHTS.md when you encounter:

- New pitfalls or recurring issues not already documented
- Project-specific architectural constraints or non-obvious design decisions
- Successful implementation patterns worth sharing across projects
- Configuration traps that wasted time or caused errors

This file prevents repeating the same mistakes and captures institutional knowledge that prevents context loss across sessions.
