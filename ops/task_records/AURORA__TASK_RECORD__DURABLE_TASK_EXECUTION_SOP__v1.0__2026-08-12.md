# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-durable-task-execution-sop`  
**Version:** `v1.0`  
**Created:** `2026-08-12`  
**Status:** `waiting_review`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `docs/durable-task-execution-sop`  
**Queue ID:** `none`  
**Issue:** `none`  
**PR:** `#1508`  
**Creation commit:** `2ce943547d6d7c7e35f86ced55baf9700dfef97a`  
**Controlling revision:** `this file v1.0 on PR #1508`

---

## 1. Objective

Establish a repo-wide operating rule that substantial Aurora implementation work has a committed, durable execution reference before substantive mutation begins, so handoffs are continuity aids rather than the sole carrier of intent.

## 2. Acceptance statement

This task is complete when:

- a repo-wide Durable Task Execution Record SOP is committed;
- a reusable DTER template is committed;
- the CloudBank work-queue guide references the DTER as part of the standard operating chain;
- the SOP clearly distinguishes queue, claim/handoff, DTER, plans/specs, implementation evidence, and PR/review authority;
- destructive operations are explicitly separated from advisory classification;
- a draft PR exposes the change for review before merge.

## 3. Authority and source inputs

### Independently verified

- `ops/work_queue/QUEUE_GUIDE.md` — existing work-queue doctrine states that the queue prioritizes work, control-plane coordination handles routing/claims/handoff, and GitHub is implementation canon.
- Current GUMAS recovery/control work in PR #1506 — demonstrated that a committed implementation plan is more durable and reviewable than handoff/chat intent alone.

### Owner decisions

- 2026-08-12: operator explicitly established that committed pre-implementation intent should be standard operating procedure for tasks of this class and that handoffs alone are insufficient.

### Assumptions

- `ops/task_records/` is an appropriate repo-wide location for durable execution records because it is operational rather than subsystem-specific.
- The queue schema does not yet require a dedicated `task_record` field; `context_pack` and issue/PR linkage can carry the reference until a schema change is separately designed.

## 4. Scope

### In scope

- define DTER trigger criteria;
- define the required reference chain;
- define required DTER sections and revision rules;
- define handoff and queue integration;
- define destructive-operation safeguards;
- provide a reusable template;
- update `QUEUE_GUIDE.md` to reference the new SOP.

### Out of scope

- changing `queue_schema.json`;
- automatically enforcing DTER presence in CI;
- retroactively creating task records for every historical PR;
- modifying control-plane claim mechanics;
- merging this doctrine without review.

### Protected / immutable surfaces

- existing GitHub history;
- existing handoff/control-plane semantics except for additive reference requirements;
- current queue source-of-truth role.

## 5. Current state and known gaps

### Current state

Before this change, CloudBank had strong queue, claim, handoff, PR, CI, and review structures, but no standard committed artifact that indexed a substantial task's objective, authority, scope, invariants, phased plan, decision deltas, validation, rollback, and cold-start continuation state.

### Known gaps / blockers

- no automated enforcement yet;
- no dedicated queue-schema field yet;
- adoption depends on review/merge and future agent adherence.

## 6. Planned mutations

| Surface / path | Intended change | Authority / rationale | Risk |
|---|---|---|---|
| `ops/task_records/AURORA__SOP__DURABLE_TASK_EXECUTION_RECORDS__v1.0__2026-08-12.md` | Add repo-wide DTER operating doctrine | Operator decision + observed continuity gap | low |
| `ops/task_records/AURORA__TEMPLATE__TASK_EXECUTION_RECORD__v1.0__2026-08-12.md` | Add reusable task-record structure | Required for repeatability | low |
| `ops/work_queue/QUEUE_GUIDE.md` | Bind queue workflow to DTER requirement | Preserve coherent coordination chain | low |
| this task record | Provide first concrete DTER example | Bootstrap the standard transparently | low |

## 7. Execution sequence and gates

### Phase 0 — Existing-process review

Actions:
- inspect work-queue and handoff conventions;
- confirm missing execution-record layer.

Gate to exit:
- existing authority roles are understood well enough to avoid duplicating or displacing them.

**Status:** complete.

### Phase 1 — Define SOP and template

Actions:
- create DTER SOP;
- create template;
- define pre-implementation commit rule, revisions, validation, rollback, and handoff requirements.

Gate to exit:
- durable reference chain and mandatory sections are explicit.

**Status:** complete.

### Phase 2 — Integrate with work queue

