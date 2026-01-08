import os
import base64
import chainlit as cl
from openai import AsyncOpenAI
from database import Chat, Message, SessionLocal, User, Feedback
from sqlalchemy import desc

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


# --- DB Helpers (Synchronous) ---
def initialize_chat_db(chat_id):
    db = SessionLocal()
    user_id = 1
    try:
        user = db.query(User).first()
        user_id = user.id if user else 1

        # Check if chat exists first to avoid IntegrityError logging
        existing_chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not existing_chat:
            new_chat = Chat(id=chat_id, user_id=user_id, title="New Chat")
            db.add(new_chat)
            db.commit()
    except Exception as e:
        print(f"Error creating chat: {e}")
    finally:
        db.close()
    return user_id


def update_model_setting_db(user_id, new_model):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.current_model = new_model
            db.commit()
    except Exception as e:
        print(f"Error saving model preference: {e}")
    finally:
        db.close()


def sync_model_from_db_helper(user_id):
    current_model = None
    if not user_id:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.current_model:
            current_model = user.current_model
    except Exception as e:
        print(f"Error syncing model from DB: {e}")
    finally:
        db.close()
    return current_model


def get_chat_history_db(chat_id, limit=20):
    db = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .all()
        )
        # Detach objects or copy data to avoid lazy loading issues after session close
        # Actually in simple cases, accessing attributes here loads them.
        # But to be safe, let's just return the list and rely on eager loading of simple columns.
        return sorted(messages, key=lambda m: m.created_at)
    finally:
        db.close()


def save_user_message_db(chat_id, content, message_id):
    db = SessionLocal()
    try:
        # Check for duplicate cl_id to prevent IntegrityError
        # (Though unique constraint handles it, avoiding the try/except overhead is better)
        if db.query(Message).filter(Message.cl_id == message_id).first():
            return

        user_msg = Message(
            chat_id=chat_id,
            author="user",
            content=content,
            cl_id=message_id,
        )
        db.add(user_msg)

        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat and chat.title == "New Chat":
            chat.title = (content[:30] + "..") if len(content) > 30 else content
            db.add(chat)

        db.commit()
    except Exception as e:
        print(f"Error saving user message: {e}")
    finally:
        db.close()


def save_ai_message_db(chat_id, content, message_id):
    db = SessionLocal()
    try:
        if db.query(Message).filter(Message.cl_id == message_id).first():
            return

        ai_msg = Message(
            chat_id=chat_id,
            author="assistant",
            content=content,
            cl_id=message_id,
        )
        db.add(ai_msg)
        db.commit()
    except Exception as e:
        print(f"Error saving AI message: {e}")
    finally:
        db.close()


def save_feedback_db(message_id, score, comment):
    db = SessionLocal()
    try:
        db_msg = db.query(Message).filter(Message.cl_id == message_id).first()
        if not db_msg:
            print(f"Feedback failed: Message {message_id} not found")
            return

        existing = db.query(Feedback).filter(Feedback.message_id == db_msg.id).first()
        if existing:
            existing.score = score
            existing.comment = comment
        else:
            new_fb = Feedback(
                message_id=db_msg.id,
                score=score,
                comment=comment,
            )
            db.add(new_fb)
        db.commit()
    except Exception as e:
        print(f"Error saving feedback: {e}")
    finally:
        db.close()


def construct_multimodal_payload(content, images):
    """
    Constructs a payload compatible with OpenAI API (and Ollama) for multimodal inputs.
    If no images are present, returns the content string as is.
    """
    if not images:
        return content

    payload = [{"type": "text", "text": content}]

    for img in images:
        # Check if img is a Chainlit Element or a mock object
        path = getattr(img, "path", None)
        mime = getattr(img, "mime", "image/png")

        if path:
            with open(path, "rb") as f:
                image_data = f.read()
                b64_data = base64.b64encode(image_data).decode("utf-8")

            payload.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64_data}"},
                }
            )

    return payload


def process_thinking_tags(text: str) -> str:
    """
    Replaces <think> and </think> tags with a collapsible HTML details block.
    Handles partial tags for streaming scenarios (simple approach).
    """
    if "<think>" in text:
        text = text.replace(
            "<think>",
            "<details open class='thinking-block'><summary>Thinking Process</summary><div class='thinking-content'>",
        )

    if "</think>" in text:
        text = text.replace("</think>", "</div></details>")

    return text


# --- Async Handlers ---


@cl.on_chat_start
async def start():
    chat_id = cl.user_session.get("id")
    # ... (rest of start is standard) ...
    # Use standard start logic, no requested_chat_id logic needed since we use Soft Nav now.

    # Async DB Call
    user_id = await cl.make_async(initialize_chat_db)(chat_id)

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
        if "embed" in raw_id:
            continue
        name = MODEL_MAPPING.get(raw_id, raw_id)
        friendly_names.append(name)
        if name not in FRIENDLY_TO_RAW:
            FRIENDLY_TO_RAW[name] = raw_id

    default_friendly = "Llama 3.1"

    # Try to load user's preferred model
    db_model = await cl.make_async(sync_model_from_db_helper)(user_id)
    if db_model:
        default_friendly = db_model

    settings.update({"model": default_friendly})
    cl.user_session.set("settings", settings)
    cl.user_session.set("available_models", friendly_names)
    cl.user_session.set("db_user_id", user_id)

    await cl.Message(
        content=f"<div id='model-data' data-model='{settings['model']}' style='display: none;'></div>"
    ).send()


