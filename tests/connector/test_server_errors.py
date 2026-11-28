"""Tool failures remain explicit and sanitized through actual MCP sessions."""
from unittest.mock import AsyncMock, patch

import pytest

from connector.tools import TOOL_REGISTRY


@pytest.mark.unit
async def test_tool_exception_does_not_include_exc_detail(mcp_client):
    async with mcp_client as client:
        secret = 'secret-internal-detail-should-not-appear'
        with patch.object(TOOL_REGISTRY['aurora_get_state'], 'run', new=AsyncMock(side_effect=RuntimeError(secret))):
            result = await client.call_tool('aurora_get_state', {})
        assert result.is_error
        assert result.content[0].text == "TOOL_EXECUTION_ERROR: tool 'aurora_get_state' failed; check server logs"
        assert secret not in result.model_dump_json()


@pytest.mark.unit
async def test_missing_bridge_credentials_fail_closed(mcp_client, monkeypatch):
    async with mcp_client as client:
        monkeypatch.delenv('AURORA_CONNECTOR_TOKEN', raising=False)
        with patch('connector.transport.bridge.httpx.AsyncClient') as http:
            result = await client.call_tool('aurora_get_state', {'include_echochain': False})
        assert result.is_error
        assert 'TOOL_EXECUTION_ERROR' in result.content[0].text
        assert 'AURORA_CONNECTOR_TOKEN' not in result.content[0].text
        http.assert_not_called()
