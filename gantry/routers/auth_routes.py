# flake8: noqa: E501
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from database import SessionLocal
from auth import (
    create_user,
    get_user_count,
    get_user,
    verify_password,
    create_access_token,
)

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login form."""
    return """
    <html>
    <head>
        <title>Nebulus - Login</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white flex items-center justify-center h-screen">
        <div class="bg-gray-800 p-8 rounded-lg shadow-lg w-96">
            <h2 class="text-2xl font-bold mb-6 text-center text-blue-400">Nebulus Login</h2>
            <form action="/login" method="post" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Email</label>
                    <input type="email" name="username" required
                           class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:border-blue-500
                                  focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Password</label>
                    <input type="password" name="password" required
                           class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:border-blue-500
                                  focus:outline-none">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200">
                    Sign In
                </button>
            </form>
        </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            const inputs = form.querySelectorAll('input');

            inputs.forEach(input => {
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        form.submit();
                    }
                });
            });
        });
    </script>
    </body>
    </html>
    """


@router.post("/login")
async def login(
    response: Response, username: str = Form(...), password: str = Form(...)
):
    """Handle login submission and set cookie."""
    db = SessionLocal()
    try:
        user = get_user(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return HTMLResponse("Invalid credentials", status_code=401)

        access_token = create_access_token(data={"sub": user.username})
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        return response
    finally:
        db.close()


@router.get("/logout")
async def logout(response: Response):
    """Clear session cookie and redirect to login."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration form only if no admin exists."""
    db = SessionLocal()
    try:
        if get_user_count(db) > 0:
            return RedirectResponse(url="/login")
    finally:
        db.close()

    return """
    <html>
    <head>
        <title>Nebulus - Admin Registration</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white flex items-center justify-center h-screen">
        <div class="bg-gray-800 p-8 rounded-lg shadow-lg w-96">
            <h2 class="text-2xl font-bold mb-2 text-center text-blue-400">Get started with Nebulus</h2>
            <p class="text-sm text-gray-400 text-center mb-6">Nebulus does not make any external connections, and your data stays securely on your locally hosted server.</p>
            <form action="/register" method="post" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Full Name</label>
                    <input type="text" name="full_name" required
                           class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:border-blue-500
                                  focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Email</label>
                    <input type="email" name="email" required
                           class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:border-blue-500
                                  focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Password</label>
                    <input type="password" name="password" required
                           class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:border-blue-500
                                  focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Confirm Password</label>
                    <input type="password" name="confirm_password" required
                           class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:border-blue-500
                                  focus:outline-none">
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200">
                    Create Admin
                </button>
            </form>
        </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            const inputs = form.querySelectorAll('input');

            inputs.forEach(input => {
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        form.submit();
                    }
                });
            });
        });
    </script>
    </body>
    </html>
    """


@router.post("/register")
async def register_user(request: Request):
    """Handle registration form submission."""
    form = await request.form()
    full_name = form.get("full_name")
    email = form.get("email")
    password = form.get("password")
    confirm = form.get("confirm_password")

    if password != confirm:
        return HTMLResponse("Passwords do not match", status_code=400)

    db = SessionLocal()
    try:
        if get_user_count(db) > 0:
            return HTMLResponse("Admin already exists", status_code=403)

        user = create_user(db, full_name, email, password, role="admin")

        # Auto-login
        access_token = create_access_token(data={"sub": user.username})
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        return response
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)
    finally:
        db.close()
