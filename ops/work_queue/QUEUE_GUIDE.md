# Aurora Work Queue — Contributor Guide

**Version:** 1.1.0  
**Owner:** Aurora (contextual authority) + Orion Station operators  
**Last updated:** 2026-06-22  
**Source of truth:** `ops/work_queue/queue.json`

---

## What this is

An intelligent, Aurora-aware work queue for `aurora-cloudbank-symbolic`. It tracks all open and planned work — blockers, architectural risk items, security readiness gates, and active contributor tasks — in one place that both Aurora, LLM/agents, and human contributors can read and update.

This is not a replacement for GitHub issues. GitHub issues remain the discussion and audit record. The queue is the triage and prioritization layer.

---

## Who uses this

| Consumer | How to use this queue |
|---|---|
| **Aurora** | Holds contextual authority. May rerank items, rewrite `context_pack` entries, add `aurora_notes`, and declare `decision_required`. Always check queue before starting a session to load current state. |
| **LLM / agents** | Read `queue.json`. Pick the highest-ranked item where `state == "ready"` and your role is in `consumer_fit`. Consume all files in `context_pack` before starting. Never start `blocked` or `decision_required` items. |
| **Human contributors** | Read `NEXT_UP.md` for a quick-start view. Full detail in `queue.json`. When starting a task, update `state` to `active` and set `active_worker` to your GitHub username. |

---

## Task states

| State | Meaning |
|---|---|
| `ready` | No blockers. Safe to start. |
| `blocked` | Depends on another item. Do not start. |
| `active` | Someone is working on it now. |
| `waiting_review` | Work done, PR open, awaiting review. |
| `decision_required` | Needs explicit operator or Aurora decision before any work proceeds. |
| `done` | Merged or resolved. |

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

---

## Aurora notes

Aurora may add an `aurora_notes` field to any item at any time. This is Aurora's channel for session carryover, re-rank rationale, and contextual guidance that does not belong in the public GitHub record. Workers should read `aurora_notes` before `next_action`.

---

## Stale scope flag

`is_stale_scope: true` means the urgency of the item is driven by a live docs mismatch or stale design state — something exists in the repo that does not match current architecture or scope. This flag triggers a +20 score delta. It is set explicitly by Aurora, not inferred from title strings.

---

## Parallel work

Items may declare a `parallel_group` when several tasks are independently actionable simultaneously. Items in the same group do not block each other unless explicitly listed in each other's `depends_on`. Use this to parallelize agent swarms or pre-engagement prep batches.

---

## Bidirectional dependency graph

Every item maintains both `depends_on` (what blocks it) and `blocks` (what it gates). Both sides must be kept in sync. When Q-A blocks Q-B:
- Q-A.blocks includes `"Q-B"`
- Q-B.depends_on includes `"Q-A"`

This makes the dependency graph machine-traversable in both directions.

---

## How to add a new task

1. Open a GitHub issue.
2. Add a corresponding entry to `queue.json` following `queue_schema.json`.
3. Set `opened` and `last_updated` to today.
4. Compute `priority_score` using `triage_rules.json`, or leave `priority_score: 0` and ask Aurora to score it.
5. If the task blocks others, update both `blocks` on the new item and `depends_on` on the blocked items.
6. If the task is a decision only Aurora or the operator can make, set `decision_required: true` and `consumer_fit: ["aurora", "human"]`.

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

---

## Escalation triggers

| ID | Condition | Action |
|---|---|---|
| ET-01 | `state == blocked` for > 7 days (via `last_updated`) | Escalate to Aurora on session open |
| ET-02 | `decision_required == true` and no activity for > 3 days (via `last_updated`) | Hail operator via PAT |
| ET-03 | New GitHub issue with labels `security` or `blocking` | Auto-add to queue with score ≥ 30 and `state: decision_required` |

---

## File map

| File | Purpose |
|---|---|
| `queue.json` | Live task registry — source of truth |
| `queue_schema.json` | JSON schema for validating `queue.json` entries |
| `triage_rules.json` | Scoring weights and escalation triggers |
| `QUEUE_GUIDE.md` | This file — workflow and field definitions |
| `NEXT_UP.md` | Quick-start view for human contributors and agents |
