# Design: nebulus-core Shared Library

**Date**: 2026-02-03
**Status**: Draft
**Author**: jlwestsr + Claude

## Problem

Nebulus exists as two projects targeting different platforms:

- **Nebulus Prime** — Linux deployment with Docker/TabbyAPI/ExLlamaV2 (NVIDIA GPU)
- **Nebulus Edge** — macOS deployment with bare-metal MLX (Apple Silicon)

Both projects share significant overlapping code (ChromaDB wrappers, FastAPI patterns,
CLI tooling, intelligence features, Pydantic models) but diverge on inference engine,
process management, and deployment strategy. Today, features are built in one project
and manually ported to the other, causing drift and duplicated effort.

## Solution

Extract shared code into a standalone Python package (`nebulus-core`) that both projects
install as a dependency. The package provides a unified CLI, data layer, intelligence
platform, and LLM client — with a platform adapter system for OS-specific operations.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM interface | OpenAI-compatible HTTP endpoint | Both projects already expose `/v1/chat/completions`. No abstraction layer needed. |
| Library location | Separate Git repo (`nebulus-core`) | Clean dependency boundary, own versioning, git-based installs. |
| CLI experience | Single `nebulus` command, auto-detect platform | Simplest UX. MLX won't run on Linux, ExLlamaV2 won't run on Mac. No ambiguity. |
| Governance docs | Per-project (not shared) | Each project has its own wiki and platform-specific context. |
| Domain templates | Bundled in shared library | Both projects need access to dealership, medical, legal templates. |

## Package Structure

```text
nebulus-core/
├── pyproject.toml
├── README.md
├── src/
│   └── nebulus_core/
│       ├── __init__.py
│       ├── cli/                    # CLI framework
│       │   ├── __init__.py
│       │   ├── main.py             # Entry point, platform detection
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   ├── services.py     # up, down, status, restart, logs
│       │   │   ├── models.py       # model list, model get
│       │   │   ├── memory.py       # memory status, memory consolidate
│       │   │   └── backup.py       # backup, restore
│       │   └── output.py           # Rich formatting helpers
│       │
│       ├── platform/               # Platform adapter system
│       │   ├── __init__.py
│       │   ├── base.py             # PlatformAdapter protocol
│       │   ├── registry.py         # Adapter discovery and registration
│       │   └── detection.py        # OS/hardware auto-detection
│       │
│       ├── llm/                    # LLM client
│       │   ├── __init__.py
│       │   └── client.py           # OpenAI-compatible HTTP client
│       │
│       ├── vector/                 # ChromaDB & memory layer
│       │   ├── __init__.py
│       │   ├── client.py           # ChromaDB wrapper (HTTP + embedded modes)
│       │   ├── collections.py      # Collection management
│       │   ├── ltm.py              # Long-term memory (conversations, messages, prefs)
│       │   ├── episodic.py         # Episodic memory + archive cycle
│       │   └── documents.py        # Document indexing for RAG
│       │
│       ├── intelligence/           # Data intelligence platform
│       │   ├── __init__.py
│       │   ├── ingest.py           # CSV ingestion with schema inference
│       │   ├── pii.py              # PII detection & masking
│       │   ├── knowledge.py        # Domain knowledge management
│       │   ├── scoring.py          # Data scoring / classification
│       │   ├── insights.py         # LLM-powered insight generation
│       │   ├── search.py           # Semantic search over collections
│       │   ├── sql_engine.py       # Safe parameterized SQL execution
│       │   ├── feedback.py         # User feedback collection
│       │   ├── refinement.py       # Knowledge refinement from feedback
│       │   ├── audit.py            # Operation audit logging
│       │   └── templates/          # Domain templates
│       │       ├── __init__.py
│       │       ├── base.py         # Base template class
│       │       ├── dealership/     # Auto dealership config
│       │       ├── medical/        # Medical practice config
│       │       └── legal/          # Law firm config
│       │
│       ├── memory/                 # Knowledge graph + consolidation
│       │   ├── __init__.py
│       │   ├── models.py           # Pydantic models (Entity, Relation, MemoryItem)
│       │   ├── graph_store.py      # NetworkX knowledge graph
│       │   └── consolidator.py     # Episodic → graph "sleep cycle"
│       │
│       └── testing/                # Shared test utilities
│           ├── __init__.py
│           ├── fixtures.py         # Mock ChromaDB, mock LLM, temp dirs
│           └── factories.py        # Test data factories
│
└── tests/
    ├── conftest.py
    ├── test_cli/
    ├── test_vector/
    ├── test_intelligence/
    ├── test_memory/
    └── test_llm/
```

