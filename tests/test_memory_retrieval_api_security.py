"""Security and isolation coverage for the Memory Retrieval HTTP router."""

import os
from copy import deepcopy
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-memory-api")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-memory-api-12345678")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-memory-api")
os.environ.setdefault("RATE_LIMIT_ENABLED", "true")

from slowapi import _rate_limit_exceeded_handler  # noqa: E402
from slowapi.errors import RateLimitExceeded  # noqa: E402
from slowapi.middleware import SlowAPIMiddleware  # noqa: E402

from modules.memory_retrieval.api import router  # noqa: E402
from modules.memory_retrieval.core import MemoryRetrievalCore  # noqa: E402
from src.middleware.fastapi_security import (  # noqa: E402
    generate_csrf_token,
    limiter,
)
from src.security.oauth2 import OAuth2Handler  # noqa: E402
from tests._slowapi_stub import assert_real_slowapi_loaded  # noqa: E402


class FakeMemoryCore:
    """Small deterministic store used to exercise API authorization boundaries."""

    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}
        self._counter = 0

    def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
        self._counter += 1
        memory_id = f"memory-{self._counter}"
        self.records[memory_id] = {
            "id": memory_id,
            "context_id": context_id,
            "content": content,
            "metadata": deepcopy(metadata),
        }
        return memory_id

    def retrieve_memories(
        self,
        context_id: str,
        query: str,
        top_k: int = 10,
        *,
        user_id: str = "default",
        max_tokens: int | None = None,
    ) -> list[dict]:
        del query, user_id, max_tokens
        matches = [
            deepcopy(memory)
            for memory in self.records.values()
            if memory["context_id"] == context_id
        ]
        return matches[:top_k]

    def get_memory(self, memory_id: str) -> dict | None:
        memory = self.records.get(memory_id)
        return deepcopy(memory) if memory is not None else None

    def delete_memory(self, memory_id: str) -> bool:
        return self.records.pop(memory_id, None) is not None

    def get_cache_stats(self) -> dict:
        return {"entries": len(self.records)}


def _headers(username: str, *, csrf: bool = False) -> dict[str, str]:
    access_token = OAuth2Handler.create_access_token(
        {"sub": username, "role": "operator"}
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    if csrf:
        headers["X-CSRF-Token"] = generate_csrf_token(f"{username}-session")
    return headers


@pytest.fixture
def fake_core(monkeypatch) -> FakeMemoryCore:
    core = FakeMemoryCore()
    monkeypatch.setattr(
        MemoryRetrievalCore,
        "get_instance",
        classmethod(lambda cls: core),
    )
    return core


@pytest.fixture
def client(fake_core) -> TestClient:
    del fake_core
    assert_real_slowapi_loaded()
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/api/memory-retrieval/memories", {"context_id": "ctx", "content": "x"}),
        ("post", "/api/memory-retrieval/retrieve", {"context_id": "ctx", "query": "x"}),
        ("get", "/api/memory-retrieval/memories/memory-1", None),
        ("delete", "/api/memory-retrieval/memories/memory-1", None),
        ("get", "/api/memory-retrieval/cache-stats", None),
    ],
)
def test_all_memory_routes_require_authentication(
    client: TestClient,
    method: str,
    path: str,
    payload: dict | None,
) -> None:
    response = getattr(client, method)(path, json=payload)
    assert response.status_code in (401, 403)


@pytest.mark.unit
def test_memory_writes_require_both_jwt_and_csrf(
    client: TestClient,
    fake_core: FakeMemoryCore,
) -> None:
    payload = {"context_id": "ctx", "content": "blocked"}

    no_csrf = client.post(
        "/api/memory-retrieval/memories",
        json=payload,
        headers=_headers("alice"),
    )
    csrf_only = client.post(
        "/api/memory-retrieval/memories",
        json=payload,
        headers={"X-CSRF-Token": generate_csrf_token("csrf-only")},
    )

    assert no_csrf.status_code == 403
    assert csrf_only.status_code in (401, 403)
    assert fake_core.records == {}


@pytest.mark.unit
def test_authenticated_contexts_and_memory_ids_are_tenant_scoped(
    client: TestClient,
    fake_core: FakeMemoryCore,
) -> None:
    alice_headers = _headers("alice", csrf=True)
    bob_headers = _headers("bob", csrf=True)

    alice_add = client.post(
        "/api/memory-retrieval/memories",
        json={"context_id": "shared", "content": "alice memory"},
        headers=alice_headers,
    )
    bob_add = client.post(
        "/api/memory-retrieval/memories",
        json={"context_id": "shared", "content": "bob memory"},
        headers=bob_headers,
    )
    assert alice_add.status_code == 200
    assert bob_add.status_code == 200

    alice_id = alice_add.json()["memory_id"]
    bob_id = bob_add.json()["memory_id"]
    internal_contexts = {
        fake_core.records[alice_id]["context_id"],
        fake_core.records[bob_id]["context_id"],
    }
    assert len(internal_contexts) == 2
    assert "shared" not in internal_contexts

    alice_retrieve = client.post(
        "/api/memory-retrieval/retrieve",
        json={"context_id": "shared", "query": "memory", "user_id": "bob"},
        headers=_headers("alice"),
    )
    bob_retrieve = client.post(
        "/api/memory-retrieval/retrieve",
        json={"context_id": "shared", "query": "memory", "user_id": "alice"},
        headers=_headers("bob"),
    )
    assert [item["content"] for item in alice_retrieve.json()["memories"]] == [
        "alice memory"
    ]
    assert [item["content"] for item in bob_retrieve.json()["memories"]] == [
        "bob memory"
    ]

    alice_get = client.get(
        f"/api/memory-retrieval/memories/{alice_id}",
        headers=_headers("alice"),
    )
    cross_user_get = client.get(
        f"/api/memory-retrieval/memories/{alice_id}",
        headers=_headers("bob"),
    )
    cross_user_delete = client.delete(
        f"/api/memory-retrieval/memories/{alice_id}",
        headers=bob_headers,
    )

    assert alice_get.status_code == 200
    assert alice_get.json()["context_id"] == "shared"
    assert "_aurora_owner" not in alice_get.json()["metadata"]
    assert cross_user_get.status_code == 404
    assert cross_user_delete.status_code == 404
    assert alice_id in fake_core.records


@pytest.mark.unit
def test_unowned_legacy_records_fail_closed(
    client: TestClient,
    fake_core: FakeMemoryCore,
) -> None:
    fake_core.records["legacy"] = {
        "id": "legacy",
        "context_id": "legacy-context",
        "content": "legacy memory",
        "metadata": {},
    }

    get_response = client.get(
        "/api/memory-retrieval/memories/legacy",
        headers=_headers("alice"),
    )
    delete_response = client.delete(
        "/api/memory-retrieval/memories/legacy",
        headers=_headers("alice", csrf=True),
    )

    assert get_response.status_code == 404
    assert delete_response.status_code == 404
    assert "legacy" in fake_core.records


@pytest.mark.unit
def test_memory_cache_stats_are_rate_limited(client: TestClient) -> None:
    headers = _headers("rate-limit-user")
    responses = [
        client.get("/api/memory-retrieval/cache-stats", headers=headers)
        for _ in range(61)
    ]

    assert all(response.status_code == 200 for response in responses[:60])
    assert responses[60].status_code == 429
