"""
Tests for connector/transport/bridge.py — fail-closed auth, identifying headers,
configurable timeout, retries with backoff, and sanitized error messages.

Covers issues #823 (sanitize BridgeError), #824 (fail-closed, retries, timeout),
and #826 (User-Agent / X-Source-Client headers).
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bridge(monkeypatch, token="test-token", base_url="http://localhost:8000", **extra_env):
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", token)
    monkeypatch.setenv("AURORA_API_BASE_URL", base_url)
    for k, v in extra_env.items():
        monkeypatch.setenv(k, v)
    # Re-import so env changes take effect on module-level reads inside __init__
    import importlib
    import connector.transport.bridge as mod
    importlib.reload(mod)
    return mod.CloudbankBridge(), mod.BridgeError


# ---------------------------------------------------------------------------
# Fail-closed auth (#824)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_missing_token_raises(monkeypatch):
    """Bridge must fail closed when AURORA_CONNECTOR_TOKEN is not set."""
    monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    import importlib
    import connector.transport.bridge as mod
    importlib.reload(mod)
    with pytest.raises(RuntimeError, match="AURORA_CONNECTOR_TOKEN is required"):
        mod.CloudbankBridge()


@pytest.mark.unit
def test_empty_token_raises(monkeypatch):
    """Empty string token should also fail closed."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    import importlib
    import connector.transport.bridge as mod
    importlib.reload(mod)
    with pytest.raises(RuntimeError):
        mod.CloudbankBridge()


# ---------------------------------------------------------------------------
# Identifying headers (#826)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_headers_include_user_agent(monkeypatch):
    """Bridge headers must include User-Agent, X-Source-Client, X-Connector-Version."""
    bridge, _ = _make_bridge(monkeypatch)
    headers = bridge._headers
    assert "User-Agent" in headers
    assert headers["User-Agent"].startswith("aurora-mcp-connector/")
    assert headers["X-Source-Client"] == "aurora-mcp-connector"
    assert "X-Connector-Version" in headers


@pytest.mark.unit
def test_authorization_header_present(monkeypatch):
    """Authorization header must be present when token is configured."""
    bridge, _ = _make_bridge(monkeypatch, token="my-secret-token")
    assert bridge._headers["Authorization"] == "Bearer my-secret-token"


# ---------------------------------------------------------------------------
# Configurable timeout (#824)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_configurable_timeout(monkeypatch):
    """Bridge timeout should be configurable via AURORA_CONNECTOR_TIMEOUT_SECONDS."""
    bridge, _ = _make_bridge(monkeypatch, AURORA_CONNECTOR_TIMEOUT_SECONDS="5")
    assert bridge._timeout == 5.0


@pytest.mark.unit
def test_default_timeout(monkeypatch):
    """Default timeout should be 10 seconds when env var not set."""
    monkeypatch.delenv("AURORA_CONNECTOR_TIMEOUT_SECONDS", raising=False)
    bridge, _ = _make_bridge(monkeypatch)
    assert bridge._timeout == 10.0


# ---------------------------------------------------------------------------
# Sanitized error messages (#823)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_bridge_error_omits_response_body(monkeypatch):
    """BridgeError for 4xx GET must not include upstream response body text."""
    bridge, BridgeError = _make_bridge(monkeypatch)

    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "secret-internal-detail-should-not-appear-in-error"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=mock_response
    )

    async def _mock_get(*args, **kwargs):
        return mock_response

    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        with pytest.raises(BridgeError) as exc_info:
            asyncio.run(bridge.get("/test"))

    assert "secret-internal-detail" not in str(exc_info.value)
    assert "400" in str(exc_info.value)


@pytest.mark.unit
def test_post_bridge_error_omits_response_body(monkeypatch):
    """BridgeError for POST must not include upstream response body text."""
    bridge, BridgeError = _make_bridge(monkeypatch)

    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.text = "confidential-error-detail-must-not-leak"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=mock_response
    )

    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        with pytest.raises(BridgeError) as exc_info:
            asyncio.run(bridge.post("/test"))

    assert "confidential-error-detail" not in str(exc_info.value)
    assert "503" in str(exc_info.value)
