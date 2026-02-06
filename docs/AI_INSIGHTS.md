# Project AI Insights (Long-Term Memory)

## Purpose

This document captures project-specific behavioral nuances, recurring pitfalls, and
architectural decisions for AI agent continuity. It is not documentation — it is
institutional knowledge that prevents repeated mistakes. Update this file whenever
you encounter a new pitfall or architectural constraint during development.

## 1. Architectural Patterns

### Service Topology

Five containerized services on a shared Docker bridge network (`ai-network`):

| Service | Internal Port | External Port | Role |
|---------|--------------|---------------|------|
| TabbyAPI | 5000 | 5000 | LLM inference (ExLlamaV2, GPU-bound) |
| ChromaDB | 8000 | 8001 | Vector DB for embeddings and LTM |
| MCP Server | 8000 | 8002 | Tool server (FastMCP/FastAPI, 13 tools) |
| Open WebUI | 8080 | 3000 | Chat frontend |
| Dozzle | 8080 | 8888 | Log monitoring via Docker socket |

### Inter-Service Communication

- Open WebUI connects to TabbyAPI at `http://tabby:5000/v1` (internal network).
- MCP Server connects to ChromaDB at `chromadb:8000` (internal), not the external 8001.
- Scheduler jobs call Ollama at `http://ollama:11434/api/generate` — this endpoint is
  a leftover from a prior Ollama-based stack and will fail unless TabbyAPI or an Ollama
  instance is running at that address.
- No authentication between services. Intended for trusted local networks only.

### Storage Locations

| Data | Location | Persistence |
|------|----------|-------------|
| LLM model weights | `./models` (host) → `/app/models` (tabby) | Git-ignored, persists on host |
| TabbyAPI config | `./config/tabby/config.yml` → `/app/config_mount` (copied at startup) | Version-controlled |
| ChromaDB data | Named volume `chroma_data` → `/chroma/chroma` | Docker volume |
| Open WebUI data | Named volume `webui_data` → `/app/backend/data` | Docker volume |
| Scheduler jobs | `src/mcp_server/scheduler.db` (SQLite) | Inside container, rebuilt on recreate |
| Knowledge graph | `data/memory_graph.json` (NetworkX) | Host filesystem |

### Dual Memory Architecture

The LTM system uses two parallel stores:

- **Vector store** (ChromaDB): Episodic memory with semantic search. Collection: `ltm_episodic_memory`.
- **Graph store** (NetworkX → JSON): Knowledge graph for entity relationships. File: `data/memory_graph.json`.
- **Consolidator**: A "sleep cycle" that reads unarchived episodic memories, calls the LLM
  to extract entities/relations, writes them to the graph, and marks memories archived.

### Non-Obvious Decisions

- The MCP server mounts the entire project as `/workspace` — all file tool operations are
  scoped to this path via `_validate_path()`.
- Graph store persists to disk on every write (add_entity, add_relation). No batching.
- The CLI dynamically loads memory commands via `src.core.memory.cli_extension.register_commands()`.
- `nebulus` with no arguments auto-runs the `status` command (health check table).

## 2. Recurring Pitfalls

### Dependency Management

- **Dual requirements files**: `requirements.txt` (project root) and `src/mcp_server/requirements.txt`
  (MCP container). They overlap significantly. Changes to shared packages must be reflected in both,
  or the container build will diverge from the venv.
- **Chroma metadata type constraint**: ChromaDB only accepts primitive types (str, int, float, bool)
  in metadata fields. Complex types must be stringified. This has caused silent data loss when
  dict/list values were passed directly.
- **APScheduler + SQLite**: The scheduler stores jobs in `scheduler.db` inside the container.
  Recreating the container loses all scheduled jobs. This is by design but catches people off guard.

### Configuration Traps

- **TabbyAPI config mounting**: The config is mounted to `/app/config_mount`, then copied to
  `/app/config.yml` by the entrypoint script. Editing the mounted file alone does nothing until
  the container restarts.
- **Port mapping mismatch**: ChromaDB listens on 8000 internally but is exposed on 8001 externally.
  The MCP server connects to `chromadb:8000` (internal). The vector store defaults to port 8001
  (external). When running outside Docker (e.g., tests), you need the external port.
- **NEBULUS_CHROMA_HOST/PORT env vars**: The vector store reads these but the MCP server's `db.py`
  hardcodes `host="chromadb"`, `port=8000`. These two code paths use different connection logic.
- **Missing .env**: Ansible creates `.env` from `.env.example` only if it doesn't exist. If the
  example changes, existing `.env` files won't pick up new variables.

### Environment-Specific Behavior

- **Linux-only enforcement**: `cli.py` exits immediately on non-Linux platforms. This is intentional.
- **Scheduler model hardcoding**: `execute_prompt_and_email()` hardcodes `llama3.1:latest` and the
  Ollama endpoint. With the TabbyAPI migration, this will fail unless updated.
- **Consolidator model hardcoding**: Same issue — uses `llama3.1` via Ollama endpoint for fact extraction.
- **Graceful degradation**: If ChromaDB is offline, the MCP server sets `ltm_client = None` and
  LTM endpoints return 503. The vector store silently returns empty results. The graph store
  is unaffected (local JSON file). This is by design but can mask real connection issues.

### Testing Gotchas

- **conftest.py patches APScheduler globally**: All tests run with a mocked scheduler. If you
  need to test real scheduling behavior, you must override the autouse fixture.
- **pytest pythonpath**: Configured in `pyproject.toml` as `["src", "gantry", "mcp_server"]`.
  The `gantry` path appears to be a legacy reference — there is no `gantry/` directory.
