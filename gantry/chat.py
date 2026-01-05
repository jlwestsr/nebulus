import os
import chainlit as cl
from openai import AsyncOpenAI


# Configure Ollama client
client = AsyncOpenAI(
    base_url=os.getenv("OLLAMA_HOST", "http://ollama:11434") + "/v1",
    api_key="ollama",  # required but unused
)

# Settings
settings = {
    "model": "Llama 3.1",
    "temperature": 0.7,
    "max_tokens": 2000,
}

MODEL_MAPPING = {
    "llama3.2-vision:latest": "Llama 3.2 Vision",
    "llama3.1:latest": "Llama 3.1",
    "qwen2.5-coder:latest": "Qwen 2.5 Coder",
}

# Reverse mapping for lookups
FRIENDLY_TO_RAW = {v: k for k, v in MODEL_MAPPING.items()}


@cl.on_chat_start
async def start():
    # Fetch available models from Ollama
    try:
        models = await client.models.list()
        raw_model_ids = [m.id for m in models.data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        raw_model_ids = ["llama3.1:latest"]

    # Filter and Map to Friendly Names
    friendly_names = []
    for raw_id in raw_model_ids:
        # Filter out embedding models
        if "embed" in raw_id:
            continue

        # Use simple mapping or fallback to raw ID
        name = MODEL_MAPPING.get(raw_id, raw_id)
        friendly_names.append(name)

        # Ensure reverse mapping exists for fallback cases
        if name not in FRIENDLY_TO_RAW:
            FRIENDLY_TO_RAW[name] = raw_id

    # Default settings
    default_friendly = "Llama 3.1"

    # Check if default is available, otherwise pick first
    initial_model = (
        default_friendly
        if default_friendly in friendly_names
        else friendly_names[0]
        if friendly_names
        else "Llama 3.1"
    )

    settings.update(
        {
            "model": initial_model,
        }
    )

    cl.user_session.set("settings", settings)
    # Store available models in session for validation
    cl.user_session.set("available_models", friendly_names)

    # Format: Hidden DIV for script.js to read
    # This requires unsafe_allow_html=true in config.toml
    await cl.Message(
        content=f"Hello from Nebulus! I am connected to your local Ollama instance "
        f"using {settings['model']}"
        f"<div id='model-data' data-model='{settings['model']}' "
        f"style='display: none;'></div>"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    # Command Interception for Model Switching
    if message.content.startswith("/model "):
        new_model = message.content.replace("/model ", "").strip()
        available_models = cl.user_session.get("available_models", [])

        # Fallback if list empty
        if new_model in available_models or not available_models:
            settings["model"] = new_model
            cl.user_session.set("settings", settings)

            # Hijack the user's command message and convert it to the system confirmation
            # This avoids race conditions with message.remove()
            message.author = "System"
            message.content = (
                f"Switched to {new_model}"
                f"<div id='model-data' data-model='{new_model}' style='display: none;'></div>"
            )
            await message.update()
            return  # Stop processing
        else:
            # Hijack for error too
            message.author = "System"
            message.content = (
                f"Error: Model '{new_model}' not found in available models: "
                f"{available_models}"
            )
            await message.update()
            return

    msg = cl.Message(content="")
    await msg.send()

    # Map Friendly Name back to Raw ID for backend
    completion_settings = settings.copy()
    friendly_name = settings["model"]
    completion_settings["model"] = FRIENDLY_TO_RAW.get(friendly_name, friendly_name)

    stream = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": message.content},
        ],
        stream=True,
        **completion_settings,
    )

    async for part in stream:
        if token := part.choices[0].delta.content:
            await msg.stream_token(token)

    await msg.update()
