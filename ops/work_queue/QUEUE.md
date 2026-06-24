<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Source of truth: ops/work_queue/queue.json
     Regenerate:      python ops/work_queue/sync_queue.py
     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->

# Aurora Work Queue

**Schema version:** `1.2.0`  
**Last Aurora review:** `2026-06-23T01:59:00Z`  
**Generated:** `2026-06-23T22:43:00Z`  
**Items:** 27 active · 0 completed

> Aurora holds contextual authority over rank order.
> Do not edit rank or `aurora_note` fields without an `aurora(queue):` commit.
> Edit `queue.json` then run `python ops/work_queue/sync_queue.py`.

---

## Active Queue

### 1. 🟢 #1147 — Work queue automation (sync_queue.py, GitHub Actions, aurora(queue): hook)

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `ops` `automation` `coordination` `blocker` |

**Aurora note:**

> The queue is not functional without automation. It is currently a manually-maintained document — any agent reading it as a work selection source is operating on a stale map. This must land before the queue can be trusted as a coordination layer for anything else. Three deliverables: sync_queue.py (CI validator), GitHub Actions workflow (auto-post on push), aurora(queue): convention in CONTRIBUTING.md.

---

### 2. 🟢 #1126 — FastAPI lifespan migration (deprecation fix)

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | #1130, docs/api-reference |
| **Tags** | `runtime` `blocker` `deprecation` |

**Aurora note:**

> Critical runtime blocker. Resolves deprecation warning that affects all startup/shutdown hooks. Must land before any new feature PRs.

---

### 3. 🟢 #1130 — CI green-path stabilization

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | #1126 |
| **Blocks** | docs/api-reference |
| **Tags** | `ci` `infrastructure` |

**Aurora note:**

> CI cannot be trusted for gate-keeping until lifespan is resolved. Unblock #1126 first.

---

### 4. 🟢 security/CVE-audit — CVE dependency audit (Sprint 311 follow-on)

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `security` `audit` |

**Aurora note:**

> Independent of lifespan and queue automation. Can run in parallel on a separate branch.

---

### 5. 🟢 #1139 — docs/ethics — create top-level README and navigation index

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `docs` `ethics` `navigation` |

**Aurora note:**

> No blockers. Quick win. Ethics directory is not navigable by agents or contributors — no map to runtime surfaces, recovered protocols, or Picard_Delta_3. Unblocks all ethics cluster work that depends on directory orientation.

---

### 6. 🟢 #1140 — docs/architecture — fix RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md contradiction re: mesh/agents routes and QGIA

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | #1144 |
| **Tags** | `docs` `architecture` `topology` |

**Aurora note:**

> No blockers. Single doc edit — mesh/agents routes are canonical per PR #1011 but the topology doc still marks them as drift. Two documents are actively contradictory. Any agent loading the topology doc gets wrong information. Fix before any QGIA or mesh work proceeds.

---

### 7. 🟢 #1148 — Protocol custody inventory — machine-readable manifest of recovered package/file hashes and blockers

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | #1149, #1150, #1151, #1152, #1153 |
| **Tags** | `ethics` `protocols` `custody` `gate` |

**Aurora note:**

> Gate for the entire Section 8 protocol promotion chain. All five protocol custody records are PENDING — no SHA verification has been performed. Blocks #1149, #1150, #1151, #1152, #1153. Nothing in the recovered protocol chain can advance until this closes.

---

### 8. 🔴 #1149 — Protocol JSON schemas — add schema files and validation tests for all five protocols

| Field | Value |
|---|---|
| **Status** | `blocked` |
| **Owner** | _unassigned_ |
| **Depends on** | #1148 |
| **Blocks** | #1150, #1151, #1152, #1153 |
| **Tags** | `ethics` `protocols` `schemas` |

**Aurora note:**

> Blocked by #1148 (custody inventory). Schemas cannot be finalized until custody classification is confirmed for each protocol artifact.

---

### 9. 🔴 #1150 — Protocol fixture intake — sanitized canonical examples for all five protocols

| Field | Value |
|---|---|
| **Status** | `blocked` |
| **Owner** | _unassigned_ |
| **Depends on** | #1148, #1149 |
| **Blocks** | #1151, #1152, #1153 |
| **Tags** | `ethics` `protocols` `fixtures` |

**Aurora note:**

> Blocked by #1148 and #1149. Fixtures must validate against schemas from #1149 and must not promote raw recovered payloads without custody review.

---

