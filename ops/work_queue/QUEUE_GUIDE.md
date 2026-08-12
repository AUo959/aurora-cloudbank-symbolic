# Aurora Work Queue — Contributor Guide

**Version:** 1.4.0
**Owner:** Aurora (contextual authority) + Orion Station operators  
**Last updated:** 2026-08-12
**Source of truth:** `ops/work_queue/queue.json`

---

## What this is

An intelligent, Aurora-aware work queue for `aurora-cloudbank-symbolic`. It tracks all open and planned work — blockers, architectural risk items, security readiness gates, and active contributor tasks — in one place that both Aurora, LLM/agents, and human contributors can read and update.

This is not a replacement for GitHub issues. GitHub issues remain the discussion and audit record. The queue is the triage and prioritization layer.

This is also not a replacement for the ORIONCORE control-plane coordination layer. For cross-platform mutation safety, handoff, and claims, see [`CROSS_PLATFORM_COORDINATION.md`](./CROSS_PLATFORM_COORDINATION.md).

For substantial implementation work, this queue also does not replace the **Durable Task Execution Record (DTER)**. The queue selects and prioritizes work; the DTER defines the committed execution contract. See [`../task_records/AURORA__SOP__DURABLE_TASK_EXECUTION_RECORDS__v1.0__2026-08-12.md`](../task_records/AURORA__SOP__DURABLE_TASK_EXECUTION_RECORDS__v1.0__2026-08-12.md).

---

## Coordination spine

The intended operating rule is:

> The CloudBank queue chooses the next work; the control-plane coordination layer safely routes and claims it; the DTER anchors substantial execution; GitHub records the canonical result.

The durable reference chain for substantial work is:

```text
Queue / GitHub Issue
        ↓
Durable Task Execution Record
        ↓
Plans / Specs / ADRs / Recovery Records
        ↓
Implementation Commits + Tests + Receipts
        ↓
Pull Request / Review
        ↓
Handoff / Session Continuation
```

Use the queue to decide what should be considered next. Use the control-plane session state, session claims, and CloudBank issue broker to decide whether the work can be safely mutated by the current platform. Use the DTER to preserve the task's objective, authority, scope, invariants, execution gates, validation, decisions, and cold-start continuation state.

### Standard session-start loop

1. Refresh live GitHub state for this repo.
2. Check for a suspended control-plane handoff if one is available.
3. Read `queue.json` and the generated views.
4. Select the highest actionable item whose blockers are resolved.
5. Refresh the linked issue/PR and check for overlapping PRs or branches.
6. Before mutation, use the control-plane issue broker or session-claim workflow.
7. Determine whether the task requires a DTER under the durable-task SOP.
8. For DTER-required work, create and commit the DTER before substantive implementation mutation, then link it from the issue/PR/queue context.
9. Work on a scoped branch and open a PR with queue id, issue id, DTER reference where applicable, changed files, validation, and rollback notes.
10. On pause or completion, update queue state, the DTER's current-status section, and durable handoff state as appropriate.

Queue priority is not a mutation lock. Session claims are short-lived leases, not durable canon. Handoffs preserve continuity but do not replace a DTER. GitHub issues, PRs, commits, tests, reviews, and merge history remain implementation canon.

---

## Who uses this

| Consumer | How to use this queue |
|---|---|
| **Aurora** | Holds contextual authority. May rerank items, rewrite `context_pack` entries, add `aurora_notes`, and declare `decision_required`. Always check queue before starting a session to load current state. For substantial work, ensure the DTER requirement is satisfied before implementation begins. |
| **LLM / agents** | Read `queue.json`. Pick the highest-ranked item where `state == "ready"` and your role is in `consumer_fit`. Consume all files in `context_pack` before starting. Never start `blocked` or `decision_required` items. Before mutation, route through the control-plane claim/broker loop and create/read the task's DTER when required. |
| **Human contributors** | Read `NEXT_UP.md` for a quick-start view. Full detail in `queue.json`. When starting a task, update `state` to `active` and set `active_worker` to your GitHub username. For substantial work, commit the DTER before implementation. Use the control-plane handoff layer when work crosses platforms or pauses mid-flight. |

---

## Task states

