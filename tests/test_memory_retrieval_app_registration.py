"""Runtime registration guards for the Memory Retrieval API (issue #1345)."""

from collections import Counter
import os
from pathlib import Path

import pytest

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-memory-router")
os.environ.setdefault("AURORA_SECRET_KEY", "test-aurora-secret-memory-router")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-memory-router")
os.environ.setdefault(
    "JWT_SECRET_KEY", "test-jwt-secret-key-memory-router-tests-12345678"
)

from tests._slowapi_stub import install_slowapi_stub  # noqa: E402

install_slowapi_stub()

from api.aurora_api import (  # noqa: E402
    MEMORY_RETRIEVAL_AVAILABLE,
    app,
)


EXPECTED_ROUTE_METHODS = {
    ("/api/memory-retrieval/memories", "POST"),
    ("/api/memory-retrieval/retrieve", "POST"),
    ("/api/memory-retrieval/memories/{memory_id}", "GET"),
    ("/api/memory-retrieval/memories/{memory_id}", "DELETE"),
    ("/api/memory-retrieval/cache-stats", "GET"),
}


def _join_route_path(prefix: str, path: str) -> str:
    if not prefix:
        return path
    if path == "/":
        return prefix
    return f"{prefix.rstrip('/')}/{path.lstrip('/')}"


def _iter_routes(routes, prefix: str = ""):
    for route in routes:
        child_prefix = prefix
        include_context = getattr(route, "include_context", None)
        if include_context:
            child_prefix = _join_route_path(
                prefix, getattr(include_context, "prefix", "")
            )
        original_router = getattr(route, "original_router", None)
        if original_router is not None:
            yield from _iter_routes(original_router.routes, child_prefix)
        else:
            yield route, child_prefix


def _route_method_counts() -> Counter:
    counts = Counter()
    for route, prefix in _iter_routes(app.routes):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        if path:
            full_path = _join_route_path(prefix, path)
            counts.update((full_path, method) for method in methods)
    return counts


@pytest.mark.unit
def test_memory_retrieval_router_is_available_and_mounted_once() -> None:
    assert MEMORY_RETRIEVAL_AVAILABLE is True
    counts = _route_method_counts()
    unexpected = {
        route_method: counts[route_method]
        for route_method in EXPECTED_ROUTE_METHODS
        if counts[route_method] != 1
    }
    assert not unexpected, (
        "Memory Retrieval routes must each be registered exactly once: "
        f"{unexpected}"
    )


@pytest.mark.unit
def test_memory_retrieval_has_one_canonical_binding() -> None:
    source = (
        Path(__file__).resolve().parents[1] / "api" / "aurora_api.py"
    ).read_text(encoding="utf-8")
    assert "modules.memory_retrieval.router" not in source
    assert source.count(
        "from modules.memory_retrieval.api import router as memory_retrieval_router"
    ) == 1
    assert source.count("app.include_router(MEMORY_RETRIEVAL_ROUTER)") == 1
