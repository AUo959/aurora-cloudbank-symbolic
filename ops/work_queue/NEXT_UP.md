<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Source of truth: ops/work_queue/queue.json
     Regenerate:      python ops/work_queue/sync_queue.py
     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->

# Next Up — Aurora Work Queue

_Generated: `2026-06-23T22:43:00Z` — edit `queue.json`, run `sync_queue.py`_

---

## 🟢 Ready to Work

Items with `status: open` and all dependencies resolved.

| Rank | ID | Title | Tags |
|---|---|---|---|
| 1 | #1147 | Work queue automation (sync_queue.py, GitHub Actions, aurora(queue): hook) | `ops` `automation` `coordination` `blocker` |
| 2 | #1126 | FastAPI lifespan migration (deprecation fix) | `runtime` `blocker` `deprecation` |
| 4 | security/CVE-audit | CVE dependency audit (Sprint 311 follow-on) | `security` `audit` |
| 5 | #1139 | docs/ethics — create top-level README and navigation index | `docs` `ethics` `navigation` |
| 6 | #1140 | docs/architecture — fix RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md contradiction re: mesh/agents routes and QGIA | `docs` `architecture` `topology` |
| 7 | #1148 | Protocol custody inventory — machine-readable manifest of recovered package/file hashes and blockers | `ethics` `protocols` `custody` `gate` |
| 13 | #1137 | docs/ethics — geometric curvature v2 supplemental warning layer has no follow-up implementation issue | `ethics` `geometric` `implementation` |
| 14 | #1138 | docs/ethics/recovered_protocols — all five custody records PENDING; custody inventory work not started | `ethics` `protocols` `custody` |
| 15 | #1142 | docs/architecture — RUNTIME_PATH_DRIFT_LEDGER.md: two unresolved items with no tracking issue | `docs` `architecture` `drift-ledger` |
| 16 | #1141 | docs/architecture — QGIA_L1_NODE_REGISTRATION.md: agent registry pending 102 days, no exchange router defined | `docs` `architecture` `QGIA` |
| 18 | #1143 | docs/architecture — scaling_plan.md has no issue coverage and no relationship to current runtime topology | `docs` `architecture` `scaling` |
| 21 | #1135 | simulation/ — L1_CANON_CHARACTER_ROSTER.md (165 KB) has no validation against QGIA or Orion registries | `simulation` `roster` `validation` |
| 22 | #1136 | simulation/ — ORION_STATION_ENHANCEMENT_PROPOSAL.md (38 KB) has no implementation tracking | `simulation` `enhancement` `tracking` |
| 23 | arch/layer-canonization | Layer architecture canonization (L1/L2/L3 enforcement in code) | `architecture` `canonical` `L1` `L2` `L3` |
| 25 | ops/QGIA-doctrine-store | QGIA analytical framework — store in ops/analytical_frameworks/QGIA/ | `QGIA` `analytical-framework` `ops` `non-canonical` |
| 26 | docs/api-reference | API reference documentation | `docs` `api` |

---

## 🔴 Blocked

Items waiting on dependencies. Do not start until blockers close.

| Rank | ID | Title | Blocked By |
|---|---|---|---|
| 3 | #1130 | CI green-path stabilization | #1126 |
| 8 | #1149 | Protocol JSON schemas — add schema files and validation tests for all five protocols | #1148 |
| 9 | #1150 | Protocol fixture intake — sanitized canonical examples for all five protocols | #1148, #1149 |
| 10 | #1151 | Runtime mapping design — map protocol decisions to EthicsEngine, ethics_gate, compliance monitor, geometric ethics | #1148, #1149, #1150 |
| 11 | #1152 | Moriarty containment tests — anomaly quarantine/review-only/rollback without L2-to-L1 bleed | #1148, #1149, #1150, #1151 |
| 12 | #1153 | Tribunal appeal tests — dispute/appeal record requirements without runtime enforcement | #1148, #1149, #1150, #1151 |
| 17 | #1144 | docs/api — api_surface_inventory.json missing four surfaces | #1140, #1141 |
| 19 | #1145 | docs/api — RD_API_REFERENCE.md version 1.0.0 (2025-11-12, 7 months stale); three gaps | #1144 |
| 20 | #1146 | docs/api — API_CATALOG_GOVERNANCE.md: three governance rules currently violated | #1142, #1144, #1145 |

---

## 🟡 Needs Decision

Items gated on a human or governance decision. Agents skip these.

| Rank | ID | Title |
|---|---|---|
| 24 | sim/SENTINEL-phase0 | PROJECT SENTINEL — Phase 0: Ethics review board constitution |
| 27 | feat/QGIA | QGIA integration hooks |
