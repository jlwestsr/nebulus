"""
Vector Store Implementation.
Wrapper for ChromaDB to handle embedding-based storage and retrieval.
"""

import os
import logging
from typing import List
import chromadb
from chromadb.config import Settings

from .models import MemoryItem

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        # Read config from environment (Dependency Injection pattern)
        self.host = os.getenv("NEBULUS_CHROMA_HOST", "chromadb")
        self.port = int(os.getenv("NEBULUS_CHROMA_PORT", "8001"))
        self.collection_name = "ltm_episodic_memory"

        self.client = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish connection to ChromaDB."""
        try:
            logger.info(f"Connecting to ChromaDB at {self.host}:{self.port}")
            self.client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(allow_reset=True, anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info("ChromaDB connection successful.")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            # We don't raise here to prevent app crash, but logic should handle None client
            self.client = None

    def add_episodic_memory(self, item: MemoryItem):
        """Add a text memory item to vector store."""
        if not self.collection:
            logger.warning("ChromaDB offline. Cannot add memory.")
            return

        try:
            # Prepare metadata with proper types
            metadata = {"timestamp": item.timestamp, "archived": item.archived}
            # Merge user metadata
            metadata.update(item.metadata)

            self.collection.add(
                documents=[item.content], metadatas=[metadata], ids=[item.id]
            )
            logger.debug(f"Added memory item {item.id} to vector store.")
        except Exception as e:
            logger.error(f"Error adding memory to ChromaDB: {e}")

    def query_hybrid(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Perform semantic search to find potential graph entry points.
        Returns a list of matching documents.
        """
        if not self.collection:
            logger.warning("ChromaDB offline. Returning empty query results.")
            return []

        try:
            results = self.collection.query(
                query_texts=[query_text], n_results=n_results
            )

            # Flatten results (Chroma returns list of lists)
            docs = []
            if results and results["documents"]:
                for doc_list in results["documents"]:
                    docs.extend(doc_list)

            return docs
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

    def get_unarchived_memories(self, n_results: int = 20) -> List[MemoryItem]:
        """Retrieve recent unarchived memories for consolidation."""
        if not self.collection:
            return []

        try:
            # Note: Chroma filtering syntax might vary by version
            results = self.collection.get(where={"archived": False}, limit=n_results)

            items = []
            if results["ids"]:
                for i, _id in enumerate(results["ids"]):
                    items.append(
                        MemoryItem(
                            id=_id,
                            content=results["documents"][i],
                            # Reconstruct basic metadata, timestamp might be lost if strict casting logic isn't here
                            metadata=(
                                results["metadatas"][i] if results["metadatas"] else {}
                            ),
                        )
                    )
            return items
        except Exception as e:
            logger.error(f"Error fetching unarchived memories: {e}")
            return []

    def mark_archived(self, memory_ids: List[str]):
        """Update metadata to set archived=True."""
        if not self.collection:
            return

        try:
            # Update specific items
            # Chroma update requires re-providing data or using update method carefully
            # Ideally we utilize `update` with partial data if supported, or get-modify-update
            # For simplicity in this implementation, we assume we just set the flag

            # We iterate to update (inefficient but safe for MVP)
            for mid in memory_ids:
                existing = self.collection.get(ids=[mid])
                if existing["ids"]:
                    meta = existing["metadatas"][0]
                    meta["archived"] = True
                    self.collection.update(ids=[mid], metadatas=[meta])
        except Exception as e:
            logger.error(f"Error marking memories as archived: {e}")
