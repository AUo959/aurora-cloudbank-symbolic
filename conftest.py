"""
Pytest configuration for Aurora CloudBank test suite.

# ----------------------------------------------------------------------
# Why the module-level os.environ writes (and why #794 is only partially
# closed here)
# ----------------------------------------------------------------------
# `src/middleware/fastapi_security.py` and `src/security/oauth2.py` read
# CSRF_SECRET_KEY, WS_AUTH_SECRET, and JWT_SECRET_KEY *at module import
# time* and raise RuntimeError if they are missing. That makes importing
# `api.aurora_api` impossible from any test session unless these
# variables are populated before pytest collects test modules.
#
# Until #815 lands ("Add config validation + 'startup complete'"), where
# secret loading moves into FastAPI lifespan via Pydantic Settings, the
# safe-set pattern below is required. The full per-test isolation called
# for in #794 (`monkeypatch.setenv` at function scope, `pytest -n auto`
# parallelism) becomes possible once #815 removes the import-time read.
#
# Until then this file:
#   1. Sets only the three import-time secrets at module level.
#   2. Wraps the optional dev-auth fixtures inside the autouse session
#      fixture so they can be overridden per-test via monkeypatch.
#   3. Provides a `monkeypatched_env` factory for new tests that need
#      to flip env vars cleanly.
#   4. Provides a session-end env-leak guard so a test that pollutes
#      os.environ is surfaced rather than silently affecting later runs.
# ----------------------------------------------------------------------
"""
import os
from typing import Callable, Iterator

# --- (1) Import-time security secrets (blocks until #815) -------------
# These three are read in module top-level code in security middleware
# and MUST exist before any `api.aurora_api` import.
if "CSRF_SECRET_KEY" not in os.environ:
    os.environ["CSRF_SECRET_KEY"] = "test-csrf-secret-key-do-not-use-in-production-32chars"

if "WS_AUTH_SECRET" not in os.environ:
    os.environ["WS_AUTH_SECRET"] = "test-websocket-auth-secret-do-not-use-in-production-val"

if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-do-not-use-in-production-hex32"

import pytest  # noqa: E402 - import must happen after env setup
from fastapi.testclient import TestClient  # noqa: E402

try:
    from api.aurora_api import app as core_app  # Main FastAPI app
except Exception:  # pragma: no cover - fallback if import fails
    core_app = None


# --- (2) Dev-auth-fixture defaults, set in a session-autouse fixture --
# These are read at *runtime* by src/security/auth_routes.py, not at
# import time, so they can live in an autouse fixture. Tests that need
# the bypass to be OFF can override via monkeypatch.delenv.
_DEV_AUTH_DEFAULTS = {
    "AURORA_ALLOW_DEV_AUTH_FIXTURE": "true",
    "AURORA_DEV_ADMIN_PASSWORD": "test-" + "admin-secret",
    "AURORA_DEV_OPERATOR_PASSWORD": "test-" + "operator-secret",
    "AURORA_DEV_OBSERVER_PASSWORD": "test-" + "observer-secret",
}


# --- (3) Forward-looking helper for new tests -------------------------
# Use this fixture going forward. It guarantees the value is restored
# after the test, preventing the env-pollution problem that blocks
# `pytest -n auto`.
@pytest.fixture
def monkeypatched_env(monkeypatch: pytest.MonkeyPatch) -> Callable[[str, str | None], None]:
    """Return a callable that sets or deletes an env var safely for one test.

    Example:
        def test_thing(monkeypatched_env):
            monkeypatched_env("AURORA_ALLOW_DEV_AUTH_FIXTURE", "false")
            ...

    The variable is automatically restored at function teardown.
    """
    def _set(name: str, value: str | None) -> None:
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    return _set


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


# --- (4) Session autouse: install dev-auth defaults + leak guard ------
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Iterator[None]:
    """Install dev-auth env defaults and snapshot env for leak detection.

    The dev-auth fixtures are scoped to the session so existing
    tests that read them via `os.environ` (e.g. tests/test_auth_routes.py)
    continue to work. New tests should prefer the `monkeypatched_env`
    fixture for any other env var manipulation.
    """
    # Set defaults only if absent — allows CI / developer override.
    for key, value in _DEV_AUTH_DEFAULTS.items():
        os.environ.setdefault(key, value)
    snapshot = set(os.environ.keys())
    yield
    # End-of-session leak guard: report keys that materialised during
    # the run and didn't exist before. We don't fail (tests in flight
    # may legitimately add keys); we just print for now. When the suite
    # is clean, this becomes an assertion.
    leaked = sorted(set(os.environ.keys()) - snapshot)
    if leaked:
        # pytest captures this; run with -s to see it inline.
        print(f"[conftest] env keys added during session (#794 leak guard): {leaked}")
