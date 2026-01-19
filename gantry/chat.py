import os
import base64
import chainlit as cl
import uuid
from openai import AsyncOpenAI
from database import Chat, Message, db_session, User, Feedback
from sqlalchemy import desc
from exec.sandbox import run_code_in_sandbox
from metrics.usage import log_usage
import re
from pypdf import PdfReader

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
    user_id = 1
    with db_session() as db:
        user = db.query(User).first()
        user_id = user.id if user else 1

        # Check if chat exists first to avoid IntegrityError logging
        existing_chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not existing_chat:
            new_chat = Chat(id=chat_id, user_id=user_id, title="New Chat")
            db.add(new_chat)
    return user_id


def update_model_setting_db(user_id, new_model):
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.current_model = new_model


def sync_model_from_db_helper(user_id):
    if not user_id:
        return None
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.current_model:
            return user.current_model
    return None


def get_chat_history_db(chat_id, limit=20):
    with db_session() as db:
        db.expire_on_commit = False
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .all()
        )
        return sorted(messages, key=lambda m: m.created_at)


def save_user_message_db(chat_id, content, message_id):
    with db_session() as db:
        # Check for existing message (Upsert for Edit)
        existing_msg = db.query(Message).filter(Message.cl_id == message_id).first()
        if existing_msg:
            # If content changed, it's an EDIT
            if existing_msg.content != content:
                existing_msg.content = content
                # Truncate history AFTER this message (Call helper directly if session permits or just inline if needed)
                # But truncate_chat_after_db opens its own session.
                # To avoid nested sessions, let's just do it here or refactor.
                # Actually, truncate_chat_after_db is safe to call inside another session IF we refactor it to accept a db instance.
                # For now, let's just do the logic here.
                target = existing_msg
                db.query(Message).filter(Message.chat_id == chat_id).filter(
                    Message.created_at > target.created_at
                ).delete()
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


def save_ai_message_db(chat_id, content, message_id):
    with db_session() as db:
        if db.query(Message).filter(Message.cl_id == message_id).first():
            return

        ai_msg = Message(
            chat_id=chat_id,
            author="assistant",
            content=content,
            cl_id=message_id,
        )
        db.add(ai_msg)


def save_feedback_db(message_id, score, comment):
    with db_session() as db:
        db_msg = db.query(Message).filter(Message.cl_id == message_id).first()
        if not db_msg:
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


def truncate_chat_after_db(chat_id, message_id, include_target=True):
    """
    Deletes messages in a chat after a specific point.
    include_target=True: Deletes target + future (Regenerate).
    include_target=False: Deletes future only (Edit).
    """
    with db_session() as db:
        # Get target message
        target = db.query(Message).filter(Message.cl_id == message_id).first()
        if not target:
            return

        # Delete messages after the target
        query = db.query(Message).filter(Message.chat_id == chat_id)

        if include_target:
            query = query.filter(Message.created_at >= target.created_at)
        else:
            query = query.filter(Message.created_at > target.created_at)

        query.delete()

    return


def delete_all_chats_for_user_db(user_id, db=None):
    """
    Deletes all chats for a specific user.
    Cascading delete should handle messages if configured, but we can be explicit.
    """
    if db:
        return _delete_chats_logic(user_id, db)

    with db_session() as session:
        return _delete_chats_logic(user_id, session)


def _delete_chats_logic(user_id, db):
    # Get all chat IDs for user
    chats = db.query(Chat).filter(Chat.user_id == user_id).all()
    chat_ids = [c.id for c in chats]

    if not chat_ids:
        return 0

    # Delete Messages (if cascade isn't fully reliable or for safety)
    db.query(Message).filter(Message.chat_id.in_(chat_ids)).delete(
        synchronize_session=False
    )

    # Delete Chats
    deleted_count = (
        db.query(Chat).filter(Chat.user_id == user_id).delete(synchronize_session=False)
    )

    return deleted_count


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


def extract_text_from_pdf(path):
    """Extracts all text from a PDF file."""
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return f"[Error extracting text from PDF: {e}]"


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


