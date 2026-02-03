"""
Tests for Hybrid LTM Module.
"""

import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nebulus_core.memory.models import Entity, Relation
from nebulus_core.memory.graph_store import GraphStore
from nebulus_core.vector.client import VectorClient

TEST_DATA_DIR = "tests/data"
TEST_GRAPH_PATH = Path(f"{TEST_DATA_DIR}/test_graph.json")


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


@patch("nebulus_core.vector.client.chromadb")
def test_vector_client_creates_collection(mock_chromadb):
    """Test VectorClient creates collections via ChromaDB."""
    mock_http = MagicMock()
    mock_collection = MagicMock()
    mock_http.get_or_create_collection.return_value = mock_collection
    mock_chromadb.HttpClient.return_value = mock_http

    client = VectorClient(settings={"mode": "http", "host": "localhost", "port": 8001})
    col = client.get_or_create_collection("test")
    assert col is not None
