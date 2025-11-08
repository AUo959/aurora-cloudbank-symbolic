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

import pytest  # noqa: E402 - import must happen after env setup


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Placeholder for additional test environment setup if needed."""
    yield
