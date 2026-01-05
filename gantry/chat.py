import os
import chainlit as cl
from openai import AsyncOpenAI
from database import Chat, Message, SessionLocal, User

# from sqlalchemy import desc

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
    # Authenticate User via Cookie (Chainlit exposes cookies in user_session.get('request')? No, difficult.
    # Alternative: Chainlit has user metadata if authenticated via CL Auth.
    # We used custom middleware auth.
    # We can try to get the user from the cl.user_session if we populate it in middleware?
    # Chainlit runs in separate process/lifecycle than FastAPI middleware sometimes for WebSocket.
    # Actually, with mount_chainlit, they share app but WS handling is tricky.
    # Workaround: Parsing 'access_token' from cl.user_session.get("http_referer") or similar is unreliable.
    # Use: cl.user_session.get("user") should be populated if we integrate CL auth, but we built custom auth.
    # Let's try to get cookies from request if available, or just fetch via HTTP call to /me?
    # No, that's inefficient.
    # Chainlit 1.0+ exposes cl.user_session.get("user") object if we use cl.password_auth_callback.
    # Since we are wrapping CL with our own AuthMiddleware, we might be bypassing CL's user object.
    # NOTE: For now, we will try to extract token from the Websocket headers if possible or rely on a "guest" fallback until we fix deep integration.
    # Wait! cl.header_auth_callback?
    # Let's simply assume we can query by a known user for now or try to parse cookies from `cl.user_session`.

    # Simple fix for sidebar MVP: We want to CREATE a chat ID in the DB so it lists in history.
    # We will try to resolve the user from the DB using a generic "admin" or the single user if count=1.

    db = SessionLocal()
    try:
        # MVP: fetch first user or default
        user = db.query(User).first()
        user_id = user.id if user else 1
    finally:
        db.close()

    chat_id = cl.user_session.get("id")

    # Persist Chat Start
    db = SessionLocal()
    try:
        new_chat = Chat(id=chat_id, user_id=user_id, title="New Chat")
        db.add(new_chat)
        db.commit()
    except Exception as e:
        print(f"Error creating chat: {e}")
    finally:
        db.close()

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

    # Store user_id for later
    cl.user_session.set("db_user_id", user_id)

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
    # user_id = cl.user_session.get("db_user_id", 1)  # Keeps finding unused variable if not used.
    # Use user_id for logic or remove. We used it in the db logic.
    # Ah, in previous edit, it was used. Let's make sure it is effectively used or remove local var if direct access.

    chat_id = cl.user_session.get("id")

    # Command Interception for Model Switching
    if message.content.startswith("/model "):
        new_model = message.content.replace("/model ", "").strip()
        available_models = cl.user_session.get("available_models", [])

        if new_model not in available_models and available_models:
            # Hijack for error too
            message.author = "System"
            message.content = (
                f"Error: Model '{new_model}' not found in available models: "
                f"{available_models}"
            )
            await message.update()
            return

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

    # Persist User Message
    db = SessionLocal()
    try:
        user_msg = Message(chat_id=chat_id, author="user", content=message.content)
        db.add(user_msg)

        # Auto-update title if it's the first message and title is "New Chat"
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat and chat.title == "New Chat":
            # Simple title generation: First 30 chars
            chat.title = (
                (message.content[:30] + "..")
                if len(message.content) > 30
                else message.content
            )
            db.add(chat)

        db.commit()
    except Exception as e:
        print(f"Error saving user message: {e}")
    finally:
        db.close()

    msg = cl.Message(content="")
    await msg.send()

    # Map Friendly Name back to Raw ID for backend
    completion_settings = settings.copy()
    friendly_name = settings["model"]
    completion_settings["model"] = FRIENDLY_TO_RAW.get(friendly_name, friendly_name)

    full_response = ""

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
            full_response += token

    await msg.update()

    # Persist AI Message
    db = SessionLocal()
    try:
        ai_msg = Message(chat_id=chat_id, author="assistant", content=full_response)
        db.add(ai_msg)
        db.commit()
    except Exception as e:
        print(f"Error saving AI message: {e}")
    finally:
        db.close()
