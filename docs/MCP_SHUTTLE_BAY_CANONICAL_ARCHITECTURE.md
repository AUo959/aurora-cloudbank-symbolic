# MCP Shuttle Bay Canonical Architecture Note

## Purpose

This note consolidates the current Shuttle Bay material into one repo-grounded
architecture statement.

It separates three things clearly:

1. what is implemented now
2. what is supported by adjacent repo canon
3. what remains proposal-level and should not be treated as established runtime truth

## Source Basis

Primary implementation sources in this repo:

- `aurora_api.py`
- `aurora_gui_cloudhub_fastapi.py`
- `src/integrations/chatgpt_agent_mode.py`
- `src/integrations/mcp_shuttle_bay.py`
- `tests/test_mcp_shuttle_bay.py`
- `docs/MCP_SHUTTLE_BAY_CONTEXT_AUDIT.md`
- `docs/MCP_SHUTTLE_BAY_WIRING_PLAN.md`

Related local design references outside this repo:

- `Aurora_New_11_9/02_DOCUMENTATION/Technical_Proposals/AURORA_MCP_SHUTTLE_BAY_PROPOSAL_v1.0.md`
- `Aurora_New_11_9/02_DOCUMENTATION/Technical_Proposals/AURORA_MCP_SHUTTLE_BAY_TECHNICAL_SPEC_v1.0.md`

## Canonical Statement

The MCP Shuttle Bay is Aurora's controlled integration surface for tool
discovery, tool execution, session management, and MCP protocol exposure.

In current repo terms, it is best understood as:

- a stable adapter over Aurora's existing agent-mode runtime
- a protocol boundary that exposes MCP-compatible discovery and execution
- a governance-aware manifest surface that carries symbolic bridge metadata
- the preferred replacement for extending the legacy `/mcp_bridge` string router

It is not yet a full mission-controller implementation with crew assignment,
drone dispatch, or enforced shuttle-to-tool orchestration.

## Current Repo-Grounded Architecture

### 1. Protocol Surfaces

The active Shuttle Bay surface is:

- `GET /mcp/shuttle-bay`
- `GET /mcp/shuttle-bay/tools`
- `POST /mcp/shuttle-bay/execute`
- `POST /mcp/shuttle-bay/session`
- `GET /mcp/shuttle-bay/status`
- `GET /mcp`
- `POST /mcp`

`POST /mcp` currently exposes a minimal JSON-RPC MCP surface for:

- `initialize`
- `ping`
- `tools/list`
- `tools/call`
- `resources/list`
- `resources/read`

### 2. Adapter Layer

`src/integrations/mcp_shuttle_bay.py` is the canonical adapter entrypoint.

Its responsibilities are:

- build the Shuttle Bay manifest
- expose a JSON-safe tool catalog
- route structured tool calls into Aurora's agent runtime
- reuse the existing session lifecycle
- expose a minimal MCP server descriptor
- expose Shuttle Bay resources, currently centered on the manifest

Current manifest resource URI:

- `aurora://mcp-shuttle-bay/manifest`

### 3. Runtime Layer

The Shuttle Bay does not define a second execution engine.

It wraps `src/integrations/chatgpt_agent_mode.py`, which remains the source of
truth for:

- available tools
- tool schemas
- tool execution
- session lifecycle
- agent status

This keeps Shuttle Bay as an interface layer rather than a duplicate runtime.

### 4. Symbolic Metadata Layer

The adapter enriches the exposed contract with `mcp_bridge_core` metadata from
`modules.symbolic_core`.

That makes bridge identity, anchor, governance, and security information
visible without requiring callers to go through the older legacy bridge routes.

### 5. Legacy Compatibility Layer

`aurora_gui_cloudhub_fastapi.py` still exposes:

- `GET /mcp_bridge`
- `POST /mcp_bridge/route_command`

Those routes now function as compatibility shims and explicitly point callers to
the Shuttle Bay paths. They should be treated as legacy, not as the canonical
extension point.

## Security Model

The implemented security model is narrow and concrete:

- loopback clients are allowed by default for local development
- remote clients must present `Authorization: Bearer <AURORA_AGENT_CONTROL_TOKEN>`
- browser origins are explicit and local by default
- the tool registry returned by the API is JSON-safe and omits runtime handlers
- the command grammar tool validates command form, including `//.` execution
  termination, without becoming a separate execution path

This is a controlled access surface, not a public anonymous MCP endpoint.

## What Adjacent Canon Supports

The context audit supports the following higher-level interpretation:

- the Shuttle Bay should preserve bridge metadata, anchor validation, ethics
  framing, drift monitoring, and governance visibility
- the L1 bridge, L2 meta-agent, and fleet registries are valid adjacent canon
  for future Shuttle Bay resource design
- fleet, bridge, and governance matrices can be surfaced as discoverable MCP
  resources without claiming unsupported runtime bindings

This means the fleet/governance vocabulary is valid as design language, but it
must be introduced carefully as metadata and routing hints first.

## What Is Still Proposal-Level

The large Shuttle Bay proposal and technical specification describe a broader
institutional model:

- MCP missions with crew assignments
- drone pre-flight and post-flight inspection
- risk-based human authorization chains
- expanded personnel rosters
- shuttle-to-domain and shuttle-to-tool governance models

That material is useful design direction, but it is not current repo truth.

Most importantly, there is no already-canonized one-to-one mapping in this repo
from named shuttles or probes directly to specific live MCP tools.

The safe interpretation is:

- fleet and governance structures are valid context
- direct ship-to-tool bindings remain implementation decisions
- those bindings should not be presented as established canon unless they are
  added explicitly to repo data and runtime behavior

## Practical Design Rule

For this repo, the safest canonical build order is:

1. keep `/mcp/shuttle-bay/*` and `/mcp` as the stable protocol boundary
2. add new Aurora tools in `chatgpt_agent_mode.py` first
3. expose bridge, fleet, and governance data as resources before claiming deep
   mission semantics
4. retain `/mcp_bridge` only as a compatibility path during migration

## Current Source of Truth

If a future thread needs the shortest reliable answer, use this ordering:

1. `src/integrations/mcp_shuttle_bay.py`
2. `aurora_api.py`
3. `tests/test_mcp_shuttle_bay.py`
4. `docs/MCP_SHUTTLE_BAY_WIRING_PLAN.md`
5. `docs/MCP_SHUTTLE_BAY_CONTEXT_AUDIT.md`

The proposal and technical spec remain useful design references, but they should
not override implemented behavior.
