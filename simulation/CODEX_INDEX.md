# CODEX Phase Index

<!-- GENERATED FILE — do not edit by hand.
     Regenerate: python scripts/generate_codex_index.py
     Source: simulation/CODEX_PHASE*_TECHNICAL_REGISTER.json -->

Index of the CODEX character-integration phases. Each phase ships a pair:
a `*_COMPLETE.md` narrative record and a `*_TECHNICAL_REGISTER.json`
machine-readable register. Created for #1133.

## Phases

| Phase | Division / scope | Roster | Date | Records |
| --- | --- | --- | --- | --- |
| 1 | Command & Ethics Division | 1.1 → 1.2 | 2025-11-09 | [narrative](CODEX_PHASE1_COMMAND_ETHICS_COMPLETE.md) · [register](CODEX_PHASE1_TECHNICAL_REGISTER.json) |
| 2 | Systems & Infrastructure Division | 1.2 → 1.3 | 2025-11-09 | [narrative](CODEX_PHASE2_SYSTEMS_INFRASTRUCTURE_COMPLETE.md) · [register](CODEX_PHASE2_TECHNICAL_REGISTER.json) |
| 3 | Simulation & Cognitive Systems Division | 1.3 → 1.4 | 2025-11-09 | [narrative](CODEX_PHASE3_SIMULATION_COGNITIVE_COMPLETE.md) · [register](CODEX_PHASE3_TECHNICAL_REGISTER.json) |
| 4 | Interface & Aesthetics Division | 1.4 → 1.5 | — | [narrative](CODEX_PHASE4_INTERFACE_AESTHETICS_COMPLETE.md) · [register](CODEX_PHASE4_TECHNICAL_REGISTER.json) |
| 5 | Operations & Quality Assurance Division | 1.5 → 1.6 | — | [narrative](CODEX_PHASE5_OPERATIONS_QA_COMPLETE.md) · [register](CODEX_PHASE5_TECHNICAL_REGISTER.json) |
| 6 | L2 Relay Agents & L3 Framework Systems | 1.6 → 2.0 (COMPLETE) | — | [narrative](CODEX_PHASE6_L2_L3_SYSTEMS_COMPLETE.md) · [register](CODEX_PHASE6_TECHNICAL_REGISTER.json) |

The roster reaches **49 entities** at the final phase, which the
Phase 6 register marks `2.0 (COMPLETE)`.

## Related documents, with their real paths

Issue #1133 refers to two of these as if they sat in `simulation/`. They do not:

| Document | Actual path |
| --- | --- |
| Layer architecture | [`docs/architecture/LAYER_ARCHITECTURE.md`](../docs/architecture/LAYER_ARCHITECTURE.md) |
| Simulation state / mission taxonomy | [`.aurora/SIMULATION_STATE.json`](../.aurora/SIMULATION_STATE.json) |
| Canonical roster | [`L1_CANON_CHARACTER_ROSTER.md`](L1_CANON_CHARACTER_ROSTER.md) |
| Crew manifest (generated) | [`.aurora/ORION_STATION_CREW_MANIFEST.md`](../.aurora/ORION_STATION_CREW_MANIFEST.md) |

## Notes recorded while indexing

These are observations from the registers themselves, not judgements about
the work:

- **QGIA postdates every phase.** The `QGIA_Integration/` package is not
  accounted for in any phase register, so the phase sequence is not a
  complete picture of the simulation layer's integrations.
- **Phases 4 and 5 record `git_commit_status: "Pending"`** in their
  registers, although both are committed. The field was never updated after
  the commit landed; it reflects the state at authoring time, not now.
- **Phases 4 and 5 both note a character-count discrepancy** (32 loaded vs
  33 total human staff; 35 vs 36), attributed in-register to parsing rather
  than to missing characters. Unresolved in both.
- **Phase 6 has no `integration_date`** and no division summary; it records
  L2/L3 systems rather than a staffed division.

The Phase 6 terminology audit against `LAYER_ARCHITECTURE.md` that #1133
also asks for is *not* done here — it is a canon-consistency review rather
than an indexing task.
