"""
Tests for connector/transport/bridge.py — CloudbankBridge HTTP client.

Covers:
  - Authorization header injection when token is set
  - Absence of Authorization header when no token
  - Content-Type and Accept headers always present
  - BridgeError raised on HTTP 4xx/5xx responses
  - BridgeError raised when the server is unreachable
  - Base URL trailing-slash normalisation
"""

import pytest
import httpx

try:
    import respx
    RESPX_AVAILABLE = True
except ImportError:
    RESPX_AVAILABLE = False

from connector.transport.bridge import CloudbankBridge, BridgeError

pytestmark = pytest.mark.skipif(
    not RESPX_AVAILABLE, reason="respx not installed — pip install respx"
)


# ---------------------------------------------------------------------------
# Header construction (unit — no HTTP)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_headers_include_content_type_and_accept(monkeypatch):
    """_headers must always include Content-Type and Accept."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    bridge = CloudbankBridge()
    headers = bridge._headers
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


@pytest.mark.unit
def test_headers_include_bearer_when_token_set(monkeypatch):
    """_headers must include Authorization: Bearer <token> when token is present."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "my-secret-token")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    bridge = CloudbankBridge()
    headers = bridge._headers
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer my-secret-token"


@pytest.mark.unit
def test_headers_omit_authorization_when_no_token(monkeypatch):
    """_headers must NOT include Authorization when AURORA_CONNECTOR_TOKEN is absent."""
    monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    bridge = CloudbankBridge()
    headers = bridge._headers
    assert "Authorization" not in headers


@pytest.mark.unit
def test_base_url_trailing_slash_stripped(monkeypatch):
    """Trailing slashes in AURORA_API_BASE_URL must be stripped."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000/")
    bridge = CloudbankBridge()
    assert not bridge.base_url.endswith("/")


@pytest.mark.unit
def test_base_url_default_when_not_set(monkeypatch):
    """base_url must default to http://localhost:8000 when env var is absent."""
    monkeypatch.delenv("AURORA_API_BASE_URL", raising=False)
    monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
    bridge = CloudbankBridge()
    assert bridge.base_url == "http://localhost:8000"


# ---------------------------------------------------------------------------
# GET — happy path and error handling (requires respx)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_returns_parsed_json(monkeypatch):
    """bridge.get() must return the parsed JSON body on 200."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok-get")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        respx.get("http://aurora-test.local/state").mock(
            return_value=httpx.Response(200, json={"vector_state": "QEM-ACTIVE"})
        )
        bridge = CloudbankBridge()
        result = await bridge.get("/state")

    assert result["vector_state"] == "QEM-ACTIVE"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_raises_bridge_error_on_404(monkeypatch):
    """bridge.get() must raise BridgeError on HTTP 404."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        respx.get("http://aurora-test.local/missing").mock(
            return_value=httpx.Response(404, text="not found")
        )
        bridge = CloudbankBridge()
        with pytest.raises(BridgeError):
            await bridge.get("/missing")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_raises_bridge_error_on_500(monkeypatch):
    """bridge.get() must raise BridgeError on HTTP 500."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        respx.get("http://aurora-test.local/state").mock(
            return_value=httpx.Response(500, text="internal error")
        )
        bridge = CloudbankBridge()
        with pytest.raises(BridgeError):
            await bridge.get("/state")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_raises_bridge_error_on_connection_failure(monkeypatch):
    """bridge.get() must raise BridgeError when the server is unreachable."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        respx.get("http://aurora-test.local/state").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        bridge = CloudbankBridge()
        with pytest.raises(BridgeError):
            await bridge.get("/state")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_includes_auth_header_in_request(monkeypatch):
    """bridge.get() must send the Authorization header to the upstream API."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "super-secret")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        route = respx.get("http://aurora-test.local/state").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        bridge = CloudbankBridge()
        await bridge.get("/state")

    sent_request = route.calls.last.request
    assert sent_request.headers["Authorization"] == "Bearer super-secret"


# ---------------------------------------------------------------------------
# POST — happy path and error handling
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_post_returns_parsed_json(monkeypatch):
    """bridge.post() must return the parsed JSON body on 200."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok-post")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        respx.post("http://aurora-test.local/memory/node").mock(
            return_value=httpx.Response(200, json={"id": "node-001", "status": "created"})
        )
        bridge = CloudbankBridge()
        result = await bridge.post("/memory/node", payload={"content": "test"})

    assert result["id"] == "node-001"
    assert result["status"] == "created"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_post_raises_bridge_error_on_422(monkeypatch):
    """bridge.post() must raise BridgeError on HTTP 422 (unprocessable entity)."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        respx.post("http://aurora-test.local/bad-endpoint").mock(
            return_value=httpx.Response(422, text="unprocessable")
        )
        bridge = CloudbankBridge()
        with pytest.raises(BridgeError):
            await bridge.post("/bad-endpoint", payload={})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_post_sends_empty_body_when_payload_is_none(monkeypatch):
    """bridge.post() must send an empty JSON object when payload is None."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "tok")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://aurora-test.local")

    with respx.mock:
        route = respx.post("http://aurora-test.local/ping").mock(
            return_value=httpx.Response(200, json={"pong": True})
        )
        bridge = CloudbankBridge()
        await bridge.post("/ping", payload=None)

    sent_request = route.calls.last.request
    import json
    body = json.loads(sent_request.content)
    assert body == {}