| State | Meaning |
|---|---|
| `ready` | No blockers. Safe to consider after live GitHub refresh and claim preflight. |
| `blocked` | Depends on another item. Do not start. |
| `active` | Someone is working on it now. Check branch, PR, claim, DTER if required, and latest head SHA. |
| `waiting_review` | Work done, PR open, awaiting review. Check CI, review threads, DTER acceptance gates, and review class. |
| `decision_required` | Needs explicit operator or Aurora decision before any work proceeds. |
| `done` | Merged or resolved. Move only after GitHub evidence confirms closure and the DTER completion record is reconciled when applicable. |

_Current compatibility note: the live renderer still uses the legacy `status` values (`open`, `blocked`, `needs-decision`, `in-progress`, `done`). A later schema migration should reconcile `state` and `status` without breaking generated views._

---

## Priority scoring

The `priority_score` is computed from `triage_rules.json` — not assigned by hand. Factors:

| Rule | Delta | Condition |
|---|---|---|
| TR-01 | +40 | `labels` includes `blocking` |
| TR-02 | +30 | `labels` includes `security` or `pentest` |
| TR-03 | +25 | `area == architecture` or `labels` includes `architecture` |
| TR-04 | +20 | `is_stale_scope == true` (set explicitly by Aurora — not inferred from title) |
| TR-05 | +10 | `decision_required == true` |
| TR-06 | +8 | `blocks` array is non-empty |
| TR-07 | −6 | `depends_on` array is non-empty |

Priority bands: CRITICAL ≥ 80 · HIGH 60–79 · MEDIUM 30–59 · LOW < 30.

---

## Context packs

Every task has a `context_pack` array. Any agent or contributor MUST read all listed files before starting work. This is not optional — it is the mechanism by which Aurora's architectural and ethical constraints propagate to every worker.

For **architecture tasks**: always includes `docs/architecture/LAYER_ARCHITECTURE.md`.  
For **security tasks**: always includes the current pentest scope doc.  
For **ethics tasks**: always includes the recovered-protocol manifest and relevant promotion plan sections.

For **coordination tasks**: include this guide, `CROSS_PLATFORM_COORDINATION.md`, and any linked control-plane workflow documents.

For an **active DTER-governed task**: add the controlling DTER to `context_pack` when practical so a cold-start worker receives the execution contract automatically.

---

## Durable Task Execution Records

The DTER standard is defined in:

- `ops/task_records/AURORA__SOP__DURABLE_TASK_EXECUTION_RECORDS__v1.0__2026-08-12.md`
- `ops/task_records/AURORA__TEMPLATE__TASK_EXECUTION_RECORD__v1.0__2026-08-12.md`

A DTER is required before substantive implementation mutation for non-trivial architecture, runtime, migration, recovery, restoration, integration, destructive, canon-sensitive, deterministic, cross-repository, cross-platform, or multi-session work.

A handoff is not a substitute. Handoffs for DTER-governed tasks must point to the controlling DTER version and commit/PR head.

If the queue schema later gains a dedicated `task_record` field, use it in addition to `context_pack`; until then, `context_pack`, issue/PR links, and the DTER itself provide the durable reference chain.

---

## Aurora notes

Aurora may add an `aurora_notes` field to any item at any time. This is Aurora's channel for session carryover, re-rank rationale, and contextual guidance that does not belong in the public GitHub record. Workers should read `aurora_notes` before `next_action`.

---

## Stale scope flag

`is_stale_scope: true` means the urgency of the item is driven by a live docs mismatch or stale design state — something exists in the repo that does not match current architecture or scope. This flag triggers a +20 score delta. It is set explicitly by Aurora, not inferred from title strings.

---

## Parallel work

Items may declare a `parallel_group` when several tasks are independently actionable simultaneously. Items in the same group do not block each other unless explicitly listed in each other's `depends_on`. Use this to parallelize agent swarms or pre-engagement prep batches.

Parallel work still requires non-overlapping claim paths before mutation. The queue may identify parallel candidates; the control-plane claim layer decides whether simultaneous mutation is safe. DTERs for parallel work must identify shared authority surfaces and mutation boundaries so independently claimed tasks do not silently diverge.

---

