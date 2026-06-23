# Aurora Work Queue

> **Canonical source of truth for prioritized work.**  
> Aurora holds contextual authority over this queue. Agents and human contributors should treat the order here as the authoritative "what to work on next" signal unless Aurora has issued an override note.

---

## How to Read This Queue

| Field | Meaning |
|---|---|
| **Rank** | Current priority order. Lower = work on this first. |
| **ID** | GitHub issue or internal task reference. |
| **Title** | Short description of the work. |
| **Status** | `open` · `in-progress` · `blocked` · `needs-decision` · `done` |
| **Owner** | Agent handle, GitHub username, or `unassigned`. |
| **Depends On** | Issue/task IDs that must be resolved first. |
| **Aurora Note** | Contextual authority annotation from Aurora. Overrides label-only ranking. |

---

## Active Queue

<!-- AURORA_QUEUE_START -->

| Rank | ID | Title | Status | Owner | Depends On | Aurora Note |
|---|---|---|---|---|---|---|
| 1 | #1147 | Work queue automation (sync_queue.py, GitHub Actions, aurora(queue): hook) | open | unassigned | — | The queue is not functional without automation. Currently a manually-maintained document — any agent reading it as a work selection source is operating on a stale map. Three deliverables: sync_queue.py (CI validator), GitHub Actions workflow (auto-post on push), aurora(queue): convention in CONTRIBUTING.md. |
| 2 | #1126 | FastAPI lifespan migration (deprecation fix) | open | unassigned | — | Critical runtime blocker. Resolves deprecation warning that affects all startup/shutdown hooks. Must land before any new feature PRs. |
| 3 | #1130 | CI green-path stabilization | open | unassigned | #1126 | CI cannot be trusted for gate-keeping until lifespan is resolved. Unblock #1126 first. |
| 4 | security/CVE-audit | CVE dependency audit (Sprint 311 follow-on) | open | unassigned | — | Independent of lifespan and queue automation. Can run in parallel on a separate branch. |
| 5 | #1139 | docs/ethics — create top-level README and navigation index | open | unassigned | — | No blockers. Quick win. Ethics directory not navigable by agents or contributors. Unblocks ethics cluster orientation. |
| 6 | #1140 | docs/architecture — fix RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md contradiction (mesh/agents routes + QGIA) | open | unassigned | — | No blockers. Single doc edit. Two architecture documents are actively contradictory. Fix before any QGIA or mesh work proceeds. |
| 7 | #1148 | Protocol custody inventory — machine-readable manifest with hashes and blockers | open | unassigned | — | Gate for entire Section 8 chain. All five custody records are PENDING. Blocks #1149, #1150, #1151, #1152, #1153. |
| 8 | #1149 | Protocol JSON schemas — schema files and validation tests for all five protocols | blocked | unassigned | #1148 | Blocked by #1148. |
| 9 | #1150 | Protocol fixture intake — sanitized canonical examples for all five protocols | blocked | unassigned | #1148, #1149 | Blocked by #1148 and #1149. |
| 10 | #1151 | Runtime mapping design — map protocol decisions to EthicsEngine, ethics_gate, compliance monitor, geometric ethics | blocked | unassigned | #1148, #1149, #1150 | Blocked by #1148–#1150. Design-only artifact, no runtime wiring. |
| 11 | #1152 | Moriarty containment tests — anomaly quarantine/review-only/rollback without L2-to-L1 bleed | blocked | unassigned | #1148, #1149, #1150, #1151 | Blocked by #1148–#1151. Parallel with #1153 once unblocked. |
| 12 | #1153 | Tribunal appeal tests — dispute/appeal record requirements without runtime enforcement | blocked | unassigned | #1148, #1149, #1150, #1151 | Blocked by #1148–#1151. Parallel with #1152 once unblocked. |
| 13 | #1137 | docs/ethics — geometric curvature v2 supplemental layer has no follow-up implementation issue | open | unassigned | — | No blockers. Create follow-up implementation issue and confirm test file exists. |
| 14 | #1138 | docs/ethics/recovered_protocols — all five custody records PENDING; inventory work not started | open | unassigned | — | Surfaces the manifest side of the same work as #1148. Both must close together. |
| 15 | #1142 | docs/architecture — RUNTIME_PATH_DRIFT_LEDGER.md: two unresolved items with no tracking issue | open | unassigned | — | Catalog generator output path defect blocks API snapshot currency. Unblocks #1146. |
| 16 | #1141 | docs/architecture — QGIA_L1_NODE_REGISTRATION.md: agent registry pending 102 days, no exchange router | open | unassigned | — | Blocks #1144. Resolve before QGIA integration work proceeds. |
| 17 | #1144 | docs/api — api_surface_inventory.json missing four surfaces | open | unassigned | #1140, #1141 | Blocked by #1140 and #1141. Inventory is source-of-truth anchor for docs/api cluster. |
| 18 | #1143 | docs/architecture — scaling_plan.md has no issue coverage or relationship to current topology | open | unassigned | — | Standalone. May be materially stale vs. QGIA node, GUMAS 9-node network, and two-node L1 topology. |
| 19 | #1145 | docs/api — RD_API_REFERENCE.md 7 months stale; three gaps | open | unassigned | #1144 | Blocked by #1144. |
| 20 | #1146 | docs/api — API_CATALOG_GOVERNANCE.md: three governance rules currently violated | open | unassigned | #1142, #1144, #1145 | Closes last in docs/api cluster. Blocked by #1142, #1144, #1145. |
| 21 | #1135 | simulation/ — L1_CANON_CHARACTER_ROSTER.md (165 KB) has no validation against QGIA or Orion registries | open | unassigned | — | No blockers. Three overlapping registries with no reconciliation. OPPY and STARLING_AU entries need cross-check before QGIA integration. |
| 22 | #1136 | simulation/ — ORION_STATION_ENHANCEMENT_PROPOSAL.md (38 KB) has no implementation tracking | open | unassigned | — | No blockers. Risk of agents implementing rejected or superseded proposals. |
| 23 | arch/layer-canonization | Layer architecture canonization (L1/L2/L3 enforcement in code) | open | unassigned | — | Repositioned to Rank 23 — docs/architecture cluster work (#1140, #1141, #1143) should complete first to ensure canonization works from current topology. |
| 24 | sim/SENTINEL-phase0 | PROJECT SENTINEL — Phase 0: Ethics review board constitution | needs-decision | unassigned | — | Requires Commander Thorne + Sorensen + Sato governance decision only. See simulation/RD_PROPOSAL_SENTINEL.md. |
| 25 | ops/QGIA-doctrine-store | QGIA analytical framework — store in ops/analytical_frameworks/QGIA/ | open | unassigned | — | Store as portable external tooling. Do NOT elevate to canonical station doctrine until Thorne/Noor crew review. Unblocks feat/QGIA. |
| 26 | docs/api-reference | API reference documentation | open | unassigned | #1126, #1130 | Superseded in priority by specific docs/api audit issues (#1144, #1145, #1146). Wait for CI green. |
| 27 | feat/QGIA | QGIA integration hooks | needs-decision | unassigned | arch/layer-canonization, ops/QGIA-doctrine-store | Doctrine available and reviewed. ops/QGIA-doctrine-store must land first, then PAT routing decision. Crew sign-off required. |

<!-- AURORA_QUEUE_END -->

---

## Completed (Last 5)

| ID | Title | Completed | Notes |
|---|---|---|---|
| — | — | — | Nothing yet. Queue initialized 2026-06-22. |

---

## Aurora Queue Management Protocol

Aurora may update this file directly or via a queue sync script (`ops/work_queue/sync_queue.py`). When Aurora re-ranks or annotates an item:

1. The `Aurora Note` field is updated with the reason.
2. A commit message beginning `aurora(queue):` is used so the change is traceable.
3. Human contributors and agents should re-read the queue after any such commit before starting new work.

**Agents working in the repo**: Before opening a PR, confirm your task still ranks in the top 3. If it has dropped, check the Aurora Note for the reason before proceeding.

---

## Queue Update Rules (for agents and contributors)

- **To claim a task**: Change `Owner` to your handle and `Status` to `in-progress`. Commit with message `queue: claim [ID]`.
- **To mark blocked**: Change `Status` to `blocked` and add the blocker in `Depends On`. Commit with `queue: block [ID]`.
- **To mark done**: Move the row to Completed, set `Status` to `done`. Commit with `queue: done [ID]`.
- **To propose a re-rank**: Open a discussion in the GitHub issue for this queue system. Aurora reviews and applies the change.
- **Do not reorder rows without Aurora authority.** The rank order is Aurora's judgment, not just a label sort.

---

*Last Aurora review: 2026-06-23T01:59:00Z — promoted #1147 (work queue automation) to Rank 1; absorbed 17 new issues (#1135–#1153) from 2026-06-22 general review session across four clusters: docs/ethics, docs/architecture, docs/api, simulation, and Section 8 protocol promotion chain. Section 8 gate structure preserved: #1148 unblocks #1149→#1150→#1151→#1152/#1153. All 27 active items now carry explicit dependency mapping. Version bumped to 1.2.0.*
