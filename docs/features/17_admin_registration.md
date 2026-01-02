# Feature: Admin Registration

## 1. Overview
**Branch**: `feat/admin-registration`

Implement a secure initialization flow for the Gantry interface. On startup, the system should check if an administrator account exists. If not, it must present a registration form to create the initial admin user. This ensures the system is not left open and establishes a root of trust.

## 2. Requirements
- [x] **Database**: Persist user credentials securely (hashed).
- [x] **Detection**: specific check on startup/access for existing admin users.
- [x] **UI/UX**:
    - If no admin exists -> Redirect to Registration.
    - Registration Form: Full Name, Email, Password, Confirm Password.
    - Validation: Passwords match, Email format, Non-empty fields.
- [x] **Logic**:
    - First user created is automatically assigned `role="admin"`.
    - Subsequent access requires Login (out of scope for *this* specific story? - assuming implied Login is required to use the app after registration).

## 3. Technical Implementation
- **Stack**: Chainlit, SQLAlchemy (SQLite), Passlib (Argon2), **Python-Jose (JWT)**.
- **Files**:
    - `gantry/routers/auth_routes.py`: Login, Register, Logout endpoints (Custom UI).
    - `gantry/auth.py`: JWT token generation/verification, user CRUD.
    - `gantry/middleware.py`: `AuthMiddleware` verifies JWT cookie for all traffic.
    - `gantry/models.py`: Database schema (User table).
    - `gantry/chat.py`: **Clean handoff** - no native auth callback.
- **Docker**: Volume `gantry_data` persists `gantry.db`.

## 4. Verification Plan
**Automated Tests**:
- [x] `pytest tests/test_auth.py`: Verify hashing, admin detection logic.

**Manual Verification**:
- [x] **Fresh Start**: Stop container, wipe volume (or use temp dev path).
- [x] **Visit UI**: Verify Redirect to Login/Register.
- [x] **Register**: Enter details. Verify success and auto-login.
- [x] **Restart**: Verify user requires login and no longer sees "Setup Admin" prompt.