## Platform Adapter Interface

Each platform project implements this protocol:

```python
from typing import Protocol

class ServiceInfo:
    """Describes a managed service."""
    name: str
    port: int
    health_endpoint: str
    description: str

class PlatformAdapter(Protocol):
    """Interface that each platform project implements."""

    @property
    def platform_name(self) -> str:
        """e.g. 'prime' or 'edge'"""
        ...

    @property
    def services(self) -> list[ServiceInfo]:
        """All services managed by this platform."""
        ...

    @property
    def llm_base_url(self) -> str:
        """OpenAI-compatible endpoint URL."""
        ...

    @property
    def chroma_settings(self) -> dict:
        """ChromaDB connection config (host, port, or embedded path)."""
        ...

    def start_services(self) -> None:
        """Start all platform services."""
        ...

    def stop_services(self) -> None:
        """Stop all platform services."""
        ...

    def restart_services(self, service: str | None = None) -> None:
        """Restart one or all services."""
        ...

    def get_logs(self, service: str, follow: bool = False) -> None:
        """Stream logs for a service."""
        ...

    def platform_specific_commands(self) -> list:
        """Return additional Click commands for this platform."""
        ...
```

### Prime Adapter (nebulus-prime)

```python
class PrimeAdapter:
    platform_name = "prime"
    llm_base_url = "http://localhost:5000/v1"

    def start_services(self):
        subprocess.run(["docker", "compose", "up", "-d", "--build"])

    def stop_services(self):
        subprocess.run(["docker", "compose", "down"])
```

### Edge Adapter (nebulus-edge)

```python
class EdgeAdapter:
    platform_name = "edge"
    llm_base_url = "http://localhost:8080/v1"

    def start_services(self):
        subprocess.run(["pm2", "start", "infrastructure/pm2_config.json"])

    def stop_services(self):
        subprocess.run(["pm2", "stop", "all"])
```

## Platform Detection

```python
import platform
import os

def detect_platform() -> str:
    system = platform.system()
    if system == "Linux":
        return "prime"
    elif system == "Darwin":
        machine = platform.machine()
        if machine == "arm64":
            return "edge"
    raise RuntimeError(f"Unsupported platform: {system}/{platform.machine()}")
```

## Adapter Registration

Platform projects register their adapter via Python entry points in `pyproject.toml`:

```toml
# In nebulus-prime/pyproject.toml
[project.entry-points."nebulus.platform"]
prime = "nebulus_prime.adapter:PrimeAdapter"

# In nebulus-edge/pyproject.toml
[project.entry-points."nebulus.platform"]
edge = "nebulus_edge.adapter:EdgeAdapter"
```

The shared CLI discovers adapters at runtime:

```python
from importlib.metadata import entry_points

def load_adapter(platform_name: str) -> PlatformAdapter:
    eps = entry_points(group="nebulus.platform")
    for ep in eps:
        if ep.name == platform_name:
            adapter_cls = ep.load()
            return adapter_cls()
    raise RuntimeError(f"No adapter found for platform: {platform_name}")
```

## LLM Client

A thin HTTP client that talks to whichever OpenAI-compatible endpoint the platform
adapter provides:

```python
import httpx

class LLMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=120.0)

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        resp = self.client.post(
            f"{self.base_url}/chat/completions",
            json={"messages": messages, "model": model},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def list_models(self) -> list[dict]:
        resp = self.client.get(f"{self.base_url}/models")
        resp.raise_for_status()
        return resp.json()["data"]
```

## ChromaDB Connection Modes

The vector client supports both deployment patterns:

```python
import chromadb

class VectorClient:
    def __init__(self, settings: dict):
        if settings.get("mode") == "embedded":
            self.client = chromadb.PersistentClient(
                path=settings["path"]
            )
        else:
            self.client = chromadb.HttpClient(
                host=settings["host"],
                port=settings["port"],
            )
```

- **Prime**: `{"mode": "http", "host": "localhost", "port": 8001}`
- **Edge**: `{"mode": "embedded", "path": "intelligence/storage/vectors"}`

## CLI Command Flow

```text
User types: nebulus status

1. CLI entry point (nebulus_core.cli.main)
2. detect_platform() → "prime" or "edge"
3. load_adapter("prime") → PrimeAdapter instance
4. Execute status command:
   a. adapter.services → list of ServiceInfo
   b. For each service, HTTP GET health_endpoint
   c. Render Rich table with status
5. adapter.platform_specific_commands() → add any extra commands
```

