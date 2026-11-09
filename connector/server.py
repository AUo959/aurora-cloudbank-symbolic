"""
Aurora Cloudbank MCP Server
============================
Entrypoint for the Aurora MCP connector.

Usage:
    python -m connector.server                          # stdio (default)
    python -m connector.server --transport sse          # SSE on port 8765
    python -m connector.server --transport sse --port 9000

The server registers all Aurora tools and handles the MCP lifecycle:
  - initialize / initialized handshake
  - tools/list  -> returns all registered tool schemas
  - tools/call  -> dispatches to individual tool handlers
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Any

# MCP SDK v2 uses typed constructor callbacks and explicit result envelopes.
# Keep this contract aligned with the standalone and repository requirements.
try:
    import jsonschema
    from mcp.server import Server, ServerRequestContext
    from mcp.server.stdio import stdio_server
    from mcp_types import (
        CallToolRequestParams,
        CallToolResult,
        ListToolsResult,
        PaginatedRequestParams,
        TextContent,
    )
except ImportError:
    print(
        'ERROR: MCP SDK dependencies not installed. Run: pip install "mcp>=2.3.0,<3.0.0"',
        file=sys.stderr,
    )
    sys.exit(1)

from connector.tools import TOOL_REGISTRY
from connector.auth.token import validate_environment

logging.basicConfig(
    level=os.getenv("AURORA_LOG_LEVEL", "INFO"),
    format="%(asctime)s [aurora-mcp] %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("aurora.connector")

APP_NAME = "aurora-cloudbank-connector"
APP_VERSION = "0.1.0"


def _error_result(message: str) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text=message)], is_error=True)


def _validation_error(tool: Any, arguments: dict[str, Any]) -> str | None:
    input_schema = tool.schema().input_schema
    if input_schema:
        try:
            jsonschema.validate(arguments, input_schema)
        except jsonschema.ValidationError as error:
            path = "/".join(str(part) for part in error.absolute_path)
            return f"TOOL_VALIDATION_ERROR: {error.message}" + (f" (path: {path})" if path else "")
    return None


def build_server() -> Server:
    """Construct v2 callbacks while preserving the connector's five tool contracts."""
    async def list_tools(
        _context: ServerRequestContext, _params: PaginatedRequestParams | None,
    ) -> ListToolsResult:
        return ListToolsResult(tools=[tool.schema() for tool in TOOL_REGISTRY.values()])

    async def call_tool(
        _context: ServerRequestContext, params: CallToolRequestParams,
    ) -> CallToolResult:
        name = params.name
        arguments = params.arguments or {}
        if name not in TOOL_REGISTRY:
            return _error_result(
                f"ERROR: Unknown tool '{name}'. Available: {', '.join(TOOL_REGISTRY.keys())}"
            )
        tool = TOOL_REGISTRY[name]
        message = _validation_error(tool, arguments)
        if message:
            return _error_result(message)
        try:
            result = await tool.run(arguments)
            return CallToolResult(content=[TextContent(type="text", text=result)])
        except Exception:  # noqa: BLE001
            log.exception("Tool '%s' raised an exception", name)
            return _error_result(f"TOOL_EXECUTION_ERROR: tool '{name}' failed; check server logs")

    return Server(APP_NAME, version=APP_VERSION, on_list_tools=list_tools, on_call_tool=call_tool)


async def run_stdio(server: Server) -> None:
    """Run the MCP server over stdio transport."""
    log.info("Aurora Cloudbank MCP Connector v%s starting (stdio)", APP_VERSION)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def build_sse_app(server: Server):
    """Build the legacy SSE endpoint as ASGI, preserving the public /sse URL."""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route

    transport = SseServerTransport("/messages/")

    class SseEndpoint:
        async def __call__(self, scope, receive, send):
            async with transport.connect_sse(scope, receive, send) as streams:
                await server.run(streams[0], streams[1], server.create_initialization_options())

    # An ASGI callable instance prevents Route from wrapping this as a
    # one-argument request handler. The transport owns the response lifecycle.
    return Starlette(routes=[
        Route("/sse", endpoint=SseEndpoint(), methods=["GET"]),
        Mount("/messages", app=transport.handle_post_message),
    ])


async def run_sse(server: Server, port: int, host: str = "127.0.0.1") -> None:
    """Run the MCP server over the existing SSE transport."""
    try:
        import uvicorn
        app = build_sse_app(server)
    except ImportError:
        log.error("SSE transport requires the connector's sse dependencies (uvicorn and starlette)")
        sys.exit(1)
    log.info("Aurora Cloudbank MCP Connector v%s starting (SSE) on port %d", APP_VERSION, port)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    await uvicorn.Server(config).serve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Aurora Cloudbank MCP Connector")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport layer (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for SSE transport (default: 8765)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Listen address for SSE transport (default: 127.0.0.1)",
    )
    args = parser.parse_args()

    # Validate required environment before starting
    validate_environment()

    server = build_server()

    if args.transport == "sse":
        asyncio.run(run_sse(server, args.port, args.host))
    else:
        asyncio.run(run_stdio(server))


if __name__ == "__main__":
    main()
