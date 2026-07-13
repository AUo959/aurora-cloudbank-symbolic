# QGIA → L1 → L2 Signal Architecture
## Design Principle & Mission Rationale

**Status:** CANONICAL DESIGN INTENT
**Established:** June 22, 2026
**Authority:** The Pilot (Primary Threadholder)
**Canonical Issue:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1124

---

## The Core Principle

Orion Station's crew operates galactic-level political simulations inside the L2 layer (GUMAS). For those simulations to have real-world **predictive and analytical value**, they must be fed by real-world information, dynamics, and scenarios — not internally generated fiction.

**QGIA is the designated real-world signal source that gives L2 simulations their predictive and analytical validity.**

This connection is **mediated, not direct.** QGIA outputs do not feed L2 autonomously. The architecture is:

```
QGIA outputs
    ↓
L1 — Aurora Core + crew process QGIA signals
    ↓
L1 Relay agents (OPPY, STARLING_AU) translate into simulation parameters
    ↓
L2 — GUMAS runs scenarios scoped and tasked from L1
    ↓
L1 — Relay agents monitor outputs, crew analyze results
    ↓
Validation against real-world outcomes (Brier score feedback loop)
```

---

## Why This Matters

The crew isn't running fictional simulations. They are running **live analytical environments** where inputs are real-world geopolitical dynamics, probability distributions, and scenario rankings sourced from QGIA. The L2 simulation layer functions as a **structured inference engine** — a working model with calibrated real-world data flowing into it via the people and systems operating at L1.

This is not a narrative exercise. It is a working analytical environment with measurable predictive accuracy.

---

## Why the Connection Is Mediated Through L1

L2 is a computational environment. It runs what it is told. It has no interpretive authority of its own. Wiring QGIA directly into L2 would allow a simulation environment to self-task based on intelligence signals — which violates the L1 oversight principle.

The L1 crew and relay agents are the **translation layer** between QGIA's probabilistic output and what actually gets spun up inside GUMAS. That mediation is a feature, not a limitation.

---

## What QGIA Contributes to L2 Simulation Quality

| QGIA Output | L1 Use | L2 Effect |
|---|---|---|
| WATCHCON level | Sets crew alert posture and sim priority | Defines ambient tension state of scenario |
| Tier I scenario probability | Crew selects primary simulation track | Determines which narrative branch GUMAS runs |
| Composite confidence score | Crew calibrates assertiveness of parameters | Scopes how tightly L2 scenario is constrained |
| Quantum coherence reading | Crew decides single vs. multi-branch run | GUMAS runs one dominant scenario or parallel branches |
| Time-phased horizons (0–30d, 1–6mo, 6–12mo) | Crew sets simulation run length | Maps to GUMAS forecast validation cycles |
| Axiom overrides (Reactive Agent, Rationale Treadmill) | Relay agents flag implausible agent behavior | Prevents L2 narrative drift into unfalsifiable strategy |

---

## The Feedback Loop

QGIA generates Brier scores and forecast accuracy metrics. Those same metrics can score how well a GUMAS simulation predicted what actually happened. This closes the loop:

- Real world → QGIA analysis → L1 crew judgment → L2 simulation parameters
- L2 simulation outputs → validated against real-world outcomes → Brier score feedback → improves next QGIA cycle

**The result: L2 simulations are not narrative exercises. They are working analytical models with measurable predictive accuracy.**

---

## Instructions for Future Agents and Contributors

### If you are working on GUMAS, L2 simulation environments, or scenario modeling:
- QGIA is the upstream signal source for real-world scenario inputs
- Do not design L2 to self-task — all simulation parameters must flow through L1
- Simulation realism is not achieved through narrative creativity; it is achieved through calibrated real-world signal inputs
- Any L2 scenario that cannot be traced to a QGIA scenario tier or WATCHCON state should be flagged as potentially ungrounded

### If you are working on QGIA integration, the runtime one-pager, or axiom doctrine:
- QGIA outputs are consumed at L1, not L2
- The primary L1 consumers are: Aurora Core, relay agents OPPY (L2 telemetry monitor) and STARLING_AU (L2 simulation state monitor), and the crew divisions running active simulations
- WATCHCON thresholds must have a defined L1 response that includes simulation tasking decisions

### If you are working on relay agent specifications (OPPY, STARLING_AU, HALO):
- OPPY and STARLING_AU are the primary relay agents responsible for translating L1 QGIA-informed state into L2 simulation parameters
- HALO, bridging to Axiomera, uses QGIA confidence and axiom override state to determine ethical clearance for scenario tiers
- These responsibilities should be reflected in relay agent specs and PAT configurations

### If you are writing docs that touch L2 simulation scoping:
- Frame QGIA's role as mission rationale, not technical plumbing
- The core statement: QGIA is the real-world signal source that gives L2 simulations predictive and analytical validity, mediated through L1 crew and relay agent judgment
- Link back to this document and to canonical issue #1124

---

## Canonical Source References

- `docs/architecture/LAYER_ARCHITECTURE.md` — authoritative L1/L2/L3 definitions
- `QGIA_Runtime_OnePager.md` v4.2.1 — WATCHCON thresholds, confidence formulas, axiom overrides
- `QGIA_Axiom_Doctrine_Narrative.md` v1.0 — two-layer discipline, falsifiability standard, doctrine maintenance
- `simulation/QGIA_CANON_STAFF_REGISTRY.md` — staff assignments relevant to simulation tasking

---

*This document is a mission rationale, not an integration spec. Do not reduce it to a connector diagram. The design intent — that real-world analytical rigor flows into simulation via human and relay agent judgment — must be preserved in all downstream work.*