## Installation & Development

### nebulus-core (the shared library)

```toml
# nebulus-core/pyproject.toml
[project]
name = "nebulus-core"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "click",
    "rich",
    "httpx",
    "pydantic",
    "chromadb",
    "networkx",
    "pandas",
    "sqlalchemy",
    "beautifulsoup4",
]

[project.scripts]
nebulus = "nebulus_core.cli.main:cli"
```

### nebulus-prime (Linux project)

```toml
# nebulus-prime/pyproject.toml
[project]
name = "nebulus-prime"
dependencies = [
    "nebulus-core @ git+https://github.com/jlwestsr/nebulus-core.git",
]

[project.entry-points."nebulus.platform"]
prime = "nebulus_prime.adapter:PrimeAdapter"
```

### nebulus-edge (macOS project)

```toml
# nebulus-edge/pyproject.toml
[project]
name = "nebulus-edge"
dependencies = [
    "nebulus-core @ git+https://github.com/jlwestsr/nebulus-core.git",
    "mlx-lm",
]

[project.entry-points."nebulus.platform"]
edge = "nebulus_edge.adapter:EdgeAdapter"
```

### Local Development

```bash
# Clone all three repos side by side
git clone ... nebulus-core
git clone ... nebulus-prime
git clone ... nebulus-edge

# Editable install for active development
cd nebulus-prime
pip install -e ../nebulus-core
pip install -e .
```

## Migration Path

### Phase 1: Foundation

1. Create `nebulus-core` repo with pyproject.toml, basic structure
2. Implement platform detection and adapter interface
3. Move CLI framework (Click + Rich) into shared library
4. Implement core commands: `status`, `up`, `down`, `logs`
5. Create PrimeAdapter in nebulus-prime, EdgeAdapter in nebulus-edge
6. Both projects install nebulus-core and verify CLI works

### Phase 2: Data Layer

1. Move ChromaDB wrapper into `nebulus_core.vector`
2. Implement dual-mode client (HTTP + embedded)
3. Move LTM operations (conversations, messages, preferences)
4. Move episodic memory and document indexing
5. Move knowledge graph (NetworkX) and consolidator
6. Update both projects to use shared vector/memory modules

### Phase 3: Intelligence

1. Move intelligence layer from Edge into `nebulus_core.intelligence`
2. Generalize any Edge-specific assumptions
3. Bundle domain templates (dealership, medical, legal)
4. Move PII detection, feedback loop, audit logging
5. Wire Prime to use intelligence features it didn't previously have
6. Update both projects to use shared intelligence modules

### Phase 4: LLM Client & Cleanup

1. Move LLM client into shared library
2. Replace all hardcoded Ollama/TabbyAPI/MLX calls with `LLMClient`
3. Remove duplicated code from both platform projects
4. Shared test fixtures and CI setup
5. Tag `v0.1.0` of nebulus-core

## What Each Project Keeps

### nebulus-prime retains

- `docker-compose.yml` and container configs
- `config/tabby/` TabbyAPI configuration
- Ansible playbooks (Linux-specific roles)
- Terraform infrastructure (GCP/AWS/Azure)
- `PrimeAdapter` implementation
- Platform-specific CLI commands (GPU info, Docker maintenance)
- Dozzle monitoring config
- MCP server container and Dockerfile

### nebulus-edge retains

- `brain/` MLX inference server
- `infrastructure/` PM2 configs and startup scripts
- `body/` Open WebUI Docker config
- Ansible playbooks (macOS-specific roles)
- `EdgeAdapter` implementation
- Platform-specific CLI commands (Apple Silicon stats, MLX model management)
- Customer-specific customizations

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes in nebulus-core affect both projects | High | Semantic versioning. Pin to tags in production. Use editable installs only in development. |
| Over-abstracting platform differences | Medium | Keep the adapter interface minimal. Only abstract what both projects actually need. |
| Intelligence layer too Edge-specific to generalize | Medium | Phase 3 is last. By then the pattern is proven. If something doesn't generalize, leave it in Edge. |
| ChromaDB embedded vs HTTP mode causes subtle bugs | Medium | Shared test suite runs both modes. Integration tests in CI. |
| Entry point discovery fails in some environments | Low | Fallback to environment variable `NEBULUS_PLATFORM=prime\|edge` for explicit override. |
