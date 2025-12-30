from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import os
import subprocess
import shlex


# Initialize FastMCP
mcp = FastMCP("Black Box Tools")


def _validate_path(path: str) -> str:
    """Validate and return absolute path within workspace."""
    base_path = "/workspace"
    target_path = os.path.join(base_path, path.lstrip("/"))

    if not os.path.abspath(target_path).startswith(base_path):
        raise ValueError("Access denied. Cannot access paths outside /workspace.")

    return target_path


# Tool: List Directory
@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List contents of a directory in the workspace."""
    try:
        target_path = _validate_path(path)
        items = os.listdir(target_path)
        return "\n".join(items) if items else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Tool: Read File
@mcp.tool()
def read_file(path: str) -> str:
    """Read certain file content from the workspace."""
    try:
        target_path = _validate_path(path)
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


# Tool: Write File
@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file in the workspace (overwrites if exists)."""
    try:
        target_path = _validate_path(path)
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


# Tool: Edit File
@mcp.tool()
def edit_file(path: str, target_text: str, replacement_text: str) -> str:
    """
    Edit a file by replacing the first occurrence of target_text with replacement_text.
    """
    try:
        target_path = _validate_path(path)
        if not os.path.exists(target_path):
            return f"Error: File {path} not found."

        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()

        if content.find(target_text) == -1:
            return f"Error: Target text missing from {path}"

        # Replace first occurrence
        new_content = content.replace(target_text, replacement_text, 1)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Successfully edited {path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"


# Tool: Run Command
@mcp.tool()
def run_command(command: str) -> str:
    """Run a safe shell command in the workspace."""
    ALLOWED_COMMANDS = {
        "ls",
        "grep",
        "cat",
        "find",
        "pytest",
        "git",
        "echo",
        "pwd",
        "tree",
    }
    BLOCKED_OPERATORS = {">", ">>", "&", "|", ";", "`", "$("}

    try:
        # Security: Check for blocked operators/characters in raw string
        for op in BLOCKED_OPERATORS:
            if op in command:
                return f"Error: Operator '{op}' is not allowed for security."

        # Security: Parse command to check first token (binary)
        args = shlex.split(command)
        if not args:
            return "Error: Empty command."

        binary = args[0]
        if binary not in ALLOWED_COMMANDS:
            return f"Error: Command '{binary}' is not allowed."

        # Execute
        result = subprocess.run(
            args, cwd="/workspace", capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Command failed (exit {result.returncode}): \n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"


# Tool: Web Search
@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=max_results)
        formatted_results = []
        for result in results:
            formatted_results.append(
                f"Title: {result['title']}\n"
                f"Link: {result['href']}\n"
                f"Snippet: {result['body']}\n"
            )
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"


if __name__ == "__main__":
    # Import uvicorn here to allow strictly running this as a script if needed,
    # though Dockerfile uses uvicorn directly on the app object.
    import uvicorn

    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8000)
else:
    # Expose the internal FastAPI app for uvicorn
    app = mcp.sse_app()
