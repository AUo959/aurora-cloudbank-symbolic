# `src/` — Runtime and Cross-Cutting Infrastructure

`src/` contains Aurora runtime services, orchestration, bridges, interfaces, and shared infrastructure. Feature-oriented capabilities generally live in `modules/`; the FastAPI composition root is `api/aurora_api.py`. Directory names alone do not establish canonical status—imports, scripts, tests, and manifests must be checked before consolidation. The complete 43-directory ownership contract is recorded in [`AUDIT.md`](AUDIT.md).

## Layer-oriented map

| Location | Current role | Layer relationship |
| --- | --- | --- |
| `aurora/` | Aurora runtime, including narrative engines and HALO/PAS continuity | L1 |
| `aurora_orchestrator/` | Triplex Handshake orchestration | L1 coordinating L3 validation and L1 consent |
| `entities/` | Crew, relay, and system-entity definitions | L1 |
| `agents/` | Agent runtime helpers | L1 / cross-cutting |
| `bridges/` | Python L1 relay bridge plus TypeScript constellation bridges | L1 and cross-system |
| `aurora_fusion/` | Simulation-fusion and memory support | L2-facing |
| `src/api/` | Reusable API routers, including the L1 relay surface; distinct from the root composition entry point | Cross-cutting |
| `core/` | DLP, command, service, and other shared foundations | Cross-cutting |
| `middleware/` | CSRF, authentication, rate limiting, PII, and request controls | Cross-cutting |
| `monitoring/`, `observability/` | Runtime checks, audit logging, telemetry, and traces | Cross-cutting |
| `synergy/`, `coordination/`, `orchestrators/` | Component registry and coordination services | Cross-cutting |
| `interfaces/`, `interface/`, `dashboard/` | Operator-facing web surfaces | L1-facing |

This is an orientation map; [`AUDIT.md`](AUDIT.md) is the complete classification audit required by issue #1255. In particular, `web_infrastructure/` remains `unknown` because its start commands are commented out and no live consumer was proven.

## Polyglot boundary

- **Python** implements the FastAPI runtime, simulation and governance services, continuity, relay APIs, and most tests.
- **TypeScript/JavaScript** implements the constellation server (`src/index.ts`), service/orchestrator components, Node bridges, visualization experiments, and browser/operator assets.
- `src/index.ts` is the compiled constellation REST/WebSocket composition entry point. `src/constellation/start.ts` is the operational CLI entry point and imports the compiled `index.js`. Both are separate from the Python FastAPI entry point `api/aurora_api.py`.
- The scenario-outcome oracle is owned by `modules/quantum_decision_oracle/`; `src/quantum_decision_oracle.py` preserves the established import path.
- The code-generation framework is owned by `modules/code_generation/`; `src/code_generation_framework.py` preserves the established import path.

## Duplicate-looking families are independent implementations

| Family | Observed distinction |
| --- | --- |
| `bridge/` / `bridges/` | `bridge/` contains Node API-bridge servers used by Node tests and scripts; `bridges/` contains the Python relay bridge and TypeScript constellation bridges. |
| `collab/` / `collaboration/` | `collab/` is an active Python capsule/API package; `collaboration/` contains a distinct JavaScript collaborative-research framework whose current owner is unknown. |
| `interface/` / `interfaces/` | `interface/` contains dynamic-adapter code and a holographic UI; `interfaces/` contains the collaboration chamber consumed by launch scripts and mesh tests. |
| `visual/` / `visualization/` | The directories contain different JavaScript implementations: visual synthesis and 3D quantum visualization. Neither currently has a proven consumer, so both remain `unknown`. |

The #1255 import-graph audit found no alias relationship in any family. Do not stub, deprecate, move, or delete one member based only on singular/plural naming. Any deletion still requires separate approval.

## Where to start

1. Read [`../ARCHITECTURE_QUICKMAP.md`](../ARCHITECTURE_QUICKMAP.md).
2. Confirm terminology in [`../docs/architecture/LAYER_ARCHITECTURE.md`](../docs/architecture/LAYER_ARCHITECTURE.md).
3. Read [`AUDIT.md`](AUDIT.md) before adding, renaming, or consolidating a top-level directory.
4. Follow imports from `api/aurora_api.py` for Python runtime ownership.
5. Check `package.json`, `tsconfig*.json`, scripts, and Node tests for TypeScript/JavaScript ownership.
6. Run focused tests for the surface you change; do not infer inactivity from a missing `__init__.py` in polyglot directories.
