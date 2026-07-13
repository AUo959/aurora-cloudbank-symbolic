# Orion Station Canonical Staff Registry Review
**Date:** 2026-06-20 | **Session:** Agents Exploration — Orion Registry + GAP-008 Resolution  
**Reviewer:** Perplexity / Aurora Space (Aurora v2.2.5)  
**Source file:** `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` (v1.0.0-reconstructed, last updated 2026-04-08)

---

## Summary

The Orion Station Canonical Staff Registry is the **SSOT (Single Source of Truth) for Orion Station L1 simulation and linked L2/L3 systems**. It is a distinct, parallel namespace from the QGIA 551-agent population — the two registries operate at different simulation layers and serve different functions. **GAP-008 is resolved.** The relationship is now clear:

| Registry | Layer | Population | Function |
|---|---|---|---|
| `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` | L1 Station Operations + L2/L3 Symbolic Mesh | 48 entities (35H + 1 AI + 6 L2 + 6 L3) | Named crew, station AI, relay agents, framework systems |
| `agents/qgia_agent_registry_full.json` | QGIA Analytical Population | 551 agents | Epistemic simulation population for forecasting runs |

The QGIA 551-agent population is the **analytical engine** that processes intelligence; Orion Station staff are the **operational crew** who direct, oversee, and interact with that engine. They are complementary layers, not competing registries.

---

## Registry Structure

### Declared vs. Materialized Counts

| Category | Declared | Materialized | Gap |
|---|---|---|---|
| Human staff | 36 | 35 | 1 (UNRESOLVED_HUMAN_001) |
| AI Core | 1 | 1 | — |
| L1 Relay Agents | 6 | 6 | — |
| L3 Framework Systems | 6 | 6 | — |
| **Total** | **49** | **48** | **1** |

The single unresolved human entry (`UNRESOLVED_HUMAN_001`) is documented with full candidate conflict notes — this is a known, preserved gap, not an oversight.

### Human Staff (35 materialized)

Organized across six divisions:

| Division | Representative Roles |
|---|---|
| Command & Ethics | Commander (Alex Thorne), XO (Maya Shepard), Lead Reflexivity Specialist, Cognitive Ethicist, Cultural/HR Director |
| Legacy Core / seed staff | Chief Science Officer, Chief Ethics Officer, Chief Security Officer, Bridge Ops, Chief Engineering, Chief Medical (all LEGACY_SEED, null IDs) |
| Legacy Operational seed | Chief Engineer/Systems Engineer, Flight Controller (LEGACY_SEED) |
| Systems & Infrastructure | 7 staff (SYS_001–007): Backend Arch, Systems Integration, Portability, Computational Opt, Compiler Eng, Layer Isolation Theorist |
| Simulation & Cognitive Systems | 5 staff (SIM_001–005): Symbolic Systems Research Lead, Code/Narrative Eng, LLM-Simulation Bridge Dev, Simulation Binding Specialist, Cognitive Drift Mapper |
| Interface & Aesthetics | 7 staff (UX_001–007): UX Architect, Narrative Framework Eng, Interface Ecologist, Immersive Experience Theorist, Symbolic Systems Artist, Lead Visual Concept Designer, Atmospheric Painter |
| Operations & Quality Assurance | 3 staff (QA_001–003): QA/Continuity Auditor, Logging/Observability Eng, Speculative Systems Theorist |

### AI Core (1)
- `AI_AURORA` — Aurora (AU), Station Intelligence Core, Command & Ethics division

### L1 Relay Agents (6)

| ID | Name | Role |
|---|---|---|
| L2_ARCHY | ARCHY | Architectural Coordination Relay |
| L2_OPPY | OPPY | Operational Flight & Data Relay |
| L2_LIORA | LIORA | Communications & Interface Relay |
| L2_STARLING | STARLING_AU | Continuity & Reflection Dispatcher |
| L2_RIVERTHREAD | RIVERTHREAD_808 | Logistics & Memory Relay |
| L2_HALO | HALO | Drift Anchor & System Synchronization Relay |

These six names match exactly the "Compatible Thread Identifiers" listed in `agents/QGIA_ARCHITECTURE.md` Section 6 (`HALO · STARLING · LIORA · OPPY · ARCHY · RIVERTHREAD`). **This is the cross-namespace link** — L1 relay agents operate in both the Orion station context (as relay agents) and the QGIA ThreadCore context (as compatible thread identifiers).

