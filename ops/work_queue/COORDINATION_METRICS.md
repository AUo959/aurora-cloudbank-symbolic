<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Source of truth: ops/work_queue/queue.json
     Regenerate:      python ops/work_queue/collect_coordination_metrics.py --markdown
     Verify:          python ops/work_queue/collect_coordination_metrics.py --check -->

# Aurora Dev Coordination Metrics Report

**Generated:** `2026-07-13T05:57:19Z`
**Repo:** `AUo959/aurora-cloudbank-symbolic`
**Queue:** `ops/work_queue/queue.json`

## Metrics

| Metric | Value |
|---|---:|
| active_count | `19` |
| completed_count | `8` |
| status_counts | `{"needs-decision": 2, "open": 17}` |
| bridge_field_counts | `{"claim_paths_set": 2, "claim_required": 2, "github_linkable": 13, "preferred_platform_set": 2, "review_class_set": 2}` |
| queue_drift_count | _not measured_ |
| generated_view_drift_count | `0` |
| claim_conflict_count | _not measured_ |
| duplicate_pr_avoidance_count | _not measured_ |
| blocked_item_aging_count | _not measured_ |
| review_debt_age_days_max | _not measured_ |
| pr_cycle_time_days_median | _not measured_ |
| handoff_success_count | _not measured_ |
| ci_validation_success_rate | _not measured_ |

## Observations

- Collector is read-only and local-file based.
- GitHub issue/PR comparison requires an explicit --github-state export.
- Control-plane session-state and claim metrics are placeholders until cross-repo input is explicitly provided.

## Blocked / not measured

- No direct GitHub API calls are made by this script.
- No control-plane file is read unless future options explicitly pass a path.
