# PROJECT SENTINEL — Canonical Architecture

**Status:** CANONICAL ARCHITECTURE — v1.0
**Supersedes:** `simulation/RD_PROPOSAL_SENTINEL.md` (NON-CANONICAL R&D Proposal, submitted 2026-04-09) as the authoritative status reference. The R&D document remains the historical record of the original proposal and rationale.
**Promoted:** 2026-07-13 (issue #1069)
**Anchors:** `T1-SENTINEL-001` (ethics/self-audit streams), `T1-RSD-002` (monitoring dashboard, `modules/resilience_sentinel/`)

## Summary

*Situational Ethics & Neural-Telemetry Integration for Networked Exploratory Leadership* (SENTINEL) is a three-stream crew-wellness and AI-integrity program. Two of its three streams are already operational in code; this document promotes the system's documentation status to match that reality and formally records what remains.

## Streams

| Stream | Description | Status | Implementation |
| --- | --- | --- | --- |
| 1 — Crew Cognitive Load Monitoring | HRV/cortisol-proxy biometric signals, aggregated and anonymized by default | **Stub — not wired** | `src/sensors/crew_load/` |
| 2 — AI Self-Audit | Reasoning-drift detection, entropy measurement, sentinel-risk mapping | **Operational** | `services/nemo_service/symbolic_bridge.py`, `src/sensors/observatory/symbolic/ethical_signal.py`, `src/sensors/constants.py` |
| 3 — Ethics Overlay | Picard_Delta_3 charter enforcement, GUMAS ethics audit log, consent hooks | **Operational** | `ethics/`, `symbolic_config.yaml` |

Stream 1+2 monitoring surfaces are additionally exposed via the Resilience Sentinel Dashboard (`modules/resilience_sentinel/`, anchor `T1-RSD-002`, 16+ live endpoints at `/sentinel/*`, now including the Stream 1 status stub at `/sentinel/crew-load/status`).

## Layer boundary (hard constraint)

**Crew cognitive-load data is never performance data.** Stream 1 exists to support crew wellbeing and safety, not evaluation. This constraint is structural, not a policy note to be revisited per-deployment:

- Stream 1 sensors (`src/sensors/crew_load/`) emit aggregated/anonymized values by default.
- No Stream 1 metric may be joined, correlated, or reported against any individual's performance record, review, or evaluation surface.
- `/sentinel/crew-load/status` currently reports registration state only (no live readings) — it cannot leak individual biometric data because no provider is wired yet. Any future provider wiring must preserve the aggregation-by-default posture before this endpoint returns live values.
- Opt-out: crew members may decline Stream 1 monitoring; declining must not affect standing, assignment, or evaluation. The original proposal cites a consent-hook file (`ethics_subroutine_v2.1.json`) for this — that file does not exist anywhere in the current repo. Stream 3's consent handling runs through the live `ethics/` stack instead; Stream 1 has no consent hook of its own yet since it has no live data path to opt out of. Flagged as an open follow-up, not asserted as done.

## Ethics review record

Per the original proposal's routing (CC: Dr. Amira Sato — Ethics & Governance; CC: Axiomera — L3 Ethics Arbitration), Stream 3's live ethics-audit path already runs through the existing `EthicsEngine`/`GeometricEthics` stack under the Picard_Delta_3 charter. No separate SENTINEL-specific ethics board was convened as a distinct body — review occurred as part of standard system-design ethics gating. This document records that as the formal review basis for canonical promotion; it does not retroactively invent a board that did not meet.

## Governance registration

**Coordinator entity:** `SENTINEL-COORDINATOR`, registered in `constellation-contracts/manifests/sentinel-coordinator.manifest.json`, governed under Picard_Delta_3 alongside the other constellation spokes.

**L3 audit authority:** **Axiomera** (Ethics Arbitration Framework, `L3_AXIOMERA`) is the named L3 audit authority for SENTINEL events. This is recorded in the coordinator manifest's `governance.primary_audit_authority` field.

*Registration note:* the original acceptance criteria for this promotion (issue #1069) asked for entries in `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` and `threadcore_registry.json`. Neither file's actual schema fits a program/system entity like SENTINEL — the staff registry is a closed personnel census (36 human + 1 AI core + 5 relay + 1 HALO continuity system-entity + 6 framework = 49 tracked entities, with its own reconciliation notes warning against inventing entries), and `threadcore_registry.json` is a ThreadCore *payload*-version registry, not an event-routing table. HALO is included because `HALOEntity` is its established living interface; that does not make the registry a general system catalog. Rather than force a mismatched SENTINEL entry into either registry, SENTINEL's governance registration lives here and in the constellation manifest, which is schema-appropriate for a system/program entity.

## Sponsoring staff

Per the original 2026-04-09 proposal, cross-checked against `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` (canonical titles used below where they differ from the proposal's informal phrasing):

| Name | Canonical role | Registry ID |
| --- | --- | --- |
| Alex Thorne | Commander, Orion Station | CMD_001 |
| Maya Shepard | Executive Officer | CMD_002 |
| Dr. Elira Noor | Lead Reflexivity Specialist | ETH_002 |
| Prof. Elena Sorensen | Cognitive Ethicist (Advisor) | ETH_003 |
| Dr. Amira Sato | Chief Ethics Officer (Legacy Core) | — |
| Lt. Julian Markov | Chief Security Officer (Legacy Core) | — |
| Jiro Tanaka | Chief Engineering Officer (Legacy Core) | — |
| Varya Lin | Chief Science Officer (Legacy Core) | — |
| Helena Vu | Cultural & HR Director | HR_001 |
| Dr. Ren Feldman | Chief Medical Officer (Legacy Core) | — |
| Leena Porter | Bridge Operations Officer (Legacy Core) | — |

## Remaining work

- Wire a real biometric provider to `src/sensors/crew_load/` (Medical division / Dr. Vasquez) — Stream 1 stays a stub until then.
- Define Stream 1's own consent/opt-out hook (Stream 3's exists; Stream 1's does not, since there is no live data path yet to opt out of).
- `docs/api/api_surface_inventory.json` should list `/sentinel/crew-load/status` once the broader API surface inventory work (#1204) covers this router.
