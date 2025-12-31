"""
Unit tests for Nebulus Manager CLI.
"""

from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner
from nebulus import cli


@pytest.fixture
def runner():
    """Returns a CliRunner instance."""
    return CliRunner()


@patch("nebulus.run_interactive")
def test_up(mock_run, runner):
    """Verifies that 'up' calls the correct docker command and shows URLs."""
    result = runner.invoke(cli, ["up"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "up", "-d"])

    # Verify Dashboard URLs are shown
    assert "http://localhost:8888" in result.output  # Dozzle
    assert "http://localhost:8000/static/index.html" in result.output  # MCP Server
    assert "http://localhost:8001/docs" in result.output  # ChromaDB
    assert "http://localhost:11435" in result.output  # Ollama


@patch("nebulus.run_interactive")
def test_down(mock_run, runner):
    """Verifies that 'down' calls the correct docker command."""
    result = runner.invoke(cli, ["down"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "down"])


@patch("nebulus.httpx.get")
def test_status_online(mock_get, runner):
    """Verifies that status shows ONLINE when services return 200."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "ONLINE" in result.output
    assert "Ollama" in result.output


@patch("nebulus.httpx.get")
def test_status_offline(mock_get, runner):
    """Verifies that status shows OFFLINE when requests fail."""
    mock_get.side_effect = Exception("Connection refused")

    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "OFFLINE" in result.output


@patch("nebulus.subprocess.run")
def test_backup(mock_run, runner):
    """Verifies that backup calls the backup script."""
    result = runner.invoke(cli, ["backup"])
    assert result.exit_code == 0
    mock_run.assert_called_with(
        ["bash", "scripts/backup.sh"], check=True, text=True, capture_output=False
    )


@patch("nebulus.webbrowser.open")
def test_monitor(mock_open, runner):
    """Verifies that monitor opens the correct URL."""
    result = runner.invoke(cli, ["monitor"])
    assert result.exit_code == 0
    mock_open.assert_called_with("http://localhost:8888")


@patch("nebulus.subprocess.run")
def test_shell(mock_run, runner):
    """Verifies that shell calls docker compose exec."""
    result = runner.invoke(cli, ["shell", "mcp-server"])
    assert result.exit_code == 0
    mock_run.assert_called_with(
        ["docker", "compose", "exec", "mcp-server", "sh"], check=False
    )


@patch("nebulus.run_interactive")
def test_restart(mock_run, runner):
    """Verifies that 'restart' calls the correct docker command."""
    result = runner.invoke(cli, ["restart"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "restart"])


@patch("nebulus.subprocess.run")
def test_logs(mock_run, runner):
    """Verifies that 'logs' calls the correct docker command."""
    result = runner.invoke(cli, ["logs", "webui"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "logs", "-f", "webui"])


@patch("nebulus.run_command")
@patch("nebulus.Path")
@patch("rich.prompt.Prompt.ask")
@patch("rich.prompt.Confirm.ask")
def test_restore(mock_confirm, mock_prompt, mock_path, mock_run_cmd, runner):
    """Verifies the restore flow."""
    # Mock backup listing
    mock_glob = [MagicMock(name="backup1.tar.gz")]
    mock_glob[0].name = "backup1.tar.gz"

    # Configure Path.exists and glob
    mock_path.return_value.exists.return_value = True
    mock_path.return_value.glob.return_value = mock_glob

    mock_prompt.side_effect = [
        "1",
        "target_vol",
    ]  # Select 1st backup, enter volume name
    mock_confirm.return_value = True  # Confirm restore

    result = runner.invoke(cli, ["restore"])

    assert result.exit_code == 0
    mock_run_cmd.assert_called_with(
        ["bash", "scripts/restore.sh", "backup1.tar.gz", "target_vol"]
    )
