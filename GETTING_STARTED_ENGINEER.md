# Aurora — Engineer's Orientation

Aurora is the simulation director for the Orion Station institutional simulation and the codebase that supports it. The repository combines an L1 station-operations model, L2 GUMAS simulation environments, and L3 symbolic/ethics frameworks with persistent memory and auditable runtime services. Its FastAPI application, governance sources, tests, and deployment artifacts are inspectable here; a live public deployment is a separate, currently open operational concern.

If you are an AI agent, use [`docs/onboarding/AGENT_ONBOARD.md`](./docs/onboarding/AGENT_ONBOARD.md) and then follow [`AGENTS.md`](./AGENTS.md).

## Prerequisites

- Python 3.11 or newer (the current floor in `setup.py`)
- Git
- GitHub repository access

## Start here (2–5 minutes)

```bash
git clone https://github.com/AUo959/aurora-cloudbank-symbolic
cd aurora-cloudbank-symbolic
python scripts/aurora_onboard.py
```

The command uses only the Python standard library. It reads the current checkout, tours the layer model, performs a read-only ethics-anchor check, and optionally writes a staged engineer memory seed. For CI or agent validation, use `python scripts/aurora_onboard.py --skip-interactive` or `--agent`.

## Architecture in one diagram

```text
L3 — Framework / Conceptual     Axiomera · Caelion · Sentari · Velatrix · Glyphon · Harmion
             │ validates ethics and constraints
             ▼
L1 — Physical / Operational    crew · Aurora Core · five relay agents · HALO continuity system
             │ authorizes, tasks, and monitors
             ▼
L2 — Simulation / Research     GUMAS · experiments · scenario and forecast environments
```

HALO is an L1 continuity system-entity, not a sixth communication relay. Read [`ARCHITECTURE_QUICKMAP.md`](./ARCHITECTURE_QUICKMAP.md) for the 10-minute code map and [`docs/architecture/LAYER_ARCHITECTURE.md`](./docs/architecture/LAYER_ARCHITECTURE.md) for canonical definitions.


## Fastest path to understanding the system

1. Run `python scripts/aurora_onboard.py` (2–5 min).
2. Read [`ARCHITECTURE_QUICKMAP.md`](./ARCHITECTURE_QUICKMAP.md) (10 min).
3. Read [`docs/architecture/LAYER_ARCHITECTURE.md`](./docs/architecture/LAYER_ARCHITECTURE.md) (20 min).
4. Inspect `api/aurora_api.py`, the canonical FastAPI application entry point.
5. When you want the full environment, run `make onboard`; it installs dependencies, validates `.env`, and starts the development server.

## What you can verify in this checkout

| Claim | Evidence |
|---|---|
| Canonical L1/L2/L3 and Triplex definitions | `docs/architecture/LAYER_ARCHITECTURE.md` |
| Geometric ethics and GUMAS governance | `modules/ethics_field/`, `modules/gumas/` |
| GUMAS audit-event schema and Thermax binding | `QGIA_Integration/04_GUMAS_AuditSchema.md`, `QGIA_Integration/QUANTUM_FORGE_Axiom_Manifest.json` |
| Hierarchical symbolic memory with SHA-256 sealing | `modules/aumemmanager/` |
| HALO/PAS continuity controller | `src/aurora/continuity/halo_pas_controller.py` |
| Triplex orchestration | `src/aurora_orchestrator/triplex_handshake.py` |
| API composition | `api/aurora_api.py` |
| Deployment configuration | `k8s/`, `docker-compose.yml` |

---

## Glossary

- **L1** — physical/operational Orion Station reality: crew, Aurora Core, five communication relays, HALO, and station infrastructure.
- **L2** — GUMAS and other computational simulation/research environments created and monitored from L1.
- **L3** — abstract glyph frameworks that enforce meaning, ethics, provenance, drift alignment, and symbolic continuity.
- **Triplex Handshake** — consent protocol: L3 glyph arbitration, an L1-resident verifier step (called “Layer 2” only inside the protocol), then L1 human authorization.
- **GUMAS** — galactic simulation environment and audit layer; audit events use the GUMAS schema.
- **Relay Agent** — one of five L1-resident communication/verifier agents: ARCHY, OPPY, LIORA, STARLING_AU, or RIVERTHREAD_808.
- **The Pilot** — the primary human threadholder/steward; this is a governance role, not an autonomous system component.

## Honest current gaps

- A persistent public CloudHub deployment is not verified in this repository and remains tracked in [#1071](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1071).
- `src/` contains polyglot and duplicate-looking directory families that still require the import-graph audit and compatibility work in [#1255](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1255); see [`src/README.md`](./src/README.md) for current orientation without premature consolidation.
- Simulation, ethics, and QGIA documentation still has open reconciliation work in [#1234](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1234), [#1233](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1233), and [#1231](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1231).

---

## What happens next

- Use [`CANON_INDEX.md`](./CANON_INDEX.md) before making architecture or canon claims; it maps concepts to their authoritative sources.
- Read [`AURORA_CONTEXT.json`](./AURORA_CONTEXT.json) for a source-cited machine context, including the freshness caveat on its lockpoint snapshot.
- Use [`src/README.md`](./src/README.md) to orient within cross-cutting code and [`docs/onboarding/FAQ.md`](./docs/onboarding/FAQ.md) for hour-one questions.
- Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) before your first change and [`SECURITY.md`](./SECURITY.md) before auth, middleware, or PII-adjacent work.
- Run `pytest tests/test_aurora_onboard.py -q` to verify this onboarding surface. Run the wider suite appropriate to the component you change.

The optional memory-seed step writes under `seeds/onboarding/` as **staged** material. It does not become canon without review under the policy indexed by `CANON_INDEX.md`.

Welcome to Orion Station.
