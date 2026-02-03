"""PrimeAdapter - Linux platform adapter for the Nebulus ecosystem.

Provides platform-specific configuration for Docker Compose-based services
running TabbyAPI (LLM), ChromaDB (vectors), and Open WebUI (frontend).
"""

import os
import subprocess
from pathlib import Path

from nebulus_core.platform.base import ServiceInfo


class PrimeAdapter:
    """Linux platform adapter using Docker Compose."""

    @property
    def platform_name(self) -> str:
        """Platform identifier."""
        return "prime"

    @property
    def llm_base_url(self) -> str:
        """TabbyAPI endpoint."""
        host = os.getenv("NEBULUS_LLM_HOST", "localhost")
        port = os.getenv("NEBULUS_LLM_PORT", "5000")
        return f"http://{host}:{port}/v1"

    @property
    def chroma_settings(self) -> dict:
        """ChromaDB HTTP connection settings."""
        return {
            "mode": "http",
            "host": os.getenv("NEBULUS_CHROMA_HOST", "localhost"),
            "port": int(os.getenv("NEBULUS_CHROMA_PORT", "8001")),
        }

    @property
    def default_model(self) -> str:
        """Default LLM model name."""
        return os.getenv("NEBULUS_MODEL", "llama3.1")

    @property
    def data_dir(self) -> Path:
        """Root directory for persistent data."""
        return Path(os.getenv("NEBULUS_DATA_DIR", "data"))

    @property
    def services(self) -> list[ServiceInfo]:
        """Managed Docker Compose services."""
        return [
            ServiceInfo(
                name="tabbyapi",
                port=5000,
                health_endpoint="http://localhost:5000/v1/models",
                description="TabbyAPI LLM inference server",
            ),
            ServiceInfo(
                name="chromadb",
                port=8001,
                health_endpoint="http://localhost:8001/api/v1/heartbeat",
                description="ChromaDB vector database",
            ),
            ServiceInfo(
                name="open-webui",
                port=3000,
                health_endpoint="http://localhost:3000",
                description="Open WebUI frontend",
            ),
        ]

    def start_services(self) -> None:
        """Start services via Docker Compose."""
        subprocess.run(
            ["docker", "compose", "up", "-d"],
            check=True,
        )

    def stop_services(self) -> None:
        """Stop services via Docker Compose."""
        subprocess.run(
            ["docker", "compose", "down"],
            check=True,
        )

    def restart_services(self, service: str | None = None) -> None:
        """Restart one or all services.

        Args:
            service: Specific service name, or None for all.
        """
        cmd = ["docker", "compose", "restart"]
        if service:
            cmd.append(service)
        subprocess.run(cmd, check=True)

    def get_logs(self, service: str, follow: bool = False) -> None:
        """Stream Docker Compose logs.

        Args:
            service: Service name.
            follow: Whether to follow/tail.
        """
        cmd = ["docker", "compose", "logs"]
        if follow:
            cmd.append("-f")
        cmd.append(service)
        subprocess.run(cmd)

    def platform_specific_commands(self) -> list:
        """No extra CLI commands for now."""
        return []
