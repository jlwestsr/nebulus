from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import os


# Initialize FastMCP
mcp = FastMCP("Black Box Tools")


# Tool: List Directory
@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List contents of a directory in the workspace."""
    base_path = "/workspace"
    target_path = os.path.join(base_path, path.lstrip("/"))

    if not os.path.abspath(target_path).startswith(base_path):
        return "Error: Access denied. Cannot access paths outside /workspace."

    try:
        items = os.listdir(target_path)
        return "\n".join(items) if items else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Tool: Read File
@mcp.tool()
def read_file(path: str) -> str:
    """Read certain file content from the workspace."""
    base_path = "/workspace"
    target_path = os.path.join(base_path, path.lstrip("/"))

    if not os.path.abspath(target_path).startswith(base_path):
        return "Error: Access denied. Cannot access paths outside /workspace."

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


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

    uvicorn.run(mcp._app, host="0.0.0.0", port=8000)
else:
    # Expose the internal FastAPI app for uvicorn
    app = mcp._app