async def handle_soft_navigation(message: cl.Message) -> bool:
    if not message.content.startswith("/load_history "):
        return False

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
                    "user_message"
                    if msg.author.lower() == "user"
                    else "assistant_message"
                ),
            }

            # Attach 'Regenerate' action to the *last* message if it is an assistant message
            if msg == history[-1] and msg.author != "User":
                msg_dict["actions"] = [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "regenerate",
                        "value": "regenerate",
                        "label": "Regenerate",
                        "collapsed": True,
                        "payload": {"value": "regenerate"},
                    }
                ]

            # We emit directly to the websocket found in context.session
            if context.session and context.session.emit:
                await context.emitter.emit("new_message", msg_dict)
    else:
        pass  # No history to load

    return True


async def build_chat_context(chat_id: str):
    history_messages = await cl.make_async(get_chat_history_db)(chat_id)
    context_messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

    for hist_msg in history_messages:
        role = "user" if hist_msg.author == "user" else "assistant"
        context_messages.append({"role": role, "content": hist_msg.content})

    return context_messages


async def handle_attachments_and_vision(
    message: cl.Message, settings: dict, completion_settings: dict, user_id: int
):
    # --- Attachment Handling (Images & PDFs) ---
    images = []
    text_attachments = ""

    if message.elements:
        for file in message.elements:
            if "image" in file.mime:
                images.append(file)
            elif "pdf" in file.mime:
                pdf_text = extract_text_from_pdf(file.path)
                text_attachments += f"\n\n--- Attachment: {file.name} ---\n{pdf_text}\n"

    # Combine original content with extracted text from documents
    combined_content = message.content + text_attachments

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

    return combined_content, images


async def handle_regenerate(
    message: cl.Message, chat_id: str, settings: dict, user_id: int
):
    if message.content.strip() != "/regenerate":
        return False

    # Remove command message
    await message.remove()

    # Get history to find last AI message
    history = await cl.make_async(get_chat_history_db)(chat_id)
    if history and history[-1].author != "User":
        target_msg = history[-1]
        await cl.make_async(truncate_chat_after_db)(chat_id, target_msg.cl_id)
        await cl.Message(id=target_msg.cl_id).remove()
        await cl.Message(content="🔄 Regenerating...").send()

        # Rebuild context
        context_messages = await build_chat_context(chat_id)
        await generate_ai_response(chat_id, context_messages, settings, user_id)
        return True
    return False


async def handle_clear_all_command(message: cl.Message, user_id: int):
    if message.content.strip() != "/clear_all":
        return False

    # Execute DB deletion
    count = await cl.make_async(delete_all_chats_for_user_db)(user_id)

    # UI Feedback
    await message.remove()
    await cl.Message(
        content=f"✅ Cleared {count} chats from history. Please refresh the page to see changes.<div id='bulk-delete-success-marker' style='display: none;'></div>"
    ).send()

    # Log action
    print(f"User {user_id} cleared {count} chats.")
    return True


@cl.on_message
async def main(message: cl.Message):
    # --- Soft Navigation Handler ---
    if await handle_soft_navigation(message):
        return
    # -------------------------------

    settings = cl.user_session.get("settings")
    chat_id = cl.user_session.get("id")
    user_id = cl.user_session.get("db_user_id")

    # --- Command: /clear_all ---
    if await handle_clear_all_command(message, user_id):
        return

    # --- Command: /regenerate ---
    if await handle_regenerate(message, chat_id, settings, user_id):
        return

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
    context_messages = await build_chat_context(chat_id)

    # --- Attachment Handling (Images & PDFs) ---
    combined_content, images = await handle_attachments_and_vision(
        message, settings, completion_settings, user_id
    )

    # Construct the final content payload for the current message
    current_message_content = construct_multimodal_payload(combined_content, images)

    # Add current message to context
    context_messages.append({"role": "user", "content": current_message_content})

    # Generate Response
    await generate_ai_response(chat_id, context_messages, settings, user_id)