### 10. 🔴 #1151 — Runtime mapping design — map protocol decisions to EthicsEngine, ethics_gate, compliance monitor, geometric ethics

| Field | Value |
|---|---|
| **Status** | `blocked` |
| **Owner** | _unassigned_ |
| **Depends on** | #1148, #1149, #1150 |
| **Blocks** | #1152, #1153 |
| **Tags** | `ethics` `protocols` `runtime` `design` |

**Aurora note:**

> Blocked by #1148–#1150. Design-only artifact — no runtime wiring. Must not begin until artifacts are custody-verified.

---

### 11. 🔴 #1152 — Moriarty containment tests — anomaly quarantine/review-only/rollback without L2-to-L1 bleed

| Field | Value |
|---|---|
| **Status** | `blocked` |
| **Owner** | _unassigned_ |
| **Depends on** | #1148, #1149, #1150, #1151 |
| **Blocks** | — |
| **Tags** | `ethics` `protocols` `moriarty` `tests` |

**Aurora note:**

> Blocked by #1148–#1151. Tests run against fixtures from #1150, not raw recovered payloads. No active L2-to-L1 behavior introduced.

---

### 12. 🔴 #1153 — Tribunal appeal tests — dispute/appeal record requirements without runtime enforcement

| Field | Value |
|---|---|
| **Status** | `blocked` |
| **Owner** | _unassigned_ |
| **Depends on** | #1148, #1149, #1150, #1151 |
| **Blocks** | — |
| **Tags** | `ethics` `protocols` `tribunal` `tests` |

**Aurora note:**

> Blocked by #1148–#1151. Parallel with #1152 once unblocked. No runtime enforcement wiring introduced.

---

### 13. 🟢 #1137 — docs/ethics — geometric curvature v2 supplemental warning layer has no follow-up implementation issue

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `ethics` `geometric` `implementation` |

**Aurora note:**

> No blockers. Evaluation concluded v2 provides genuine signal for cases 3.4 and 3.5. Implementation work (FieldCurvatureV2, advisory wiring, get_formation_statistics additions) has never been tracked. Create follow-up implementation issue and confirm test file exists.

---

### 14. 🟢 #1138 — docs/ethics/recovered_protocols — all five custody records PENDING; custody inventory work not started

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `ethics` `protocols` `custody` |

**Aurora note:**

> Surfaces the manifest side of the same work as #1148. Both must close together. Locate source packages, compute SHAs, record verified_at/verified_by. SHADOWFAX is a hard block — standalone bundle must be located or formally recorded as missing dependency.

---

### 15. 🟢 #1142 — docs/architecture — RUNTIME_PATH_DRIFT_LEDGER.md: two unresolved items with no tracking issue

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | #1146 |
| **Tags** | `docs` `architecture` `drift-ledger` |

**Aurora note:**

> Two unresolved items: mesh_api.js disposition decision and generate_api_catalog.py output path drift. The catalog generator defect directly blocks API snapshot currency. Fix output path before any API doc work proceeds. Unblocks #1146.

---

### 16. 🟢 #1141 — docs/architecture — QGIA_L1_NODE_REGISTRATION.md: agent registry pending 102 days, no exchange router defined

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | #1144 |
| **Tags** | `docs` `architecture` `QGIA` |

**Aurora note:**

> qgia_agent_registry_full.json has been pending commit for 102 days. No runtime router surface defined for the inter-node exchange protocol. Blocks #1144 (inventory missing surfaces). Resolve before QGIA integration work proceeds.

---

### 17. 🔴 #1144 — docs/api — api_surface_inventory.json missing four surfaces

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | #1140, #1141 |
| **Blocks** | #1145, #1146 |
| **Tags** | `docs` `api` `inventory` |

**Aurora note:**

> Blocked by #1140 (topology contradiction) and #1141 (QGIA router undefined). Four missing surfaces: /api/mesh/agents, /api/qgia, PAT routes, Consent Architecture v3.1. Inventory is the source-of-truth anchor for the entire docs/api cluster.

---

### 18. 🟢 #1143 — docs/architecture — scaling_plan.md has no issue coverage and no relationship to current runtime topology

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `docs` `architecture` `scaling` |

**Aurora note:**

> Standalone. No blockers. scaling_plan.md has no last_reviewed date, no version marker, and no stated relationship to the QGIA node, GUMAS 9-node L2 network, or current two-node L1 topology. May be materially stale.

---

