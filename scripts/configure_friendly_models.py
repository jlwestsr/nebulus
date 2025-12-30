import sqlite3
import json
import time

# Configuration
USER_ID = "682267a5-e64f-4d20-94eb-1b685d514c70"
FRIENDLY_MODELS = [
    {
        "id": "llama-3.2-vision",
        "name": "Llama 3.2 Vision",
        "base_model_id": "llama3.2-vision:latest",
        "description": "Llama 3.2 Vision (11B) - Multimodal support",
    },
    {
        "id": "llama-3.1",
        "name": "Llama 3.1",
        "base_model_id": "llama3.1:latest",
        "description": "Llama 3.1 (8B) - General purpose",
    },
    {
        "id": "qwen-2.5-coder",
        "name": "Qwen 2.5 Coder",
        "base_model_id": "qwen2.5-coder:latest",
        "description": "Qwen 2.5 Coder (7B) - Specialized for code",
    },
]

RAW_MODELS = [
    "llama3.2-vision:latest",
    "llama3.1:latest",
    "qwen2.5-coder:latest",
    "nomic-embed-text:latest",
]


def configure_models():
    print("Configuring friendly models...")

    try:
        conn = sqlite3.connect("/data/webui.db")
        cursor = conn.cursor()

        now = int(time.time())

        # 1. Upsert Friendly Models
        for model in FRIENDLY_MODELS:
            print(f"Upserting {model['name']}...")

            meta = json.dumps({"description": model["description"]})
            params = json.dumps({})
            access_control = json.dumps({})

            cursor.execute("SELECT id FROM model WHERE id=?", (model["id"],))
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    """
                    UPDATE model
                    SET
                        user_id=?, base_model_id=?, name=?, meta=?, params=?,
                        updated_at=?, is_active=1
                    WHERE id=?
                    """,
                    (
                        USER_ID,
                        model["base_model_id"],
                        model["name"],
                        meta,
                        params,
                        now,
                        model["id"],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO model (
                        id, user_id, base_model_id, name, meta, params,
                        created_at, updated_at, access_control, is_active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        model["id"],
                        USER_ID,
                        model["base_model_id"],
                        model["name"],
                        meta,
                        params,
                        now,
                        now,
                        access_control,
                    ),
                )

        # 2. Delete Raw Models (Let Filter Handle Them)
        for raw_id in RAW_MODELS:
            print(f"Deleting raw model entry: {raw_id}...")
            cursor.execute("DELETE FROM model WHERE id=?", (raw_id,))

        conn.commit()
        print("Success! Models configured.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    configure_models()
