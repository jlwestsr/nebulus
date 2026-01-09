from fastapi import FastAPI, Depends
from chainlit.utils import mount_chainlit
from database import init_db, migrate_db, UsageLog, get_db
from starlette.middleware import Middleware
from middleware import AuthMiddleware
from routers import auth_routes, chat_routes, notes_routes, workspace_routes
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from openai import AsyncOpenAI
from ops.ollama import create_model, generate_modelfile
from ui.pages import get_notes_page, get_workspace_page
from sqlalchemy.orm import Session
from sqlalchemy import func

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


@app.post("/api/models/create")
async def api_create_model(data: dict):
    try:
        name = data.get("name")
        base = data.get("base")
        system = data.get("system", "")
        params = data.get("parameters", {})

        if not name or not base:
            return JSONResponse(
                content={"error": "Name and Base Model are required"}, status_code=400
            )

        modelfile = generate_modelfile(base, system, params)
        result = await create_model(name, modelfile, base=base)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/metrics/usage")
async def get_usage_metrics(db: Session = Depends(get_db)):
    """
    Returns aggregated token usage metrics.
    """
    # Total tokens per model
    stats = (
        db.query(
            UsageLog.model,
            func.sum(UsageLog.prompt_tokens).label("prompt"),
            func.sum(UsageLog.completion_tokens).label("completion"),
            func.sum(UsageLog.total_tokens).label("total"),
            func.sum(UsageLog.cost).label("cost"),
        )
        .group_by(UsageLog.model)
        .all()
    )

    result = []
    for s in stats:
        result.append(
            {
                "model": s.model,
                "prompt_tokens": int(s.prompt or 0),
                "completion_tokens": int(s.completion or 0),
                "total_tokens": int(s.total or 0),
                "cost_micro": int(s.cost or 0),
            }
        )

    # Recent history
    recent = db.query(UsageLog).order_by(UsageLog.created_at.desc()).limit(10).all()

    recent_list = []
    for r in recent:
        recent_list.append(
            {
                "id": r.id,
                "model": r.model,
                "total_tokens": r.total_tokens,
                "timestamp": r.created_at.isoformat(),
            }
        )

    return {"summary": result, "recent": recent_list}


@app.get("/notes", response_class=HTMLResponse)
async def notes_page():
    return get_notes_page()


@app.get("/workspace", response_class=HTMLResponse)
async def workspace_page():
    return get_workspace_page()


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
