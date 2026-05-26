# Runtime Topology and L3 Communications Authority

**Status:** Current repo evidence review
**Last reviewed:** 2026-05-26
**Scope:** CloudBank runtime and operator entrypoints in this repository

This document resolves the active runtime topology and the L3 communications
authority map from committed repo evidence. It does not claim that any service
is deployed in production unless a deployment surface in this repo proves that
mount.

## Topology Decision

The canonical HTTP application is the FastAPI app in `api/aurora_api.py`. The
repo also contains standalone and compatibility surfaces, but those must be
declared in the API surface inventory before they are treated as active service
entrypoints.

Runtime entrypoint classes:

| Class | Runtime surface | Status | Evidence |
| --- | --- | --- | --- |
| Primary application | `api/aurora_api.py` | active in repo | Defines `app = FastAPI(...)` and includes module routers. |
| Main module routers | `/memory`, `/data`, `/ledger`, `/simulate`, `/rd`, `/hr_system`, `/collab`, `/subroutines`, `/api/coordination`, `/api/fleet`, `/relay`, `/synergy`, `/api/synergy`, `/sentinel`, `/monitoring`, `/gumas`, `/api/auth`, `/r2-telemetry`, `/api/l2-agents`, `/api/drift`, `/playground` | active or active-optional in repo | Included by `api/aurora_api.py`; optional modules use guarded imports. |
| Mesh runtime V1 | `src/servers/l2_integration_server.py` with `src/mesh/runtime.py` | active standalone | Provides implemented mesh routes, bridge compatibility routes, `/ws/mesh`, `/chamber`, and root dashboard routes; covered by `tests/test_mesh_router_v1.py`. |
| JavaScript mesh router | `src/api/mesh_api.js` | inactive for production mount, test-mounted only | Defines an Express router and is mounted in `tests/node/mesh_api_activation.test.js`; no repo production server mount was found in the current review. |
| Enhanced API bridge | `src/bridge/enhanced_api_bridge.js` | superseded compatibility bridge | Defines Custom GPT bridge handlers and is covered by node tests, but current canonical mesh endpoints are provided by the Python mesh runtime surface. |
| API bridge server | `src/bridge/api_bridge_server.js` | active standalone helper | Started by station initialization scripts and covered by `tests/node/api_bridge_server.test.js`; it is not mounted into the FastAPI app. |

## Active FastAPI Router Map

`api/aurora_api.py` is the aggregation point for the primary HTTP surface. It
loads optional module routers with guarded imports so a missing optional
dependency degrades that module rather than disabling the full app.

| Owner lane | Mount path | Entrypoint | Status |
| --- | --- | --- | --- |
| AuMemManager | `/memory` | `modules/aumemmanager/api_integration.py` | active-optional |
| Data Guardian | `/data` | `modules/data_guardian/api.py` | active-optional |
| Insight Ledger | `/ledger` | `modules/insight_ledger/api.py` | active-optional |
| Quantum Simulator | `/simulate` | `modules/quantum_simulator/api.py` | active-optional |
| R&D pipeline | `/rd` | `modules/hr/rd_api.py` | active |
| HR staffing system | `/hr_system` | `modules/hr_system/api/hr_routes.py` | active |
| Cross-repo collaboration | `/collab` | `src/collab/api_routes.py` | active |
| Subroutines | `/subroutines` | `src/subroutines/api.py`, `src/subroutines/api_enhanced.py` | active |
| Event coordination | `/api/coordination` | `src/coordination/event_api.py` | active-optional |
| Fleet bridge | `/api/fleet` | `src/integrations/fleet_bridge.py` | active-optional |
| Relay manager | `/relay` | `src/aurora/relays/api_routes.py` | active-optional |
| Synergy | `/synergy`, `/api/synergy` | `src/synergy/api.py`, `src/synergy/dashboard_api.py` | active |
| Resilience sentinel | `/sentinel` | `modules/resilience_sentinel/api.py` | active |
| Monitoring dashboard | `/monitoring` | `src/monitoring/dashboard_api.py` | active |
| GUMAS ethics | `/gumas` | `modules/gumas/api/routes.py` | active |
| OAuth2/RBAC | `/api/auth` | `src/security/auth_routes.py` | active |
| R2 telemetry | `/r2-telemetry` | `api/r2_telemetry_routes.py` | active |
| L2 meta-agent bridge | `/api/l2-agents` | `src/api/l2_meta_agent_api.py` | active |
| Drift metrics | `/api/drift` | `src/observability/drift_metrics_api.py` | active |
| Playground | `/playground` | `src/playground/api.py` | active |

The API governance registry for these surfaces lives at
`docs/api/api_surface_inventory.json`.

## Mesh and Bridge Authority

The implemented Python mesh runtime V1 surface currently confirmed by
`src/servers/l2_integration_server.py` and `tests/test_mesh_router_v1.py` is:

- `GET /api/mesh/status`
- `POST /api/mesh/messages`
- `GET /api/mesh/channels/{id}/history`
- `GET /api/mesh/events?after=<cursor>`
- `POST /api/bridge/gpt/connect/{agent_id}`
- `GET /api/bridge/constellation/status`
- `GET /ws/mesh` by native WebSocket
- `GET /chamber`
- `GET /`

`skills/mesh-router/references/runtime-contract.md` lists additional
`/api/mesh/agents` routes. Those routes are an expected contract surface, but
they are not verified as implemented in `create_app()` during this review and
are therefore tracked as path drift rather than current runtime authority.

`src/api/mesh_api.js` still has value as a legacy Express router and node test
target, but it is not the production-mounted authority in the current repo
evidence. `src/bridge/enhanced_api_bridge.js` remains a compatibility bridge
for Custom GPT style handlers, but the route authority has moved to the mesh
runtime and L2 integration server.

## L3 Authority Map

`docs/LAYER_BOUNDARY_REFERENCE.md` remains the canonical layer definition:

- L1 is Orion Station physical or station-operation context.
- L2 is sandboxed simulation and meta-agent context.
- L3 is the ethics, continuity, anchor, DLP, and drift overlay spanning L1 and
  L2.

L3 does not independently authorize runtime mutation. It evaluates, blocks,
requires human consent, or records lineage. Runtime mutation still requires the
appropriate L1/L2 owner path, authentication, CSRF or route-specific mutation
guard, and any human approval required by the operation.

| L3 function | Current owner surface | Authority boundary |
| --- | --- | --- |
| Ethics evaluation | `modules/gumas/api/routes.py`, `src/monitoring/ethics_engine.py`, `src/entities/framework_agents.py` | Can evaluate and report violations; cannot bypass route auth or human-consent gates. |
| Anchor and continuity validation | `src/entities/framework_agents.py`, `src/core/native_dlp_export.py`, thread continuity modules | Can validate continuity and emit DLP lineage; cannot silently promote or execute state changes. |
| Drift detection and metrics | `src/monitoring/drift_detector.py`, `src/observability/drift_metrics_api.py`, `src/entities/relay_agents.py` | Can expose drift and trigger recommended intervention; direct corrective action remains an owning runtime concern. |
| Mesh communication | `src/servers/l2_integration_server.py`, `src/mesh/runtime.py` | Routes mesh messages through declared mesh endpoints; L3 assessment does not equal approval to send or mutate. |
| Audit trail | `src/monitoring/audit_logger.py`, `modules/insight_ledger/api.py` | Records evidence and lineage; not a deploy or execution authority. |

## Operator Rule

When docs disagree with the committed runtime, prefer the committed entrypoint,
router, test, and inventory evidence. Label older claims as stale or unverified
instead of repeating them as active topology.
