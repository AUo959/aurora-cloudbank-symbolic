"""
Tests for connector/server.py dispatch logic and tool registry.
Covers: unknown tool, known tool dispatch, exception sanitization, list_tools.
"""

import json
from importlib.metadata import version
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import TextContent

from connector.tools import TOOL_REGISTRY
from connector.server import build_server


# ---------------------------------------------------------------------------
# TOOL_REGISTRY membership tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_all_tools_registered():
    """TOOL_REGISTRY must contain every expected Aurora tool."""
    assert "aurora_get_state" in TOOL_REGISTRY
    assert "aurora_get_agents" in TOOL_REGISTRY
    assert "aurora_get_drift" in TOOL_REGISTRY
    assert "aurora_get_ethics_log" in TOOL_REGISTRY
    assert "aurora_get_capsules" in TOOL_REGISTRY


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tool_registry_length():
    """TOOL_REGISTRY must have exactly 5 registered tools."""
    assert len(TOOL_REGISTRY) == 5


# ---------------------------------------------------------------------------
# call_tool dispatch tests — exercised through the registered handler.
# build_server() decorates functions with @server.call_tool(); we extract
# the underlying handler by looking at the request_handlers mapping.
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_mcp_v1_handler_registration_contract():
    """The supported MCP v1 range must expose both connector handlers."""
    from mcp.types import CallToolRequest, ListToolsRequest

    sdk_version = version("mcp")
    assert sdk_version.split(".", maxsplit=1)[0] == "1"

    server = build_server()
    assert server.request_handlers.get(ListToolsRequest) is not None
    assert server.request_handlers.get(CallToolRequest) is not None


def _get_call_tool_handler():
    """
    Build a server instance and extract the call_tool handler so we can
    invoke it directly without starting a transport.
    """
    server = build_server()

    async def dispatch(name: str, arguments: dict) -> list[TextContent]:
        # The MCP Server stores handlers keyed by request type.
        # We find the call_tool handler and invoke it directly.
        from mcp.types import CallToolRequest, CallToolRequestParams

        req = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name=name, arguments=arguments),
        )
        # Access internal handler dict; key is the request type class.
        handler = server.request_handlers.get(CallToolRequest)
        if handler is None:
            raise RuntimeError("No call_tool handler registered on server")
        # handler returns a ServerResult; the actual CallToolResult is in .root
        server_result = await handler(req)
        return server_result.root.content

    return dispatch


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unknown_tool_returns_error():
    """Calling a non-existent tool name must return a TextContent error message."""
    dispatch = _get_call_tool_handler()
    results = await dispatch("nonexistent_tool_xyz", {})
    assert len(results) >= 1
    text = results[0].text
    # server.py returns "ERROR: Unknown tool ..." for unknown names
    assert "Unknown tool" in text or "ERROR" in text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_known_tool_dispatched():
    """A known tool whose run() is mocked must have its return value surfaced."""
    dispatch = _get_call_tool_handler()

    mock_output = json.dumps({"status": "ok"})
    with patch.object(TOOL_REGISTRY["aurora_get_state"], "run", new=AsyncMock(return_value=mock_output)):
        results = await dispatch("aurora_get_state", {})

    assert len(results) >= 1
    assert results[0].text == mock_output


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tool_exception_sanitized():
    """
    If a tool raises an exception, the error message in TextContent must
    NOT expose the verbatim internal exception message. The raw secret detail
    must not leak.
    """
    dispatch = _get_call_tool_handler()

    secret = "secret internal message"
    with patch.object(
        TOOL_REGISTRY["aurora_get_state"],
        "run",
        new=AsyncMock(side_effect=ValueError(secret)),
    ):
        results = await dispatch("aurora_get_state", {})

    assert len(results) >= 1
    text = results[0].text
    assert text == "TOOL_EXECUTION_ERROR: tool 'aurora_get_state' failed; check server logs"
    assert secret not in text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_tools_returns_all():
    """list_tools() handler must return Tool objects for all registered tools."""
    from mcp.types import ListToolsRequest

    server = build_server()
    req = ListToolsRequest(method="tools/list", params=None)
    handler = server.request_handlers.get(ListToolsRequest)
    assert handler is not None, "No list_tools handler registered on server"

    # handler returns a ServerResult; the actual ListToolsResult is in .root
    server_result = await handler(req)
    tool_names = [t.name for t in server_result.root.tools]

    assert "aurora_get_state" in tool_names
    assert "aurora_get_agents" in tool_names
    assert "aurora_get_drift" in tool_names
    assert "aurora_get_ethics_log" in tool_names
    assert "aurora_get_capsules" in tool_names
