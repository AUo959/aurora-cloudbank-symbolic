"""Temporary branch-only patch helper for issue #1345 diagnostics."""

from pathlib import Path


api_path = Path("api/aurora_api.py")
api_text = api_path.read_text(encoding="utf-8")

duplicate_import = '''# Import Memory Retrieval API router
try:
    from modules.memory_retrieval.router import router as memory_retrieval_router
    MEMORY_RETRIEVAL_AVAILABLE = True
    MEMORY_RETRIEVAL_ROUTER = memory_retrieval_router
except ImportError:
    logging.getLogger("aurora_api").warning("Memory Retrieval not available - memory retrieval features disabled")
    MEMORY_RETRIEVAL_AVAILABLE = False
    MEMORY_RETRIEVAL_ROUTER = None

'''
assert api_text.count(duplicate_import) == 1, "unexpected duplicate import block count"
api_text = api_text.replace(duplicate_import, "", 1)

mount_block = '''# Include Memory Retrieval API routes if available
if MEMORY_RETRIEVAL_AVAILABLE and MEMORY_RETRIEVAL_ROUTER:
    try:
        app.include_router(MEMORY_RETRIEVAL_ROUTER)
        logger.info("Memory Retrieval API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Memory Retrieval API routes: %s", e)
        MEMORY_RETRIEVAL_AVAILABLE = False

'''
assert api_text.count(mount_block) == 2, "unexpected memory retrieval mount block count"
first = api_text.find(mount_block)
second = api_text.find(mount_block, first + len(mount_block))
assert second != -1, "second memory retrieval mount block not found"
api_text = api_text[:second] + api_text[second + len(mount_block):]

optional_before = '''        "aumemmanager": AUMEMMANAGER_AVAILABLE,
        "data_guardian": DATA_GUARDIAN_AVAILABLE,'''
optional_after = '''        "aumemmanager": AUMEMMANAGER_AVAILABLE,
        "memory_retrieval": MEMORY_RETRIEVAL_AVAILABLE,
        "data_guardian": DATA_GUARDIAN_AVAILABLE,'''
assert api_text.count(optional_before) == 1, "startup optional-module block changed unexpectedly"
api_text = api_text.replace(optional_before, optional_after, 1)

assert "modules.memory_retrieval.router" not in api_text
assert api_text.count("app.include_router(MEMORY_RETRIEVAL_ROUTER)") == 1
api_path.write_text(api_text, encoding="utf-8")

inventory_path = Path("docs/api/api_surface_inventory.json")
inventory_text = inventory_path.read_text(encoding="utf-8")
inventory_text = inventory_text.replace(
    '"last_reviewed": "2026-07-16"',
    '"last_reviewed": "2026-07-26"',
    1,
)
evidence_start = inventory_text.index(
    '"api/aurora_api.py includes it twice, both gated behind MEMORY_RETRIEVAL_AVAILABLE'
)
evidence_end = inventory_text.index("\n", evidence_start)
replacement = (
    '"api/aurora_api.py imports modules.memory_retrieval.api and includes '
    'the router once when MEMORY_RETRIEVAL_AVAILABLE is true.",'
)
inventory_text = (
    inventory_text[:evidence_start]
    + replacement
    + inventory_text[evidence_end:]
)
inventory_path.write_text(inventory_text, encoding="utf-8")

test_path = Path("tests/test_memory_retrieval_app_registration.py")
test_path.write_text(
    '''"""Runtime registration guards for the Memory Retrieval API (issue #1345)."""

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


def _route_method_counts() -> Counter:
    counts = Counter()
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        if path:
            counts.update((path, method) for method in methods)
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
''',
    encoding="utf-8",
)
