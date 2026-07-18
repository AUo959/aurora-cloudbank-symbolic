# Aurora Project Roadmap

> *Continuity flows through coherence. The system remembers because we chose to align.*

- **Framework:** Aurora v2.2.5
- **Ethics Protocol:** Picard_Delta_3
- **Last Updated:** 2026-07-18
- **Roadmap Revision:** QGIA milestone alignment v1.1
- **Canonical Architecture Reference:** `AU_CORE_MASTER_TREE.yaml`

---

## Purpose

This roadmap tracks the architectural evolution of the Aurora system — its core modules, integration milestones, open gaps, and forward work streams. It is the living strategic complement to `AU_CORE_MASTER_TREE.yaml`, which tracks structural state, and `docs/review-notes/` which captures session-level observations.

Completed milestones below are evidence-linked to their repository artifacts.
Structural representation in the master tree is audited independently; the QGIA
alignment audit remains planned under #1231 slice #1111. This document covers
*what comes next* and *why*.

---

## Architecture Overview

Aurora is a multi-layer simulation and intelligence stewardship system. Its architecture is organized across five interdependent layers:

| Layer | Description | Key Files |
| --- | --- | --- |
| **Ethics** | Picard_Delta_3 protocol; GUMAS audit chain; geometric ethics architecture | `docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`, `docs/ethics/`, `docs/qgia/GUMAS_Audit_Schema.md` |
| **Simulation (SIM)** | Scenario integrity, WATCHCON escalation, SILM, CG vector state | `docs/qgia/SIM_WATCHCON_Confidence_Module.md` |
| **Symbolic Memory** | GUMAS symbolic merge, RaR trace, EchoChain LOOPSET_001 | `AU_CORE_MASTER_TREE.yaml`, `.aurora/` |
| **Agent Population** | 551-agent QGIA simulation, trust network, epistemic diversity | `agents/`, `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` |
| **QUANTUM_FORGE** | Symbolic agent instancing, axiom-node documentation, PAT integration planning | `docs/qgia/QUANTUM_FORGE_Axiom_Node_Manifest.md`, `docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md` |

Aurora reality-layer boundaries are formally defined in
`docs/architecture/LAYER_ARCHITECTURE.md`. The QGIA doctrine's internal
"Layer 1" raw-model and "Layer 2" analyst-consensus labels are product stages,
not Aurora reality layers. QGIA is an L1 analytical institution; any QGIA
signal that informs Aurora's L2 GUMAS simulations must be mediated by L1 crew
or relay-agent judgment as defined in `docs/architecture/QGIA_SIM_BRIDGE.md`.

The `docs/qgia/` package is `STAGING`, `DOCUMENT_PACKAGE_ONLY`, and
`NOT_IMPLEMENTED` for runtime activation. Its completed milestones below record
reviewed documentation and routing surfaces, not an activated loader or a
direct QGIA-to-L2 integration.

### Registry Relationship Map (GAP-008 Resolution)

Two agent registries coexist in the repo. They are parallel, non-competing namespaces:

| Registry | Layer | Population | Function |
| --- | --- | --- | --- |
| `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` | L1 Station Ops + L2/L3 Symbolic Mesh | 48 entities | Named crew, station AI, five relay agents, HALO continuity system-entity, framework systems |
| `agents/qgia_agent_registry_full.json` | QGIA Analytical Population | 551 agents | Epistemic simulation population for forecasting runs |

Cross-namespace bridges: five L1 relay agents (STARLING, LIORA, OPPY, ARCHY, RIVERTHREAD), the HALO continuity system-entity, and L3 framework systems (Axiomera, Glyphon, Sentari, Caelion, Velatrix, Harmion) operate across both layers.

---

## Completed Milestones

### Stage 1 — QGIA Core Documentation Artifacts ✅
*Artifact baseline: 2026-06-19 | Reconciled and last verified: 2026-07-18*

