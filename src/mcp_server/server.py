from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import os
import subprocess
import shlex
import re
import httpx
from selectolax.parser import HTMLParser
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
import pypdf
import docx
from scheduler import TaskScheduler
from db import LTMClient
from pydantic import BaseModel

# Initialize FastMCP
mcp = FastMCP("Black Box Tools")

# Initialize Scheduler
scheduler = TaskScheduler()

# Initialize LTM Client
# We initialize lazily or globally depending on preference, but here globally for simplicity
# Ensure ChromaDB service is running/resolvable
try:
    ltm_client = LTMClient(host="chromadb")
except Exception as e:
    print(f"Warning: Could not connect to LTM Database: {e}")
    ltm_client = None

# --- Pydantic Models for LTM ---


class ConversationCreate(BaseModel):
    topic: str
    user_id: str = "default_user"


class ConversationUpdate(BaseModel):
    topic: str


class MessageCreate(BaseModel):
    content: str
    sender: str = "user"
    receiver: str = "ai"


class UserPreferenceSet(BaseModel):
    key: str
    value: str  # Simplified for now


# Tool: Schedule Task
@mcp.tool()
def schedule_task(
    title: str, prompt: str, schedule_cron: str, recipients_str: str
) -> str:
    """
    Schedule a recurring task that emails a report.
    Args:
        title: Name of the task
        prompt: Instructions for the LLM
        schedule_cron: Cron expression (e.g., "0 8 * * *")
        recipients_str: Comma-separated email addresses
    """
    recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
    return scheduler.add_task(title, prompt, schedule_cron, recipients)


# Tool: List Tasks
@mcp.tool()
def list_scheduled_tasks() -> str:
    """List all currently scheduled automated tasks."""
    return scheduler.list_tasks()


# Tool: Delete Task
@mcp.tool()
def delete_scheduled_task(job_id: str) -> str:
    """Delete a scheduled task by its Job ID."""
    return scheduler.delete_task(job_id)


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


