#!/usr/bin/env python3
"""
Nebulus Manager CLI
Unified command-line interface for the Nebulus AI ecosystem.
"""

__version__ = "0.1.0"


import subprocess
import sys
from pathlib import Path
import webbrowser
from typing import List, Optional

import click
import httpx
from rich.console import Console
from rich.table import Table

console = Console()


def run_command(
    command: List[str], capture_output: bool = False
) -> subprocess.CompletedProcess:
    """Runs a shell command and returns the process result.

    Args:
        command: The command and its arguments as a list of strings.
        capture_output: Whether to capture stdout and stderr.

    Returns:
        The result of the subprocess run.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        return subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=capture_output,
        )
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold red]Error:[/bold red] Command failed: {' '.join(command)}"  # noqa: E231, E501
        )
        if e.stderr:
            console.print(e.stderr)
        sys.exit(1)


def run_interactive(command: List[str]) -> None:
    """Runs a command directly in the terminal for real-time output.

    Args:
        command: The command and its arguments as a list of strings.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    result = subprocess.run(command)
    if result.returncode != 0:
        console.print(
            f"\n[bold red]Note:[/bold red] Command returned exit code {result.returncode}"  # noqa: E231, E501
        )
        # We don't always exit 1 here to allow viewing output
    sys.stdout.flush()
    sys.stderr.flush()


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Nebulus Manager - Manage your AI ecosystem."""
    pass


@cli.command()
def up() -> None:
    """Start all services."""
    console.print("[bold green]Starting Nebulus services...[/bold green]")
    run_interactive(["docker", "compose", "up", "-d"])
    console.print("[bold green]Done.[/bold green]")


@cli.command()
def down() -> None:
    """Stop all services."""
    console.print("[bold yellow]Stopping Nebulus services...[/bold yellow]")
    run_interactive(["docker", "compose", "down"])
    console.print("[bold yellow]Done.[/bold yellow]")


@cli.command()
def restart() -> None:
    """Restart all services."""
    console.print("[bold blue]Restarting Nebulus services...[/bold blue]")
    run_interactive(["docker", "compose", "restart"])
    console.print("[bold green]Restart complete.[/bold green]")


@cli.command()
@click.argument("service", required=False)
def logs(service: Optional[str]) -> None:
    """Stream service logs."""
    cmd = ["docker", "compose", "logs", "-f"]
    if service:
        cmd.append(service)
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass


@cli.command()
def status() -> None:
    """Check the health of all services."""
    table = Table(title="Nebulus Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Endpoint", style="magenta")
    table.add_column("Status", justify="center")

    services = [
        ("Ollama", "http://localhost:11435/api/tags", "11435"),
        ("ChromaDB", "http://localhost:8001/api/v2/heartbeat", "8001"),
        ("MCP Server", "http://localhost:8000/health", "8000"),
        ("Open WebUI", "http://localhost:3000/health", "3000"),
    ]

    with console.status("[bold green]Checking health..."):
        for name, url, port in services:
            try:
                response = httpx.get(url, timeout=5.0)
                if response.status_code < 400:
                    status_text = "[bold green]ONLINE[/bold green]"
                else:
                    status_text = (
                        f"[bold yellow]HTTP {response.status_code}[/bold yellow]"
                    )
            except Exception:
                status_text = "[bold red]OFFLINE[/bold red]"
            table.add_row(name, f"localhost:{port}", status_text)  # noqa: E231

    console.print(table)


@cli.command()
def backup() -> None:
    """Run the backup script."""
    console.print("[bold green]Starting backup...[/bold green]")
    run_command(["bash", "scripts/backup.sh"])


@cli.command()
def restore() -> None:
    """Run the restore script."""
    console.print("[bold yellow]Starting restore...[/bold yellow]")

    # List available backups
    backup_dir = Path("backups")
    if not backup_dir.exists():
        console.print("[bold red]Error:[/bold red] 'backups' directory not found.")
        return

    backups = sorted([f.name for f in backup_dir.glob("*.tar.gz")], reverse=True)
    if not backups:
        console.print(
            "[bold red]Error:[/bold red] No backup files found in 'backups' directory."
        )
        return

    # Prompt user to select a backup
    from rich.prompt import Prompt, Confirm

    console.print("\n[bold]Available Backups:[/bold]")
    for i, backup in enumerate(backups, 1):
        console.print(f"{i}. {backup}")

    choice = Prompt.ask(
        "\nSelect a backup file", choices=[str(i) for i in range(1, len(backups) + 1)]
    )
    selected_backup = backups[int(choice) - 1]

    # Prompt user for volume name
    # Can try to guess based on backup name or just ask
    suggested_volume = "nebulus_webui_data"  # Default suggestion
    if "ollama" in selected_backup:
        suggested_volume = "nebulus_ollama_data"
    elif "chroma" in selected_backup:
        suggested_volume = "nebulus_chroma_data"

    volume = Prompt.ask("Enter target Docker volume name", default=suggested_volume)

    console.print("\n[bold green]Preparing to restore:[/bold green]")
    console.print(f"  Backup: [cyan]{selected_backup}[/cyan]")
    console.print(f"  Volume: [cyan]{volume}[/cyan]")

    if not Confirm.ask("Proceed?"):
        console.print("[yellow]Restore cancelled.[/yellow]")
        return

    run_command(["bash", "scripts/restore.sh", selected_backup, volume])


@cli.command()
def monitor() -> None:
    """Launch the log monitoring dashboard (Dozzle)."""
    url = "http://localhost:8888"
    console.print(f"Opening monitoring dashboard at {url}...")
    webbrowser.open(url)


@cli.command()
@click.argument("service")
def shell(service: str) -> None:
    """Open an interactive shell in a service container."""
    console.print(f"Opening shell in [bold cyan]{service}[/bold cyan]...")
    subprocess.run(["docker", "compose", "exec", service, "sh"], check=False)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Show status if no command provided
        status.callback()  # type: ignore
    else:
        cli()
