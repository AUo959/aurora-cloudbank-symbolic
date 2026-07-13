# Aurora Dev Coordination Spine

**Status:** Draft coordination contract  
**Owner:** Aurora / ORIONCORE operators  
**Tracked in:** #1161  
**Applies to:** `AUo959/aurora-cloudbank-symbolic` work coordinated with the ORIONCORE control-plane repo

---

## Purpose

The CloudBank work queue and the ORIONCORE cross-platform coordination layer are complementary systems. This document defines how they should work as one development aid without collapsing their authority boundaries.

The operating rule is:

> The CloudBank queue chooses the next work; the control-plane coordination layer safely routes and claims it; GitHub records the canonical result.

This document is intentionally coordination-only. It does not authorize runtime wiring, canon promotion, recovered-protocol enforcement, or L1/L2/L3 boundary changes.

---

## Authority map

| Surface | Authority | Must not do |
|---|---|---|
| `ops/work_queue/queue.json` | CloudBank-local work priority and queue state | Act as a mutation lock or replace GitHub issue truth |
| `ops/work_queue/QUEUE.md` | Generated human queue view | Be edited by hand |
| `ops/work_queue/NEXT_UP.md` | Generated quick-start view | Override `queue.json` |
| `ops/work_queue/OPEN_GATES.md` | Generated gate view | Close gates without source queue changes |
| `catalog/session_state.json` in the control-plane repo | Durable cross-platform handoff, suspended task state, platform routing, known workspace state | Duplicate the full CloudBank queue |
| `catalog/session_claims/*.json` in the control-plane repo | Short-lived local mutation leases | Serve as durable canon or long-term handoff |
| `tools/cloudbank_issue_broker.py` in the control-plane repo | Queue/issue-to-claim/worktree preflight | Mutate CloudBank or GitHub by itself |
| GitHub issues, PRs, commits, and reviews | Canonical implementation and audit surface | Be bypassed by chat, queue notes, claims, or local handoffs |
| Cross-platform peer-review protocol | Independent re-verification and review debt for floor-touching changes | Be skipped for coordination/security/ethics floor changes |

---

## Standard session-start loop

A CloudBank development session should follow this sequence:

1. Refresh GitHub state for the target repo.
2. Check whether there is an active or suspended control-plane handoff for the task.
3. Read `ops/work_queue/queue.json` and generated views.
4. Select the highest actionable queue item whose blockers are resolved.
5. Refresh the linked GitHub issue and any linked/open PRs.
6. Check for branches or PRs touching the same intended paths.
7. If mutation is needed, use the control-plane issue broker or session-claim workflow before editing.
8. Work on a scoped branch.
9. Open a PR with queue id, issue id, changed files, validation, and rollback notes.
10. Update queue status and durable handoff state when pausing, handing off, or finishing.

Read-only inspection may skip the claim step, but must still label findings as observed, derived, recommended, blocked, or assumption when producing repo reports.

---

## Queue item lifecycle

| Queue status | Coordination meaning | Required action |
|---|---|---|
| `open` | Candidate work exists | Refresh GitHub before starting |
| `blocked` | Declared dependency is unresolved | Do not start except to resolve blocker |
| `needs-decision` | Human/governance gate exists | Wait for named decision |
| `in-progress` | Active branch/PR/session exists | Check owner, PR, branch, claim, and latest SHA |
| `waiting-review` | Work is ready for review | Check CI, review threads, linked issue, and peer-review class |
| `done` | Work merged or issue resolved | Move to `completed[]` after GitHub evidence confirms closure |

`queue.json` priority is a routing signal, not permission to mutate.

---

## Bridge metadata

Queue entries may carry optional bridge fields. These fields should be additive and should not break the existing renderer.

```json
{
  "github_issue": 1161,
  "preferred_platform": "either",
  "claim_required": true,
  "claim_paths": ["ops/work_queue/CROSS_PLATFORM_COORDINATION.md", "ops/work_queue/QUEUE_GUIDE.md"],
  "session_state_ref": null,
  "review_class": "coordination-layer",
  "handoff_surface": "catalog/session_state.json",
  "coordination_notes": "Use control-plane session claims before mutating shared queue/coordination files."
}
```

### Field meanings

