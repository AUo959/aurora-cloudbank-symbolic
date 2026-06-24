# Aurora Dev Coordination Metrics

**Status:** Metrics skeleton  
**Tracked in:** #1161  
**Depends on:** `ops/work_queue/CROSS_PLATFORM_COORDINATION.md`  
**Purpose:** Measure whether the queue + control-plane coordination spine improves development flow.

---

## Measurement principle

The coordination spine is useful only if it reduces stale state, duplicate work, unsafe mutation, unclear handoffs, and review lag.

This file defines the initial measurable signals. A future script may render this file from live GitHub, queue, control-plane session-state, and claim data.

---

## Current metrics table

| Metric | Definition | Source surfaces | Desired trend | Current collection |
|---|---|---|---|---|
| Queue drift count | Queue entries whose status disagrees with live GitHub issue/PR state | `queue.json`, GitHub issues/PRs | Down to zero | Manual review |
| Time-to-safe-next-action | Steps/time from session start to a claim-safe next task | session log, queue, broker output | Down | Not yet automated |
| Claim conflict count | Active/stale path conflicts detected before mutation | control-plane `catalog/session_claims/*.json` | Visible; prevents collisions | Not yet automated |
| Duplicate PR avoidance | Existing branch/PR detected before creating new work | GitHub PRs/branches, broker report | Up initially, then stable | Manual review |
| Blocked-item aging | Queue items blocked beyond threshold | `queue.json`, GitHub issue state | Down | Not yet automated |
| Review debt age | Floor-touching changes awaiting cross-platform review | control-plane peer-review ledger/session state | Down | Not yet automated |
| PR cycle time | Queue active → PR open → merged/closed | `queue.json`, GitHub PR timestamps | Down | Not yet automated |
| Handoff success | Suspended task resumed without missing context | `session_state.json`, PR/issue comments | Up | Manual review |
| Generated-view drift | Whether generated queue views match `queue.json` | `sync_queue.py --check` | Zero | Queue Validation CI |
| CI validation success | Coordination PRs passing required checks | GitHub Actions | Up | GitHub Actions |

---

## Future machine-readable shape

A future generated metrics artifact should be able to emit this shape:

```json
{
  "schema_version": 1,
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "repo": "AUo959/aurora-cloudbank-symbolic",
  "queue_ref": "ops/work_queue/queue.json",
  "control_plane_ref": "AUo959/Aurora_ORIONCORE_Directory_Main/catalog/session_state.json",
  "metrics": {
    "queue_drift_count": null,
    "time_to_safe_next_action_steps": null,
    "claim_conflict_count": null,
    "duplicate_pr_avoidance_count": null,
    "blocked_item_aging_count": null,
    "review_debt_age_days_max": null,
    "pr_cycle_time_days_median": null,
    "handoff_success_count": null,
    "generated_view_drift_count": null,
    "ci_validation_success_rate": null
  },
  "observations": [],
  "blocked": [
    "Automated metrics collector not yet implemented.",
    "Control-plane session-state access is cross-repo and must be explicit."
  ]
}
```

---

## Minimum viable collector

The first collector should remain read-only and should not require local credentials beyond normal Git/GitHub access.

Suggested path:

- `ops/work_queue/collect_coordination_metrics.py`

Suggested inputs:

- `ops/work_queue/queue.json`
- `ops/work_queue/QUEUE.md`
- `ops/work_queue/NEXT_UP.md`
- `ops/work_queue/OPEN_GATES.md`
- GitHub issue/PR state for queue items with `github_issue` or `pr`
- Optional control-plane session-state export, passed explicitly as a path

Suggested outputs:

- `ops/work_queue/COORDINATION_METRICS.md`
- optional JSON: `ops/work_queue/coordination_metrics.json`

---

## Safety boundaries

The metrics collector must be read-only.

It must not:

- mutate queue state,
- create or close GitHub issues,
- create claims,
- edit control-plane files,
- infer canon promotion,
- touch runtime code,
- merge PRs,
- bypass peer-review debt.

---

## Initial manual baseline

Current known baseline from the June 24 queue audit:

- Queue drift was observed: #1147, #1148, #1149, and #1150 remained active in queue state after closure/completion evidence.
- Queue Validation exists and runs when `ops/work_queue/**` changes.
- Coordination spine contract is in progress under #1161 / PR #1162.
- Automated bridge fields and metrics collection are not yet implemented.

---

## Next implementation step

After PR #1160 and PR #1162 land:

1. Add non-breaking bridge metadata to representative queue entries.
2. Add a read-only metrics collector skeleton.
3. Render this metrics file from collector output.
4. Add CI check mode only after the output is deterministic.