async def handle_model_command(message: cl.Message, settings: dict):
    if not message.content.startswith("/model "):
        return False

    new_model = message.content.replace("/model ", "").strip()
    available_models = cl.user_session.get("available_models", [])

    if new_model not in available_models and available_models:
        message.author = "System"
        message.content = (
            f"Error: Model '{new_model}' not found in available models: "
            f"{available_models}"
        )
        await message.update()
        return True

    settings["model"] = new_model
    cl.user_session.set("settings", settings)

    user_id = cl.user_session.get("db_user_id")
    await cl.make_async(update_model_setting_db)(user_id, new_model)

    message.author = "System"
    message.content = (
        f"Switched to {new_model}"
        f"<div id='model-data' data-model='{new_model}' style='display: none;'></div>"
    )
    await message.update()
    return True


@cl.on_message
async def main(message: cl.Message):
    # --- Soft Navigation Handler ---
    if message.content.startswith("/load_history "):
        # Extract ID
        new_chat_id = message.content.replace("/load_history ", "").strip()

        # Remove the command message from UI to keep it clean
        await message.remove()

        # Update Session
        cl.user_session.set("id", new_chat_id)

        # Load History
        history = await cl.make_async(get_chat_history_db)(new_chat_id)
        if history:
            # We must manually emit the "new_message" event to bypass Chainlit's
            # tight coupling with the *initial* session ID context.
            from chainlit.context import context

            for msg in history:
                # Chainlit 1.3+ structure approximation
                # We remove 'threadId' to prevent frontend filtering mismatch
                msg_dict = {
                    "id": msg.cl_id,
                    "createdAt": msg.created_at.isoformat() if msg.created_at else None,
                    "content": msg.content,
                    "author": msg.author,
                    "output": msg.content,
                    "type": (
                        "user_message" if msg.author == "User" else "assistant_message"
                    ),
                }

                # We emit directly to the websocket found in context.session
                if context.session and context.session.emit:
                    await context.emitter.emit("new_message", msg_dict)
        else:
            pass  # No history to load

        return
    # -------------------------------

    settings = cl.user_session.get("settings")
    chat_id = cl.user_session.get("id")
    user_id = cl.user_session.get("db_user_id")

    # Refresh Model from DB (Async)
    db_model = await cl.make_async(sync_model_from_db_helper)(user_id)
    if db_model:
        settings["model"] = db_model
    cl.user_session.set("settings", settings)

    if await handle_model_command(message, settings):
        return

    # Persist User Message (Async)
    await cl.make_async(save_user_message_db)(chat_id, message.content, message.id)

    completion_settings = settings.copy()
    friendly_name = settings["model"]
    completion_settings["model"] = FRIENDLY_TO_RAW.get(friendly_name, friendly_name)

    # Build Context (Async)
    history_messages = await cl.make_async(get_chat_history_db)(chat_id)
    context_messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

    for hist_msg in history_messages:
        role = "user" if hist_msg.author == "user" else "assistant"
        context_messages.append({"role": role, "content": hist_msg.content})

    # --- Multi-Modal Handling ---
    images = (
        [file for file in message.elements if "image" in file.mime]
        if message.elements
        else []
    )

    # Auto-switch to Vision model if images are present
    if images and completion_settings.get("model") != "llama3.2-vision:latest":
        completion_settings["model"] = "llama3.2-vision:latest"

        # Update user session to persist the switch
        settings["model"] = "Llama 3.2 Vision"
        cl.user_session.set("settings", settings)

        # Persist to DB so it survives refresh
        await cl.make_async(update_model_setting_db)(user_id, "Llama 3.2 Vision")

        # Notify user of switch and trigger UI update via hidden div
        await cl.Message(
            author="System",
            content="Switched to Llama 3.2 Vision for image analysis.<div id='model-data' data-model='Llama 3.2 Vision' style='display: none;'></div>",
        ).send()

    # Construct the final content payload for the current message
    current_message_content = construct_multimodal_payload(message.content, images)

    # Add current message to context
    context_messages.append({"role": "user", "content": current_message_content})

    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    stream = await client.chat.completions.create(
        messages=context_messages,
        stream=True,
        **completion_settings,
    )

    async for part in stream:
        if token := part.choices[0].delta.content:
            await msg.stream_token(token)
            full_response += token

            # Real-time update for thinking tags if they appear
            if "<think>" in token or "</think>" in token:
                msg.content = process_thinking_tags(full_response)
                await msg.update()

    # Final pass to ensure everything is formatted correctly
    msg.content = process_thinking_tags(full_response)
    await msg.update()

    # Persist AI Message (Async)
    await cl.make_async(save_ai_message_db)(chat_id, full_response, msg.id)


@cl.on_feedback
async def on_feedback(feedback):
    await cl.make_async(save_feedback_db)(
        feedback.message_id, feedback.score, feedback.comment
    )
