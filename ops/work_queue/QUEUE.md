<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Source of truth: ops/work_queue/queue.json
     Regenerate:      python ops/work_queue/sync_queue.py
     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->

# Aurora Work Queue

**Schema version:** `1.3.0`
**Last Aurora review:** `2026-07-16T00:36:36Z`
**Generated:** `2026-07-16T00:36:36Z`
**Items:** 10 active · 21 completed

> Aurora holds contextual authority over rank order.
> Do not edit rank or `aurora_note` fields without an `aurora(queue):` commit.
> Edit `queue.json` then run `python ops/work_queue/sync_queue.py`.

---

## Active Queue

### 1. 🟢 security/CVE-audit — CVE dependency audit (Sprint 311 follow-on)

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

### 2. 🟢 arch/layer-canonization — Layer architecture canonization (L1/L2/L3 enforcement in code)

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

### 3. 🟡 sim/SENTINEL-phase0 — PROJECT SENTINEL — Phase 0: Ethics review board constitution

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

### 4. 🟢 ops/QGIA-doctrine-store — QGIA analytical framework — store in ops/analytical_frameworks/QGIA/

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

### 5. 🟢 docs/api-reference — API reference documentation

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `docs` `api` |

**Aurora note:**

> The specific docs/API audit issues #1144, #1145, and #1146 and pentest scope issue #1130 are complete. Refresh the live API inventory before starting so documentation targets current main.

---

### 6. 🟡 feat/QGIA — QGIA integration hooks

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

### 7. 🟢 #1329 — Prevent AI model catalog drift: validate model IDs and capabilities against provider catalogs

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `blocking` `ci` `needs info` `owner-decision` |

**Aurora note:**

> auto-ingested from GitHub labels — awaiting Aurora triage; priority_score is advisory, rank is tail placement only

---

### 8. 🟢 #1233 — Ethics documentation follow-ups (consolidated)

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `backlog` `documentation` `ethics` `implementation-needed` `needs info` `security` |

**Aurora note:**

> auto-ingested from GitHub labels — awaiting Aurora triage; priority_score is advisory, rank is tail placement only

---

### 9. 🟢 #1361 — security: resolve SHADOWFAX identity and custody ambiguity across ORD runtime surfaces

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `audit-integrity` `high-priority` `needs info` `owner-decision` `security` |

**Aurora note:**

> auto-ingested from GitHub labels — awaiting Aurora triage; priority_score is advisory, rank is tail placement only

---

### 10. 🟢 #1530 — security(playground): fail closed when isolated sandbox runtime is unavailable

| Field | Value |
|---|---|
| **Status** | `open` |
| **Owner** | _unassigned_ |
| **Depends on** | — |
| **Blocks** | — |
| **Tags** | `bug` `security` |

**Aurora note:**

> auto-ingested from GitHub labels — awaiting Aurora triage; priority_score is advisory, rank is tail placement only

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
| #1130 | SECURITY — pentest scope is stale against the current API surface |
| #1139 | docs/ethics — create top-level README and navigation index |
| #1140 | docs/architecture — fix RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md contradiction re: mesh/agents routes and QGIA |
| #1137 | docs/ethics — geometric curvature v2 supplemental warning layer has no follow-up implementation issue |
| #1138 | docs/ethics/recovered_protocols — all five custody records PENDING; custody inventory work not started |
| #1142 | docs/architecture — RUNTIME_PATH_DRIFT_LEDGER.md: two unresolved items with no tracking issue |
| #1141 | docs/architecture — QGIA_L1_NODE_REGISTRATION.md: agent registry pending 102 days, no exchange router defined |
| #1144 | docs/api — api_surface_inventory.json missing four surfaces |
| #1143 | docs/architecture — scaling_plan.md has no issue coverage and no relationship to current runtime topology |
| #1145 | docs/api — RD_API_REFERENCE.md version 1.0.0 (2025-11-12, 7 months stale); three gaps |
| #1146 | docs/api — API_CATALOG_GOVERNANCE.md: three governance rules currently violated |
| #1135 | simulation/ — L1_CANON_CHARACTER_ROSTER.md (165 KB) has no validation against QGIA or Orion registries |
| #1136 | simulation/ — ORION_STATION_ENHANCEMENT_PROPOSAL.md (38 KB) has no implementation tracking |
