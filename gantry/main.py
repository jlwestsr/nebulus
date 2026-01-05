from fastapi import FastAPI
from chainlit.utils import mount_chainlit
from database import init_db
from starlette.middleware import Middleware
from middleware import AuthMiddleware
from routers import auth_routes

# ... existing code ...
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from openai import AsyncOpenAI

app = FastAPI(middleware=[Middleware(AuthMiddleware)])

app.mount("/public", StaticFiles(directory="public"), name="public")

# Configure Ollama client for API
client = AsyncOpenAI(
    base_url=os.getenv("OLLAMA_HOST", "http://ollama:11434") + "/v1",
    api_key="ollama",
)

MODEL_MAPPING = {
    "llama3.2-vision:latest": "Llama 3.2 Vision",
    "llama3.1:latest": "Llama 3.1",
    "qwen2.5-coder:latest": "Qwen 2.5 Coder",
}


@app.get("/models")
async def get_models():
    try:
        models = await client.models.list()
        raw_model_ids = [m.id for m in models.data]

        friendly_models = []
        for raw_id in raw_model_ids:
            if "embed" in raw_id:
                continue
            friendly_models.append(MODEL_MAPPING.get(raw_id, raw_id))

        return JSONResponse(content={"models": friendly_models, "raw": raw_model_ids})
    except Exception as e:
        return JSONResponse(
            content={"models": ["Llama 3.1"], "error": str(e)}, status_code=500
        )


# ... existing code ...


@app.get("/notes", response_class=HTMLResponse)
async def notes_page():
    return """
    <html>
    <head><title>Nebulus - Notes</title></head>
    <body style="background-color: #111; color: white; display: flex;
                 justify-content: center; align-items: center;
                 height: 100vh; font-family: sans-serif;">
        <div style="text-align: center;">
            <h1>Notes</h1>
            <p>Persistent notes feature coming soon.</p>
            <a href="/" style="color: #4a90e2;">Back to Chat</a>
        </div>
    </body>
    </html>
    """


@app.get("/workspace", response_class=HTMLResponse)
async def workspace_page():
    return """
    <html>
    <head><title>Nebulus - Workspace</title></head>
    <body style="background-color: #111; color: white; display: flex;
                 justify-content: center; align-items: center;
                 height: 100vh; font-family: sans-serif;">
        <div style="text-align: center;">
            <h1>Workspace</h1>
            <p>Workspace management feature coming soon.</p>
            <a href="/" style="color: #4a90e2;">Back to Chat</a>
        </div>
    </body>
    </html>
    """


# Include routers
app.include_router(auth_routes.router)


# Initialize Database on startup
@app.on_event("startup")
async def startup():
    init_db()


# Mount Chainlit app on root
mount_chainlit(app=app, target="chat.py", path="/")
