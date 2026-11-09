"""Public SDK v2 sessions preserve tool discovery and dispatch contracts."""
import json
from importlib.metadata import version
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from connector.server import build_server
from connector.tools import TOOL_REGISTRY


@pytest.mark.unit
def test_mcp_v2_handler_registration_contract():
    assert version('mcp').split('.', maxsplit=1)[0] == '2'
    server = build_server()
    assert server.get_request_handler('tools/list') is not None
    assert server.get_request_handler('tools/call') is not None


@pytest.mark.unit
async def test_list_tools_preserves_v1_wire_schemas(mcp_client):
    async with mcp_client as client:
        result = await client.list_tools()
        baseline = json.loads((Path(__file__).parent / 'fixtures/tool_schemas_v1.json').read_text())
        assert [tool.model_dump(by_alias=True, exclude_none=True) for tool in result.tools] == baseline
        assert len(result.tools) == len(TOOL_REGISTRY) == 5


@pytest.mark.unit
async def test_known_tool_dispatched(mcp_client):
    async with mcp_client as client:
        payload = json.dumps({'status': 'ok'})
        with patch.object(TOOL_REGISTRY['aurora_get_state'], 'run', new=AsyncMock(return_value=payload)) as run:
            result = await client.call_tool('aurora_get_state', {})
        assert not result.is_error
        assert result.content[0].text == payload
        run.assert_awaited_once_with({})


@pytest.mark.unit
async def test_unknown_tool_returns_error(mcp_client):
    async with mcp_client as client:
        result = await client.call_tool('nonexistent_tool_xyz', {})
        assert result.is_error
        assert "ERROR: Unknown tool 'nonexistent_tool_xyz'." in result.content[0].text
