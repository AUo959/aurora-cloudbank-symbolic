# Runtime Path Drift Ledger

**Status:** Current repo evidence review
**Last reviewed:** 2026-06-09
**Purpose:** Track stale, conflicting, legacy, test-only, and unverified runtime
or operator entrypoint claims.

This ledger is a documentation control surface. It does not move files, rename
entrypoints, or change runtime behavior.

## Classification

| Classification | Meaning |
| --- | --- |
| canonical | Current owner path or operating reference confirmed by committed repo evidence. |
| active | Current runtime path included or launched by committed repo surfaces. |
| active-optional | Current runtime path included through guarded optional import. |
| standalone | Current service or helper that runs separately from the main FastAPI app. |
| legacy | Older path or command that may remain in archived docs, scripts, or compatibility notes. |
| stale | Claim contradicted by current committed runtime evidence. |
| test-only | Path is mounted or exercised only by tests in current evidence. |
| unverified | Mention exists, but current production or operator mount was not verified in this review. |

## Ledger

| Claim or path | Classification | Current evidence | Canonical replacement or action |
| --- | --- | --- | --- |
| `aurora_api.py` at repo root | stale | `find . -maxdepth 2 -name aurora_api.py` finds only `api/aurora_api.py`. Multiple archived docs still mention the root path. | Use `api/aurora_api.py`, `python api/aurora_api.py`, or `uvicorn api.aurora_api:app`. |
| `api/aurora_api.py` | canonical, active | Defines the primary FastAPI app and includes module routers. | Keep as the main HTTP aggregation point. |
| `docs/reports/SYSTEM_RETROSPECTIVE_REPORT.md` statements that `hr_system`, monitoring dashboard, resilience sentinel, and GUMAS API are not integrated | stale | Current `api/aurora_api.py` includes `modules.hr_system.api.hr_routes`, `src.monitoring.dashboard_api`, `modules.resilience_sentinel.api`, and `modules.gumas.api`. | Treat the retrospective as historical. Current topology is in `docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md`. |
| `/quantum/*` as the quantum simulator mount | legacy/stale for current router | `modules/quantum_simulator/api.py` declares `APIRouter(prefix="/simulate")`. Some older docs describe `/quantum/*`. | Use `/simulate/*` for current Quantum Simulator API unless a migration explicitly reintroduces `/quantum`. |
| `src/api/mesh_api.js` as production mesh authority | test-only, unverified production mount | The Express router is mounted in `tests/node/mesh_api_activation.test.js`. No current production server mount was found in this review. | Use `src/servers/l2_integration_server.py` and `src/mesh/runtime.py` for canonical mesh runtime endpoints. |
| `src/servers/l2_integration_server.py` | canonical, standalone | Defines `create_app()` with `/api/mesh/*`, `/api/bridge/*`, `/ws/mesh`, `/chamber`, and dashboard routes; covered by `tests/test_mesh_router_v1.py`. | Keep as Mesh Runtime V1 entrypoint. |
| `skills/mesh-router/references/runtime-contract.md` `/api/mesh/agents` routes | unverified contract drift | The contract lists `/api/mesh/agents`, `/api/mesh/agents/{id}`, and `/api/mesh/agents/{id}/activate`; current `src/servers/l2_integration_server.py#create_app()` evidence does not show those mesh-agent routes. | Keep the implemented surface documented in `RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md`; add or verify the missing routes in a runtime issue before treating them as active. |
| `src/bridge/enhanced_api_bridge.js` as route authority | superseded, test-covered | Defines bridge handlers and is tested by node tests. Current canonical route surface is the Python mesh runtime. | Treat as compatibility bridge until a deployment surface mounts it explicitly. |
| `src/bridge/api_bridge_server.js` | standalone | Instantiated by station initialization scripts and tested by `tests/node/api_bridge_server.test.js`. | Document as standalone helper, not a FastAPI route. |
| `modules/hr/rd_api.py` and `modules/hr_system/api/hr_routes.py` relationship | canonical split | R&D productization is mounted at `/rd`; HR staffing and character generation is mounted at `/hr_system`. | Keep both inventory records; do not collapse them into one owner. |
| `docs/api/API_CATALOG.json` and `docs/api/api_schema.json` | generated snapshot | Snapshot was generated in 2025 and may not reflect current router additions. | Use `docs/api/api_surface_inventory.json` for governance ownership, and regenerate catalog snapshots when route details must be current. |
| `scripts/generate_api_catalog.py` output location | unverified workflow drift | Script writes `api_schema.json`, `API_CATALOG.json`, and `API_CATALOG.md` to the current working directory. Existing tracked snapshots live under `docs/api/`. | Run from `docs/api` or update the generator in a separate issue before treating output paths as canonical. |
| `docs/LAYER_BOUNDARY_REFERENCE.md` references to `aurora_api.py` without `api/` | legacy wording inside canonical boundary doc | The layer definitions remain canonical, but the entrypoint spelling reflects older path language. | Interpret the API component as `api/aurora_api.py` until the boundary doc is updated. |
| `package.json` `start` script pointing to `aurora_api_server.py` | resolved | Updated in issue #759. `npm start` and `npm run dev` now invoke `uvicorn api.aurora_api:app`. Old command retained as `npm run start:legacy`. | `npm start` → `uvicorn api.aurora_api:app --host 0.0.0.0 --port 8000` |
| `scripts/deployment/start_aurora.sh` requiring `aurora_api_server.py`, `aurora_master_integration.py`, etc. | resolved | Rewritten in issue #759 to use `uvicorn api.aurora_api:app`. All root-level file prerequisites removed. Three modes: foreground, background, dev-reload. | `scripts/deployment/start_aurora.sh` → canonical uvicorn launch |
| `scripts/deployment/stop_aurora.sh` `pkill -f aurora_api_server.py` | resolved | Updated in issue #759 to `pkill -f "api.aurora_api:app"`. | `stop_aurora.sh` now targets canonical process pattern |
| `Makefile` `run` target launching loom restore script | active (intentional) | `make run` is a dedicated reflective_autonomy utility, not the main API. New `make serve` and `make serve-dev` targets added as canonical API start commands. | Use `make serve` to start the API; `make run` is a separate tool target. |

## Maintenance Rule

When adding or modifying a runtime entrypoint, update:

1. `docs/api/api_surface_inventory.json`
2. `docs/api/API_CATALOG_GOVERNANCE.md`
3. This ledger if an older path or status changes

Do not delete stale references from archived reports just to make search output
clean. Mark the authoritative replacement instead.
