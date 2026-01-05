from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
from fastapi import Request
from auth import verify_token, get_user_count
from database import SessionLocal


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow static assets and auth endpoints
        if request.url.path.startswith(
            (
                "/login",
                "/logout",
                "/register",
                "/assets",
                "/public",
                "/favicon",
                "/logo",
                "/models",
            )
        ):
            return await call_next(request)

        # Check for first run (no users)
        db = SessionLocal()
        try:
            count = get_user_count(db)
        finally:
            db.close()

        if count == 0:
            return RedirectResponse(url="/register")

        # Check for access token
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login")

        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # Verify token
        if not verify_token(token):
            return RedirectResponse(url="/login")

        return await call_next(request)
