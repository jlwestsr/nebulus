import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import sys
import subprocess

# Add mcp_server to path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../mcp_server"))
)


# Mock FastMCP to return a dummy decorator that leaves functions unchanged
def dummy_decorator():
    def wrapper(func):
        return func

    return wrapper


mock_mcp = MagicMock()
mock_mcp.tool.side_effect = dummy_decorator

with patch("mcp.server.fastmcp.FastMCP", return_value=mock_mcp):
    from server import (
        read_file,
        write_file,
        edit_file,
        list_directory,
        run_command,
        scrape_url,
        _validate_path,
    )


class TestMCPTools(unittest.TestCase):
    def setUp(self):
        # Create a dummy workspace for testing
        self.test_dir = os.path.abspath("tests/test_workspace")
        os.makedirs(self.test_dir, exist_ok=True)

        # Patch the base path in the server module to point to our test dir
        self.patcher = patch("server._validate_path")
        self.mock_validate = self.patcher.start()

        # Define a side effect that mimics the real logic but uses our test_dir
        def side_effect(path):
            base_path = self.test_dir
            target_path = os.path.join(base_path, path.lstrip("/"))
            if not os.path.abspath(target_path).startswith(base_path):
                raise ValueError("Access denied")
            return target_path

        self.mock_validate.side_effect = side_effect

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_write_and_read_file(self):
        filename = "test.txt"
        content = "Hello, World!"

        # write
        result = write_file(filename, content)
        self.assertIn("Successfully wrote", result)

        # read
        read_content = read_file(filename)
        self.assertEqual(read_content, content)

    def test_edit_file(self):
        filename = "edit_test.txt"
        initial_content = "Hello, World!"
        write_file(filename, initial_content)

        # edit
        result = edit_file(filename, "World", "Nebulus")
        self.assertIn("Successfully edited", result)

        # verify
        new_content = read_file(filename)
        self.assertEqual(new_content, "Hello, Nebulus!")

    def test_list_directory(self):
        os.makedirs(os.path.join(self.test_dir, "subdir"), exist_ok=True)
        write_file("subdir/file1.txt", "content")

        listing = list_directory("subdir")
        self.assertIn("file1.txt", listing)

    def test_security_traversal(self):
        # The mock side_effect enforces the logic we want to test
        with self.assertRaises(ValueError):
            _validate_path("../outside.txt")

    @patch("subprocess.run")
    def test_run_command_security(self, mock_run):
        # Configure successful run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_run.return_value = mock_result

        # Test allowed command
        result = run_command("ls -la")
        self.assertEqual(result, "output")
        mock_run.assert_called_with(
            ["ls", "-la"], cwd="/workspace", capture_output=True, text=True, timeout=30
        )

        # Test blocked binary
        result = run_command("rm file.txt")
        self.assertIn("Error: Command", result)
        self.assertIn("not allowed", result)

        # Test blocked operator
        result = run_command("ls; rm file")
        self.assertIn("Error: Operator", result)
        self.assertIn("not allowed", result)

        # Test timeout (simulate exception)
        mock_run.side_effect = subprocess.TimeoutExpired(["echo"], 30)
        result = run_command("echo test_timeout")
        self.assertIn("Error: Command timed out", result)

    @patch("httpx.Client")
    def test_scrape_url(self, mock_client_cls):
        # Mock client context manager
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = (
            "<html><body><h1>Title</h1><p>Content  with  spaces</p>"
            "<script>var x=1;</script></body></html>"
        )
        mock_client.get.return_value = mock_response

        # Call scrape_url
        result = scrape_url("https://example.com")

        # Verify
        self.assertIn("Title", result)
        self.assertIn("Content with spaces", result)
        self.assertNotIn("var x=1", result)  # Script should be removed

        # Verify call arguments
        mock_client.get.assert_called_with(
            "https://example.com",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            },
        )

        # Test request error
        mock_client.get.side_effect = Exception("Connection error")
        result = scrape_url("https://example.com")
        self.assertIn("Unexpected error", result)


if __name__ == "__main__":
    unittest.main()
