# Aurora — Architecture Quickmap

## What this is

Aurora CloudBank Symbolic is the code and canon repository for Aurora, the simulation director of the Orion Station institutional simulation, plus the runtime services that support ethics-governed simulation, symbolic memory, QGIA signal intake, and auditable operations. The repository has one ontological layer model—L1 station operations, L2 simulation/research environments, and L3 conceptual frameworks—and a separate three-step Triplex consent protocol. Treat those two uses of “layer” as distinct.

## Layer architecture → code map

| Reality layer | Role | Primary code and authority |
|---|---|---|
| **L1 — Physical/Operational** | Orion Station crew, Aurora Core, five relay agents, HALO continuity system-entity, and station operations | `src/aurora/`, `src/aurora_orchestrator/`, `src/entities/`, `src/agents/`, `src/bridges/`, `config/mesh/` |
| **L2 — Simulation/Research** | GUMAS and other computational experiments, scenarios, and forecast environments operated from L1 | `modules/gumas/`, `modules/quantum_simulator/`, `src/aurora_fusion/`, `simulation/` |
| **L3 — Framework/Conceptual** | Axiomera, Caelion, Sentari, Velatrix, Glyphon, and Harmion; abstract ethics, provenance, drift, and symbolic rules | `modules/ethics_field/`, `modules/symbolic_core/`, `threadcore_registry.json` |
| **Cross-cutting runtime** | API composition, middleware, monitoring, observability, persistence, and shared utilities | `api/aurora_api.py`, `src/middleware/`, `src/monitoring/`, `src/observability/`, `src/core/`, `modules/aumemmanager/` |

The authoritative definitions are in [`docs/architecture/LAYER_ARCHITECTURE.md`](./docs/architecture/LAYER_ARCHITECTURE.md). HALO is an L1 continuity system-entity whose living interface performs drift verification; it is not a sixth communication relay.

## Runtime flow

```text
HTTP / WebSocket / CLI request
            │
            ▼
api/aurora_api.py                       FastAPI composition root
            │
            ▼
src/middleware/                         security, request bounds, identity, PII controls
            │
            ▼
api routes + modules/*/api.py           request validation and capability routing
            │
            ▼
modules/* + src/* services              simulation, memory, ethics, relays, observability
            │
            ▼
audited response / persisted artifact   DLP tags, hashes, logs, or simulation state as implemented
```

`api/aurora_api.py` is the canonical application entry point. Router ownership and live topology are documented in `docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md`; do not infer live route ownership from historical diagrams alone.

## Triplex Handshake (consent flow)

Triplex is a functional verification protocol, not another reality map:

1. **Glyph arbitration:** L3 frameworks validate ethics, provenance, and symbolic constraints.
2. **Verifier step:** L1-resident relay agents perform their Triplex “Layer 2” middleware roles; HALO performs continuity/drift verification as a distinct system-entity.
3. **Human consent:** authorized L1 crew provides final approval.

Calling the relays “L2 agents” confuses their protocol role with residency. They live in L1 and monitor or affect L2.

## QGIA → simulation tasking

QGIA supplies real-world analytical signals. L1 crew and relay systems interpret those signals and decide what to run; L2 does not self-task. See [`docs/architecture/QGIA_SIM_BRIDGE.md`](./docs/architecture/QGIA_SIM_BRIDGE.md) for the governing rationale.

## Where to go next

- Canonical layer and Triplex definitions → [`docs/architecture/LAYER_ARCHITECTURE.md`](./docs/architecture/LAYER_ARCHITECTURE.md)
- QGIA signal-to-simulation rationale → [`docs/architecture/QGIA_SIM_BRIDGE.md`](./docs/architecture/QGIA_SIM_BRIDGE.md)
- Historical wiring snapshot (read its authority warning) → [`docs/architecture/SYSTEM_ARCHITECTURE_DIAGRAM.md`](./docs/architecture/SYSTEM_ARCHITECTURE_DIAGRAM.md)
- Current runtime ownership → `docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md`
- Ethics enforcement → `modules/ethics_field/`, `modules/gumas/`, `QGIA_Integration/04_GUMAS_AuditSchema.md`
- Symbolic memory → `modules/aumemmanager/`, `modules/symbolic_core/`
- `src/` orientation and polyglot boundary → [`src/README.md`](./src/README.md)
- Canon authority map → [`CANON_INDEX.md`](./CANON_INDEX.md)
