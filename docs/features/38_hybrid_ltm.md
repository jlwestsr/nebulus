# Feature: Hybrid Long-Term Memory (LTM)

## 1. Overview
**Branch**: `feat/hybrid-ltm`

Implement a Hybrid Long-Term Memory (LTM) system that combines Vector Search (ChromaDB) with a Knowledge Graph (NetworkX). This system will allow the AI agent to store and retrieve facts using both semantic and associative memory, addressing the "amnesia" and context saturation issues of pure RAG systems.

## 2. Requirements
- [ ] **Hybrid Architecture**: Integrate Vector Store (ChromaDB) and Graph Store (NetworkX).
- [ ] **Graph Operations**: `add_entity`, `add_relation`, `save_graph`, `load_graph`.
- [ ] **Vector Operations**: `add_episodic_memory`, `query_hybrid`.
- [ ] **Consolidation**: "Sleep Cycle" script to summarize logs and update the graph.
- [ ] **CLI Integration**:
    - `nebulus memory status`: Print graph stats.
    - `nebulus memory consolidate`: Trigger manual consolidation.
- [ ] **Resilience**: Gracefully handle offline services (Ollama/Chroma).
- [ ] **Type Safety**: Use Pydantic models and type hints throughout.

## 3. Technical Implementation
- **Directory**: `nebulus/core/memory/`
- **Modules**:
    - `models.py`: Pydantic data models.
    - `graph_store.py`: NetworkX wrapper for Knowledge Graph.
    - `vector_store.py`: ChromaDB wrapper.
    - `consolidator.py`: Logic for memory consolidation (LLM-based).
    - `cli_extension.py`: CLI command registration.
- **Dependencies**: `networkx`, `chromadb`, `ollama` (already in env, verify versions).
- **Data**: Persistence via `data/memory_graph.json` and ChromaDB collections.

## 4. Verification Plan
**Automated Tests**:
- [ ] Unit Tests: `pytest tests/test_memory.py` covering graph ops and vector wrapper mocking.

**Manual Verification**:
- [ ] Run `nebulus memory status` to verify graph loading.
- [ ] Store a fact via code/script and verify it appears in the graph.
- [ ] Run `nebulus memory consolidate` and verify "Fact Sheet" generation.

## 5. Workflow Checklist
- [ ] **Branch**: Created `feat/hybrid-ltm`?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
