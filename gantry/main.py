from fastapi import FastAPI
from chainlit.utils import mount_chainlit
from database import init_db, migrate_db
from starlette.middleware import Middleware
from middleware import AuthMiddleware
from routers import auth_routes, chat_routes, notes_routes
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from openai import AsyncOpenAI

app = FastAPI(middleware=[Middleware(AuthMiddleware)])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount(
    "/public", StaticFiles(directory=os.path.join(BASE_DIR, "public")), name="public"
)

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


@app.get("/notes", response_class=HTMLResponse)
async def notes_page():
    return """
    <html>
    <head>
        <title>Nebulus - Notes</title>
        <link rel="stylesheet" href="/public/style.css">
        <style>
             body { background-color: #111; color: white; margin: 0; display: flex; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
             #notes-app { padding: 80px 20px 20px 80px; width: 100%; max-width: 1200px; margin: 0 auto; display: flex; gap: 20px; height: 100vh; box-sizing: border-box; }
             .notes-list { width: 300px; background: #1a1a1a; border-radius: 8px; border: 1px solid #333; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 5px; }
             .notes-editor { flex: 1; background: #1a1a1a; border-radius: 8px; border: 1px solid #333; display: flex; flex-direction: column; padding: 20px; }
             .note-item { padding: 10px; border-radius: 6px; cursor: pointer; transition: background 0.2s; color: #ccc; }
             .note-item:hover, .note-item.active { background: #333; color: white; }
             .note-item .date { font-size: 0.75rem; color: #777; margin-top: 4px; }
             input.note-title { background: transparent; border: none; font-size: 1.5rem; color: white; width: 100%; margin-bottom: 20px; outline: none; font-weight: bold; }
             textarea.note-content { background: transparent; border: none; width: 100%; flex: 1; color: #ddd; font-size: 1rem; line-height: 1.5; resize: none; outline: none; font-family: monospace; }
             .btn { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: opacity 0.2s; }
             .btn-primary { background: #F80061; color: white; }
             .btn-danger { background: #dc3545; color: white; }
             .btn:hover { opacity: 0.9; }
             .toolbar { display: flex; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        </style>
    </head>
    <body class="dark">
        <!-- Sidebar injected by script.js -->

        <div id="notes-app">
            <div class="notes-list" id="notes-list">
                <div style="padding: 10px; text-align: center; color: #777;">Loading notes...</div>
            </div>
            <div class="notes-editor" id="notes-editor" style="display: none;">
                <div class="toolbar">
                    <button id="save-btn" class="btn btn-primary">Save Note</button>
                    <button id="delete-btn" class="btn btn-danger">Delete</button>
                </div>
                <input type="text" id="note-title" class="note-title" placeholder="Untitled Note">
                <textarea id="note-content" class="note-content" placeholder="Start typing..."></textarea>
            </div>
            <div class="notes-editor" id="empty-state" style="align-items: center; justify-content: center; color: #555;">
                <p>Select a note or create a new one.</p>
                <button id="new-note-btn" class="btn btn-primary" style="margin-top: 10px;">+ New Note</button>
            </div>
        </div>

        <script src="/public/script.js"></script>
        <script src="/public/notes.js"></script>
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
app.include_router(chat_routes.router)
app.include_router(notes_routes.router)


# Initialize Database on startup
@app.on_event("startup")
async def startup():
    init_db()
    migrate_db()


# Mount Chainlit app on root
mount_chainlit(app=app, target=os.path.join(BASE_DIR, "chat.py"), path="/")
