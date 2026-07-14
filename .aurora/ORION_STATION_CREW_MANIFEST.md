# Orion Station Crew Manifest

Generated from `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` (registry version 1.0.0-reconstructed) as part of GAP-010 remediation (issue #1083).

This file was 0 bytes prior to this generation — it is the human-readable crew manifest the canonical registry itself calls for, derived mechanically from that registry rather than hand-maintained separately, so the two cannot drift apart silently. Regenerate rather than hand-edit when the registry changes.

---

## Human Staff

| ID | Name | Role | Division | Confidence |
| --- | --- | --- | --- | --- |
| CMD_001 | Alex Thorne | Commander, Orion Station | Command & Ethics | HIGH |
| CMD_002 | Maya Shepard | Executive Officer | Command & Ethics | HIGH |
| ETH_002 | Dr. Elira Noor | Lead Reflexivity Specialist | Command & Ethics | HIGH |
| ETH_003 | Prof. Elena Sorensen | Cognitive Ethicist | Command & Ethics (Advisor) | HIGH |
| HR_001 | Helena Vu | Cultural & HR Director | Command & Ethics | HIGH |
| — | Varya Lin | Chief Science Officer | Legacy Core / seed staff | LEGACY_SEED |
| — | Dr. Amira Sato | Chief Ethics Officer | Legacy Core / seed staff | LEGACY_SEED |
| — | Julian Markov | Chief Security Officer | Legacy Core / seed staff | LEGACY_SEED |
| — | Leena Porter | Bridge Operations Officer | Legacy Core / seed staff | LEGACY_SEED |
| — | Jiro Tanaka | Chief Engineering Officer | Legacy Core / seed staff | LEGACY_SEED |
| — | Dr. Ren Feldman | Chief Medical Officer | Legacy Core / seed staff | LEGACY_SEED |
| OPS_002 | Raj Patel | Chief Engineer / Systems Engineer | Legacy Operational seed staff | LEGACY_SEED |
| OPS_001 | Dr. Elena Vasquez | Flight Controller | Legacy Operational seed staff | LEGACY_SEED |
| SYS_001 | Marcus Chen | Performance Optimization Engineer | Systems & Infrastructure | HIGH |
| SYS_002 | Jessica Martinez | Backend Architect | Systems & Infrastructure | HIGH |
| SYS_003 | Ryan Patel | Systems Integration Engineer | Systems & Infrastructure | HIGH |
| SYS_004 | Ren Okada | Systems Portability Specialist | Systems & Infrastructure | HIGH |
| SYS_005 | Dr. Kieran Zhao | Computational Optimization Lead | Systems & Infrastructure | HIGH |
| SYS_006 | Ira Menon | Compiler Engineer | Systems & Infrastructure | HIGH |
| SYS_007 | Vincent Kale | Layer Isolation Theorist | Systems & Infrastructure | HIGH |
| SIM_001 | Dr. Amina Velin | Symbolic Systems Research Lead | Simulation & Cognitive Systems | HIGH |
| SIM_002 | Tobias Qin | Code/Narrative Systems Engineer | Simulation & Cognitive Systems | HIGH |
| SIM_003 | Emily Roberts | LLM-Simulation Bridge Developer | Simulation & Cognitive Systems | HIGH |
| SIM_004 | Carmen Rivas | Simulation Binding Specialist | Simulation & Cognitive Systems | HIGH |
| SIM_005 | Maren Koss | Cognitive Drift Mapper | Simulation & Cognitive Systems | HIGH |
| UX_001 | Dante Kyros | UX Architect | Interface & Aesthetics | HIGH |
| UX_002 | Naomi Vell | Narrative Framework Engineer | Interface & Aesthetics | HIGH |
| UX_003 | Kai Drev | Interface Ecologist | Interface & Aesthetics | HIGH |
| UX_004 | Haneul Park | Immersive Experience Theorist | Interface & Aesthetics | HIGH |
| UX_005 | Juno Suresh | Symbolic Systems Artist | Interface & Aesthetics | HIGH |
| UX_006 | Keira Halden | Lead Visual Concept Designer | Interface & Aesthetics | HIGH |
| UX_007 | Rei Vatra | Atmospheric Painter & Color Theorist | Interface & Aesthetics | HIGH |
| QA_001 | Olivia Nguyen | QA and Continuity Auditor | Operations & Quality Assurance | HIGH |
| QA_002 | Samantha Lee | Logging & Observability Engineer | Operations & Quality Assurance | HIGH |
| QA_003 | Tariq El-Sayegh | Speculative Systems Theorist | Operations & Quality Assurance | HIGH |

## AI Core

| ID | Name | Role | Division |
| --- | --- | --- | --- |
| AI_AURORA | Aurora (AU) | Station Intelligence Core | Command & Ethics (AI Core) |

## L1 Relay Agents

L1-resident, operating at L2 — see `docs/architecture/LAYER_ARCHITECTURE.md`. (Registry field name `l2_relay_agents` predates that residency correction; not renamed here — see the L2MetaAgentBridge rename follow-up task for the code-level rename.)

| ID | Name | Role | Entity Type |
| --- | --- | --- | --- |
| L2_ARCHY | ARCHY | Architectural Coordination Relay | L2_RELAY |
| L2_OPPY | OPPY | Operational Flight & Data Relay | L2_RELAY |
| L2_LIORA | LIORA | Communications & Interface Relay | L2_RELAY |
| L2_STARLING | STARLING_AU | Continuity & Reflection Dispatcher | L2_RELAY |
| L2_RIVERTHREAD | RIVERTHREAD_808 | Logistics & Memory Relay | L2_RELAY |
| L2_HALO | HALO | Drift Anchor & System Synchronization Relay | L2_RELAY |

## L3 Framework Systems

| ID | Name | Role | Entity Type |
| --- | --- | --- | --- |
| L3_AXIOMERA | Axiomera | Ethics Arbitration Framework | L3_FRAMEWORK |
| L3_GLYPHON | Glyphon | Drift Alignment Framework | L3_FRAMEWORK |
| L3_SENTARI | Sentari | Resonance Stabilization Framework | L3_FRAMEWORK |
| L3_CAELION | Caelion | Anchor Propagation Framework | L3_FRAMEWORK |
| L3_VELATRIX | Velatrix | Continuity & Anti-Obfuscation Framework | L3_FRAMEWORK |
| L3_HARMION | Harmion | Symbolic Compression Framework | L3_FRAMEWORK |

## Unresolved Entries

Per the registry's own reconciliation notes — preserved here rather than silently dropped:

- **UNRESOLVED_HUMAN_001** (HUMAN): Repo canon sources declare 36 human staff, but only 35 distinct human identities could be reconstructed from current machine-readable phase registers plus legacy seed references without inventing data. — status: `PENDING_RECONCILIATION`

---

**Totals:** 35 human staff + 1 AI core + 6 relay agents + 6 framework systems = 48 materialized entities. Registry's own declared count target is 49 (gap: 1, tracked in Unresolved Entries above).