Actions:
- update contributor guide;
- add DTER to session-start loop, context packs, escalation conditions, and file map.

Gate to exit:
- queue and DTER roles are non-conflicting and cross-referenced.

**Status:** complete.

### Phase 3 — Review and adoption

Actions:
- review draft PR #1508;
- inspect CI and comments;
- merge only after operator/reviewer approval.

Gate to exit:
- review accepts the operating doctrine.

**Status:** active.

## 8. Invariants and non-negotiables

- handoffs remain useful but are not durable execution authority;
- queue remains prioritization source of truth;
- claims remain mutation-coordination leases;
- GitHub remains implementation canon;
- DTER does not replace detailed plans/specs; it indexes and governs them;
- destructive classification never implies deletion authority;
- filename/basename equality is never sufficient evidence for destructive deduplication;
- prior plan decisions are not silently rewritten after implementation depends on them.

## 9. Validation and acceptance tests

| ID | Validation | Expected result | Evidence / receipt |
|---|---|---|---|
| `V-01` | SOP file exists on scoped branch | present | branch diff |
| `V-02` | Template file exists on scoped branch | present | branch diff |
| `V-03` | Queue guide references SOP/template and session-start rule | present | branch diff |
| `V-04` | Draft PR contains only operating-doctrine changes | four intended files | PR #1508 |
| `V-05` | CI/document checks | green or understood | pending |

## 10. Stop conditions and owner decisions

Stop and request owner/authority input if:

- reviewers identify conflict with existing control-plane authority;
- adoption would require queue-schema migration or CI enforcement beyond this task's scope;
- the proposed SOP would accidentally make trivial work procedurally heavy.

## 11. Rollback and recovery

### Pre-mutation recovery points

- branch created from `main` before changes;
- all changes confined to a dedicated documentation branch.

### Rollback procedure

1. close draft PR #1508 without merge; or
2. revert the documentation commits if already merged.

No runtime or data migration occurs in this task.

## 12. Decision and plan-delta log

| Date / commit | Decision or delta | Evidence / reason | Authority | Consequence |
|---|---|---|---|---|
| `2026-08-12` | Create a repo-wide execution-record layer rather than expanding handoff payloads | Handoffs do not provide a stable structured execution reference | Operator | New DTER SOP + template |
| `2026-08-12` | Keep DTER separate from queue and control-plane claims | Existing queue guide already assigns those roles clearly | Existing repo doctrine | Additive coordination layer, not replacement |
| `2026-08-12` | Bootstrap exception: first SOP/template commits precede this task record | DTER mechanism did not exist before those commits | Transparent procedural necessity | Record exception explicitly; future DTER-required tasks follow pre-implementation rule |
| `2026-08-12` | Separate this governance change from PR #1506 | Repo-wide SOP should not be buried inside a simulation PR | Aurora operational judgment | Dedicated branch/PR #1508 |

## 13. Evidence and receipts

### Commits

- `13910272a3ece6ecff2828523a0ae4d84c7551cf` — add DTER SOP
- `b737ae51d1ae5ab4c7fe80e50543a9fff5672a6e` — add DTER template
- `76fe98cdd23e9d8124a405347b28dea54a7781cc` — bind work queue to DTER operating rule
- `2ce943547d6d7c7e35f86ced55baf9700dfef97a` — add bootstrap DTER example

### CI / tests / replay / audit

- draft PR #1508 opened; CI pending.

## 14. Current status and next action

**Current phase:** `Phase 3 — Review and adoption`  
**Completed gates:** `existing-process review; SOP/template definition; queue integration; draft PR creation`  
**Open blockers:** `CI/review not yet complete`  
**Owner decision required:** `yes before merge/adoption`  
**Exact next action:** `inspect PR #1508 changed-file and CI state, address any review conflict, and merge only after approval.`

## 15. Handoff anchor

Any handoff for this task must reference:

- task record: `ops/task_records/AURORA__TASK_RECORD__DURABLE_TASK_EXECUTION_SOP__v1.0__2026-08-12.md`
- task record version: `v1.0`
- controlling PR: `#1508`
- current phase: `Phase 3 — Review and adoption`
- exact next action: `review draft PR and CI; merge only with approval`
- unresolved blocker / decision: `operator/reviewer adoption approval`

## 16. Completion record

**Final status:** `pending`  
**Merge / closing PR:** `#1508 (draft)`  
**Final controlling commit:** `pending`  
**Validation result:** `pending`  
**Residual risks / follow-ups:** `possible future queue-schema task_record field and CI enforcement`  
**Successor task record(s):** `none yet`
