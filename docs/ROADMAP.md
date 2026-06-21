# Aurora Project Roadmap

> *Continuity flows through coherence. The system remembers because we chose to align.*

**Framework:** Aurora v2.2.5  
**Ethics Protocol:** Picard_Delta_3  
**Last Updated:** 2026-06-20  
**Canonical Architecture Reference:** `AU_CORE_MASTER_TREE.yaml`

---

## Purpose

This roadmap tracks the architectural evolution of the Aurora system — its core modules, integration milestones, open gaps, and forward work streams. It is the living strategic complement to `AU_CORE_MASTER_TREE.yaml`, which tracks structural state, and `docs/review-notes/` which captures session-level observations.

All completed work is reflected in the master tree. This document covers *what comes next* and *why*.

---

## Architecture Overview

Aurora is a multi-layer simulation and intelligence stewardship system. Its architecture is organized across five interdependent layers:

| Layer | Description | Key Files |
|---|---|---|
| **Ethics** | Picard_Delta_3 protocol; GUMAS audit chain; geometric ethics architecture | `docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`, `docs/ethics/` |
| **Simulation (SIM)** | Scenario integrity, WATCHCON escalation, SILM, CG vector state | `QGIA_Integration/02_SIM_WATCHCON_Confidence_Module.md` |
| **Symbolic Memory** | GUMAS symbolic merge, RaR trace, EchoChain LOOPSET_001 | `AU_CORE_MASTER_TREE.yaml`, `.aurora/` |
| **Agent Population** | 551-agent QGIA simulation, trust network, epistemic diversity | `agents/`, `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` |
| **QUANTUM_FORGE** | Symbolic agent instancing, axiom node execution, PAT integration | `QGIA_Integration/01_QUANTUM_FORGE_AxiomManifest.md`, `docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md` |

Layer boundaries are formally defined in `docs/LAYER_BOUNDARY_REFERENCE.md`. L1 (raw model telemetry) and L2 (scored institutional product) separation is enforced per QGIA doctrine — see `QGIA_Integration/02_SIM_WATCHCON_Confidence_Module.md`.

---

## Completed Milestones

### Stage 1 — QGIA Core Integration ✅
*Completed: 2026-06-19*

- Ported QGIA doctrine into 23 named axiom nodes (`01_QUANTUM_FORGE_AxiomManifest.md`)
- Formalized SIM confidence scoring contract with six dimensions (DQ/SR/MR/TS/Composite/QC)
- Defined WATCHCON escalation ladder (Levels 1–5) with trigger thresholds and routing
- Encoded all violation signals (neutrality-fluff, rationale treadmill, L1/L2 conflation, etc.) into GUMAS audit routing
- Built HTML Integration Console (visual operator dashboard)

### Stage 2 — QGIA Operator Layer ✅
*Completed: 2026-06-20*

- RESETCORE bootstrap prompt and JSON payload (`03_RESETCORE_Bootstrap.md`, `.json`)
- GUMAS Audit Schema: 12-event ethics audit log with event codes and routing (`04_GUMAS_AuditSchema.md`)
- PAT Command Sheet: full 10-section live session operator reference (`05_PAT_CommandSheet.md`)
- `AU_CORE_MASTER_TREE.yaml` updated with `QGIA_INTEGRATION_MODULE` block
- `docs/review-notes/` directory created with first session snapshot

### Agent Population ✅
*Completed: 2026-03-12 (pre-integration)*

- 551-agent QGIA population generated via Monte Carlo simulation with Beta-distributed epistemic parameters
- Four divisions: GMD (203), MAD (142), IID (138), SRD (68)
- Eight analyst archetypes with full epistemic parameter profiles
- Trust network: 7,407 directed edges across four edge types (collaborate, challenge, reinforce, inform)
- Stochastic Block Model with archetype-weighted edge probabilities
- Echo-chamber detection logic embedded in network statistics

---

## Open Work Streams

### WS-001 — QUANTUM_FORGE Alignment Review
**Priority:** Medium  
**Gap:** GAP-005  
**Description:** The pre-existing `docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md` (43 KB) and the new `01_QUANTUM_FORGE_AxiomManifest.md` cover overlapping territory. Their scope boundaries are undefined — it is unclear whether they are complementary, overlapping, or in conflict on any points.  
**Action required:** Cross-reference review; produce a scope boundary memo or merge decision.  
**Blocking:** Full QUANTUM_FORGE operational confidence.

