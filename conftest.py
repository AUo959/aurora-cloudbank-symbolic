"""
Pytest configuration for Aurora CloudBank test suite.

Sets up test environment variables and fixtures.

Security note: CSRF_SECRET_KEY, WS_AUTH_SECRET, and JWT_SECRET_KEY are checked
at module import time by src/middleware/fastapi_security.py. They must therefore
be present in os.environ before any test module is collected (i.e. here at the
module level, guarded so real environment values are never overwritten).
Cleanup is handled by the session-scoped ``test_env_vars`` autouse fixture below.

AURORA_ALLOW_DEV_AUTH_FIXTURE and the associated password variables are NOT set
globally. Tests that require the dev-auth fixture user store must explicitly
request the ``dev_auth_fixture_env`` fixture.
"""
import os

# ---------------------------------------------------------------------------
# Import-time guards – required so security middleware can be imported safely.
# These only write to os.environ when the variable is not already set, so real
# secrets in a CI/CD environment are never clobbered.
# ---------------------------------------------------------------------------
_TEST_ENV_DEFAULTS = {
    "CSRF_SECRET_KEY": "test-csrf-secret-key-do-not-use-in-production-32chars",
    "WS_AUTH_SECRET": "test-websocket-auth-secret-do-not-use-in-production-val",
    "JWT_SECRET_KEY": "test-jwt-secret-key-do-not-use-in-production-hex32",
}

# Track which keys were injected by this conftest so they can be cleaned up.
_INJECTED_BY_CONFTEST: set = set()

for _key, _value in _TEST_ENV_DEFAULTS.items():
    if _key not in os.environ:
        os.environ[_key] = _value
        _INJECTED_BY_CONFTEST.add(_key)

import pytest  # noqa: E402 - import must happen after env setup
from fastapi.testclient import TestClient  # noqa: E402

try:
    from api.aurora_api import app as core_app  # Main FastAPI app
except Exception:  # pragma: no cover - fallback if import fails
    core_app = None


# ---------------------------------------------------------------------------
# Session-scoped autouse fixture: owns the lifecycle of the security env vars
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def test_env_vars():
    """Ensure core security env vars are present for the test session and
    remove any values that were injected by this conftest upon teardown.

    Variables that already existed in the environment before the session
    started are left untouched at teardown.
    """
    # Values were already written at module-import time above.  Yield to let
    # the entire test session run.
    yield

    # Teardown: remove only the variables that this conftest injected.
    for key in _INJECTED_BY_CONFTEST:
        os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# Narrow, non-autouse fixture for the dev-auth fixture user store
# ---------------------------------------------------------------------------

@pytest.fixture()
def dev_auth_fixture_env(monkeypatch):
    """Activate the dev/test auth fixture user store for a single test.

    Sets AURORA_ALLOW_DEV_AUTH_FIXTURE and the three dev password variables.
    These values are automatically removed after the requesting test finishes
    thanks to monkeypatch's built-in teardown.

    Only tests that explicitly request this fixture receive the dev-auth bypass.
    """
    monkeypatch.setenv("AURORA_ALLOW_DEV_AUTH_FIXTURE", "true")
    monkeypatch.setenv("AURORA_DEV_ADMIN_PASSWORD", "test-admin-secret")
    monkeypatch.setenv("AURORA_DEV_OPERATOR_PASSWORD", "test-operator-secret")
    monkeypatch.setenv("AURORA_DEV_OBSERVER_PASSWORD", "test-observer-secret")


# ---------------------------------------------------------------------------
# General-purpose fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    """Provide a TestClient for core FastAPI app endpoints.

    Many tests expect a 'client' fixture to interact with API routes.
    If the main app cannot be imported, skip dependent tests gracefully.
    """
    if core_app is None:
        pytest.skip("Core FastAPI app unavailable for testing")
    return TestClient(core_app)


@pytest.fixture(scope="session")
def cmd():
    """Provide a simple command executor used by gitwiz functionality tests.

    Returns a callable: cmd(args: list[str]) -> (returncode:int, stdout:str, stderr:str)
    """
    import subprocess

    def _run(args, timeout=30):
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr

    return _run
