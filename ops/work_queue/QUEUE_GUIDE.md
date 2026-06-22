# Aurora Work Queue — Contributor Guide

**Version:** 1.0.0  
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
| **Aurora** | Holds contextual authority. May rerank, rewrite context packs, and declare decision-required items. Always check queue before starting a session to load current state. |
| **LLM / agents** | Read `queue.json`. Pick the highest-ranked `ready` task that matches your `consumer_fit`. Consume `context_pack` before starting work. Do NOT start `blocked` tasks or `decision_required` tasks. |
| **Human contributors** | Read `NEXT_UP.md` for a quick-start view. Full detail in `queue.json`. If starting work on a task, update `state` from `ready` to `active` and record your GitHub username in the `active_worker` field. |

---

## Task states

| State | Meaning |
|---|---|
| `ready` | No blockers. Safe to start. |
| `blocked` | Depends on another item. Do not start. |
| `active` | Someone is working on it now. |
| `waiting_review` | Work done, PR open, awaiting review. |
| `decision_required` | Needs explicit owner or Aurora decision before any work can proceed. Do not touch without that decision. |
| `done` | Merged or resolved. |

---

## Priority scoring

The `priority_score` is computed — not just a label. Factors:

- +40 if item is blocking another task
- +30 if item is security or pentest-relevant
- +25 if item touches canonical architecture or layer integrity
- +20 if item involves stale scope, live docs mismatch, or an unresolved design decision
- +10 for known active blocker chains
- −6 if item has unresolved dependencies (it cannot be started yet)

A CRITICAL item is generally score ≥ 80. HIGH is 60–79. MEDIUM is 30–59. LOW is below 30.

---

## Context packs

Every task has a `context_pack` — an array of canonical constraints that any agent or contributor MUST read before starting work. The context pack is not optional.

For architecture tasks: the context pack always references `docs/architecture/LAYER_ARCHITECTURE.md` and includes forbidden terminology patterns.  
For security tasks: the context pack references the current pentest scope doc and any relevant pre-conditions.  
For ethics tasks: the context pack includes recovery/promotion status and explicit deferred-wiring notes.

---

## How to add a new task

1. Open a GitHub issue.
2. Add a corresponding entry to `queue.json` following the schema in `ops/work_queue/queue_schema.json`.
3. Compute a priority score using the rules above, or leave `priority_score: 0` and request Aurora to score it.
4. If the task blocks other tasks, update the `blocks` array of existing tasks.
5. If the task is a decision that only the owner/Aurora can make, set `decision_required: true` and `consumer_fit: ["aurora", "human"]`.

---

## How to update task state

When picking up a task:
```json
"state": "active",
"active_worker": "@your-handle-or-agent-id",
"started": "2026-06-22"
```

When opening a PR:
```json
"state": "waiting_review",
"pr": 1234
```

When merged:
```json
"state": "done",
"closed": "2026-06-22"
```

---

## Aurora's role

Aurora maintains contextual authority over this queue. This means:

- Aurora may change `priority_score` values between sessions based on architectural risk or new information.
- Aurora may add or modify `context_pack` entries to reflect session learnings.
- Aurora may escalate `decision_required` on any task where agent autonomy would be unsafe.
- Human operators always retain final authority over decisions flagged as `decision_required`.

---

## File map

| File | Purpose |
|---|---|
| `queue.json` | Live task registry — source of truth |
| `QUEUE_GUIDE.md` | This file — workflow and field definitions |
| `queue_schema.json` | JSON schema for validating `queue.json` entries |
| `triage_rules.json` | Scoring weights used by Aurora or a sync script |
| `NEXT_UP.md` | Quick-start view for human contributors and agents |
