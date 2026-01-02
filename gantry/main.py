from fastapi import FastAPI
from chainlit.utils import mount_chainlit
from database import init_db
from starlette.middleware import Middleware
from middleware import AuthMiddleware
from routers import auth_routes
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(middleware=[Middleware(AuthMiddleware)])

app.mount("/public", StaticFiles(directory="public"), name="public")


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