@cl.action_callback("regenerate")
async def on_regenerate(action: cl.Action):
    chat_id = cl.user_session.get("id")
    user_id = cl.user_session.get("db_user_id")
    message_id = action.forId

    # 1. Truncate DB (remove this AI message)
    await cl.make_async(truncate_chat_after_db)(chat_id, message_id)

    # 2. Remove from UI
    await cl.Message(content="", id=message_id).remove()

    # 3. Feedback
    await cl.Message(content="🔄 Regenerating...").send()

    # 4. Rebuild context from DB (excluding truncated part)
    history = await cl.make_async(get_chat_history_db)(chat_id)
    if not history:
        return

    settings = cl.user_session.get("settings")

    context_messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    for hist_msg in history:
        role = "user" if hist_msg.author == "user" else "assistant"
        context_messages.append({"role": role, "content": hist_msg.content})

    await generate_ai_response(chat_id, context_messages, settings, user_id)


@cl.action_callback("run_code")
async def on_run_code(action: cl.Action):
    code = action.payload.get("code", "")
    language = action.payload.get("language", "python")

    # Send "Running..." status
    msg = cl.Message(content=f"🚀 Running {language} code...")
    await msg.send()

    # Execute (Sync via make_async)
    output = await cl.make_async(run_code_in_sandbox)(language, code)

    # Update message with output
    msg.content = f"```\n{output}\n```"
    await msg.update()


@cl.on_feedback
async def on_feedback(feedback):
    await cl.make_async(save_feedback_db)(
        feedback.message_id, feedback.score, feedback.comment
    )


async def generate_ai_response(chat_id, context_messages, settings, user_id):
    """
    Helper to call LLM, stream response, and attach actions.
    Used by main, on_regenerate, and /regenerate command.
    """
    completion_settings = settings.copy()
    friendly_name = settings["model"]
    completion_settings["model"] = FRIENDLY_TO_RAW.get(friendly_name, friendly_name)

    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    try:
        stream = await client.chat.completions.create(
            messages=context_messages,
            stream=True,
            stream_options={"include_usage": True},
            **completion_settings,
        )

        full_usage = None
        async for part in stream:
            # Handle usage data if present
            if hasattr(part, "usage") and part.usage:
                full_usage = part.usage
                total_tokens = part.usage.total_tokens

                # Add to footer
                full_response += f"\n\n---\n*Tokens: {total_tokens}*"
                msg.content = process_thinking_tags(full_response)
                await msg.update()

            token = (
                part.choices[0].delta.content
                if (hasattr(part, "choices") and len(part.choices) > 0)
                else ""
            )
            if token:
                await msg.stream_token(token)
                full_response += token
    except Exception as e:
        print(f"Error exploring model: {e}")
        error_msg = f"Error generating response: {e}"
        msg.content = error_msg
        await msg.update()
        full_response = error_msg

    # Final pass to ensure formatting
    msg.content = process_thinking_tags(full_response)

    # Attach action directly to message update
    # This is more reliable than action.send() for the initial response
    action = cl.Action(
        name="regenerate",
        value="regenerate",
        label="Regenerate",
        icon="refresh-cw",
        payload={"value": "regenerate"},
    )
    msg.actions = [action]
    await msg.update()

    # Detect code blocks and attach Run action
    code_blocks = re.findall(r"```(python|python3)\n(.*?)```", full_response, re.DOTALL)
    if code_blocks:
        # Take the last block for now or multiple? Let's just do one action for the last block to keep UI clean
        # or separate actions if we can.
        # Simple for now: If *any* python code, attach "Run Code" for the *last* block found.
        lang, code = code_blocks[-1]
        run_action = cl.Action(
            name="run_code",
            value="run_code",
            label="Run Code",
            icon="play",
            payload={"language": lang, "code": code},
        )
        msg.actions.append(run_action)
        await msg.update()

    # Persist AI Message (Async)
    await cl.make_async(save_ai_message_db)(chat_id, full_response, msg.id)

    # Log usage after message is persisted
    if full_usage:
        with db_session() as db:
            ai_msg = db.query(Message).filter(Message.cl_id == msg.id).first()
            if ai_msg:
                log_usage(
                    db,
                    user_id,
                    chat_id,
                    ai_msg.id,
                    completion_settings["model"],
                    full_usage.prompt_tokens,
                    full_usage.completion_tokens,
                )