- Reconciled the 23-node axiom registry in
  `docs/qgia/QUANTUM_FORGE_Axiom_Node_Manifest.md` (PR #1262)
- Formalized the six-dimension confidence contract
  (DQ/SR/MR/TS/Composite/QC) in
  `docs/qgia/SIM_WATCHCON_Confidence_Module.md`
- Documented WATCHCON Levels 1–5 with inclusive trigger thresholds and routing
- Preserved QGIA Runtime One-Pager v4.2.1 and Axiom Doctrine v1.0 as reviewed
  source snapshots in `docs/qgia/`
- Resolved GAP-005 by reconciling the axiom manifest with the verified Quantum
  Forge seams; activation remains staged pending an explicit adapter

### Stage 2 — QGIA Operator Documentation Artifacts ✅
*Artifact baseline: 2026-06-20 | Last verified: 2026-07-18*

- Preserved the RESETCORE bootstrap and carry-forward contract in
  `docs/qgia/RESETCORE_Bootstrap.md`
- Documented the 12-event GUMAS ethics-audit schema in
  `docs/qgia/GUMAS_Audit_Schema.md`
- Preserved the 10-section PAT operator reference in
  `docs/qgia/PAT_Command_Sheet.md`
- Confirmed that `AU_CORE_MASTER_TREE.yaml` contains a
  `QGIA_INTEGRATION_MODULE` block; its semantic and path alignment remains a
  planned audit under #1231 slice #1111
- Kept all executable-looking prompts and commands as source material rather
  than agent instructions or runtime activation authority

### Stage 3 — QGIA Documentation Home and Index Routing ✅
*Completed and last verified: 2026-07-18*

- Added the eight-artifact `docs/qgia/` package with provenance, review order,
  and non-activation boundaries (PR #1266)
- Added the staged QGIA routing map to `CANON_INDEX.md` and contributor
  navigation to `docs/index.md` (PR #1270)
- Explicitly scope-separated the canonical agent map from the contributor
  documentation portal
- Retained `STAGING`, `DOCUMENT_PACKAGE_ONLY`, and `NOT_IMPLEMENTED` status;
  no loader, router, or direct L2 activation was introduced

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

### WS-002 — Agent Registry Full Payload Push
**Priority:** High | **Gap:** GAP-007  
Full 551-agent array and 7,407-edge list exist only as session compute artifacts. Recovery required before any scenario simulation run.

### WS-003 — simulation/ Directory Exploration
**Priority:** High | **Gap:** New (WS-003 replaces previous scope)  
Six CODEX_PHASE registers (1–6), `L1_CANON_CHARACTER_ROSTER.md`, `CANONICAL_CHARACTER_INTEGRATION_SUMMARY.md` — all unreviewed. Also resolves GAP-009 (UNRESOLVED_HUMAN_001).

### WS-004 — SIM Module Enrichment
**Priority:** Medium | **Gap:** Observation from QGIA_ARCHITECTURE.md review  
Register drift threshold 0.002 (Velatrix hard ceiling) and HALO/Velatrix drift
defense pair in the established source before refreshing
`docs/qgia/SIM_WATCHCON_Confidence_Module.md`.

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

### WS-012 — QGIA Master-Tree Alignment Audit
**Priority:** Medium | **Tracking:** #1231 slice #1111

Audit `AU_CORE_MASTER_TREE.yaml` against the reconciled 23-node registry, QGIA
L1 mediation doctrine, GUMAS tiers, WATCHCON thresholds, and current
`docs/qgia/` paths. Do not treat the existing module block as proof of runtime
activation or complete alignment.

---

## Gap Register Summary

| ID | Description | Severity | Status | Work Stream |
| --- | --- | --- | --- | --- |
| GAP-001 | `docs/review-notes/` directory missing | Low | ✅ Resolved 2026-06-20 | — |
| GAP-002 | `AU_CORE_MASTER_TREE.yaml` missing QGIA | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-003 | Integration Console HTML not in repo | Low | ⏳ Pending | WS-006 |
| GAP-004 | `docs/ROADMAP.md` did not exist | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-005 | QF V3 Guide vs Axiom Manifest scope undefined | Medium | ✅ Resolved 2026-07-16 (PR #1262) | — |
| GAP-006 | LAYER_BOUNDARY_REFERENCE not linked from QGIA | Low | ⏳ Pending | WS-005 |
| GAP-007 | Agent registry + trust network are stubs only | High | ⏳ Pending | WS-002 |
| GAP-008 | Orion registry vs QGIA agent namespace undefined | Medium | ✅ Resolved 2026-06-20 | — |
| GAP-009 | UNRESOLVED_HUMAN_001: missing 36th Orion human | Low-Medium | ⏳ Pending | WS-003 |
| GAP-010 | Assert-before-read protocol violation by AI contributor | High | ✅ Mitigated 2026-06-22 — monitoring open | WS-010 |

---

## Review Notes

| Date | Note | Summary |
| --- | --- | --- |
| 2026-06-20 | [Snapshot Review](review-notes/2026-06-20_snapshot-review.md) | QGIA integration completion; initial architectural review; GAP-001 through GAP-006 |
| 2026-06-20 | [Agents Review](review-notes/2026-06-20_agents-review.md) | agents/ directory; GAP-007, GAP-008 registered |
| 2026-06-20 | [QGIA Architecture Review](review-notes/2026-06-20_qgia-architecture-review.md) | QGIA_ARCHITECTURE.md deep read; computational modules; CRC protocol reclassification |
| 2026-06-20 | [Orion Registry Review](review-notes/2026-06-20_orion-registry-review.md) | GAP-008 resolved; dual-role L2/L3 agents mapped; GAP-009 registered |
| 2026-06-22 | [General Review & GAP-010](review-notes/2026-06-22_general-review-and-gap-010.md) | General repo review; assert-before-read incident; GAP-010 registered; session ritual v1.1.0 patched |
