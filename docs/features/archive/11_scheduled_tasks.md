# Feature: Scheduled Tasks & Reporting

## Goal
Enable users to define automated, recurring tasks (prompts) that execute on a schedule and deliver results via email.

## User Stories
- **As a user**, I want to tell the system "Send me a summary of the latest AI news every morning at 8 AM" and have it happen automatically.
- **As a user**, I want to define a specific prompt (e.g., "Analyze my daily logs") and have the report emailed to me.
- **As a user**, I want to list and cancel active scheduled tasks.

## Technical Components

### 1. Scheduler Engine
- **Library**: `APScheduler` (Advanced Python Scheduler).
- **Location**: Integrated into `blackbox-mcp` (MCP Server).
- **Persistence**: SQLite database (`scheduler.db`) to persist jobs across restarts.

### 2. MCP Tools
The scheduler will be exposed via MCP tools, utilizing the Agentic interface:
- `schedule_task(title, prompt, schedule_cron, recipients)`: Creates a new job.
- `list_tasks()`: Returns all active jobs.
- `delete_task(job_id)`: Removes a scheduled job.

### 3. Execution Logic
- When a job triggers:
    1.  **Generate**: The MCP server calls the LLM (Ollama or OpenAI API) with the user's prompt.
    2.  **Format**: The result is formatted into a report (Markdown/HTML).
    3.  **Deliver**: The report is emailed to the specified recipients.

### 4. Configuration
New environment variables in `docker-compose.yml`:
- `SMTP_HOST`: Mail server host (e.g., `smtp.gmail.com`).
- `SMTP_PORT`: Mail server port (e.g., `587`).
- `SMTP_USER`: Mail user.
- `SMTP_PASS`: Mail password (app password).
- `EMAIL_FROM`: Sender address.

## Data Flow
User -> "Schedule task..." -> LLM -> `schedule_task` Tool -> `APScheduler` (persists to DB).
...[Time Passes]...
`APScheduler` -> Triggers Job -> Calls LLM Configured -> Generates Content -> Sends Email.
