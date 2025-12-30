# Feature: Scheduler Dashboard

## Goal
Provide a graphical user interface (GUI) for users to manage Scheduled Tasks (Add, List, Edit, Delete) without using chat commands.

## Constraints
- Open WebUI does not natively support adding custom links/views to the sidebar.
- **Solution**: We will host a standalone dashboard on the MCP Server (`http://localhost:8000/dashboard`) which runs alongside Open WebUI.

## User Stories
- **As a user**, I want to see a list of all active scheduled jobs with their next run times.
- **As a user**, I want a form to easily create a new task (Title, Prompt, Schedule, Recipients).
- **As a user**, I want to manually trigger a task immediately to verify it works ("Run Now").

## Technical Components

### 1. Backend (MCP Server)
- **Framework**: `FastAPI` (exposed via `mcp.sse_app()`).
- **Static Files**: Mount a `/static` directory to serve the frontend.
- **API Endpoints**:
    - `GET /api/tasks`: List tasks (JSON).
    - `POST /api/tasks`: Create task.
    - `DELETE /api/tasks/{job_id}`: Delete task.
    - `POST /api/tasks/{job_id}/run`: Manually trigger task.
    - *Note*: These endpoints will reuse the logic from `scheduler.py`.

### 2. Frontend
- **Technology**: Vanilla HTML/JS/CSS (keep it lightweight and dependency-free).
- **Design**: Dark mode to match Open WebUI aesthetics.
- **Location**: `mcp_server/static/`
    - `index.html`: The main view.
    - `app.js`: Logic for fetching data and handling form submissions.
    - `style.css`: Styling.

## Data Flow
Browser -> `GET /dashboard` -> Loads HTML/JS.
Browser -> `GET /api/tasks` -> `TaskScheduler.list_tasks()` -> JSON Response.
Browser -> `POST /api/tasks` -> `TaskScheduler.add_task()` -> Database Update.
