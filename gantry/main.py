from fastapi import FastAPI
from chainlit.utils import mount_chainlit
from database import init_db
from starlette.middleware import Middleware
from middleware import AuthMiddleware
from routers import auth_routes

app = FastAPI(middleware=[Middleware(AuthMiddleware)])

# Include routers
app.include_router(auth_routes.router)


# Initialize Database on startup
@app.on_event("startup")
async def startup():
    init_db()


# Mount Chainlit app on root
mount_chainlit(app=app, target="chat.py", path="/")
