import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add mcp_server to path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp_server"))
)


def _make_mock_mcp():
    """Create a mock FastMCP that tracks tool registrations."""
    mock = MagicMock()
    registered_tools = []

    def tool_decorator():
        def wrapper(func):
            registered_tools.append(func.__name__)
            return func

        return wrapper

    mock.tool.side_effect = tool_decorator
    mock._registered_tools = registered_tools
    return mock


class TestSchedulerTools(unittest.TestCase):
    """Test Prime-only scheduler MCP tools."""

    @patch("db.LTMClient")
    @patch("scheduler.TaskScheduler")
    @patch("nebulus_core.mcp.create_server")
    def test_schedule_task(self, mock_create_server, mock_scheduler_cls, mock_ltm):
        mock_mcp = _make_mock_mcp()
        mock_create_server.return_value = mock_mcp

        mock_sched = MagicMock()
        mock_sched.add_task.return_value = "Task scheduled: test-123"
        mock_scheduler_cls.return_value = mock_sched

        import importlib
        import server

        importlib.reload(server)

        result = server.schedule_task(
            "Daily Report", "Generate report", "0 8 * * *", "a@b.com, c@d.com"
        )

        mock_sched.add_task.assert_called_once_with(
            "Daily Report", "Generate report", "0 8 * * *", ["a@b.com", "c@d.com"]
        )
        self.assertEqual(result, "Task scheduled: test-123")

    @patch("db.LTMClient")
    @patch("scheduler.TaskScheduler")
    @patch("nebulus_core.mcp.create_server")
    def test_list_scheduled_tasks(
        self, mock_create_server, mock_scheduler_cls, mock_ltm
    ):
        mock_mcp = _make_mock_mcp()
        mock_create_server.return_value = mock_mcp

        mock_sched = MagicMock()
        mock_sched.list_tasks.return_value = "No tasks scheduled."
        mock_scheduler_cls.return_value = mock_sched

        import importlib
        import server

        importlib.reload(server)

        result = server.list_scheduled_tasks()
        mock_sched.list_tasks.assert_called_once()
        self.assertEqual(result, "No tasks scheduled.")

    @patch("db.LTMClient")
    @patch("scheduler.TaskScheduler")
    @patch("nebulus_core.mcp.create_server")
    def test_delete_scheduled_task(
        self, mock_create_server, mock_scheduler_cls, mock_ltm
    ):
        mock_mcp = _make_mock_mcp()
        mock_create_server.return_value = mock_mcp

        mock_sched = MagicMock()
        mock_sched.delete_task.return_value = "Deleted task: job-456"
        mock_scheduler_cls.return_value = mock_sched

        import importlib
        import server

        importlib.reload(server)

        result = server.delete_scheduled_task("job-456")
        mock_sched.delete_task.assert_called_once_with("job-456")
        self.assertEqual(result, "Deleted task: job-456")


class TestCoreToolRegistration(unittest.TestCase):
    """Verify that create_server is called and scheduler tools are registered."""

    @patch("db.LTMClient")
    @patch("scheduler.TaskScheduler")
    @patch("nebulus_core.mcp.create_server")
    def test_server_registers_scheduler_tools(
        self, mock_create_server, mock_scheduler_cls, mock_ltm
    ):
        mock_mcp = _make_mock_mcp()
        mock_create_server.return_value = mock_mcp

        import importlib
        import server

        importlib.reload(server)

        # Verify create_server was called with correct config
        mock_create_server.assert_called_once()
        config = mock_create_server.call_args[0][0]
        self.assertEqual(str(config.workspace_path), "/workspace")
        self.assertEqual(config.server_name, "Black Box Tools")

        # Verify the 3 scheduler tools were registered on the mock
        registered = mock_mcp._registered_tools
        self.assertIn("schedule_task", registered)
        self.assertIn("list_scheduled_tasks", registered)
        self.assertIn("delete_scheduled_task", registered)


if __name__ == "__main__":
    unittest.main()