- **Path validation in tests**: MCP tool tests must mock `_validate_path()` to point at a test
  directory, or they will try to operate under `/workspace` (which doesn't exist outside Docker).

## 3. Workflow Nuances

### Pre-Commit Pipeline

The `.pre-commit-config.yaml` runs these hooks in order:

1. `trailing-whitespace` — auto-fixes
2. `end-of-file-fixer` — auto-fixes
3. `check-yaml` — blocks on invalid YAML
4. `check-added-large-files` — blocks on large binaries
5. `black` — auto-formats Python
6. `flake8` — blocks on lint errors
7. `ansible-lint` — blocks on Ansible issues
8. `markdownlint --fix` — auto-fixes markdown, blocks on unfixable issues
9. `pytest` — runs full test suite, blocks on failures

**Key behavior**: When pre-commit auto-fixes files (black, markdownlint, trailing-whitespace),
the commit is rejected. You must `git add` the fixed files and commit again. This is normal
and expected — not a sign of failure.

### Markdownlint Specifics

- Fenced code blocks require a language tag (MD040). Use `text` for generic output blocks.
- This has tripped up CLAUDE.md and similar files with unlabeled code fences.

### Test Execution

```bash
# scripts/run_tests.sh runs:
flake8 .
pytest -p no:cacheprovider
```

- The `-p no:cacheprovider` flag disables pytest caching. No `.pytest_cache` artifacts
  should accumulate.
- Tests expect the venv to be activated (`source venv/bin/activate`).

### Docker Compose Behavior

- `nebulus up` runs `docker compose up -d --build` — always rebuilds images.
- Before starting, the CLI attempts to stop/remove any standalone `open-webui` container
  to avoid port conflicts on 3000.
- All services have resource limits. TabbyAPI gets the GPU (device 1). If only one GPU
  exists, this may need to change to device 0.

### Backup and Restore

- Backups are `.tar.gz` files in `backups/` directory.
- Restore is interactive (prompts for backup selection and volume name).
- Volume name is auto-suggested from the filename pattern (e.g., `chroma` → `chroma_data`).

---

## 4. Cross-Project Learnings

### Pattern: Large-Scale Feature Implementation (from Atom Project)

When implementing complex multi-component features:

**✅ Successful Patterns:**

1. **Incremental Feature Branches** — one branch per major component
2. **Test-First Development** — write tests before/during implementation
3. **Continuous Integration** — run full test suite after each merge
4. **E2E Tests as Gate** — comprehensive integration tests before production
5. **Fast Test Suite** — keep tests under 2-3 seconds for rapid iteration

**❌ Anti-Patterns to Avoid:**

- Don't implement multiple components in one massive commit
- Don't write tests after implementation (leads to implementation-biased tests)
- Don't merge to main without full test suite passing
- Don't skip E2E validation for "simple" features

**Metrics That Matter:**

- 100% test success rate on merge
- Sub-3-second test suite (enables rapid iteration)
- Zero rollbacks (proper testing prevents this)
- Feature branches live <24 hours (prevents merge conflicts)

### Pattern: AI Instruction Files

Maintain three instruction files with distinct purposes:

- **CLAUDE.md** — Project context, architecture, standards (read-first)
- **GEMINI.md** — Gemini-specific instructions and patterns
- **AI_INSIGHTS.md** — Long-term memory, pitfalls, lessons learned (this file)

**Update triggers:**

- CLAUDE.md: Architecture changes, new standards, new tools
- GEMINI.md: Gemini-specific discoveries, brainstorming patterns
- AI_INSIGHTS.md: Pitfalls encountered, recurring issues, project-specific quirks

---

## 5. Recommendations for Future Sessions

### Before Starting Work

1. Read CLAUDE.md (project context)
2. Read AI_INSIGHTS.md (this file) for pitfalls
3. Run `git status` and `git stash list` to check for uncommitted work
4. Run test suite to establish baseline (`scripts/run_tests.sh`)

### During Development

1. Commit frequently (every 10-15 minutes of significant work)
2. Run tests after each logical change
3. Use feature branches for all non-trivial changes
4. Keep branch lifetime under 24 hours

### Before Merging

1. Run full test suite
2. Run pre-commit hooks
3. Verify Docker services if infrastructure changed
4. Update documentation if adding features

### Session End

1. Commit all work (never leave uncommitted changes)
2. Update AI_INSIGHTS.md if new pitfalls discovered
3. Push to remote if work is ready for integration
4. Document any open questions or blockers

## 6. Documentation & Wiki

- **GitHub wiki**: Cloned at `../nebulus-prime.wiki/` (sibling directory). Uses SSH remote (`git@github.com:jlwestsr/nebulus-prime.wiki.git`), `master` branch.
- **Wiki pages** (10): Home, Architecture, Setup-and-Installation, Docker-Services, MCP-Server, CLI-Reference, Models, Development-Guide, Troubleshooting.
- **Wiki initialization**: GitHub wikis must be initialized via the web UI first (create one placeholder page), then local content can be force-pushed.
- **Ecosystem wikis**: All four project wikis are live:
  - `nebulus-prime.wiki` — 10 pages (this project)
  - `nebulus-edge.wiki` — 5 pages
  - `nebulus-core.wiki` — 8 pages
  - `nebulus-gantry.wiki` — 9 pages
- **Cross-project doc sync**: When a feature ships, update the corresponding wiki. Wiki repos are independent git repos — commit and push separately from the main repo.
- **README links old wiki URL**: The README currently links to `github.com/jlwestsr/nebulus/wiki` (old repo name). These should be updated to `github.com/jlwestsr/nebulus-prime/wiki` when convenient.
