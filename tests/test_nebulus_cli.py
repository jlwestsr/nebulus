"""
Unit tests for Nebulus Manager CLI.
"""

from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner
from src.cli import cli


@pytest.fixture
def runner():
    """Returns a CliRunner instance."""
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_linux_platform():
    """Mocks sys.platform to 'linux' for all tests by default."""
    with patch("sys.platform", "linux"):
        yield


@patch("src.cli.subprocess.run")
@patch("src.cli.run_interactive")
def test_up(mock_interactive, mock_run, runner):
    """Verifies that 'up' calls the correct docker command and shows URLs."""
    result = runner.invoke(cli, ["up"])
    assert result.exit_code == 0
    mock_interactive.assert_called_with(["docker", "compose", "up", "-d"])

    # Verify cleanup calls
    stop_call = MagicMock()
    stop_call.args = ["docker", "stop", "open-webui"]
    mock_run.assert_any_call(
        ["docker", "stop", "open-webui"],
        capture_output=True,
        check=False,
        timeout=10,
    )
    mock_run.assert_any_call(
        ["docker", "rm", "open-webui"],
        capture_output=True,
        check=False,
        timeout=10,
    )

    # Verify Dashboard URLs are shown
    assert "http://localhost:3000" in result.output  # Open WebUI
    assert "http://localhost:8888" in result.output  # Dozzle
    assert (
        "http://localhost:8002/static/index.html" in result.output
    )  # MCP Server (New Port)
    assert "http://localhost:8001/docs" in result.output  # ChromaDB
    assert "http://localhost:5000/v1/models" in result.output  # TabbyAPI


@patch("src.cli.subprocess.run")
@patch("src.cli.run_interactive")
def test_down(mock_interactive, mock_run, runner):
    """Verifies that 'down' calls the correct docker command."""
    result = runner.invoke(cli, ["down"])
    assert result.exit_code == 0
    mock_interactive.assert_called_with(["docker", "compose", "down"])

    # Verify cleanup calls
    mock_run.assert_any_call(
        ["docker", "stop", "open-webui"],
        capture_output=True,
        check=False,
        timeout=10,
    )
    mock_run.assert_any_call(
        ["docker", "rm", "open-webui"],
        capture_output=True,
        check=False,
        timeout=10,
    )


@patch("src.cli.httpx.get")
def test_status_online(mock_get, runner):
    """Verifies that status shows ONLINE when services return 200."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "ONLINE" in result.output
    assert "ONLINE" in result.output
    assert "Open WebUI" in result.output
    assert "TabbyAPI" in result.output


@patch("src.cli.httpx.get")
def test_status_offline(mock_get, runner):
    """Verifies that status shows OFFLINE when requests fail."""
    mock_get.side_effect = Exception("Connection refused")

    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "OFFLINE" in result.output


@patch("src.cli.subprocess.run")
def test_backup(mock_run, runner):
    """Verifies that backup calls the backup script."""
    result = runner.invoke(cli, ["backup"])
    assert result.exit_code == 0
    mock_run.assert_called_with(
        ["bash", "scripts/backup.sh"], check=True, text=True, capture_output=False
    )


@patch("src.cli.webbrowser.open")
def test_monitor(mock_open, runner):
    """Verifies that monitor opens the correct URL."""
    result = runner.invoke(cli, ["monitor"])
    assert result.exit_code == 0
    mock_open.assert_called_with("http://localhost:8888")


@patch("src.cli.subprocess.run")
def test_shell(mock_run, runner):
    """Verifies that shell calls docker compose exec."""
    result = runner.invoke(cli, ["shell", "mcp-server"])
    assert result.exit_code == 0
    mock_run.assert_called_with(
        ["docker", "compose", "exec", "mcp-server", "sh"], check=False
    )


@patch("src.cli.run_interactive")
def test_restart(mock_run, runner):
    """Verifies that 'restart' calls the correct docker command."""
    result = runner.invoke(cli, ["restart"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "restart"])


@patch("src.cli.run_interactive")
def test_rebuild(mock_run, runner):
    """Verifies that 'rebuild' calls the correct docker command."""
    # Test rebuilding all services
    result = runner.invoke(cli, ["rebuild"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "up", "-d", "--build"])

    # Test rebuilding a single service
    result = runner.invoke(cli, ["rebuild", "mcp-server"])
    assert result.exit_code == 0
    mock_run.assert_called_with(
        ["docker", "compose", "up", "-d", "--build", "mcp-server"]
    )

    mock_run.assert_called_with(
        ["docker", "compose", "up", "-d", "--build", "mcp-server"]
    )


def test_help(runner):
    """Verifies that 'help' command shows the main help message."""
    # Mock sys.platform to be linux for this test to pass
    with patch("sys.platform", "linux"):
        result = runner.invoke(cli, ["help"])
        assert result.exit_code == 0
        assert "Nebulus Prime Manager - Manage your AI ecosystem." in result.output
        assert "Commands:" in result.output


def test_linux_only_enforcement(runner):
    """Verifies that CLI exits on non-Linux platforms."""
    with patch("sys.platform", "darwin"):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 1
        assert "Nebulus Prime is a Linux-only system." in result.output


@patch("src.cli.subprocess.run")
def test_logs(mock_run, runner):
    """Verifies that 'logs' calls the correct docker command."""
    result = runner.invoke(cli, ["logs"])
    assert result.exit_code == 0
    mock_run.assert_called_with(["docker", "compose", "logs", "-f", "tabby"])


@patch("src.cli.run_interactive")
def test_model_get(mock_interactive, runner):
    """Verifies 'model get' calls the download script."""
    result = runner.invoke(cli, ["model", "get", "repo/id"])
    assert result.exit_code == 0
    mock_interactive.assert_called_with(
        ["python3", "scripts/download_model.py", "repo/id"]
    )


@patch("src.cli.run_command")
@patch("src.cli.Path")
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