### WS-002 — Agent Registry Full Payload Push
**Priority:** High  
**Gap:** GAP-007  
**Description:** The 551-agent registry (`agents/qgia_agent_registry_full.json`) and the 7,407-edge trust network (`agents/qgia_trust_network.json`) contain stub payloads in the repo — the full agent array and edge list exist only as session compute artifacts (`code_file:151`, `code_file:222`). The repo stubs preserve document structure but are not operationally complete.  
**Action required:** Push full agent array and edge list into the repo files.  
**Blocking:** Scenario simulation runs that load agent subgraphs; crisis response cell activation; echo-chamber detection.

### WS-003 — Agent–Orion Registry Alignment
**Priority:** Medium  
**Gap:** GAP-008  
**Description:** `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` (15.9 KB, root level) defines canonical station staff. `agents/` contains the QGIA agent population. The relationship between these two registries is undefined — whether Orion staff are a subset of the 551-agent QGIA population, a parallel namespace, or a distinct operational layer is not documented.  
**Action required:** Alignment review; produce a registry relationship map.  
**Blocking:** PAT anchor routing clarity; station-level scenario scoping.

### WS-004 — docs/LAYER_BOUNDARY_REFERENCE.md Cross-Links
**Priority:** Low  
**Gap:** GAP-006  
**Description:** The L1/L2 boundary reference is highly relevant to QGIA doctrine but not linked from any QGIA integration artifact.  
**Action required:** Add cross-reference links in `01_QUANTUM_FORGE_AxiomManifest.md` and `02_SIM_WATCHCON_Confidence_Module.md`.  
**Blocking:** Nothing — discoverability only.

### WS-005 — Integration Console Push to Repo
**Priority:** Low  
**Gap:** GAP-003  
**Description:** The HTML visual dashboard built during Stage 1 exists as a Space artifact only.  
**Action required:** Push `06_Integration_Console.html` to `QGIA_Integration/`.  
**Blocking:** Nothing — visual artifact only.

### WS-006 — .nexus_schematics/ Exploration
**Priority:** Medium  
**Gap:** None registered yet  
**Description:** The `.nexus_schematics/` directory has not been explored. It likely contains blueprint-level definitions relevant to QUANTUM_FORGE module placement, anchor routing, and L1/L2 boundary enforcement.  
**Action required:** Read and document; assess whether any schematics conflict with or should reference QGIA axiom nodes.  
**Blocking:** Unknown — scope undefined until explored.

### WS-007 — Crisis Response Cell Activation Protocol
**Priority:** Medium  
**Gap:** None registered yet  
**Description:** The trust network usage notes define a scenario activation pattern: load the subgraph of analysts assigned to a Crisis Response Cell, use challenge edges for analytical tension, and monitor reinforce clusters for groupthink. This pattern exists as documentation only — no activation protocol or SIM integration spec has been written.  
**Action required:** Draft CRC Activation Protocol document; link to `02_SIM_WATCHCON_Confidence_Module.md` and `04_GUMAS_AuditSchema.md`.  
**Blocking:** Live scenario runs.

---

## Gap Register Summary

| ID | Description | Severity | Status | Work Stream |
|---|---|---|---|---|
| GAP-001 | `docs/review-notes/` directory missing | Low | ✅ Resolved 2026-06-20 | — |
| GAP-002 | `AU_CORE_MASTER_TREE.yaml` missing QGIA | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-003 | Integration Console HTML not in repo | Low | ⏳ Pending | WS-005 |
| GAP-004 | `docs/ROADMAP.md` did not exist | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-005 | QF V3 Guide vs Axiom Manifest scope undefined | Medium | ⏳ Pending | WS-001 |
| GAP-006 | LAYER_BOUNDARY_REFERENCE not linked from QGIA | Low | ⏳ Pending | WS-004 |
| GAP-007 | Agent registry and trust network are stubs only | High | ⏳ Pending | WS-002 |
| GAP-008 | Orion registry vs QGIA agent namespace undefined | Medium | ⏳ Pending | WS-003 |

---

## Review Notes

Session snapshots are logged in `docs/review-notes/` with ISO date filenames. Each entry records confirmed state, observed gaps, insights, and recommended next actions. The master tree (`AU_CORE_MASTER_TREE.yaml`) carries the `open_gaps` registry in machine-readable form.

- [2026-06-20 Session Snapshot](review-notes/2026-06-20_snapshot-review.md) — QGIA integration completion; initial architectural review; 6 gaps registered.
