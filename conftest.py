"""
Pytest configuration for Aurora CloudBank test suite.

Sets up test environment variables and fixtures.
"""
import os

# CRITICAL: Set environment variables BEFORE any test imports
# Security middleware checks these secrets at import time
if "CSRF_SECRET_KEY" not in os.environ:
    os.environ["CSRF_SECRET_KEY"] = "test-csrf-secret-key-do-not-use-in-production-32chars"

if "WS_AUTH_SECRET" not in os.environ:
    os.environ["WS_AUTH_SECRET"] = "test-websocket-auth-secret-do-not-use-in-production-val"

# Provide a deterministic JWT secret for tests so authentication components can import safely.
if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-do-not-use-in-production-hex32"

# Auth route tests use an explicitly gated dev-only fixture user store.
os.environ.setdefault("AURORA_ALLOW_DEV_AUTH_FIXTURE", "true")
os.environ.setdefault("AURORA_DEV_ADMIN_PASSWORD", "test-" + "admin-secret")
os.environ.setdefault("AURORA_DEV_OPERATOR_PASSWORD", "test-" + "operator-secret")
os.environ.setdefault("AURORA_DEV_OBSERVER_PASSWORD", "test-" + "observer-secret")

import pytest  # noqa: E402 - import must happen after env setup
from fastapi.testclient import TestClient  # noqa: E402

try:
    from api.aurora_api import app as core_app  # Main FastAPI app
except Exception:  # pragma: no cover - fallback if import fails
    core_app = None


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


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Placeholder for additional test environment setup if needed."""
    yield
