<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Source of truth: ops/work_queue/queue.json
     Regenerate:      python ops/work_queue/sync_queue.py
     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->

# Aurora Work Queue

**Schema version:** `1.3.0`
**Last Aurora review:** `2026-07-13T05:57:19Z`
**Generated:** `2026-07-13T05:57:19Z`
**Items:** 19 active · 8 completed

> Aurora holds contextual authority over rank order.
> Do not edit rank or `aurora_note` fields without an `aurora(queue):` commit.
> Edit `queue.json` then run `python ops/work_queue/sync_queue.py`.

---

## Active Queue

### 1. 🟢 #1130 — SECURITY — pentest scope is stale against the current API surface

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | docs/api-reference |
| **Tags** | `security` `pentest` `api-surface` `blocking` |

**Aurora note:**

> Live GitHub refresh on 2026-07-13 confirmed this pre-engagement security issue remains open. The former #1126 dependency is complete; remaining work includes the v2 scope, current API inventory alignment, QGIA/R&D disposition, and approval signatures.

---

### 2. 🟢 security/CVE-audit — CVE dependency audit (Sprint 311 follow-on)

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

### 3. 🟢 #1139 — docs/ethics — create top-level README and navigation index

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

### 4. 🟢 #1140 — docs/architecture — fix RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md contradiction re: mesh/agents routes and QGIA

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

### 5. 🟢 #1137 — docs/ethics — geometric curvature v2 supplemental warning layer has no follow-up implementation issue

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

### 6. 🟢 #1138 — docs/ethics/recovered_protocols — all five custody records PENDING; custody inventory work not started

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `ethics` `protocols` `custody` |

**Aurora note:**

> Partially superseded by completed #1148, #1149, and #1150: custody fixture, schema, and sanitized fixture scaffolding now exist. Remaining live work is true custody verification: source/internal SHA resolution, verified_at/verified_by fields, and SHADOWFAX standalone bundle disposition.

---

### 7. 🟢 #1142 — docs/architecture — RUNTIME_PATH_DRIFT_LEDGER.md: two unresolved items with no tracking issue

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

### 8. 🟢 #1141 — docs/architecture — QGIA_L1_NODE_REGISTRATION.md: agent registry pending 102 days, no exchange router defined

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

### 9. 🟢 #1144 — docs/api — api_surface_inventory.json missing four surfaces

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

### 10. 🟢 #1143 — docs/architecture — scaling_plan.md has no issue coverage and no relationship to current runtime topology

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

### 11. 🟢 #1145 — docs/api — RD_API_REFERENCE.md version 1.0.0 (2025-11-12, 7 months stale); three gaps

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

### 12. 🟢 #1146 — docs/api — API_CATALOG_GOVERNANCE.md: three governance rules currently violated

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

### 13. 🟢 #1135 — simulation/ — L1_CANON_CHARACTER_ROSTER.md (165 KB) has no validation against QGIA or Orion registries

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

### 14. 🟢 #1136 — simulation/ — ORION_STATION_ENHANCEMENT_PROPOSAL.md (38 KB) has no implementation tracking

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

### 15. 🟢 arch/layer-canonization — Layer architecture canonization (L1/L2/L3 enforcement in code)

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | feat/QGIA |
| **Tags** | `architecture` `canonical` `L1` `L2` `L3` |

**Aurora note:**

> Ensures no code path violates the canonical layer definitions. Foundational for all new agent work. Repositioned after docs/architecture cluster work (#1140, #1141, #1143) so canonization works from current topology.

---

### 16. 🟡 sim/SENTINEL-phase0 — PROJECT SENTINEL — Phase 0: Ethics review board constitution

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

### 17. 🟢 ops/QGIA-doctrine-store — QGIA analytical framework — store in ops/analytical_frameworks/QGIA/

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

### 18. 🟢 docs/api-reference — API reference documentation

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | #1130 |
| **Blocks** | — |
| **Tags** | `docs` `api` |

**Aurora note:**

> Do not write API docs against a moving target. Wait for CI green. Superseded in priority by the specific docs/api audit issues (#1144, #1145, #1146) which address the same surface with more precision.

---

### 19. 🟡 feat/QGIA — QGIA integration hooks

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

## Completed

| ID | Title |
|---|---|
| #1126 | docs/specs/AUMEMMANAGER_PROMOTION_STARTER_SPEC.md — confirm promotion status and link to recovered_protocols/ |
| #1147 | feat: Aurora-Aware Work Queue System (ops/work_queue/) |
| #1148 | Protocol custody inventory — machine-readable manifest of recovered package/file hashes and blockers |
| #1149 | Protocol JSON schemas — add schema files and validation tests for Sherlock, Watson, Moriarty, Tribunal, SHADOWFAX |
| #1150 | Protocol fixture intake — add sanitized canonical examples for Sherlock, Watson, Moriarty, Tribunal, SHADOWFAX |
| #1151 | Runtime mapping design — decide how protocol decisions map to EthicsEngine, ethics_gate, compliance monitor, and geometric ethics |
| #1152 | Moriarty containment tests — test anomaly quarantine/review-only/rollback rules without enabling active L2-to-L1 behavior |
| #1153 | Tribunal appeal tests — test dispute/appeal record requirements without runtime enforcement |
