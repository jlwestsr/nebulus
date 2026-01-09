from sqlalchemy.orm import Session
from database import UsageLog

# Costs per 1M tokens in USD ($)
# Local models are free (0.0), but we can add nominal costs for tracking "value"
# or actual costs for OpenAI/external models.
COST_MAP = {
    "llama3.1:latest": {"prompt": 0.0, "completion": 0.0},
    "llama3.2-vision:latest": {"prompt": 0.0, "completion": 0.0},
    "qwen2.5-coder:latest": {"prompt": 0.0, "completion": 0.0},
    "default": {"prompt": 0.0, "completion": 0.0},
}


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> int:
    """
    Calculates cost in micro-dollars ($0.000001).
    """
    costs = COST_MAP.get(model, COST_MAP["default"])

    # Simple calculation: (tokens / 1,000,000) * cost_per_1m
    # We work in micro-dollars to avoid floating point issues in DB.
    prompt_cost = (prompt_tokens / 1_000_000) * costs["prompt"] * 1_000_000
    completion_cost = (completion_tokens / 1_000_000) * costs["completion"] * 1_000_000

    return int(prompt_cost + completion_cost)


def log_usage(
    db: Session,
    user_id: int,
    chat_id: str,
    message_id: int,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
):
    """
    Logs the token usage and cost for a specific message.
    """
    total_tokens = prompt_tokens + completion_tokens
    cost = calculate_cost(model, prompt_tokens, completion_tokens)

    usage_entry = UsageLog(
        user_id=user_id,
        chat_id=chat_id,
        message_id=message_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost=cost,
    )

    db.add(usage_entry)
    db.commit()
    return usage_entry
