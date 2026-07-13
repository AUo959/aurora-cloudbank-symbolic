# Aurora Project Roadmap

> *Continuity flows through coherence. The system remembers because we chose to align.*

**Framework:** Aurora v2.2.5  
**Ethics Protocol:** Picard_Delta_3  
**Last Updated:** 2026-06-22  
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

### Registry Relationship Map (GAP-008 Resolution)

Two agent registries coexist in the repo. They are parallel, non-competing namespaces:

| Registry | Layer | Population | Function |
|---|---|---|---|
| `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` | L1 Station Ops + L2/L3 Symbolic Mesh | 48 entities | Named crew, station AI, relay agents, framework systems |
| `agents/qgia_agent_registry_full.json` | QGIA Analytical Population | 551 agents | Epistemic simulation population for forecasting runs |

Cross-namespace bridges: L1 relay agents (HALO, STARLING, LIORA, OPPY, ARCHY, RIVERTHREAD) and L3 framework systems (Axiomera, Glyphon, Sentari, Caelion, Velatrix, Harmion) operate across both layers.

---

## Completed Milestones

### Stage 1 — QGIA Core Integration ✅
*Completed: 2026-06-19*

- Ported QGIA doctrine into 23 named axiom nodes (`01_QUANTUM_FORGE_AxiomManifest.md`)
- Formalized SIM confidence scoring contract with six dimensions (DQ/SR/MR/TS/Composite/QC)
- Defined WATCHCON escalation ladder (Levels 1–5) with trigger thresholds and routing
- Encoded all violation signals into GUMAS audit routing
- Built HTML Integration Console (visual operator dashboard)

### Stage 2 — QGIA Operator Layer ✅
*Completed: 2026-06-20*

- RESETCORE bootstrap prompt and JSON payload
- GUMAS Audit Schema: 12-event ethics audit log
- PAT Command Sheet: full 10-section live session operator reference
- `AU_CORE_MASTER_TREE.yaml` updated with `QGIA_INTEGRATION_MODULE` block
- `docs/review-notes/` directory created with session snapshots

### Agent Population ✅
*Completed: 2026-03-12 (pre-integration)*

- 551-agent QGIA population via Monte Carlo simulation, Beta-distributed epistemic parameters
- Four divisions: GMD (203), MAD (142), IID (138), SRD (68)
- Eight analyst archetypes with full epistemic parameter profiles
- Trust network: 7,407 directed edges, four edge types (collaborate, challenge, reinforce, inform)
- Stochastic Block Model with archetype-weighted edge probabilities
- Echo-chamber detection logic embedded in network statistics

### Registry Alignment Review ✅
*Completed: 2026-06-20*

- Confirmed Orion Station registry and QGIA agent registry are parallel, non-competing namespaces
- Mapped dual-role L2/L3 agents across both registries
- Identified `simulation/` as next major unexplored directory
- Registered GAP-009 (UNRESOLVED_HUMAN_001)

### AI Contributor Review Governance ✅
*Completed: 2026-06-22*

- Documented GAP-010: assert-before-read protocol violation by AI contributor during review session
- Patched `ops/work_queue/session_open_ritual.md` v1.1.0 with Step 0 Review Conduct Clause
- Created `docs/REVIEW_PROTOCOL.md` as standalone review standard for all agents and contributors
- Full incident record: `docs/review-notes/2026-06-22_general-review-and-gap-010.md`

