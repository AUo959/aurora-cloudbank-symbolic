# `src/` Structure Audit

This audit records the live ownership evidence for every tracked top-level
directory under `src/` on 2026-07-16. It is a compatibility and routing
contract, not deletion authorization.

## Method and status vocabulary

The audit used the tracked-file inventory, Python imports, JavaScript/CommonJS
and TypeScript imports, `package.json` and `tsconfig*.json`, runtime/deployment
scripts, API composition, and focused tests. Archived reports, generated
manifests, commented-out start commands, and a producer that merely writes a
file do not establish a live consumer.

- **active**: a current executable import, start/build path, API composition,
  or focused test consumes the directory.
- **deprecated**: a current explicit deprecation marker or compatibility-only
  contract applies to the directory.
- **unknown**: tracked implementation exists, but no current consumer or owner
  was proven. Unknown is not deprecated and is not deletion approval.

The live inventory contains **43** top-level directories, not the 44 recorded
when issue #1255 was opened. The table contains all 43: 35 active, 0
deprecated, and 8 unknown.

## Directory inventory

The **Canonical decision** column is meaningful for the four duplicate-looking
families. `independent` means the names do not represent aliases, so neither
member may replace the other. All other rows are `n/a`.

| Directory | Status | Layer role | Implementation role | Canonical decision | Migration target / live evidence |
| --- | --- | --- | --- | --- | --- |
| `agents/` | active | L1 / cross-cutting | Agent runtimes and crew helpers | n/a | Retain; consumed by agent tests and Aurora integrations. |
| `api/` | active | cross-cutting | Reusable routers and L1 relay API | n/a | Retain; `tests/test_l1_station_api.py` exercises the relay surface. |
| `audio/` | unknown | L1-facing | Immersive audio experiment | n/a | Owner review; only generator/config history and commented start commands were found. |
| `aurora/` | active | L1 / L3 | Aurora runtime, continuity, narrative, and ethics integration | n/a | Retain; imported by API/runtime code and focused tests. |
| `aurora_fusion/` | active | L2-facing | Simulation fusion, profiles, and memory support | n/a | Retain; `tests/test_aurora_fusion_engine.py` imports it. |
| `aurora_orchestrator/` | active | L1 / L3 | Triplex and autonomous orchestration | n/a | Retain; `tests/aurora_orchestrator/` imports it. |
| `bridge/` | active | cross-cutting | Node API bridge servers | independent | Retain; Node tests and start scripts execute these servers. |
| `bridges/` | active | L1 / cross-cutting | Python L1 relay and TypeScript constellation bridges | independent | Retain; Python tests/API and `src/index.ts` consume it. |
| `collab/` | active | cross-cutting | Python collaboration capsule and API package | independent | Retain; `api/aurora_api.py` and collab tests import it. |
| `collaboration/` | unknown | L2 / cross-cutting | JavaScript collaborative-research framework | independent | Owner review; the sequential implementor writes it, but no live consumer was found. |
| `config/` | active | cross-cutting | Runtime settings and Orion configuration | n/a | Retain; `tests/test_config_settings.py` imports it. |
| `constellation/` | active | cross-cutting | Constellation CLI start and health/seal commands | n/a | Retain; `package.json` starts it and it imports `src/index.ts`. |
| `coordination/` | active | cross-cutting | Event models, registry, API, and hybrid coordination | n/a | Retain; event coordination/API tests import it. |
| `core/` | active | cross-cutting | DLP, commands, services, storage, and orchestration foundations | n/a | Retain; runtime code and `tests/core/` consume it. |
| `dashboard/` | active | L1-facing | Operator dashboard assets | n/a | Retain; `src/servers/l2_integration_server.py` serves `agent_constellation.html`. |
| `entities/` | active | L1 | Crew, relay, and fleet entity models | n/a | Retain; crew and fleet tests import them. |
| `handlers/` | unknown | L1-facing | Gesture, neural, symbolic, voice, and fusion handlers | n/a | Owner review; only generated/historical inventory references were found. |
| `improvement/` | active | L2 / cross-cutting | Improvement engine and API | n/a | Retain; `tests/test_improvement_engine.py` and API tests import it. |
| `integrations/` | active | cross-cutting | External-agent and Aurora integration adapters | n/a | Retain; API composition and integration tests consume it. |
| `interface/` | active | L1-facing | Dynamic adapters and holographic command UI | independent | Retain; the holographic orchestrator serves the UI. |
| `interfaces/` | active | L1-facing | Collaboration chamber UI | independent | Retain; the L2 server and mesh tests consume it. |
| `mesh/` | active | cross-cutting | Mesh runtime, manifests, and models | n/a | Retain; mesh runtime and PAT-terminal tests import it. |
| `middleware/` | active | cross-cutting | Request, auth, validation, PII, CSRF, and rate controls | n/a | Retain; FastAPI composition and middleware tests consume it. |
| `monitoring/` | active | L3 / cross-cutting | Drift, ethics, audit, and behavior monitoring | n/a | Retain; API/runtime code and monitoring tests import it. |
| `nodes/` | active | L1 / cross-cutting | JavaScript relay and command nodes | n/a | Retain; `tests/node/command_node.test.js` and related tests execute them. |
| `observability/` | active | cross-cutting | Telemetry, tracing, and metrics | n/a | Retain; telemetry integration tests import it. |
| `orchestrators/` | active | cross-cutting | Holographic interface orchestration | n/a | Retain; phase-7 deployment starts it and validators check it. |
| `output/` | unknown | L1-facing | Multi-modal output coordination experiment | n/a | Owner review; generator/fixer references exist, but no live consumer was found. |
| `playground/` | active | L2 / cross-cutting | Authenticated code-execution playground | n/a | Retain; `api/aurora_api.py` and playground tests import it. |
| `pqn/` | active | L2 | CommonJS prioritization and symbolic indexing | n/a | Retain; `demos/demo_entropy_fix.cjs` executes the prioritizer (path repaired in #1255). |
| `prediction/` | unknown | L2 | Predictive analytics experiment | n/a | Owner review; a generator writes it, but no live consumer was found. |
| `quantum_core/` | active | L2 | Quantum-processing and symbolic-CPU anchors | n/a | Retain; quantum-core and native-implementation tests import it. |
| `runtime/` | active | cross-cutting | Process lifecycle and shutdown coordination | n/a | Retain; `api/aurora_api.py` and shutdown tests import it. |
| `security/` | active | cross-cutting | OAuth, RBAC, and authentication routes | n/a | Retain; API composition and security tests import it. |
| `sensors/` | active | L1 / L2 | Symbolic sensor core, arrays, fusion, and salvage | n/a | Retain; `tests/sensors/` imports it. |
| `servers/` | active | cross-cutting | L2 integration and mesh runtime server | n/a | Retain; launch scripts, mesh skill contract, and server tests consume it. |
| `subroutines/` | active | L3 / cross-cutting | Ethics, alignment, registry, and system subroutines | n/a | Retain; API composition, examples, and subroutine tests import it. |
| `synergy/` | active | cross-cutting | Component registry, graph analysis, and dashboards | n/a | Retain; API composition and synergy tests import it. |
| `system/` | active | cross-cutting | JavaScript command routing and agent synchronization | n/a | Retain; command-system and Node integration tests consume it. |
| `utils/` | active | cross-cutting | Atomic I/O, logging, redaction, and shared helpers | n/a | Retain; runtime modules and utility tests import it. |
| `visual/` | unknown | L1-facing | JavaScript quantum visual synthesis experiment | independent | Owner review; a generator and directory-presence test exist, but no live consumer was found. |
| `visualization/` | unknown | L1 / L2-facing | JavaScript 3D quantum visualization experiment | independent | Owner review; a generator writes it, but no live consumer was found. |
| `web_infrastructure/` | unknown | cross-cutting | Experimental quantum-enhanced backend | n/a | Owner review; start commands are commented out and no live consumer was found. |

## Duplicate-looking family decisions

| Family | Import-graph decision | Compatibility action |
| --- | --- | --- |
| `bridge/` / `bridges/` | Both are active and implement different runtime contracts: Node API servers versus Python/TypeScript relay and constellation bridges. | Keep both; no alias, rename, deprecation, or migration. |
| `collab/` / `collaboration/` | They implement different language and API contracts. `collab/` is active; ownership of `collaboration/` is unknown. | Keep both; investigate the JavaScript owner separately. Do not route it through `collab/`. |
| `interface/` / `interfaces/` | Both are active operator surfaces with different consumers and content. | Keep both; no alias, rename, deprecation, or migration. |
| `visual/` / `visualization/` | The files implement visual synthesis and 3D visualization respectively, but neither currently has a proven consumer. | Preserve both as unknown pending owner decisions; naming similarity alone is not a consolidation basis. |

## Top-level file decisions

- `src/index.ts` is active. It is the compiled constellation REST/WebSocket
  composition entry point included by `tsconfig.constellation.json`.
  `src/constellation/start.ts` is the operational CLI entry point and imports
  the compiled `index.js`; the Python FastAPI composition root remains
  `api/aurora_api.py`.
- The scenario-outcome implementation formerly at
  `src/quantum_decision_oracle.py` is now owned by
  `modules/quantum_decision_oracle/`. The `src` path is a compatibility import.
  This implementation is distinct from the weighted-alternative engine in
  `tools/simulation_engine/quantum_decision_oracle.py`.
- The implementation formerly at `src/code_generation_framework.py` is now
  owned by `modules/code_generation/`. The `src` path is a compatibility
  import.

No compatibility import or unknown directory is approved for deletion by this
audit. Removal requires a separate PR and owner approval under issue #1255.
