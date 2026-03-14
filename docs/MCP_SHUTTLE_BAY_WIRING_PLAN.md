# MCP Shuttle Bay Wiring Plan

## Current State

- The legacy MCP surface in `aurora_gui_cloudhub_fastapi.py` is a metadata endpoint plus a string router.
- Aurora's reusable tool, session, and execution logic already lives in `src/integrations/chatgpt_agent_mode.py`.
- The new shuttle-bay surface in `aurora_api.py` now wraps that existing runtime instead of duplicating command logic.

## What Is Wired Now

- `POST /mcp` exposes a minimal JSON-RPC MCP surface for `initialize`, `ping`, `tools/list`, `tools/call`, `resources/list`, and `resources/read`.
- `GET /mcp` exposes a human-readable endpoint summary for local inspection.
- `GET /mcp/shuttle-bay` returns a structured manifest with transport, legacy-route mapping, bridge metadata, and the tool catalog.
- `GET /mcp/shuttle-bay/tools` exposes the JSON-safe Aurora tool registry.
- `POST /mcp/shuttle-bay/execute` routes structured tool calls into the existing agent runtime.
- `POST /mcp/shuttle-bay/session` reuses the existing session lifecycle.
- `GET /mcp/shuttle-bay/status` combines runtime status with bridge metadata.

## Security Model

- Loopback clients work without extra friction for local development.
- Remote clients must send `Authorization: Bearer <AURORA_AGENT_CONTROL_TOKEN>`.
- Browser origins are explicit and local by default.
- The legacy `/mcp_bridge` routes remain available, but they are marked as legacy in responses and point callers at the shuttle-bay paths.

## Recommended Next Build Steps

1. Treat `/mcp/shuttle-bay/*` as the canonical Aurora integration surface and stop extending `/mcp_bridge/route_command`.
2. Add a transport adapter if a true remote MCP client must connect over `stdio`, SSE, or streaming HTTP; keep the current `/mcp` JSON-RPC layer as the protocol core.
3. Move any future Aurora tools into `chatgpt_agent_mode.py` first, then expose them automatically through shuttle-bay discovery.
4. Decide whether the legacy GUI MCP bridge should be retired or kept as a compatibility shim once downstream callers migrate.
