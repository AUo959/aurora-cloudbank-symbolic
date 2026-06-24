# Aurora Dev Coordination Metrics

**Status:** Metrics skeleton  
**Tracked in:** #1161  
**Depends on:** `ops/work_queue/CROSS_PLATFORM_COORDINATION.md`  
**Purpose:** Measure whether the queue and coordination spine improve development flow.

---

## Measurement principle

The coordination spine is useful only if it reduces stale state, duplicate work, unsafe mutation, unclear handoffs, and review lag.

This file defines the initial measurable signals. Future automation can render this file from queue, GitHub, control-plane handoff, and claim data.

---

## Current metrics table

| Metric | Definition | Source surfaces | Desired trend | Current collection |
|---|---|---|---|---|
| Queue drift count | Queue entries whose status disagrees with live GitHub issue or PR state | `queue.json`, GitHub issues or PRs | Down to zero | Manual review |
| Time-to-safe-next-action | Steps from session start to a claim-safe task recommendation | session log, queue, broker output | Down | Not yet automated |
| Claim conflict count | Path conflicts detected before editing | control-plane claims | Visible and actionable | Not yet automated |
| Duplicate PR avoidance | Existing branch or PR detected before new work begins | GitHub PRs and branches | Up initially, then stable | Manual review |
| Blocked-item aging | Queue items blocked beyond threshold | `queue.json`, GitHub issue state | Down | Not yet automated |
| Review debt age | Floor-touching changes awaiting review | control-plane review ledger or session state | Down | Not yet automated |
| PR cycle time | Queue active to PR open to merged or closed | `queue.json`, GitHub PR timestamps | Down | Not yet automated |
| Handoff success | Suspended task resumed without missing context | handoff state, PR or issue comments | Up | Manual review |
| Generated-view drift | Whether generated queue views match `queue.json` | `sync_queue.py --check` | Zero | Queue Validation CI |
| CI validation success | Coordination PRs passing required checks | GitHub Actions | Up | GitHub Actions |

---

## Future machine-readable shape

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
    "Control-plane inputs must be passed explicitly."
  ]
}
```

---

## Minimum viable collector

Suggested path:

- `ops/work_queue/collect_coordination_metrics.py`

Suggested inputs:

- `ops/work_queue/queue.json`
- generated queue views
- GitHub issue or PR state for queue items with `github_issue` or `pr`
- optional control-plane handoff export, passed explicitly as a path

Suggested outputs:

- `ops/work_queue/COORDINATION_METRICS.md`
- optional JSON: `ops/work_queue/coordination_metrics.json`

---

## Safety boundaries

The metrics collector should remain read-only. It should report evidence and gaps; it should not change repo, queue, claim, GitHub, or runtime state.

---

## Initial manual baseline

Current known baseline from the June 24 queue audit:

- Queue drift was observed: #1147, #1148, #1149, and #1150 remained active in queue state after closure or completion evidence.
- Queue Validation exists and runs when `ops/work_queue/**` changes.
- Coordination spine contract landed under #1161 via PR #1166.
- Automated bridge fields and metrics collection are not yet implemented.

---

## Next implementation step

After PR #1160 and PR #1166 land:

1. Add non-breaking bridge metadata to representative queue entries.
2. Add a read-only metrics collector skeleton.
3. Render this metrics file from collector output.
4. Add CI check mode only after output is deterministic.
