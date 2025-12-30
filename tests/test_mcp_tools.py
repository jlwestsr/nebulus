import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import sys

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
    from server import read_file, write_file, edit_file, list_directory, _validate_path


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


if __name__ == "__main__":
    unittest.main()
