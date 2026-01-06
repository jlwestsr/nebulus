from fastapi import FastAPI
from chainlit.utils import mount_chainlit
from database import init_db, migrate_db
from starlette.middleware import Middleware
from middleware import AuthMiddleware
from routers import auth_routes, chat_routes, notes_routes, workspace_routes
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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script>
            (function() {
                const storedTheme = localStorage.getItem('vite-ui-theme');
                const isDark = storedTheme === 'dark';
                if (isDark) {
                    document.documentElement.classList.add('dark');
                }
            })();
        </script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    </head>
    <body>
        <!-- Sidebar injected by script.js -->

        <div id="notes-app">
            <div class="notes-list" id="notes-list">
                <div style="padding: 10px; text-align: center; color: var(--text-secondary);">Loading notes...</div>
            </div>
            <div class="notes-editor" id="notes-editor" style="display: none;">
                <div class="toolbar">
                    <button id="save-btn" class="btn btn-primary">Save Note</button>
                    <button id="preview-btn" class="btn btn-secondary" style="margin-left: 10px;">Preview</button>
                    <div style="flex:1"></div>
                    <button id="delete-btn" class="btn btn-danger">Delete</button>
                </div>
                <input type="text" id="note-category" class="note-category" placeholder="Category (e.g. Work, Personal)" style="margin-bottom: 5px; width: 100%; padding: 8px; background: transparent; border: none; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); font-size: 0.9em;">
                <input type="text" id="note-title" class="note-title" placeholder="Untitled Note">
                <textarea id="note-content" class="note-content" placeholder="Start typing..."></textarea>
                <div id="note-preview" class="note-preview" style="display: none;"></div>
            </div>
            <div class="notes-editor" id="empty-state" style="align-items: center; justify-content: center; color: var(--text-secondary);">
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
    <head>
        <title>Nebulus - Workspace</title>
        <link rel="stylesheet" href="/public/style.css">
        <link rel="stylesheet" href="/public/workspace.css">
        <script>
            (function() {
                const storedTheme = localStorage.getItem('vite-ui-theme');
                const isDark = storedTheme === 'dark';
                if (isDark) {
                    document.documentElement.classList.add('dark');
                }
            })();
        </script>
    </head>
    <body>
        <!-- Sidebar injected by script.js -->

        <div id="workspace-app">
            <header>
                <h1>Workspace Management</h1>
                <p class="subtitle">Manage Models, Tools, and Knowledge</p>
            </header>

            <div class="workspace-grid">
                <!-- Models Section -->
                <div class="card" id="models-card">
                    <div class="card-header">
                        <h2>Models</h2>
                        <button id="refresh-models-btn" class="icon-btn" title="Refresh">↻</button>
                    </div>
                    <div class="card-body">
                         <div class="input-group">
                            <input type="text" id="pull-model-input" placeholder="Pull model (e.g. llama3:8b)" />
                            <button id="pull-model-btn" class="btn btn-sm btn-primary">Pull</button>
                        </div>
                        <div id="model-list" class="list-group">
                            <!-- Injected JS -->
                            <div class="spinner">Loading...</div>
                        </div>
                    </div>
                </div>

                <!-- Tools Section -->
                <div class="card" id="tools-card">
                     <div class="card-header">
                        <h2>MCP Tools</h2>
                    </div>
                     <div class="card-body">
                        <div id="tool-list" class="list-group">
                             <!-- Injected JS -->
                             <div class="spinner">Loading...</div>
                        </div>
                    </div>
                </div>

                 <!-- Knowledge Section -->
                <div class="card" id="knowledge-card">
                     <div class="card-header">
                        <h2>Knowledge (RAG)</h2>
                    </div>
                     <div class="card-body">
                        <div id="knowledge-list" class="list-group">
                             <!-- Injected JS -->
                             <div class="spinner">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="/public/script.js"></script>
        <script src="/public/workspace.js"></script>
    </body>
    </html>
    """


# Include routers
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(notes_routes.router)
app.include_router(workspace_routes.router)


# Initialize Database on startup
@app.on_event("startup")
async def startup():
    init_db()
    migrate_db()


# Mount Chainlit app on root
mount_chainlit(app=app, target=os.path.join(BASE_DIR, "chat.py"), path="/")