### PROJECT SENTINEL Canonical Promotion ✅
*Completed: 2026-07-13 (issue #1069)*

- Promoted SENTINEL from NON-CANONICAL R&D proposal to canonical architecture — Streams 2 (AI self-audit) and 3 (ethics overlay) were already operational in code
- Created `docs/architecture/SENTINEL_ARCHITECTURE.md` as the canonical technical reference
- Registered `SENTINEL-COORDINATOR` in `constellation-contracts/manifests/sentinel-coordinator.manifest.json`, with Axiomera as named L3 audit authority
- Added Stream 1 (crew cognitive load) stub sensors at `src/sensors/crew_load/` and a stub status endpoint at `/sentinel/crew-load/status` — not wired to a real biometric provider yet
- Full detail, including two schema mismatches found (staff registry and ThreadCore payload registry don't fit a program entity like SENTINEL): `docs/architecture/SENTINEL_ARCHITECTURE.md`

---

## Open Work Streams

### WS-011 — SENTINEL Stream 1 Biometric Provider
**Priority:** Medium | **Owner:** Medical division (Dr. Vasquez)
Wire a real HRV/cortisol-proxy data source to `src/sensors/crew_load/`, and define Stream 1's own consent/opt-out hook. See `docs/architecture/SENTINEL_ARCHITECTURE.md` — Remaining Work.

### WS-001 — QUANTUM_FORGE Alignment Review
**Priority:** Medium | **Gap:** GAP-005  
Cross-reference `docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md` vs `01_QUANTUM_FORGE_AxiomManifest.md`. Note: QGIA_ARCHITECTURE.md Section 8 names 10 computational modules (Lanchester, QSFE, EDM, ABCP, RPRN, TCA, etc.) not in the axiom manifest — these are complementary layers, not conflicts.

### WS-002 — Agent Registry Full Payload Push
**Priority:** High | **Gap:** GAP-007  
Full 551-agent array and 7,407-edge list exist only as session compute artifacts. Recovery required before any scenario simulation run.

### WS-003 — simulation/ Directory Exploration
**Priority:** High | **Gap:** New (WS-003 replaces previous scope)  
Six CODEX_PHASE registers (1–6), `L1_CANON_CHARACTER_ROSTER.md`, `CANONICAL_CHARACTER_INTEGRATION_SUMMARY.md` — all unreviewed. Also resolves GAP-009 (UNRESOLVED_HUMAN_001).

### WS-004 — SIM Module Enrichment
**Priority:** Medium | **Gap:** Observation from QGIA_ARCHITECTURE.md review  
Register drift threshold 0.002 (Velatrix hard ceiling) and HALO/Velatrix drift defense pair in `02_SIM_WATCHCON_Confidence_Module.md`.

### WS-005 — docs/LAYER_BOUNDARY_REFERENCE.md Cross-Links
**Priority:** Low | **Gap:** GAP-006  
Add cross-reference links in `01_QUANTUM_FORGE_AxiomManifest.md` and `02_SIM_WATCHCON_Confidence_Module.md`.

### WS-006 — Integration Console Push to Repo
**Priority:** Low | **Gap:** GAP-003  
Push `06_Integration_Console.html` to `QGIA_Integration/`.

### WS-007 — CRC Activation Protocol Document
**Priority:** Medium | **Gap:** Identified via QGIA_ARCHITECTURE.md Section 9  
**Reclassified:** Section 9 of QGIA_ARCHITECTURE.md is already the protocol in operational form. WS-007 is now a formalization task — extract, expand, and link Section 9 into a standalone `CRC_ACTIVATION_PROTOCOL.md` in `QGIA_Integration/`.

### WS-008 — .nexus_schematics/ Exploration
**Priority:** Medium  
Blueprint-level definitions; likely relevant to QUANTUM_FORGE module placement, anchor routing, L1/L2 boundary enforcement.

### WS-009 — Remaining File Review Pass
**Priority:** Medium  
Unreviewed files identified: `threadcore_registry.json`, `staff_registry.json`, `symbolic_config.yaml`.

### WS-010 — Review Governance Hardening
**Priority:** High | **Gap:** GAP-010  
Follow-on work from the 2026-06-22 assert-before-read incident. Three sub-tasks remain open:
- Verify `CLAUDE.md`, `COPILOT_INSTRUCTIONS.md`, and `CONTRIBUTING.md` all reference `ops/work_queue/` as the authoritative task surface for agent and human contributors
- Consolidate `QGIA_Integration/` and `QGIA_integration/` case split at root
- Evaluate whether root-level operational artifacts (`aurora_dashboard.html`, `AU_CORE_MASTER_TREE.yaml`, `activate_aurora.sh`, etc.) should migrate into `ops/` or retain root placement with explicit justification

---

## Gap Register Summary

| ID | Description | Severity | Status | Work Stream |
|---|---|---|---|---|
| GAP-001 | `docs/review-notes/` directory missing | Low | ✅ Resolved 2026-06-20 | — |
| GAP-002 | `AU_CORE_MASTER_TREE.yaml` missing QGIA | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-003 | Integration Console HTML not in repo | Low | ⏳ Pending | WS-006 |
| GAP-004 | `docs/ROADMAP.md` did not exist | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-005 | QF V3 Guide vs Axiom Manifest scope undefined | Medium | ⏳ Pending | WS-001 |
| GAP-006 | LAYER_BOUNDARY_REFERENCE not linked from QGIA | Low | ⏳ Pending | WS-005 |
| GAP-007 | Agent registry + trust network are stubs only | High | ⏳ Pending | WS-002 |
| GAP-008 | Orion registry vs QGIA agent namespace undefined | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-009 | UNRESOLVED_HUMAN_001: missing 36th Orion human | Low-Medium | ⏳ Pending | WS-003 |
| GAP-010 | Assert-before-read protocol violation by AI contributor | High | ✅ Mitigated 2026-06-22 — monitoring open | WS-010 |

---

## Review Notes

| Date | Note | Summary |
|---|---|---|
| 2026-06-20 | [Snapshot Review](review-notes/2026-06-20_snapshot-review.md) | QGIA integration completion; initial architectural review; GAP-001 through GAP-006 |
| 2026-06-20 | [Agents Review](review-notes/2026-06-20_agents-review.md) | agents/ directory; GAP-007, GAP-008 registered |
| 2026-06-20 | [QGIA Architecture Review](review-notes/2026-06-20_qgia-architecture-review.md) | QGIA_ARCHITECTURE.md deep read; computational modules; CRC protocol reclassification |
| 2026-06-20 | [Orion Registry Review](review-notes/2026-06-20_orion-registry-review.md) | GAP-008 resolved; dual-role L2/L3 agents mapped; GAP-009 registered |
| 2026-06-22 | [General Review & GAP-010](review-notes/2026-06-22_general-review-and-gap-010.md) | General repo review; assert-before-read incident; GAP-010 registered; session ritual v1.1.0 patched |
