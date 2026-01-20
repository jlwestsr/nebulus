"""
Memory Consolidator ("Sleep Cycle").
Fetches unarchived memories from Vector Store, uses LLM to extract facts,
and updates the Graph Store.
"""

import logging
import json
import ollama

from .graph_store import GraphStore
from .vector_store import VectorStore
from .models import Entity, Relation

logger = logging.getLogger(__name__)


class Consolidator:
    def __init__(self, vector_store: VectorStore, graph_store: GraphStore):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.model = "llama3.1"  # Default consolidation model

    def consolidate(self):
        """
        Run the consolidation process.
        """
        logger.info("Starting memory consolidation cycle...")

        # 1. Fetch raw logs
        memories = self.vector_store.get_unarchived_memories(n_results=20)
        if not memories:
            logger.info("No new memories to consolidate.")
            return

        logger.info(f"Processing {len(memories)} memory items.")

        processed_ids = []
        for memory in memories:
            try:
                # 2. Extract facts using LLM
                facts = self._extract_facts(memory.content)

                # 3. Update Graph
                self._update_graph(facts)

                processed_ids.append(memory.id)
            except Exception as e:
                logger.error(f"Failed to process memory {memory.id}: {e}")

        # 4. Archive processed logs
        if processed_ids:
            self.vector_store.mark_archived(processed_ids)
            logger.info(f"Archived {len(processed_ids)} memory items.")

    def _extract_facts(self, text: str) -> dict:
        """
        Use Ollama to extract entities and relations from text.
        Returns a dictionary with 'entities' and 'relations' lists.
        """
        prompt = f"""
        Analyze the following text and extract key entities and relationships.
        Return ONLY a JSON object with this structure:
        {{
            "entities": [{{"id": "EntityName", "type": "EntityType"}}],
            "relations": [{{"source": "EntityName", "target": "TargetEntity", "relation": "RELATION_TYPE"}}]
        }}

        Text: "{text}"
        """

        try:
            response = ollama.chat(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )
            content = response["message"]["content"]

            # Simple parsing attempt (robustness would require more checks)
            # Find the start and end of the JSON block if wrapped in code blocks
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                logger.warning("Could not find JSON in LLM response.")
                return {"entities": [], "relations": []}

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return {"entities": [], "relations": []}

    def _update_graph(self, facts: dict):
        """Update graph store with extracted facts."""
        for ent in facts.get("entities", []):
            try:
                entity = Entity(
                    id=ent["id"], type=ent.get("type", "Unknown"), properties={}
                )
                self.graph_store.add_entity(entity)
            except Exception as e:
                logger.warning(f"Skipping invalid entity {ent}: {e}")

        for rel in facts.get("relations", []):
            try:
                relation = Relation(
                    source=rel["source"],
                    target=rel["target"],
                    relation=rel["relation"],
                    weight=1.0,
                )
                self.graph_store.add_relation(relation)
            except Exception as e:
                logger.warning(f"Skipping invalid relation {rel}: {e}")
