"""
Graph Store Implementation.
Uses NetworkX to maintain a directed knowledge graph.
Persists data to specific JSON file in the data directory.
"""

import json
import logging
from pathlib import Path
from typing import List, Tuple
import networkx as nx
from networkx.readwrite import json_graph

from .models import Entity, Relation, GraphStats

logger = logging.getLogger(__name__)


class GraphStore:
    def __init__(self, storage_path: str = "data/memory_graph.json"):
        self.storage_path = Path(storage_path)
        self.graph = nx.DiGraph()
        self._ensure_storage_dir()
        self.load_graph()

    def _ensure_storage_dir(self):
        """Ensure the parent directory of storage_path exists."""
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_graph(self):
        """Load graph from JSON file if it exists."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.graph = json_graph.node_link_graph(
                        data, directed=True, edges="links"
                    )
                logger.info(
                    f"Loaded graph from {self.storage_path} with {self.graph.number_of_nodes()} nodes."
                )
            except Exception as e:
                logger.error(f"Failed to load graph: {e}")
                self.graph = nx.DiGraph()
        else:
            logger.info("No existing graph found. Initialized empty graph.")

    def save_graph(self):
        """Persist graph to JSON file."""
        try:
            data = json_graph.node_link_data(self.graph, edges="links")
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved graph to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")

    def add_entity(self, entity: Entity):
        """Add a node to the graph. Idempotent."""
        self.graph.add_node(entity.id, type=entity.type, **entity.properties)
        self.save_graph()

    def add_relation(self, relation: Relation):
        """Add a directional edge between nodes."""
        if not self.graph.has_node(relation.source):
            logger.warning(
                f"Source node {relation.source} does not exist. Adding as generic entity."
            )
            self.graph.add_node(relation.source, type="Unknown")

        if not self.graph.has_node(relation.target):
            logger.warning(
                f"Target node {relation.target} does not exist. Adding as generic entity."
            )
            self.graph.add_node(relation.target, type="Unknown")

        self.graph.add_edge(
            relation.source,
            relation.target,
            relation=relation.relation,
            weight=relation.weight,
        )
        self.save_graph()

    def get_neighbors(self, node_id: str) -> List[Tuple[str, str]]:
        """
        Get 1-hop neighbors for a node.
        Returns list of (relation, target_node_id).
        """
        if not self.graph.has_node(node_id):
            return []

        results = []
        for neighbor in self.graph.neighbors(node_id):
            edge_data = self.graph.get_edge_data(node_id, neighbor)
            relation_type = edge_data.get("relation", "RELATED_TO")
            results.append((relation_type, neighbor))
        return results

    def get_stats(self) -> GraphStats:
        """Return current graph statistics."""
        types = set()
        for _, data in self.graph.nodes(data=True):
            if "type" in data:
                types.add(data["type"])

        return GraphStats(
            node_count=self.graph.number_of_nodes(),
            edge_count=self.graph.number_of_edges(),
            entity_types=list(types),
        )
