import chromadb
from chromadb.config import Settings
import uuid
import time
from typing import Dict, List, Optional, Any


class LTMClient:
    def __init__(self, host: str = "chromadb", port: int = 8000):
        """Initialize connection to ChromaDB service."""
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(allow_reset=True, anonymized_telemetry=False),
            )
            # Initialize collections
            self.conversations = self.client.get_or_create_collection("conversations")
            self.messages = self.client.get_or_create_collection("messages")
            self.attachments = self.client.get_or_create_collection("attachments")
            self.users = self.client.get_or_create_collection("users")
        except Exception as e:
            print(f"Error initializing ChromaDB client: {e}")
            # We might want to handle this more gracefully depending on app startup requirements
            raise e

    def _generate_id(self) -> str:
        return str(uuid.uuid4())

    def _get_timestamp(self) -> float:
        return time.time()

    # --- Conversations ---

    def create_conversation(
        self, topic: str, user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Create a new conversation node."""
        conv_id = self._generate_id()
        timestamp = self._get_timestamp()

        metadata = {
            "node_type": "conversation",
            "topic": topic,
            "user_id": user_id,
            "start_time": timestamp,
            "last_updated": timestamp,
        }

        # We use a dummy embedding or document content since we are primarily using it as a store
        self.conversations.add(
            ids=[conv_id], documents=[f"Conversation: {topic}"], metadatas=[metadata]
        )

        return {"id": conv_id, **metadata}

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific conversation."""
        result = self.conversations.get(ids=[conv_id])
        if not result["ids"]:
            return None

        # Construct response from the first (and only) result
        return {"id": conv_id, **result["metadatas"][0]}

    def update_conversation(
        self, conv_id: str, topic: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update conversation properties."""
        current = self.get_conversation(conv_id)
        if not current:
            return None

        new_metadata = current.copy()
        # Remove 'id' as it's not stored in metadata
        del new_metadata["id"]

        if topic:
            new_metadata["topic"] = topic

        new_metadata["last_updated"] = self._get_timestamp()

        self.conversations.update(
            ids=[conv_id],
            documents=[f"Conversation: {new_metadata.get('topic', 'Untitled')}"],
            metadatas=[new_metadata],
        )

        return {"id": conv_id, **new_metadata}

    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation and its messages."""
        # First delete associate messages
        # Note: Chroma "where" filter allows deleting by metadata
        self.messages.delete(where={"conversation_id": conv_id})

        # Delete the conversation itself
        self.conversations.delete(ids=[conv_id])
        return True

    # --- Messages ---

    def add_message(
        self,
        conversation_id: str,
        content: str,
        sender: str = "user",
        receiver: str = "ai",
    ) -> Dict[str, Any]:
        """Add a message to a conversation."""
        # Verify conversation exists first (optional integrity check)
        if not self.get_conversation(conversation_id):
            raise ValueError(f"Conversation {conversation_id} not found")

        msg_id = self._generate_id()
        timestamp = self._get_timestamp()

        metadata = {
            "node_type": "message",
            "conversation_id": conversation_id,
            "sender": sender,
            "receiver": receiver,
            "timestamp": timestamp,
        }

        self.messages.add(ids=[msg_id], documents=[content], metadatas=[metadata])

        # Update conversation last_updated
        self.update_conversation(conversation_id)

        return {"id": msg_id, "content": content, **metadata}

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve messages for a conversation."""
        results = self.messages.get(
            where={"conversation_id": conversation_id}
            # Note: Chroma results are not strictly ordered by insertion time by default
            # We will need to sort in memory
        )

        output = []
        for i, msg_id in enumerate(results["ids"]):
            item = {
                "id": msg_id,
                "content": results["documents"][i],
                **results["metadatas"][i],
            }
            output.append(item)

        # Sort by timestamp
        output.sort(key=lambda x: x.get("timestamp", 0))
        return output

    # --- User Preferences ---

    def set_user_preference(self, user_id: str, key: str, value: Any) -> Dict[str, Any]:
        """Set a user preference. Stored as flexible metadata on a single User node."""
        # Attempt to get existing user node
        result = self.users.get(ids=[user_id])

        if not result["ids"]:
            # Create new user node
            current_metadata = {
                "node_type": "user",
                "created_at": self._get_timestamp(),
            }
            # Chroma metadata must be primitives, best to stringify unknown types for now
            current_metadata[key] = str(value)

            self.users.add(
                ids=[user_id],
                documents=[f"User Profile: {user_id}"],
                metadatas=[current_metadata],
            )
        else:
            # Update existing
            current_metadata = result["metadatas"][0]
            current_metadata[key] = str(value)

            self.users.update(ids=[user_id], metadatas=[current_metadata])

        return {"user_id": user_id, **current_metadata}

    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get all preferences for a user."""
        result = self.users.get(ids=[user_id])
        if not result["ids"]:
            return None

        return result["metadatas"][0]
