"""
CLI Extension for Memory Module.
Registers 'memory' commands with the main application entry point.
"""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from nebulus_core.memory.graph_store import GraphStore
from nebulus_core.memory.consolidator import Consolidator
from nebulus_core.vector.client import VectorClient
from nebulus_core.vector.episodic import EpisodicMemory
from nebulus_core.llm.client import LLMClient

console = Console()

# Default configuration (overridable via environment variables)
_CHROMA_HOST = os.getenv("NEBULUS_CHROMA_HOST", "chromadb")
_CHROMA_PORT = int(os.getenv("NEBULUS_CHROMA_PORT", "8000"))
_GRAPH_PATH = Path(os.getenv("NEBULUS_GRAPH_PATH", "data/memory_graph.json"))
_LLM_URL = os.getenv("NEBULUS_LLM_URL", "http://localhost:5000/v1")
_MODEL = os.getenv("NEBULUS_MODEL", "llama3.1")


def register_commands(cli_group: click.Group):
    """Register memory commands to the main CLI group."""

    @cli_group.group()
    def memory():
        """Manage Long-Term Memory (LTM)."""
        pass

    @memory.command()
    def status():
        """Show memory system status."""
        graph = GraphStore(storage_path=_GRAPH_PATH)
        vector = VectorClient(
            settings={"mode": "http", "host": _CHROMA_HOST, "port": _CHROMA_PORT}
        )

        stats = graph.get_stats()

        table = Table(title="Memory System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")

        table.add_row("Graph Store", "Nodes", str(stats.node_count))
        table.add_row("Graph Store", "Edges", str(stats.edge_count))
        table.add_row("Graph Store", "Entity Types", ", ".join(stats.entity_types[:5]))

        chroma_ok = vector.heartbeat()
        chroma_status = "Connected" if chroma_ok else "Offline"
        chroma_style = "green" if chroma_ok else "red"
        table.add_row(
            "Vector Store",
            "Status",
            f"[{chroma_style}]{chroma_status}[/{chroma_style}]",
        )

        console.print(table)

    @memory.command()
    def consolidate():
        """Trigger manual memory consolidation (Sleep Cycle)."""
        console.print("[bold yellow]Starting memory consolidation...[/bold yellow]")

        graph = GraphStore(storage_path=_GRAPH_PATH)
        vector = VectorClient(
            settings={"mode": "http", "host": _CHROMA_HOST, "port": _CHROMA_PORT}
        )
        episodic = EpisodicMemory(vector_client=vector)
        llm = LLMClient(base_url=_LLM_URL)

        consolidator = Consolidator(
            episodic=episodic, graph=graph, llm=llm, model=_MODEL
        )

        result = consolidator.consolidate()
        console.print(f"[bold green]Consolidation complete: {result}[/bold green]")
