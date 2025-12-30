import sqlite3
import json
import time

# Configuration
USER_ID = "682267a5-e64f-4d20-94eb-1b685d514c70"
MODELS = [
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
        "is_active": 1,
    },
    # Hidden Base Models
    {
        "id": "llama3.2-vision:latest",
        "name": "llama3.2-vision:latest",
        "base_model_id": "llama3.2-vision:latest",
        "description": "Base Model (Hidden)",
        "is_active": 0,
    },
    {
        "id": "llama3.1:latest",
        "name": "llama3.1:latest",
        "base_model_id": "llama3.1:latest",
        "description": "Base Model (Hidden)",
        "is_active": 0,
    },
    {
        "id": "qwen2.5-coder:latest",
        "name": "qwen2.5-coder:latest",
        "base_model_id": "qwen2.5-coder:latest",
        "description": "Base Model (Hidden)",
        "is_active": 0,
    },
    {
        "id": "nomic-embed-text:latest",
        "name": "nomic-embed-text:latest",
        "base_model_id": "nomic-embed-text:latest",
        "description": "Base Model (Hidden)",
        "is_active": 0,
    },
]


def configure_models():
    print(f"Configuring {len(MODELS)} friendly models...")

    try:
        conn = sqlite3.connect("/data/webui.db")
        cursor = conn.cursor()

        now = int(time.time())

        for model in MODELS:
            print(f"Upserting {model['name']}...")

            meta = json.dumps({"description": model["description"]})
            params = json.dumps({})
            access_control = json.dumps({})  # Open access

            # Check if exists
            cursor.execute("SELECT id FROM model WHERE id=?", (model["id"],))
            exists = cursor.fetchone()

            is_active = model.get("is_active", 1)

            if exists:
                cursor.execute(
                    """
                    UPDATE model
                    SET
                        user_id=?, base_model_id=?, name=?, meta=?, params=?,
                        updated_at=?, is_active=?
                    WHERE id=?
                    """,
                    (
                        USER_ID,
                        model["base_model_id"],
                        model["name"],
                        meta,
                        params,
                        now,
                        is_active,
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
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        is_active,
                    ),
                )

        conn.commit()
        print("Success! Models configured.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    configure_models()
