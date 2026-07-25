"""Shared fixtures and guards for the MCP connector test package.

Several tests here construct a live ``CloudbankBridge``, which fails closed
without ``AURORA_CONNECTOR_TOKEN`` (see #824) and then issues real HTTP
requests to ``AURORA_API_BASE_URL``. They are integration tests despite
carrying ``@pytest.mark.unit``.

Rather than let them fail on every developer machine — and leak partially
initialised connector state into unrelated tests that run after them — they
are skipped unless the connector environment is actually configured.

To run them:

    export AURORA_CONNECTOR_TOKEN=<token>
    export AURORA_API_BASE_URL=http://localhost:8000   # optional, this is the default
    make serve-dev                                     # in another terminal
    pytest tests/connector
"""

import os

import pytest

# Modules whose tests reach a live bridge. Everything else in this package
# (seal HMAC, schema validation of declared inputs, server dispatch and error
# mapping) is genuinely offline and always runs.
_REQUIRES_LIVE_BRIDGE = {
    "test_tools.py",
    "test_bridge_headers.py",
    "test_transport.py",
    "test_schema_validation.py",
}

_SKIP_REASON = (
    "connector integration tests need AURORA_CONNECTOR_TOKEN and a running "
    "Aurora API; see tests/connector/conftest.py"
)


def _connector_env_configured() -> bool:
    return bool(os.getenv("AURORA_CONNECTOR_TOKEN"))


def pytest_collection_modifyitems(config, items):
    """Skip live-bridge tests unless the connector environment is configured."""
    if _connector_env_configured():
        return

    skip_marker = pytest.mark.skip(reason=_SKIP_REASON)
    for item in items:
        if item.path.name in _REQUIRES_LIVE_BRIDGE:
            item.add_marker(skip_marker)
