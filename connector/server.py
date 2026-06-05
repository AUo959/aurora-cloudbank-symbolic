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

# MCP SDK -- install via: pip install mcp
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print(
        "ERROR: MCP SDK not installed. Run: pip install mcp",
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


def build_server() -> Server:
    """Construct and configure the MCP server instance."""
    server = Server(APP_NAME)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Return schemas for all registered Aurora tools."""
        return [tool.schema() for tool in TOOL_REGISTRY.values()]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Dispatch a tool call to the appropriate handler."""
        if name not in TOOL_REGISTRY:
            return [TextContent(
                type="text",
                text=f"ERROR: Unknown tool '{name}'. "
                     f"Available: {', '.join(TOOL_REGISTRY.keys())}"
            )]

        tool = TOOL_REGISTRY[name]
        try:
            result = await tool.run(arguments)
            return [TextContent(type="text", text=result)]
        except Exception as exc:  # noqa: BLE001
            log.exception("Tool '%s' raised an exception", name)
            return [TextContent(
                type="text",
                text=f"TOOL_EXECUTION_ERROR: tool '{name}' failed; check server logs"
            )]

    return server


async def run_stdio(server: Server) -> None:
    """Run the MCP server over stdio transport."""
    log.info("Aurora Cloudbank MCP Connector v%s starting (stdio)", APP_VERSION)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


async def run_sse(server: Server, port: int) -> None:
    """Run the MCP server over SSE (HTTP streaming) transport."""
    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        import uvicorn
    except ImportError:
        log.error("SSE transport requires: pip install mcp[sse] uvicorn starlette")
        sys.exit(1)

    log.info(
        "Aurora Cloudbank MCP Connector v%s starting (SSE) on port %d",
        APP_VERSION,
        port,
    )

    sse_transport = SseServerTransport("/messages")

    async def handle_sse(scope, receive, send):
        async with sse_transport.connect_sse(scope, receive, send) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse_transport.handle_post_message),
        ]
    )

    config = uvicorn.Config(starlette_app, host="0.0.0.0", port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


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
    args = parser.parse_args()

    # Validate required environment before starting
    validate_environment()

    server = build_server()

    if args.transport == "sse":
        asyncio.run(run_sse(server, args.port))
    else:
        asyncio.run(run_stdio(server))


if __name__ == "__main__":
    main()
