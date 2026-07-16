# `src/` — Runtime and Cross-Cutting Infrastructure

`src/` contains Aurora runtime services, orchestration, bridges, interfaces, and shared infrastructure. Feature-oriented capabilities generally live in `modules/`; the FastAPI composition root is `api/aurora_api.py`. Directory names alone do not establish canonical status—imports, scripts, tests, and manifests must be checked before consolidation.

## Layer-oriented map

| Location | Current role | Layer relationship |
|---|---|---|
| `aurora/` | Aurora runtime, including narrative engines and HALO/PAS continuity | L1 |
| `aurora_orchestrator/` | Triplex Handshake orchestration | L1 coordinating L3 validation and L1 consent |
| `entities/` | Crew, relay, and system-entity definitions | L1 |
| `agents/` | Agent runtime helpers | L1 / cross-cutting |
| `bridges/` | Python L1 relay bridge plus TypeScript constellation bridges | L1 and cross-system |
| `aurora_fusion/` | Simulation-fusion and memory support | L2-facing |
| `api/` | Reusable API routers, including the L1 relay surface | Cross-cutting |
| `core/` | DLP, command, service, and other shared foundations | Cross-cutting |
| `middleware/` | CSRF, authentication, rate limiting, PII, and request controls | Cross-cutting |
| `monitoring/`, `observability/` | Runtime checks, audit logging, telemetry, and traces | Cross-cutting |
| `synergy/`, `coordination/`, `orchestrators/` | Component registry and coordination services | Cross-cutting |
| `interfaces/`, `dashboard/`, `web_infrastructure/` | Operator-facing web surfaces and support | L1-facing |

This is an orientation map, not the complete classification audit required by issue #1255.

## Polyglot boundary

- **Python** implements the FastAPI runtime, simulation and governance services, continuity, relay APIs, and most tests.
- **TypeScript/JavaScript** implements the constellation server (`src/index.ts`), service/orchestrator components, Node bridges, visualization experiments, and browser/operator assets.
- `src/index.ts` is a constellation REST/WebSocket server entry point. It is separate from the Python FastAPI entry point `api/aurora_api.py`; `package.json` exposes the constellation build/start commands.
- Root-level `quantum_decision_oracle.py` and `code_generation_framework.py` remain in place pending the import and ownership audit in #1255.

## Duplicate-looking families are not yet aliases

| Family | Observed distinction |
|---|---|
| `bridge/` / `bridges/` | `bridge/` contains Node API-bridge servers used by Node tests and scripts; `bridges/` contains the Python relay bridge and TypeScript constellation bridges. |
| `collab/` / `collaboration/` | `collab/` is an imported Python capsule/API package; `collaboration/` contains a JavaScript collaborative-research framework. |
| `interface/` / `interfaces/` | `interface/` contains dynamic-adapter code and a holographic UI; `interfaces/` contains the collaboration chamber consumed by launch scripts and mesh tests. |
| `visual/` / `visualization/` | The directories contain different JavaScript implementations: visual synthesis and 3D quantum visualization. |

Do not stub, deprecate, move, or delete one member of these families based only on singular/plural naming. Issue #1255 requires a live import-graph audit, compatibility decisions, and separate approval before deletion.

## Where to start

1. Read [`../ARCHITECTURE_QUICKMAP.md`](../ARCHITECTURE_QUICKMAP.md).
2. Confirm terminology in [`../docs/architecture/LAYER_ARCHITECTURE.md`](../docs/architecture/LAYER_ARCHITECTURE.md).
3. Follow imports from `api/aurora_api.py` for Python runtime ownership.
4. Check `package.json`, `tsconfig*.json`, scripts, and Node tests for TypeScript/JavaScript ownership.
5. Run focused tests for the surface you change; do not infer inactivity from a missing `__init__.py` in polyglot directories.
