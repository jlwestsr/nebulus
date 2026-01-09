from .model_builder import MODEL_BUILDER_HTML, MODEL_BUILDER_CSS
from version import UI_CSS_VERSION, UI_JS_VERSION


def get_notes_page():
    return f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <title>Nebulus - Notes</title>
        <link rel="stylesheet" href="/public/style.css?v={UI_CSS_VERSION}">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
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
                <div class="toolbar" style="display: flex; gap: 10px; margin-bottom:10px;">
                    <button id="save-btn" class="btn btn-primary">Save Note</button>
                    <button id="preview-btn" class="btn btn-secondary">Preview</button>
                    <div style="flex:1"></div>
                    <button id="delete-btn" class="btn btn-danger" style="background:transparent; color:#ef4444; border:1px solid #ef4444;">Delete</button>
                </div>
                <input type="text" id="note-category" class="note-category" placeholder="Category (e.g. Work, Personal)" style="margin-bottom: 5px; width: 100%; padding: 8px; background: transparent; border: none; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); font-size: 0.9em; outline:none;">
                <input type="text" id="note-title" class="note-title" placeholder="Untitled Note">
                <textarea id="note-content" class="note-content" placeholder="Start typing..."></textarea>
                <div id="note-preview" class="note-preview" style="display: none;"></div>
            </div>
            <div class="notes-editor" id="empty-state" style="align-items: center; justify-content: center; color: var(--text-secondary); display:flex;">
                <div style="text-align:center;">
                    <p style="margin-bottom:15px;">Select a note or create a new one.</p>
                    <button id="new-note-btn" class="btn btn-primary">+ New Note</button>
                </div>
            </div>
        </div>

        <script src="/public/script.js?v={UI_JS_VERSION}"></script>
        <script src="/public/notes.js"></script>
    </body>
    </html>
    """


def get_workspace_page():
    return f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <title>Nebulus - Workspace</title>
        <link rel="stylesheet" href="/public/style.css?v={UI_CSS_VERSION}">
        <link rel="stylesheet" href="/public/workspace.css?v={UI_CSS_VERSION}">
        <style>{MODEL_BUILDER_CSS}</style>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
    </head>
    <body>
        <!-- Sidebar injected by script.js -->

        <div id="workspace-app">
            <header>
                <h1>Workspace Management</h1>
                <p class="subtitle">Manage Models, Tools, and Knowledge</p>
            </header>

            <div class="workspace-stacked">
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
                            <button id="open-builder-btn" class="btn btn-sm btn-secondary" style="margin-left:5px;">Build</button>
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

            {MODEL_BUILDER_HTML}
        </div>

        <script src="/public/script.js?v={UI_JS_VERSION}"></script>
        <script src="/public/workspace.js"></script>
    </body>
    </html>
    """