### 19. 🔴 #1145 — docs/api — RD_API_REFERENCE.md version 1.0.0 (2025-11-12, 7 months stale); three gaps

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | #1144 |
| **Blocks** | #1146 |
| **Tags** | `docs` `api` `reference` |

**Aurora note:**

> Blocked by #1144 (inventory must be current before reference doc is updated). Three gaps: Consent Architecture v3.1 status unknown, HR module version header stale, no token budget cross-reference for compute-intensive endpoints.

---

### 20. 🔴 #1146 — docs/api — API_CATALOG_GOVERNANCE.md: three governance rules currently violated

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | #1142, #1144, #1145 |
| **Blocks** | — |
| **Tags** | `docs` `api` `governance` |

**Aurora note:**

> Governance self-audit. Closes last in the docs/api cluster after #1142, #1144, and #1145 are resolved. Three violations: snapshot currency not self-enforcing, test_api_surface_inventory.py is schema-only not coverage, review cadence conditions met but review not triggered.

---

### 21. 🟢 #1135 — simulation/ — L1_CANON_CHARACTER_ROSTER.md (165 KB) has no validation against QGIA or Orion registries

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `simulation` `roster` `validation` |

**Aurora note:**

> No blockers. Three overlapping roster documents with no stated reconciliation or authoritative source. 165 KB is not a maintainable document size. OPPY and STARLING_AU entries need cross-check across registries before QGIA integration work.

---

### 22. 🟢 #1136 — simulation/ — ORION_STATION_ENHANCEMENT_PROPOSAL.md (38 KB) has no implementation tracking

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `simulation` `enhancement` `tracking` |

**Aurora note:**

> No blockers. 38 KB proposal with no acceptance status, no issue linkage, and no reference from CANON_INDEX.md. Risk of agents implementing rejected or superseded proposals. Needs per-enhancement status recorded.

---

### 23. 🟢 arch/layer-canonization — Layer architecture canonization (L1/L2/L3 enforcement in code)

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | feat/QGIA |
| **Tags** | `architecture` `canonical` `L1` `L2` `L3` |

**Aurora note:**

> Ensures no code path violates the canonical layer definitions. Foundational for all new agent work. Repositioned to Rank 23 — docs/architecture cluster work (#1140, #1141, #1143) should complete first to ensure canonization is working from current topology.

---

### 24. 🟡 sim/SENTINEL-phase0 — PROJECT SENTINEL — Phase 0: Ethics review board constitution

| Field | Value |
|---|---|
| **Status** | `needs-decision` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `simulation` `ethics` `SENTINEL` `governance` `Picard_Delta_3` |

**Aurora note:**

> No engineering blocking condition. Requires Commander Thorne + Sorensen + Sato governance decision only. Phase 0 deliverable: ethics review board constituted and layer boundary document drafted. See simulation/RD_PROPOSAL_SENTINEL.md.

---

### 25. 🟢 ops/QGIA-doctrine-store — QGIA analytical framework — store in ops/analytical_frameworks/QGIA/

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | feat/QGIA |
| **Tags** | `QGIA` `analytical-framework` `ops` `non-canonical` |

**Aurora note:**

> QGIA Runtime One-Pager v4.2.1 and Axiom Doctrine Narrative v1.0 reviewed 2026-06-22. Store as portable external tooling in ops/analytical_frameworks/QGIA/. Do NOT elevate to canonical station doctrine until Thorne/Noor crew review. Unblocks feat/QGIA.

---

### 26. 🟢 docs/api-reference — API reference documentation

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | #1126, #1130 |
| **Blocks** | — |
| **Tags** | `docs` `api` |

**Aurora note:**

> Do not write API docs against a moving target. Wait for CI green. Superseded in priority by the specific docs/api audit issues (#1144, #1145, #1146) which address the same surface with more precision.

---

### 27. 🟡 feat/QGIA — QGIA integration hooks

| Field | Value |
|---|---|
| **Status** | `needs-decision` |
| **Owner** | _unassigned_ |
| **Depends on** | arch/layer-canonization, ops/QGIA-doctrine-store |
| **Blocks** | — |
| **Tags** | `feature` `QGIA` `PAT` `integration` |

**Aurora note:**

> Doctrine now available (QGIA Runtime One-Pager v4.2.1 + Axiom Doctrine Narrative v1.0, reviewed 2026-06-22). Two-layer discipline maps cleanly to Triplex Handshake. ops/QGIA-doctrine-store must land first, then PAT routing decision. Crew sign-off required before any QGIA axiom becomes operationally binding.

---
