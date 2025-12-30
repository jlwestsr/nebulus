import os
import smtplib
from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
import httpx
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Persistence Check
DB_PATH = "/workspace/mcp_server/scheduler.db"
JOB_STORES = {
    "default": SQLAlchemyJobStore(url=f"sqlite:///{DB_PATH}"),  # noqa: E231
}


class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(jobstores=JOB_STORES)
        self.scheduler.start()
        logger.info("Task Scheduler started.")

    def add_task(
        self, title: str, prompt: str, schedule_cron: str, recipients: list[str]
    ):
        """schedule_cron expected format: '* * * * *' (standard cron)"""
        try:
            # Parse simple 5-part cron
            parts = schedule_cron.split()
            if len(parts) != 5:
                return (
                    "Error: Schedule must be in standard 5-part cron format "
                    "(e.g., '0 8 * * *')."
                )

            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
            )

            job = self.scheduler.add_job(
                execute_prompt_and_email,
                trigger=trigger,
                args=[title, prompt, recipients],
                name=title,
                replace_existing=True,
            )
            return f"Task '{title}' scheduled successfully (Job ID: {job.id})."
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return f"Error scheduling task: {str(e)}"

    def list_tasks(self):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return "No scheduled tasks found."

        result = "Scheduled Tasks:\n"
        for job in jobs:
            # next_run_time is timezone aware, might need str()
            result += f"- [{job.id}] {job.name} (Next Run: {job.next_run_time})\n"
        return result

    def delete_task(self, job_id: str):
        try:
            self.scheduler.remove_job(job_id)
            return f"Task {job_id} deleted."
        except Exception as e:
            return f"Error deleting task: {str(e)}"

    def get_tasks(self):
        """Returns a list of tasks as dictionaries for the API."""
        jobs = self.scheduler.get_jobs()
        tasks = []
        for job in jobs:
            # Job args: [title, prompt, recipients]
            tasks.append(
                {
                    "id": job.id,
                    "title": job.name,
                    "prompt": job.args[1] if len(job.args) > 1 else "",
                    "schedule": str(job.trigger),
                    "next_run": str(job.next_run_time),
                    "recipients": job.args[2] if len(job.args) > 2 else [],
                }
            )
        return tasks

    def run_task(self, job_id: str):
        """Manually trigger a task immediately."""
        job = self.scheduler.get_job(job_id)
        if not job:
            return f"Error: Job {job_id} not found."

        # Execute in background to avoid blocking API
        # job.func is execute_prompt_and_email
        # job.args are [title, prompt, recipients]
        self.scheduler.add_job(job.func, args=job.args, name=f"Manual Run: {job.name}")
        return f"Task '{job.name}' triggered manually."


def execute_prompt_and_email(title: str, prompt: str, recipients: list[str]):
    """Job Execution Logic"""
    logger.info(f"Executing job: {title}")

    # 1. Generate Content (Call Ollama)
    try:
        report_content = generate_llm_response(prompt)
    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        report_content = f"Error generating report: {str(e)}"

    # 2. Send Email
    try:
        send_email(title, report_content, recipients)
        logger.info(f"Email sent for {title}")
    except Exception as e:
        logger.error(f"Email failed: {e}")


def generate_llm_response(prompt: str) -> str:
    """Calls Ollama to generate text."""
    # Assuming Ollama is at http://ollama:11434
    url = "http://ollama:11434/api/generate"
    payload = {
        "model": "llama3.1:latest",  # Use default model
        "prompt": prompt,
        "stream": False,
    }

    # Use httpx for sync request (since we are in a background thread, sync is fine)
    response = httpx.post(url, json=payload, timeout=120.0)
    response.raise_for_status()
    return response.json().get("response", "No response from LLM.")


def send_email(subject: str, body: str, recipients: list[str]):
    """Sends email via SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"[Report] {subject}"
    msg["From"] = os.getenv("EMAIL_FROM", "nebulus@local")
    msg["To"] = ", ".join(recipients)

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_host:
        logger.warning("SMTP Config missing. Skipping email.")
        return

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
