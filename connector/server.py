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
from contextlib import AsyncExitStack
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


LOOPBACK_NAMES = ("127.0.0.1", "localhost", "[::1]")
_WILDCARD_BINDS = ("", "0.0.0.0", "::")  # nosec B104 - recognised only to refuse implicit trust


def _bracket(host: str) -> str:
    return f"[{host}]" if ":" in host and not host.startswith("[") else host


def _check_entry(value: str, kind: str) -> str:
    """Accept only exact entries, or a trailing ':*' port wildcard; never a name wildcard."""
    entry = value.strip()
    if not entry or any(c.isspace() for c in entry):
        raise ValueError(f"empty or malformed allowed {kind}: {value!r}")
    if entry.count("*") > (1 if entry.endswith(":*") else 0):
        raise ValueError(f"wildcards are not accepted in allowed {kind} {value!r} (only a trailing ':*' port)")
    if kind == "host" and ("://" in entry or "/" in entry):
        raise ValueError(f"allowed host {value!r} must be a bare Host header value (host[:port])")
    if kind == "origin" and not (entry.startswith(("http://", "https://")) and "/" not in entry.split("://", 1)[1]):
        raise ValueError(f"allowed origin {value!r} must look like http(s)://host[:port]")
    return entry


def build_transport_security(
    host: str = "127.0.0.1",
    port: int | None = None,
    allowed_hosts: tuple[str, ...] | list[str] = (),
    allowed_origins: tuple[str, ...] | list[str] = (),
):
    """DNS-rebinding settings for the SSE transport (SDK ``TransportSecuritySettings``).

    Host: loopback names on the exact listen port, plus a concrete (non-wildcard) bind
    address, plus operator-supplied entries. Origin: absent is accepted by the SDK;
    otherwise only loopback web origins (any port) and operator-supplied origins.
    Wildcard binds such as 0.0.0.0 add nothing: remote names must be allowed explicitly.
    """
    from mcp.server.transport_security import TransportSecuritySettings

    suffix = f":{port}" if port else ":*"
    hosts = [f"{name}{suffix}" for name in LOOPBACK_NAMES]
    bound = _bracket(host.strip())
    if bound not in _WILDCARD_BINDS and bound not in LOOPBACK_NAMES:
        hosts.append(f"{bound}{suffix}")
    hosts += [_check_entry(h, "host") for h in allowed_hosts]
    origins = [f"http://{name}:*" for name in LOOPBACK_NAMES]
    origins += [_check_entry(o, "origin") for o in allowed_origins]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=list(dict.fromkeys(hosts)),
        allowed_origins=list(dict.fromkeys(origins)),
    )


def build_sse_app(server: Server, security_settings=None):
    """Build the legacy SSE endpoint as ASGI, preserving the public /sse URL.

    The SDK validates Host/Origin on both the SSE connection and message POSTs.
    Without explicit settings the loopback-only profile applies (any port).
    """
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route

    transport = SseServerTransport("/messages/", security_settings or build_transport_security())

    class SseEndpoint:
        async def __call__(self, scope, receive, send):
            async with AsyncExitStack() as stack:
                try:
                    streams = await stack.enter_async_context(transport.connect_sse(scope, receive, send))
                except ValueError:
                    # connect_sse has already sent the 421/403 for a Host/Origin it refuses and then
                    # raises; swallowing it here keeps hostile requests from becoming ASGI tracebacks.
                    return
                await server.run(streams[0], streams[1], server.create_initialization_options())

    # An ASGI callable instance prevents Route from wrapping this as a
    # one-argument request handler. The transport owns the response lifecycle.
    return Starlette(routes=[
        Route("/sse", endpoint=SseEndpoint(), methods=["GET"]),
        Mount("/messages", app=transport.handle_post_message),
    ])


async def run_sse(
    server: Server,
    port: int,
    host: str = "127.0.0.1",
    allowed_hosts: tuple[str, ...] = (),
    allowed_origins: tuple[str, ...] = (),
) -> None:
    """Run the MCP server over the existing SSE transport."""
    try:
        import uvicorn
        app = build_sse_app(server, build_transport_security(host, port, allowed_hosts, allowed_origins))
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
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        metavar="HOST[:PORT]",
        help="Additional exact Host header value accepted by SSE (repeatable; 'host:*' = any port; "
        "no other wildcards). Required for remote names behind a gateway.",
    )
    parser.add_argument(
        "--allowed-origin",
        action="append",
        default=[],
        metavar="ORIGIN",
        help="Additional browser Origin accepted by SSE, e.g. https://app.example.com (repeatable).",
    )
    args = parser.parse_args()
    if args.transport != "sse" and (args.allowed_host or args.allowed_origin):
        parser.error("--allowed-host/--allowed-origin apply only to --transport sse")
    try:
        build_transport_security(args.host, args.port, args.allowed_host, args.allowed_origin)
    except ValueError as error:
        parser.error(str(error))

    # Validate required environment before starting
    validate_environment()

    server = build_server()

    if args.transport == "sse":
        asyncio.run(run_sse(server, args.port, args.host, tuple(args.allowed_host), tuple(args.allowed_origin)))
    else:
        asyncio.run(run_stdio(server))


if __name__ == "__main__":
    main()
