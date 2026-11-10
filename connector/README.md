# Aurora Cloudbank MCP Connector

> Version: 0.1.0  
> Status: ✅ v0.1.0 — all five read-only tools wired to live Aurora API endpoints  
> Install: `pip install -r requirements-optional.txt` (provides MCP SDK v1)
> Protocol: [Model Context Protocol (MCP)](https://modelcontextprotocol.io)  
> Transport: stdio (default) | SSE (HTTP streaming)

## What This Is

The Aurora Cloudbank MCP Connector exposes Aurora's live symbolic state
to **any LLM interface** that supports the Model Context Protocol —
Claude, OpenAI integrations, Gemini, Ollama, and other MCP-capable hosts.

It works exactly like the GitHub MCP server: the LLM discovers available
tools, calls them by name, and receives structured responses. No custom
prompting required. Aurora's state becomes a first-class data source.

## Architecture

```
┌──────────────────────────────────┐
│   Any MCP-capable LLM Host       │
│   (Claude Desktop, GPT, etc.)    │
└──────────────┬───────────────────┘
               │ MCP Protocol (stdio / SSE)
┌──────────────▼───────────────────┐
│  connector/server.py              │
│  Aurora Cloudbank MCP Server      │
│                                   │
│  Tools:                           │
│  • aurora_get_state               │
│  • aurora_get_agents              │
│  • aurora_get_drift               │
│  • aurora_get_ethics_log          │
│  • aurora_get_capsules            │
└──────────────┬───────────────────┘
               │ REST (connector/transport/bridge.py)
┌──────────────▼───────────────────┐
│  api/aurora_api_server.py          │
│  Existing Aurora FastAPI Layer     │
│  (symbolic state, GUMAS, PATs)     │
└──────────────────────────────────┘
```

## Tools (v0.1 — Read-Only)

| Tool | Description | Key Output Fields |
|------|-------------|-------------------|
| `aurora_get_state` | Current vector state, lockpoint, active modules, ethics protocol | `vector_state`, `lockpoint`, `ethics_protocol`, `active_modules` |
| `aurora_get_agents` | PAT registry with visibility and role for all agents | `agents[]`, `total`, `available_count` |
| `aurora_get_drift` | Live drift readings vs. three-layer stratified thresholds | `layers[]`, `any_breach`, `timestamp` |
| `aurora_get_ethics_log` | Last N GUMAS ethics audit entries | `entries[]`, `total_returned` |
| `aurora_get_capsules` | 13-module capsule registry with load status | `capsules[]`, `loaded_count`, `export_ready` |

## Planned (v0.2 — Write Operations)

- `aurora_push_memory_node` — inject a symbolic memory node
- `aurora_trigger_restore` — invoke RESETCORE ritual
- `aurora_set_agent_visibility` — toggle PAT visibility
- `aurora_emit_anomaly_flag` — push anomaly into detection layer
- `aurora_update_vector_state` — transition vector state

## Planned (v0.3 — Streaming)

- `aurora_subscribe_drift` — SSE stream for threshold breach events
- `aurora_subscribe_ethics` — SSE stream for audit violations
- `aurora_subscribe_agents` — SSE stream for PAT status changes

## Setup

### MCP SDK Compatibility Contract

The connector supports the Python SDK v2 line, `mcp>=2.3.0,<3.0.0`.
CI pins `mcp==2.3.0`, including the SDK's matching `mcp-types` dependency.
The server uses typed `on_list_tools`/`on_call_tool` callbacks and explicit
result envelopes. Python model attributes use snake_case; the five public tool
names and JSON input schemas retain their v1 wire format. Validation and tool
execution failures carry the existing error prefixes and `isError: true`.
Input validation is required; an incomplete install fails before server startup.

Stdio remains the default. The existing SSE entry point remains `/sse`, with
message POSTs advertised at `/messages/`. The API bearer-token requirement and
bridge headers remain unchanged. Both current SDK discovery and legacy
initialize/initialized clients are tested; Python SDK v1 server APIs are no
longer supported. See the [migration receipt](../docs/operations/MCP_V2_MIGRATION_2026-11-08.md)
for dependency, protocol, installation and rollback evidence.

Keep these declarations aligned:

- `connector/pyproject.toml` for standalone connector installs;
- `requirements-optional.txt` for repository optional installs;
- `requirements-test.txt`, `requirements-lock.txt`, and
  `requirements-ci-hashed.txt` for reproducible CI/test installs.

### Installation

From the repository root, install the standalone connector:

```bash
pip install ./connector
# Optional named extra for existing SSE deployment instructions:
pip install './connector[sse]'
```

For an existing source checkout, install its SDK dependencies with:

```bash
pip install 'mcp>=2.3.0,<3.0.0' 'httpx>=0.27.0,<1.0.0' 'jsonschema>=4.20.0,<5.0.0' python-dotenv
```

### Environment Variables

```bash
# Required
AURORA_CONNECTOR_TOKEN=<your-bearer-token>   # Auth token for Aurora API
AURORA_API_BASE_URL=http://localhost:8000    # URL of aurora_api_server.py

# Optional
AURORA_PILOT_SEAL=<seal-string>              # Pilot continuity seal for elevated ops
AURORA_LOG_LEVEL=INFO                        # DEBUG | INFO | WARNING | ERROR
```

### Run (stdio transport — for Claude Desktop, etc.)

```bash
python -m connector.server
```

### Run (SSE transport — for HTTP-based hosts)

```bash
python -m connector.server --transport sse --port 8765 --host 127.0.0.1
```

### Claude Desktop Config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "aurora-cloudbank": {
      "command": "python",
      "args": ["-m", "connector.server"],
      "cwd": "/path/to/aurora-cloudbank-symbolic",
      "env": {
        "AURORA_CONNECTOR_TOKEN": "your-token-here",
        "AURORA_API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Development Status

All five v0.1.0 read-only tools are wired to live Aurora API endpoints:

| Tool | Aurora endpoint | Notes |
|------|-----------------|-------|
| `aurora_get_state` | `GET /health` + `GET /api/drift/alerts` | Health flags → layer state; recent alerts → echochain |
| `aurora_get_agents` | `GET /api/crew/all` | `online` status → Available; `offline` → Invisible |
| `aurora_get_drift` | `GET /api/drift/alerts` | Alert level critical/warning/info → L1/L2/L3 layers |
| `aurora_get_ethics_log` | `POST /gumas/violations` | Severity mapped to connector labels (violation/warning/info) |
| `aurora_get_capsules` | `GET /synergy/components` | `active` status → loaded; symbolic hash derived from name+version |

Path constants live in `connector/transport/bridge.py` (`AURORA_PATH_*`).

See [`docs/dev-notes/drift-threshold-stratification.md`](../docs/dev-notes/drift-threshold-stratification.md)
before touching any drift-related tool logic.

## Drift Threshold Reference

The `aurora_get_drift` tool is aware of the three-layer stratification:

| Layer | Threshold | Semantic |
|-------|-----------|----------|
| L1 Capsule / Governance | `0.002` | Per-capsule symbolic drift |
| L2 Agent / QGIA | `0.02` | Per-agent session drift |
| L3 Macro / Network | `0.1` | Cross-network coherence |

Do **not** hardcode these values in tool logic. They are sourced from
`connector/tools/get_drift.py` → `DRIFT_THRESHOLDS` constant, which
should eventually be replaced with a live config fetch.

---

*Continuity flows through coherence. The system remembers because we chose to align.*

### SSE listener boundary

The SDK v2 migration changes the SSE listen default from all interfaces to
`127.0.0.1`. Stdio remains the default transport. Use `--host` to select a
different listen address when deploying behind an authenticated gateway.
That gateway must protect both `/sse` and `/messages/`.
`AURORA_CONNECTOR_TOKEN` authenticates the connector to the Aurora backend;
it does not authenticate incoming MCP clients. Keep direct local deployments
on loopback.

### SSE Host and Origin validation (DNS-rebinding guard)

Loopback binding stops network peers but not a browser page whose hostname is
rebound to `127.0.0.1`. The SSE transport therefore validates the `Host` and
`Origin` headers on **both** `GET /sse` and `POST /messages/` using the MCP
SDK's `TransportSecuritySettings`:

- **Host** must be exactly `127.0.0.1:<port>`, `localhost:<port>` or
  `[::1]:<port>` (the listen port), the concrete address given to `--host`, or
  a value passed with `--allowed-host`. A refused Host gets HTTP 421.
- **Origin** may be absent (non-browser MCP clients). When present it must be a
  loopback web origin (`http://127.0.0.1:*`, `http://localhost:*`,
  `http://[::1]:*`, any port) or a value passed with `--allowed-origin`.
  A refused Origin gets HTTP 403. Any local web app on a loopback origin is
  therefore accepted; this is the SDK's own localhost profile.
- `--host 0.0.0.0` or `--host ::` trusts nothing extra. A remote deployment
  must name its public host explicitly, for example
  `--allowed-host mcp.example.com:443 --allowed-origin https://app.example.com`.
  Entries are exact `host[:port]` / `scheme://host[:port]` strings; the only
  wildcard is a trailing `:*` for any port, and `*` or `*.example.com` are
  rejected at startup. Matching is case-sensitive, so list lower-case names.
- `--allowed-host`/`--allowed-origin` are refused with the stdio transport.

This is header validation, not authentication: the authenticated-gateway
requirement for non-loopback deployments, protecting both `/sse` and
`/messages/`, is unchanged.