| Field | Meaning |
|---|---|
| `github_issue` | Numeric issue id for live GitHub refresh |
| `preferred_platform` | `codex`, `claude-code`, `either`, or another explicit agent surface |
| `claim_required` | Whether path mutation must run through claim/broker preflight |
| `claim_paths` | Intended mutation paths for conflict checks |
| `session_state_ref` | Optional pointer to a durable handoff entry |
| `review_class` | Peer-review / risk category |
| `handoff_surface` | Where suspended work should be recorded |
| `coordination_notes` | Human-readable routing or safety instruction |

---

## Broker handoff packet

A queue-selected issue should be convertible into a broker packet before mutation:

```json
{
  "queue_id": "#1161",
  "github_issue": 1161,
  "repo": "AUo959/aurora-cloudbank-symbolic",
  "intended_paths": [
    "ops/work_queue/CROSS_PLATFORM_COORDINATION.md",
    "ops/work_queue/QUEUE_GUIDE.md"
  ],
  "preferred_platform": "either",
  "claim_status": "pending_preflight",
  "branch_pattern": "<platform>/cloudbank-issue-1161-<slug>",
  "handoff_surface": "catalog/session_state.json"
}
```

The broker or session-claim layer decides whether the work is claim-ready. The queue does not decide that by itself.

---

## Session-close handoff packet

When a queue item pauses or hands off, durable state should include:

```json
{
  "queue_id": "#1161",
  "github_issue": 1161,
  "status": "suspended",
  "branch": "aurora/1161-coordination-spine-contract",
  "head_sha": "<sha>",
  "changed_files": [
    "ops/work_queue/CROSS_PLATFORM_COORDINATION.md",
    "ops/work_queue/QUEUE_GUIDE.md"
  ],
  "claim_id": "<claim-or-null>",
  "claim_released": true,
  "validation": ["queue validation", "targeted docs review"],
  "next_step": "review PR and merge after CI",
  "blockers": []
}
```

A claim is not enough for handoff. If a future thread or platform must resume the task, the resume context belongs in the durable control-plane handoff surface.

---

## Peer-review classification

Changes to this coordination spine may trigger peer-review obligations.

Treat these as coordination-layer / floor-touching changes unless proven mechanical:

- Changes to queue authority rules.
- Changes to generated-view enforcement.
- Changes to session-state synchronization.
- Changes to claim or broker behavior.
- Changes to cross-platform review requirements.
- Changes that alter GitHub mutation, branch, PR, or merge gates.

Generated queue-view refreshes alone are usually mechanical. Queue schema migrations and bridge automation are not mechanical.

---

## Metrics

This system should aid development measurably. Initial metrics:

| Metric | Definition | Desired trend |
|---|---|---|
| Queue drift count | Queue entries whose status disagrees with live GitHub issue/PR state | Down |
| Time-to-safe-next-action | Steps/time from session start to a claim-safe next task | Down |
| Claim conflict count | Overlap conflicts detected before mutation | Visible; should prevent collisions |
| Duplicate PR avoidance | Existing branch/PR detected before new work begins | Up initially, then stable |
| Blocked-item aging | Items blocked beyond threshold | Down |
| Review debt age | Floor-touching changes awaiting independent review | Down |
| PR cycle time | Queue active → PR open → merged/closed | Down |
| Handoff success | Suspended work resumed without missing context | Up |
| Generated-view drift | Whether views match `queue.json` | Zero |
| CI validation success | Queue/coordination PRs passing required checks | Up |

A future metrics script may render `ops/work_queue/COORDINATION_METRICS.md` or `reports/analysis/dev_coordination_metrics_latest.md`.

---

## Non-goals

- Do not replace GitHub issues, PRs, commits, or reviews as canon.
- Do not make `queue.json` a mutation lock.
- Do not make session claims durable canon.
- Do not duplicate the full queue into `session_state.json`.
- Do not bypass peer-review debt for coordination-layer mutations.
- Do not use this system to promote recovered protocol material into runtime enforcement.
- Do not blur L1/L2/L3 authority boundaries.

---

## First implementation slice

The first safe slice is documentation and compatibility only:

1. Add this coordination contract.
2. Update `QUEUE_GUIDE.md` to point contributors at this session-start/session-close loop.
3. Add bridge fields to queue entries in a later PR after PR #1160 lands and queue validation is green.
4. Add metrics generation after bridge fields stabilize.

This order avoids mixing stale-state cleanup, schema migration, broker integration, and metrics automation into one oversized change.
