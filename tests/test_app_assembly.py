"""
App assembly tests for Aurora CloudBank Symbolic (fixes #793).

Covers:
- Route inventory: assert a representative set of known route prefixes is present.
- Middleware registration: assert SlowAPIMiddleware is in the middleware stack.
- Lifespan startup: assert the app starts without crashing and that app.state.limiter is set.
"""

import os
import pytest

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-app-assembly")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-app-assembly")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-app-assembly-tests-12345678")

from tests._slowapi_stub import install_slowapi_stub  # noqa: E402

install_slowapi_stub()

from fastapi.testclient import TestClient  # noqa: E402
from api.aurora_api import app  # noqa: E402


# ---------------------------------------------------------------------------
# Module-level constant: representative path prefixes that MUST exist.
#
# Each entry is matched against the registered routes using a prefix check,
# so parameterised paths (e.g. /api/crew/{id}) are captured by /api/crew.
# The set covers the core routers that are unconditionally registered; it
# intentionally omits optional routers that gracefully degrade when their
# backing module is absent (e.g. /simulate, /memory, /sentinel).
# ---------------------------------------------------------------------------
EXPECTED_ROUTE_PREFIXES = {
    # Core in-process routes defined directly on the app
    "/health",
    "/api/health",
    "/agent/execute",
    "/agent/status",
    "/agent/tools",
    # Crew router (unconditionally registered alongside r2-telemetry)
    "/api/crew",
    # Always-available routers
    "/api/synergy",
    "/api/drift",
    "/api/coordination",
    "/api/fleet",
    "/api/l2-agents",
    "/r2-telemetry",
    # Thread-bridge endpoints
    "/api/thread-bridge",
    # Core module routers that load reliably
    "/data",
    "/ledger",
    "/gumas",
    "/collab",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_route_paths(application) -> set:
    """Return the set of all paths registered on the application."""
    paths = set()
    for route in application.routes:
        path = getattr(route, "path", None)
        if path:
            paths.add(path)
    return paths


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_route_inventory():
    """Assert that all expected route prefixes (or exact paths) are present.

    A prefix match is used so that parameterised routes (e.g. /api/crew/{id})
    still satisfy a prefix like /api/crew.  The test fails if any expected
    prefix has no matching route, catching accidental router removals.
    """
    route_paths = _collect_route_paths(app)

    missing = []
    for prefix in EXPECTED_ROUTE_PREFIXES:
        matched = any(
            path == prefix
            or path.startswith(prefix + "/")
            or path.startswith(prefix + "{")
            for path in route_paths
        )
        if not matched:
            missing.append(prefix)

    assert not missing, (
        f"The following expected route prefixes are not registered in the app: {missing}.\n"
        f"Registered paths (sample): {sorted(route_paths)[:40]}"
    )


@pytest.mark.unit
def test_middleware_registered():
    """Assert that SlowAPIMiddleware is present in the app's middleware stack."""
    middleware_repr = str(app.user_middleware)
    # Check by class name so the test works whether the real package or the
    # test stub's _SlowAPIMiddleware is active.
    assert "SlowAPIMiddleware" in middleware_repr, (
        f"SlowAPIMiddleware not found in app.user_middleware: {middleware_repr}"
    )


@pytest.mark.integration
def test_lifespan_startup_no_crash():
    """Assert that the app starts up without raising an exception.

    Uses TestClient as a context manager which drives the lifespan (startup +
    shutdown).  Also verifies that app.state.limiter is populated by the
    startup sequence.
    """
    with TestClient(app) as client:
        response = client.get("/health")
        # /health should return 200 (or at minimum not 5xx from a startup crash)
        assert response.status_code < 500, (
            f"Unexpected server error during lifespan startup: {response.status_code}"
        )

    # After the context manager the lifespan has completed; limiter must be set.
    assert hasattr(app.state, "limiter"), (
        "app.state.limiter was not set during startup — SlowAPI initialisation may have failed."
    )
    assert app.state.limiter is not None, "app.state.limiter is None after startup"
