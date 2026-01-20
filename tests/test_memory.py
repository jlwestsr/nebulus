"""
Tests for Hybrid LTM Module.
"""

import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from src.core.memory.models import Entity, Relation, MemoryItem
from src.core.memory.graph_store import GraphStore
from src.core.memory.vector_store import VectorStore

TEST_DATA_DIR = "tests/data"
TEST_GRAPH_PATH = f"{TEST_DATA_DIR}/test_graph.json"


@pytest.fixture
def graph_store():
    # Setup
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
    os.makedirs(TEST_DATA_DIR)

    store = GraphStore(storage_path=TEST_GRAPH_PATH)
    yield store

    # Teardown
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)


def test_graph_add_entity(graph_store):
    entity = Entity(id="TestNode", type="TestType")
    graph_store.add_entity(entity)

    assert graph_store.graph.has_node("TestNode")
    assert graph_store.graph.nodes["TestNode"]["type"] == "TestType"


def test_graph_add_relation(graph_store):
    e1 = Entity(id="Node1", type="TypeA")
    e2 = Entity(id="Node2", type="TypeB")
    graph_store.add_entity(e1)
    graph_store.add_entity(e2)

    rel = Relation(source="Node1", target="Node2", relation="CONNECTS_TO")
    graph_store.add_relation(rel)

    assert graph_store.graph.has_edge("Node1", "Node2")
    assert graph_store.graph.edges["Node1", "Node2"]["relation"] == "CONNECTS_TO"


def test_graph_persistence(graph_store):
    e1 = Entity(id="PersistentNode", type="Saved")
    graph_store.add_entity(e1)

    # Reload from disk
    new_store = GraphStore(storage_path=TEST_GRAPH_PATH)
    assert new_store.graph.has_node("PersistentNode")


@patch("src.core.memory.vector_store.chromadb.HttpClient")
def test_vector_store_add(mock_client_cls):
    """Test VectorStore interactions with mocked ChromaDB."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client_cls.return_value = mock_client

    store = VectorStore()
    item = MemoryItem(content="Test memory log")

    store.add_episodic_memory(item)

    # Verify add was called
    mock_collection.add.assert_called_once()
    call_args = mock_collection.add.call_args[1]
    assert call_args["documents"][0] == "Test memory log"
    assert call_args["ids"][0] == item.id
