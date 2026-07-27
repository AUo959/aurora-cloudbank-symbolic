"""Tests for the authenticated Memory Retrieval REST API router."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.memory_retrieval.api import _scoped_context_id, router
from src.middleware.fastapi_security import generate_csrf_token
from src.security.oauth2 import OAuth2Handler

TEST_USER = "memory-api-test-user"
TEST_CONTEXT = "ctx-1"


def _auth_headers(*, csrf: bool = False) -> dict[str, str]:
    access_token = OAuth2Handler.create_access_token(
        {"sub": TEST_USER, "role": "relay_operator"}
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    if csrf:
        headers["X-CSRF-Token"] = generate_csrf_token("memory-api-test-session")
    return headers


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
        {
            "id": "mem-abc-123",
            "score": 0.95,
            "content": "hello world",
            "metadata": {
                "_aurora_owner": TEST_USER,
                "_aurora_context_id": TEST_CONTEXT,
            },
        }
    ]
    core.get_memory.return_value = {
        "id": "mem-abc-123",
        "content": "hello world",
        "context_id": _scoped_context_id(TEST_USER, TEST_CONTEXT),
        "metadata": {
            "_aurora_owner": TEST_USER,
            "_aurora_context_id": TEST_CONTEXT,
        },
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
            json={
                "context_id": TEST_CONTEXT,
                "content": "hello world",
                "metadata": {"tag": "test"},
            },
            headers=_auth_headers(csrf=True),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["memory_id"] == "mem-abc-123"
    assert data["status"] == "ok"
    mock_core.add_memory.assert_called_once_with(
        _scoped_context_id(TEST_USER, TEST_CONTEXT),
        "hello world",
        {
            "tag": "test",
            "_aurora_owner": TEST_USER,
            "_aurora_context_id": TEST_CONTEXT,
        },
    )


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
            json={"context_id": TEST_CONTEXT, "content": "hello world"},
            headers=_auth_headers(csrf=True),
        )
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/memory-retrieval/retrieve
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_retrieve_memories_success(client, mock_core):
    """Retrieve returns memories list and count within the authenticated scope."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.post(
            "/api/memory-retrieval/retrieve",
            json={"context_id": TEST_CONTEXT, "query": "hello", "top_k": 5},
            headers=_auth_headers(),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["memories"][0]["id"] == "mem-abc-123"
    assert "_aurora_owner" not in data["memories"][0]["metadata"]
    mock_core.retrieve_memories.assert_called_once_with(
        _scoped_context_id(TEST_USER, TEST_CONTEXT),
        "hello",
        top_k=5,
        user_id=TEST_USER,
    )


# ---------------------------------------------------------------------------
# GET /api/memory-retrieval/memories/{memory_id}
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_get_memory_found(client, mock_core):
    """An owned memory_id returns 200 with the public memory dict."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.get(
            "/api/memory-retrieval/memories/mem-abc-123",
            headers=_auth_headers(),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mem-abc-123"
    assert data["context_id"] == TEST_CONTEXT
    assert "_aurora_owner" not in data["metadata"]


@pytest.mark.unit
@pytest.mark.api
def test_get_memory_not_found(client, mock_core):
    """An unknown memory_id returns 404."""
    mock_core.get_memory.return_value = None
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.get(
            "/api/memory-retrieval/memories/nonexistent",
            headers=_auth_headers(),
        )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/memory-retrieval/memories/{memory_id}
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_delete_memory_success(client, mock_core):
    """Deleting an owned memory returns 200 with status=deleted."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.delete(
            "/api/memory-retrieval/memories/mem-abc-123",
            headers=_auth_headers(csrf=True),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    assert data["memory_id"] == "mem-abc-123"


@pytest.mark.unit
@pytest.mark.api
def test_delete_memory_not_found(client, mock_core):
    """Deleting a non-existent memory returns 404."""
    mock_core.get_memory.return_value = None
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.delete(
            "/api/memory-retrieval/memories/nonexistent",
            headers=_auth_headers(csrf=True),
        )
    assert response.status_code == 404
    mock_core.delete_memory.assert_not_called()


# ---------------------------------------------------------------------------
# GET /api/memory-retrieval/cache-stats
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_get_cache_stats(client, mock_core):
    """Cache-stats endpoint returns 200 with stats for an authenticated user."""
    with patch(
        "modules.memory_retrieval.core.MemoryRetrievalCore.get_instance",
        return_value=mock_core,
    ):
        response = client.get(
            "/api/memory-retrieval/cache-stats",
            headers=_auth_headers(),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["hits"] == 5
    assert data["misses"] == 2
    assert data["size"] == 7
