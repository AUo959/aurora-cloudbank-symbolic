"""
Tests for connector/transport/bridge.py — CloudbankBridge HTTP client.

Covers:
  - Authorization header injection when token is set
  - Absence of Authorization header when no token
  - Content-Type and Accept headers always present
  - BridgeError raised on HTTP 4xx/5xx responses
  - BridgeError raised when the server is unreachable
  - Base URL trailing-slash normalisation
  - User-Agent, X-Source-Client, X-Connector-Version identifying headers (Issue #826)
"""

import pytest
import httpx

try:
    import respx
    RESPX_AVAILABLE = True
except ImportError:
    RESPX_AVAILABLE = False

from unittest.mock import AsyncMock, MagicMock, patch

from connector import __version__ as _CONNECTOR_VERSION
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


# ---------------------------------------------------------------------------
# Identifying headers — Issue #826 (User-Agent, X-Source-Client, X-Connector-Version)
# ---------------------------------------------------------------------------

# Helpers for mock-based tests


def _make_ok_response(body: dict | None = None) -> MagicMock:
    """Return a mock httpx.Response that succeeds and returns JSON."""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()  # does not raise
    resp.json.return_value = body or {"status": "ok"}
    return resp


def _make_error_response(status_code: int = 500) -> MagicMock:
    """Return a mock that simulates an HTTP error status."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = "Internal Server Error"

    http_err = httpx.HTTPStatusError(
        message=f"{status_code}",
        request=MagicMock(),
        response=resp,
    )
    resp.raise_for_status.side_effect = http_err
    return resp


@pytest.mark.unit
class TestBridgeHeadersProperty:
    """Test the _headers property directly — no HTTP calls needed."""

    def test_user_agent_present(self):
        bridge = CloudbankBridge()
        assert "User-Agent" in bridge._headers

    def test_user_agent_value(self):
        bridge = CloudbankBridge()
        assert bridge._headers["User-Agent"] == f"aurora-mcp-connector/{_CONNECTOR_VERSION}"

    def test_x_source_client_present(self):
        bridge = CloudbankBridge()
        assert "X-Source-Client" in bridge._headers

    def test_x_source_client_value(self):
        bridge = CloudbankBridge()
        assert bridge._headers["X-Source-Client"] == "aurora-mcp-connector"

    def test_x_connector_version_present(self):
        bridge = CloudbankBridge()
        assert "X-Connector-Version" in bridge._headers

    def test_x_connector_version_value(self):
        bridge = CloudbankBridge()
        assert bridge._headers["X-Connector-Version"] == _CONNECTOR_VERSION

    def test_standard_headers_still_present(self):
        bridge = CloudbankBridge()
        headers = bridge._headers
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_authorization_absent_without_token(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge.__new__(CloudbankBridge)
        bridge.base_url = "http://localhost:8000"
        bridge.token = ""
        assert "Authorization" not in bridge._headers

    def test_authorization_present_with_token(self, monkeypatch):
        monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
        bridge = CloudbankBridge()
        assert bridge._headers["Authorization"] == "Bearer test-token-abc"


@pytest.mark.unit
class TestBridgeGetHeaders:
    """Verify identifying headers are sent on GET requests."""

    @pytest.mark.asyncio
    async def test_get_sends_user_agent(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_get(url, headers=None, params=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.get = AsyncMock(side_effect=fake_get)
            mock_client_cls.return_value = instance

            await bridge.get("/state")

        assert captured["headers"]["User-Agent"] == f"aurora-mcp-connector/{_CONNECTOR_VERSION}"

    @pytest.mark.asyncio
    async def test_get_sends_x_source_client(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_get(url, headers=None, params=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.get = AsyncMock(side_effect=fake_get)
            mock_client_cls.return_value = instance

            await bridge.get("/state")

        assert captured["headers"]["X-Source-Client"] == "aurora-mcp-connector"

    @pytest.mark.asyncio
    async def test_get_sends_x_connector_version(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_get(url, headers=None, params=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.get = AsyncMock(side_effect=fake_get)
            mock_client_cls.return_value = instance

            await bridge.get("/state")

        assert captured["headers"]["X-Connector-Version"] == _CONNECTOR_VERSION


@pytest.mark.unit
class TestBridgePostHeaders:
    """Verify identifying headers are sent on POST requests."""

    @pytest.mark.asyncio
    async def test_post_sends_user_agent(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_post(url, headers=None, json=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)
            mock_client_cls.return_value = instance

            await bridge.post("/memory/node", payload={"key": "value"})

        assert captured["headers"]["User-Agent"] == f"aurora-mcp-connector/{_CONNECTOR_VERSION}"

    @pytest.mark.asyncio
    async def test_post_sends_x_source_client(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_post(url, headers=None, json=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)
            mock_client_cls.return_value = instance

            await bridge.post("/memory/node", payload={"key": "value"})

        assert captured["headers"]["X-Source-Client"] == "aurora-mcp-connector"

    @pytest.mark.asyncio
    async def test_post_sends_x_connector_version(self, monkeypatch):
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_post(url, headers=None, json=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)
            mock_client_cls.return_value = instance

            await bridge.post("/memory/node", payload={"key": "value"})

        assert captured["headers"]["X-Connector-Version"] == _CONNECTOR_VERSION

    @pytest.mark.asyncio
    async def test_post_no_payload_still_sends_headers(self, monkeypatch):
        """Ensure headers are present even when no payload is given."""
        monkeypatch.delenv("AURORA_CONNECTOR_TOKEN", raising=False)
        bridge = CloudbankBridge()
        captured = {}

        async def fake_post(url, headers=None, json=None):
            captured["headers"] = headers
            return _make_ok_response()

        with patch("httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)
            mock_client_cls.return_value = instance

            await bridge.post("/anomaly/flag")

        headers = captured["headers"]
        assert headers["User-Agent"] == f"aurora-mcp-connector/{_CONNECTOR_VERSION}"
        assert headers["X-Source-Client"] == "aurora-mcp-connector"
        assert headers["X-Connector-Version"] == _CONNECTOR_VERSION
