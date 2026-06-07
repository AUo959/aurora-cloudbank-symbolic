"""Tests for the Memory Retrieval REST API router."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.memory_retrieval.api import router


@pytest.fixture()
def app():
    """Minimal FastAPI app with the memory retrieval router mounted."""
    _app = FastAPI()
    _app.include_router(router)
    return _app


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def mock_core():
    """Return a mock MemoryRetrievalCore instance."""
    core = MagicMock()
    core.add_memory.return_value = "mem-abc-123"
    core.retrieve_memories.return_value = [
        {"id": "mem-abc-123", "score": 0.95, "content": "hello world", "metadata": {}}
    ]
    core.get_memory.return_value = {
        "id": "mem-abc-123",
        "content": "hello world",
        "context_id": "ctx-1",
        "metadata": {},
    }
    core.delete_memory.return_value = True
    core.get_cache_stats.return_value = {"hits": 5, "misses": 2, "size": 7}
    return core


# ---------------------------------------------------------------------------
# POST /api/memory-retrieval/memories
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_add_memory_success(client, mock_core):
    """Adding a memory returns 200 with a memory_id."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.post(
            "/api/memory-retrieval/memories",
            json={"context_id": "ctx-1", "content": "hello world", "metadata": {"tag": "test"}},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["memory_id"] == "mem-abc-123"
    assert data["status"] == "ok"
    mock_core.add_memory.assert_called_once_with("ctx-1", "hello world", {"tag": "test"})


@pytest.mark.unit
@pytest.mark.api
def test_add_memory_server_error(client, mock_core):
    """A core exception is surfaced as a 500."""
    mock_core.add_memory.side_effect = RuntimeError("store failure")
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.post(
            "/api/memory-retrieval/memories",
            json={"context_id": "ctx-1", "content": "hello world"},
        )
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/memory-retrieval/retrieve
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_retrieve_memories_success(client, mock_core):
    """Retrieve returns memories list and count."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.post(
            "/api/memory-retrieval/retrieve",
            json={"context_id": "ctx-1", "query": "hello", "top_k": 5},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["memories"][0]["id"] == "mem-abc-123"
    mock_core.retrieve_memories.assert_called_once_with("ctx-1", "hello", top_k=5, user_id="default")


# ---------------------------------------------------------------------------
# GET /api/memory-retrieval/memories/{memory_id}
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_get_memory_found(client, mock_core):
    """A known memory_id returns 200 with the memory dict."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.get("/api/memory-retrieval/memories/mem-abc-123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mem-abc-123"


@pytest.mark.unit
@pytest.mark.api
def test_get_memory_not_found(client, mock_core):
    """An unknown memory_id returns 404."""
    mock_core.get_memory.return_value = None
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.get("/api/memory-retrieval/memories/nonexistent")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/memory-retrieval/memories/{memory_id}
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_delete_memory_success(client, mock_core):
    """Deleting an existing memory returns 200 with status=deleted."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.delete("/api/memory-retrieval/memories/mem-abc-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    assert data["memory_id"] == "mem-abc-123"


@pytest.mark.unit
@pytest.mark.api
def test_delete_memory_not_found(client, mock_core):
    """Deleting a non-existent memory returns 404."""
    mock_core.delete_memory.return_value = False
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.delete("/api/memory-retrieval/memories/nonexistent")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/memory-retrieval/cache-stats
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_get_cache_stats(client, mock_core):
    """Cache-stats endpoint returns 200 with stats dict."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.get("/api/memory-retrieval/cache-stats")
    assert response.status_code == 200
    data = response.json()
    assert data["hits"] == 5
    assert data["misses"] == 2
    assert data["size"] == 7
