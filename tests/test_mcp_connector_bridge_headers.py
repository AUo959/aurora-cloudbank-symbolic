from connector import __version__
from connector.transport.bridge import CloudbankBridge


def test_bridge_headers_include_connector_identity(monkeypatch) -> None:
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token")

    headers = CloudbankBridge()._headers

    assert headers["User-Agent"] == f"aurora-mcp-connector/{__version__}"
    assert headers["X-Source-Client"] == "aurora-mcp-connector"
    assert headers["X-Connector-Version"] == __version__
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


def test_curl_equivalent_does_not_match_connector_signature(monkeypatch) -> None:
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token")

    connector_headers = CloudbankBridge()._headers
    curl_headers = {"User-Agent": "curl/8.0.0", "Accept": "*/*"}

    assert curl_headers.get("User-Agent") != connector_headers["User-Agent"]
    assert curl_headers.get("X-Source-Client") != connector_headers.get("X-Source-Client")
    assert curl_headers.get("X-Connector-Version") != connector_headers.get("X-Connector-Version")
