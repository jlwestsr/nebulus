import os
from pathlib import Path

from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from pydantic import BaseModel

from nebulus_core.mcp import create_server, MCPConfig
from scheduler import TaskScheduler
from db import LTMClient

# Create MCP server with core tools
config = MCPConfig(workspace_path=Path("/workspace"), server_name="Black Box Tools")
mcp = create_server(config)

# Initialize Scheduler
scheduler = TaskScheduler()

# Initialize LTM Client
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
    value: str


# Prime-only scheduler tools


@mcp.tool()
def schedule_task(
    title: str, prompt: str, schedule_cron: str, recipients_str: str
) -> str:
    """Schedule a recurring task that emails a report.

    Args:
        title: Name of the task.
        prompt: Instructions for the LLM.
        schedule_cron: Cron expression (e.g., "0 8 * * *").
        recipients_str: Comma-separated email addresses.
    """
    recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
    return scheduler.add_task(title, prompt, schedule_cron, recipients)


@mcp.tool()
def list_scheduled_tasks() -> str:
    """List all currently scheduled automated tasks."""
    return scheduler.list_tasks()


@mcp.tool()
def delete_scheduled_task(job_id: str) -> str:
    """Delete a scheduled task by its Job ID."""
    return scheduler.delete_task(job_id)


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


# TODO(NPRIME-06): Add API key authentication middleware to all /api/* endpoints.
# All task, conversation, and user preference endpoints below are currently
# unauthenticated. Implement FastAPI Depends() with X-API-Key header validation.
# Primary mitigation: services bound to 127.0.0.1 only (NPRIME-02).


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
    pass
