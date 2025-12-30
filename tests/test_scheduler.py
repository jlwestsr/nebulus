import pytest
from unittest.mock import patch
from mcp_server.scheduler import TaskScheduler, execute_prompt_and_email


@pytest.fixture
def mock_scheduler():
    with patch("mcp_server.scheduler.BackgroundScheduler") as mock_bg:
        scheduler_instance = mock_bg.return_value
        task_scheduler = TaskScheduler()
        yield task_scheduler, scheduler_instance


def test_add_structure_task(mock_scheduler):
    ts, mock_bg_instance = mock_scheduler

    # Test valid cron
    result = ts.add_task("Test Task", "Prompt", "0 8 * * *", ["test@example.com"])
    assert "scheduled successfully" in result
    mock_bg_instance.add_job.assert_called_once()


def test_add_task_invalid_cron(mock_scheduler):
    ts, _ = mock_scheduler
    result = ts.add_task("Test Task", "Prompt", "invalid", ["test@example.com"])
    assert "Error: Schedule must be" in result


@patch("mcp_server.scheduler.generate_llm_response")
@patch("mcp_server.scheduler.send_email")
def test_execute_job(mock_email, mock_llm):
    mock_llm.return_value = "Generated Report"

    execute_prompt_and_email("Daily Report", "Summarize stuff", ["user@test.com"])

    mock_llm.assert_called_with("Summarize stuff")
    mock_email.assert_called_with("Daily Report", "Generated Report", ["user@test.com"])
