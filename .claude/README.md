# Claude Code Configuration — nebulus-prime

**Project Type:** Python CLI + Backend Services
**Platform:** Linux (Docker Compose, NVIDIA GPU)
**Configuration Date:** 2026-02-06

---

## Overview

Per-project Claude Code plugin configuration for Nebulus Prime, the Linux deployment platform with TabbyAPI/ExLlamaV2 inference and Docker orchestration.

## Enabled Plugins

### High Priority

- ✅ **Pyright LSP** — Type checking for CLI and service code
- ✅ **Serena** — Navigate large codebase (CLI, adapters, services)
- ✅ **Superpowers** — TDD and debugging workflows

### Medium Priority

- ✅ **Context7** — Live docs for FastAPI, Docker, TabbyAPI, ChromaDB
- ✅ **PR Review Toolkit** — Code quality checks
- ✅ **Commit Commands** — Git workflow automation
- ✅ **Feature Dev** — Feature development workflows
- ✅ **GitHub** — Release management and wiki publishing

## Disabled Plugins

- ❌ **TypeScript LSP** — No TypeScript
- ❌ **Playwright** — No UI testing
- ❌ **Supabase** — Not using Supabase
- ❌ **Ralph Loop** — No automation loops

## LSP Configuration

### Pyright

Configuration: `pyrightconfig.json` (project root)

**Settings:**

- Type checking: basic
- Python version: 3.10+
- Include: `src/`, `nebulus_prime/`
- Exclude: `__pycache__`, `.pytest_cache`, `data/`, `models/`
- Virtual environment: `./venv`

## Architecture

Prime follows the shared core + platform adapter pattern:

- Installs `nebulus-core` as dependency
- Registers `PrimeAdapter` via entry points
- Provides TabbyAPI inference endpoint
- Manages Docker Compose orchestration

## Testing

Run tests via pytest:

```bash
pytest tests/ -v
```

## Workflow

This project follows the develop→main git workflow:

1. Branch off `develop` for new work
2. Merge features back to `develop` with `--no-ff`
3. Release from `develop` to `main` with version tags

## Why These Plugins?

**Pyright LSP** — Platform adapter code interfaces with nebulus-core. Type checking prevents integration bugs.

**Serena** — Large codebase with CLI, adapters, Docker configs, and service orchestration. Semantic navigation essential.

**Context7** — TabbyAPI and Docker Compose have active development. Live docs keep us current.

**GitHub** — Prime has releases and wiki documentation. GitHub integration streamlines publishing.

## Maintenance

Update this configuration when:

- Adding new services or components
- Performance issues (disable low-value plugins)
- New Claude Code plugins that benefit deployment projects

---

*Part of the West AI Labs plugin strategy. See `../docs/claude-code-plugin-strategy.md` for ecosystem-wide strategy.*
