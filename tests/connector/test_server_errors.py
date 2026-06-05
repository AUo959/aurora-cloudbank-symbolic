"""
Tests for connector/server.py — sanitized error messages on tool dispatch (issue #823).
"""

import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unit
def test_tool_execution_error_code_in_source():
    """
    The server catch block must use TOOL_EXECUTION_ERROR, not raw str(exc).
    This guards against regressions that re-introduce the leaky pattern.
    """
    from connector import server as server_module
    source = inspect.getsource(server_module)

    # The stable error code must be present
    assert "TOOL_EXECUTION_ERROR" in source, \
        "connector/server.py catch block must use TOOL_EXECUTION_ERROR error code"

    # The leaky pattern must be absent
    assert 'f"ERROR executing' not in source and "f'ERROR executing" not in source, \
        "connector/server.py must not interpolate {exc} into the model-facing error message"


@pytest.mark.unit
def test_unknown_tool_response_does_not_raise():
    """Unknown-tool path returns an error TextContent, not an exception."""
    try:
        from mcp.types import CallToolRequest, CallToolRequestParams
    except ImportError:
        pytest.skip("mcp SDK not installed")

    import asyncio
    from connector.server import build_server

    server = build_server()
    handler = server.request_handlers[CallToolRequest]

    req = CallToolRequest(
        method="tools/call",
        params=CallToolRequestParams(name="__nonexistent_tool__", arguments={}),
    )
    result = asyncio.run(handler(req))

    # Should get a result with some error text, not raise
    assert result is not None
    content = result.root.content if hasattr(result, "root") else result.content
    assert len(content) >= 1
    text = content[0].text
    assert "__nonexistent_tool__" not in text or "ERROR" in text


@pytest.mark.unit
def test_tool_exception_does_not_include_exc_detail():
    """When a known tool raises, the TextContent must not include str(exc)."""
    try:
        from mcp.types import CallToolRequest, CallToolRequestParams
    except ImportError:
        pytest.skip("mcp SDK not installed")

    import asyncio

    boom = RuntimeError("secret-internal-detail-should-not-appear")

    try:
        from mcp.types import Tool as McpTool
    except ImportError:
        pytest.skip("mcp SDK not installed")

    fake_tool = MagicMock()
    fake_tool.schema.return_value = McpTool(
        name="secret_tool",
        description="Test tool",
        inputSchema={"type": "object", "properties": {}},
    )
    fake_tool.run = AsyncMock(side_effect=boom)

    registry = {"secret_tool": fake_tool}
    with patch("connector.server.TOOL_REGISTRY", registry):
        from connector.server import build_server
        server = build_server()
        handler = server.request_handlers[CallToolRequest]

        req = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="secret_tool", arguments={}),
        )
        result = asyncio.run(handler(req))

    content = result.root.content if hasattr(result, "root") else result.content
    text = content[0].text

    assert "secret-internal-detail" not in text, \
        "Exception detail must not reach the model channel"
    assert "TOOL_EXECUTION_ERROR" in text