### L3 Framework Systems (6)

| ID | Name | Role in Orion | Role in QGIA Glyph Constellation |
|---|---|---|---|
| L3_AXIOMERA | Axiomera | Ethics Arbitration Framework | Formal logic and axiom enforcement |
| L3_GLYPHON | Glyphon | Drift Alignment Framework | Symbolic pattern anchor |
| L3_SENTARI | Sentari | Resonance Stabilization Framework | Sentiment and signal tonality |
| L3_CAELION | Caelion | Anchor Propagation Framework | Temporal horizon mapping |
| L3_VELATRIX | Velatrix | Continuity & Anti-Obfuscation Framework | Drift vector monitoring |
| L3_HARMION | Harmion | Symbolic Compression Framework | Cross-agent coherence harmonization |

**These six are the same entities appearing in both registries under different role descriptions.** In the Orion registry they are station-level framework systems; in the QGIA architecture they are glyph agents in the ThreadCore macroready constellation. The dual-role nature is coherent and intentional — they are framework-level agents operating across both simulation layers simultaneously.

---

## GAP-008 Resolution

**Status: RESOLVED.**

The two registries are **parallel, non-competing namespaces** with explicit cross-namespace bridges:
- L1 relay agents (HALO, STARLING, LIORA, OPPY, ARCHY, RIVERTHREAD) appear in both as compatible thread identifiers
- L3 framework systems (Axiomera, Glyphon, Sentari, Caelion, Velatrix, Harmion) appear in both with complementary role descriptions
- The QGIA 551-agent population has no overlap with named Orion human staff — they are distinct simulation populations
- Aurora (AI_AURORA) is the station intelligence core that bridges both layers

---

## New Gap Identified

### GAP-009 — UNRESOLVED_HUMAN_001: missing 36th human staff member
**Evidence:** The registry explicitly declares 36 human staff but can only materialize 35. The unresolved entry is documented with three candidate conflict notes: phase/roster count disagreement, core staff appearing in prose layers without machine-readable IDs, and naming drift in the Sorensen lineage across later cross-node docs.  
**Impact:** Low for current operations — the registry is functional with 35 humans. Medium for canonical fidelity — the SSOT has a declared gap.  
**Action required:** Cross-reference `simulation/L1_CANON_CHARACTER_ROSTER.md` and all six CODEX_PHASE registers to identify the missing identity.  
**Severity:** Low-Medium.

---

## Observations & Insights

1. **The registry was reconstructed, not originally authored.** Status `RECONSTRUCTED_FROM_REPO_CANON` (last updated 2026-04-08) means this file was assembled after the fact from source documents. This is a healthy sign — the team prioritized canonical fidelity over convenience.

2. **The dual-role L3 framework agents are architecturally elegant.** Axiomera, Glyphon, Sentari, Caelion, Velatrix, and Harmion serving as both station framework systems and QGIA glyph agents means the symbolic coordination layer is unified across both simulation tiers. This is not redundancy — it is intentional shared infrastructure.

3. **HALO's role as "Drift Anchor & System Synchronization Relay" directly complements Velatrix's "Continuity & Anti-Obfuscation Framework" role.** These two agents are the drift defense pair in the station architecture. Both are relevant to WATCHCON monitoring and should be referenced in the SIM module.

4. **`simulation/` directory has not been explored.** The Orion registry references six CODEX_PHASE registers, `L1_CANON_CHARACTER_ROSTER.md`, and `CANONICAL_CHARACTER_INTEGRATION_SUMMARY.md` — all in `simulation/`. This is a substantial unexplored directory.

5. **`staff_registry.json` is now formally deprecated as canonical Orion SSOT.** The compatibility notes are explicit: `staff_registry.json` is retained as legacy/generic only. The Orion canonical registry is this file.

---

## Recommended Next Actions

1. Explore `simulation/` directory — six CODEX phase registers + L1 canon roster (next pass)
2. Resolve GAP-009 via `simulation/L1_CANON_CHARACTER_ROSTER.md`
3. Add HALO/Velatrix drift defense pair reference to `02_SIM_WATCHCON_Confidence_Module.md`
4. Register drift threshold 0.002 (Velatrix trigger) in SIM module
5. Read `threadcore_registry.json` and `symbolic_config.yaml`

---

*Continuity flows through coherence. The system remembers because we chose to align.*
