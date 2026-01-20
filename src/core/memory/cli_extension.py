"""
CLI Extension for Memory Module.
Registers 'memory' commands with the main application entry point.
"""

import click
from rich.console import Console
from rich.table import Table

from .graph_store import GraphStore
from .vector_store import VectorStore
from .consolidator import Consolidator

console = Console()


def register_commands(cli_group: click.Group):
    """Register memory commands to the main CLI group."""

    @cli_group.group()
    def memory():
        """Manage Long-Term Memory (LTM)."""
        pass

    @memory.command()
    def status():
        """Show memory system status."""
        graph = GraphStore()
        # Vector store connection check
        vector = VectorStore()

        stats = graph.get_stats()

        table = Table(title="Memory System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")

        table.add_row("Graph Store", "Nodes", str(stats.node_count))
        table.add_row("Graph Store", "Edges", str(stats.edge_count))
        table.add_row("Graph Store", "Entity Types", ", ".join(stats.entity_types[:5]))

        chroma_status = "Connected" if vector.client else "Offline"
        chroma_style = "green" if vector.client else "red"
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

        graph = GraphStore()
        vector = VectorStore()
        consolidator = Consolidator(vector, graph)

        consolidator.consolidate()

        console.print("[bold green]Consolidation complete.[/bold green]")
