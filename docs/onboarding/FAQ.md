# Engineer Onboarding FAQ

## 1. What is Aurora in this repository?

Aurora is the simulation director for the Orion Station institutional simulation and the runtime/canon surface supporting it. Start with `AURORA_CONTEXT.json`; it cites the source for each identity claim.

## 2. Are L1, L2, and L3 software tiers?

No. They are reality/ontology layers: L1 station operations, L2 simulation/research environments, and L3 conceptual frameworks. Read `docs/architecture/LAYER_ARCHITECTURE.md` before using the terms.

## 3. Why does Triplex also use layer numbers?

Triplex describes three functional consent steps. Its “Layer 2” verifier role is performed by L1-resident systems, so protocol role and reality residency must not be conflated.

## 4. Is HALO the sixth relay agent?

No. HALO retains the `RELAY_006` registry designation and performs Triplex drift verification, but it is the station continuity system-entity and does not relay messages. There are exactly five communication relay agents.

## 5. What is the server entry point?

`api/aurora_api.py` composes the FastAPI application. Check `docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md` for current router/service ownership.

## 6. What belongs in `modules/` versus `src/`?

Feature capabilities generally live in `modules/`; runtime, orchestration, bridge, interface, and cross-cutting services live in `src/`. The current boundary has exceptions, documented in `src/README.md` and tracked for audit in #1255.

## 7. Can I trust `.aurora/SIMULATION_STATE.json` as live state?

Not without checking `last_updated`. `AURORA_CONTEXT.json` records a known freshness caveat; the onboarding CLI reports the lockpoint as a context snapshot rather than a live-state claim.

## 8. Where are ethics rules and audit evidence?

Start with `modules/ethics_field/`, `modules/gumas/`, `QGIA_Integration/04_GUMAS_AuditSchema.md`, and `QGIA_Integration/QUANTUM_FORGE_Axiom_Manifest.json`.

## 9. Does the first memory seed become canon?

No. `scripts/aurora_onboard.py` writes it as staged material under `seeds/onboarding/`. Promotion requires review under the policy referenced by `CANON_INDEX.md`.

## 10. What should I validate before a pull request?

Run focused tests and hooks for the files you changed, then follow `CONTRIBUTING.md`. For the onboarding module itself, run `pytest tests/test_aurora_onboard.py -q` and `python scripts/aurora_onboard.py --skip-interactive`.