## Bidirectional dependency graph

Every item maintains both `depends_on` (what blocks it) and `blocks` (what it gates). Both sides must be kept in sync. When Q-A blocks Q-B:
- Q-A.blocks includes `"Q-B"`
- Q-B.depends_on includes `"Q-A"`

This makes the dependency graph machine-traversable in both directions.

---

## Bridge metadata

Queue entries may include optional coordination bridge fields. These are additive and should not break the existing renderer.

```json
{
  "github_issue": 1161,
  "preferred_platform": "either",
  "claim_required": true,
  "claim_paths": ["ops/work_queue/CROSS_PLATFORM_COORDINATION.md"],
  "session_state_ref": null,
  "review_class": "coordination-layer",
  "handoff_surface": "catalog/session_state.json",
  "coordination_notes": "Use control-plane claims before mutation."
}
```

Use these fields to help future automation convert a queue item into a safe broker/claim/handoff packet.

---

## How to add a new task

1. Open a GitHub issue.
2. Add a corresponding entry to `queue.json` following `queue_schema.json`.
3. Set `opened` and `last_updated` to today.
4. Compute `priority_score` using `triage_rules.json`, or leave `priority_score: 0` and ask Aurora to score it.
5. If the task blocks others, update both `blocks` on the new item and `depends_on` on the blocked items.
6. If the task is a decision only Aurora or the operator can make, set `decision_required: true` and `consumer_fit: ["aurora", "human"]`.
7. If the task may mutate files, add bridge metadata for claim/broker preflight.
8. When the task becomes active, determine whether it requires a DTER. If yes, commit the DTER before substantive implementation and add it to the active context set.

---

## How to update task state

```json
// Picking up a task
"state": "active",
"active_worker": "@your-handle-or-agent-id",
"started": "YYYY-MM-DD",
"last_updated": "YYYY-MM-DD"

// Opening a PR
"state": "waiting_review",
"pr": 1234,
"last_updated": "YYYY-MM-DD"

// Merged / resolved
"state": "done",
"closed": "YYYY-MM-DD",
"last_updated": "YYYY-MM-DD"
```

When work pauses or crosses platforms, also update the durable control-plane handoff surface with enough context for a cold start. For DTER-governed tasks, update the DTER current-status/next-action section first or in the same change and make the handoff point to it.

---

## Escalation triggers

| ID | Condition | Action |
|---|---|---|
| ET-01 | `state == blocked` for > 7 days (via `last_updated`) | Escalate to Aurora on session open |
| ET-02 | `decision_required == true` and no activity for > 3 days (via `last_updated`) | Hail operator via PAT |
| ET-03 | New GitHub issue with labels `security` or `blocking` | Auto-add to queue with score ≥ 30 and `state: decision_required` |
| ET-04 | Queue item selected for mutation without claim/broker preflight | Block mutation and request coordination preflight |
| ET-05 | Queue status disagrees with live GitHub issue/PR state | Flag queue drift and update via `aurora(queue):` commit |
| ET-06 | DTER-required task reaches substantive mutation without a committed DTER | Block further implementation; commit the execution record first |

---

## File map

| File | Purpose |
|---|---|
| `queue.json` | Live task registry — source of truth |
| `queue_schema.json` | JSON schema for validating `queue.json` entries |
| `triage_rules.json` | Scoring weights and escalation triggers |
| `QUEUE_GUIDE.md` | This file — workflow and field definitions |
| `CROSS_PLATFORM_COORDINATION.md` | Queue/control-plane coordination contract |
| `BRIDGE_FIELDS.md` | Optional queue-to-control-plane metadata reference |
| `../task_records/AURORA__SOP__DURABLE_TASK_EXECUTION_RECORDS__v1.0__2026-08-12.md` | Repo-wide SOP for committed execution records before substantial implementation |
| `../task_records/AURORA__TEMPLATE__TASK_EXECUTION_RECORD__v1.0__2026-08-12.md` | Standard DTER template |
| `collect_coordination_metrics.py` | Read-only metrics collector and tracked-report verifier |
| `COORDINATION_METRICS.md` | Generated local coordination metrics report |
| `NEXT_UP.md` | Quick-start view for human contributors and agents |