# Tool: Scrape URL
@mcp.tool()
async def scrape_url(url: str) -> str:
    """Scrape and parse the textual content of a webpage."""
    if not (url.startswith("http://") or url.startswith("https://")):
        return "Error: Invalid URL. Must start with http:// or https://"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            tree = HTMLParser(response.text)

            # Remove scripts and styles
            for tag in tree.css("script, style"):
                tag.decompose()

            # Get text
            if tree.body:
                text = tree.body.text(separator="\n", strip=True)
            else:
                text = tree.text(separator="\n", strip=True)

            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            # Collapse internal whitespace
            cleaned_lines = (re.sub(r"\s+", " ", line) for line in lines)
            text = "\n".join(line for line in cleaned_lines if line)

            return text

    except httpx.RequestError as e:
        return f"Error scraping URL: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code} while scraping URL."
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# Tool: Search Code
@mcp.tool()
def search_code(query: str, path: str = ".") -> str:
    """
    Search for a text pattern in the codebase using grep.
    Args:
        query: The regex pattern to search for.
        path: The path to search within (defaults to workspace root).
    """
    try:
        target_path = _validate_path(path)

        # Construct grep command
        # -r: recursive
        # -n: line numbers
        # -I: ignore binary files
        # -H: print filename
        # --exclude-dir: skip common non-code directories
        cmd = [
            "grep",
            "-r",
            "-n",
            "-I",
            "-H",
            "--exclude-dir={.git,__pycache__,node_modules,venv,.env}",
            query,
            target_path,
        ]

        result = subprocess.run(
            cmd, cwd="/workspace", capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            return result.stdout.strip()
        elif result.returncode == 1:
            return "No matches found."
        else:
            return f"Error executing grep (exit {result.returncode}): \n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: Search timed out after 30 seconds."
    except Exception as e:
        return f"Error executing search: {str(e)}"


# Tool: Web Search
def _search_google_api(query: str, max_results: int) -> list[str]:
    """Helper for Google Custom Search API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        raise ValueError(
            "Error: Google Search requires GOOGLE_API_KEY and GOOGLE_CSE_ID "
            "environment variables."
        )

    try:
        from googleapiclient.discovery import build

        service = build("customsearch", "v1", developerKey=api_key)
        result = service.cse().list(q=query, cx=cse_id, num=max_results).execute()

        items = result.get("items", [])
        return [
            f"Title: {item.get('title')}\n"
            f"Link: {item.get('link')}\n"
            f"Snippet: {item.get('snippet')}\n"
            for item in items
        ]
    except ImportError:
        raise ImportError("Error: google-api-python-client not installed.")


def _search_ddg(query: str, max_results: int) -> list[str]:
    """Helper for DuckDuckGo Search."""
    results = DDGS().text(query, max_results=max_results)
    return [
        f"Title: {result['title']}\n"
        f"Link: {result['href']}\n"
        f"Snippet: {result['body']}\n"
        for result in results
    ]


def _search_google_fallback(query: str, max_results: int) -> list[str]:
    """Helper for Google Search Fallback (Scraper)."""
    try:
        from googlesearch import search

        # advanced=True yields objects with title, url, description
        g_results = search(query, num_results=max_results, advanced=True)
        formatted_results = []
        for res in g_results:
            formatted_results.append(
                f"Title: {res.title}\n"
                f"Link: {res.url}\n"
                f"Snippet: {res.description}\n"
            )
        return formatted_results
    except Exception as e:
        print(f"Google fallback failed: {e}")
        return []


@mcp.tool()
def search_web(query: str, max_results: int = 5, engine: str = "duckduckgo") -> str:
    """
    Search the web using DuckDuckGo or Google.
    Args:
        query: Search query
        max_results: Number of results to return (default: 5)
        engine: "duckduckgo" (default) or "google"
    """
    try:
        formatted_results = []

        if engine.lower() == "google":
            try:
                formatted_results = _search_google_api(query, max_results)
            except (ValueError, ImportError) as e:
                return str(e)
        else:
            # Default to DuckDuckGo
            formatted_results = _search_ddg(query, max_results)

        if not formatted_results:
            # Fallback to Google Search (Scraper)
            formatted_results = _search_google_fallback(query, max_results)

        if not formatted_results:
            return "No results found."

        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"


# Tool: Read PDF
@mcp.tool()
def read_pdf(path: str) -> str:
    """Read text content from a PDF file."""
    try:
        target_path = _validate_path(path)
        reader = pypdf.PdfReader(target_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Tool: Read DOCX
@mcp.tool()
def read_docx(path: str) -> str:
    """Read text content from a DOCX file."""
    try:
        target_path = _validate_path(path)
        doc = docx.Document(target_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"


# Expose the internal FastAPI app
app = mcp.sse_app()


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


app.add_route("/health", health_check)

# Mount Static Files
app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    ),
    name="static",
)


# API: List Tasks
async def get_tasks_api(request: Request):
    return JSONResponse(scheduler.get_tasks())


# API: Add Task
async def add_task_api(request: Request):
    try:
        data = await request.json()
        title = data.get("title")
        prompt = data.get("prompt")
        schedule = data.get("schedule")
        recipients = data.get("recipients", [])

        if not title or not prompt or not schedule:
            return JSONResponse({"error": "Missing fields"}, status_code=400)

        result = scheduler.add_task(title, prompt, schedule, recipients)
        if "Error" in result:
            return JSONResponse({"error": result}, status_code=400)

        return JSONResponse({"message": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# API: Delete Task
async def delete_task_api(request: Request):
    job_id = request.path_params["job_id"]
    result = scheduler.delete_task(job_id)
    return JSONResponse({"message": result})


# API: Run Task
async def run_task_api(request: Request):
    job_id = request.path_params["job_id"]
    result = scheduler.run_task(job_id)
    if "Error" in result:
        return JSONResponse({"error": result}, status_code=404)
    return JSONResponse({"message": result})


# Register Routes
app.add_route("/api/tasks", get_tasks_api, methods=["GET"])
app.add_route("/api/tasks", add_task_api, methods=["POST"])
app.add_route("/api/tasks/{job_id}", delete_task_api, methods=["DELETE"])
app.add_route("/api/tasks/{job_id}/run", run_task_api, methods=["POST"])

# --- LTM API Endpoints ---


# Conversations


async def create_conversation_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    try:
        data = await request.json()
        model = ConversationCreate(**data)
        result = ltm_client.create_conversation(model.topic, model.user_id)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def get_conversation_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    conv_id = request.path_params["conv_id"]
    result = ltm_client.get_conversation(conv_id)
    if not result:
        return JSONResponse({"error": "Conversation not found"}, status_code=404)
    return JSONResponse(result)


async def update_conversation_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    try:
        conv_id = request.path_params["conv_id"]
        data = await request.json()
        model = ConversationUpdate(**data)
        result = ltm_client.update_conversation(conv_id, topic=model.topic)
        if not result:
            return JSONResponse({"error": "Conversation not found"}, status_code=404)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def delete_conversation_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    conv_id = request.path_params["conv_id"]
    ltm_client.delete_conversation(conv_id)
    return JSONResponse({"message": "Deleted"})


# Messages
async def add_message_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    try:
        conv_id = request.path_params["conv_id"]
        data = await request.json()
        model = MessageCreate(**data)
        result = ltm_client.add_message(
            conv_id, model.content, model.sender, model.receiver
        )
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def get_messages_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    conv_id = request.path_params["conv_id"]
    result = ltm_client.get_messages(conv_id)
    return JSONResponse(result)


# User Preferences
async def set_user_pref_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    try:
        user_id = request.path_params["user_id"]
        data = await request.json()
        model = UserPreferenceSet(**data)
        result = ltm_client.set_user_preference(user_id, model.key, model.value)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def get_user_prefs_api(request: Request):
    if not ltm_client:
        return JSONResponse({"error": "LTM Database not available"}, status_code=503)
    user_id = request.path_params["user_id"]
    result = ltm_client.get_user_preferences(user_id)
    if not result:
        return JSONResponse({"error": "User not found"}, status_code=404)
    return JSONResponse(result)


# Register LTM Routes
app.add_route("/api/conversations", create_conversation_api, methods=["POST"])
app.add_route("/api/conversations/{conv_id}", get_conversation_api, methods=["GET"])
app.add_route("/api/conversations/{conv_id}", update_conversation_api, methods=["PUT"])
app.add_route(
    "/api/conversations/{conv_id}", delete_conversation_api, methods=["DELETE"]
)
app.add_route(
    "/api/conversations/{conv_id}/messages", add_message_api, methods=["POST"]
)
app.add_route(
    "/api/conversations/{conv_id}/messages", get_messages_api, methods=["GET"]
)
app.add_route("/api/users/{user_id}/preferences", set_user_pref_api, methods=["POST"])
app.add_route("/api/users/{user_id}/preferences", get_user_prefs_api, methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    # Expose app for uvicorn (if running via uvicorn mcp_server.server:app)
    pass
