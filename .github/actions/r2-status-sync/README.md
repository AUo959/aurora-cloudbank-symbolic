# R2 Status Sync Action

**Version:** 2.0.0  
**Type:** Composite Action  
**Purpose:** Propagates R-2 agent operational status across collaborative environments

## Overview

The R2 Status Sync action enables real-time status propagation from Aurora CloudBank Symbolic to collaborative runtime environments. It collects operational health, performance metrics, and drift status, then propagates to target repositories with DLP compliance and symbolic anchor tracking.

## Features

- ✅ **Multi-Severity Support** - Info, warning, error, critical levels
- ✅ **Health Monitoring** - Operational status and uptime tracking
- ✅ **Performance Metrics** - Success rates, response times, error rates
- ✅ **Drift Detection** - Real-time symbolic drift monitoring
- ✅ **Symbolic Anchors** - T1/SRB state included in status payloads
- ✅ **Ethics Protocol** - Picard_Delta_3 compliance

## Symbolic Tags

- `T1:STATUS_SYNC` - Temporal anchor for status operations
- `SRB:STATUS_PROPAGATE` - Spatial-relational boundary for propagation
- `DLP:collab_status` - Data lineage protocol tag

**Anchor Seed:** `EOS_SEED_ORION_v2.0.0`  
**Ethics Protocol:** `Picard_Delta_3`

## Usage

### Basic Usage

```yaml
- name: R2 status sync
  uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-status-sync@main
```

### Full Configuration

```yaml
- name: R2 status sync
  uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-status-sync@main
  with:
    target_repository: 'AUo959/aurora-cloudbank-runtime'
    status_type: 'health'
    severity: 'info'
    include_metrics: 'true'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `target_repository` | Target repository (format: `owner/repo`) | No | `AUo959/aurora-cloudbank-runtime` |
| `status_type` | Type: `health`, `performance`, `error`, or `alert` | No | `health` |
| `severity` | Level: `info`, `warning`, `error`, or `critical` | No | `info` |
| `include_metrics` | Include performance metrics | No | `true` |

## Outputs

| Output | Description |
|--------|-------------|
| `propagation_status` | Result: `success`, `partial`, or `failed` |
| `target_notified` | Whether target was successfully notified |
| `status_hash` | SHA256 hash of status payload |
| `timestamp` | ISO 8601 timestamp of propagation |

## Status Types

### Health Status
- Operational status (healthy, degraded, down)
- Uptime tracking
- Last health check timestamp
- Component availability

### Performance Status
- Operations per minute
- Success rate percentage
- Average response time (ms)
- Error rate tracking

### Error Status
- Error details and stack traces
- Failed operation counts
- Error categories and severity
- Remediation recommendations

### Alert Status
- Critical alerts and incidents
- Threshold breaches
- Anomaly detection results
- Immediate action items

## Severity Levels

| Severity | Usage | GitHub Annotation |
|----------|-------|-------------------|
| `info` | Normal operations, routine status | `::notice::` |
| `warning` | Degraded performance, minor issues | `::warning::` |
| `error` | Operation failures, service disruption | `::error::` |
| `critical` | System-wide failures, data loss risk | `::error::` + escalation |

## Status Payload Structure

```json
{
  "status_type": "health",
  "severity": "info",
  "timestamp": "2025-11-13T00:30:00Z",
  "source_repository": "AUo959/aurora-cloudbank-symbolic",
  "health": {
    "status": "operational",
    "uptime_hours": 168,
    "last_check": "2025-11-13T00:30:00Z"
  },
  "metrics": {
    "operations_per_minute": 120,
    "success_rate": 99.5,
    "avg_response_time_ms": 45,
    "error_rate": 0.5
  },
  "symbolic_anchors": {
    "T1_state": 42,
    "SRB_resolution": 1337,
    "chain_notation": "001//999//"
  },
  "drift_status": {
    "drift_detected": false,
    "drift_delta": 0.0,
    "baseline_hash": "BASELINE_v2"
  }
}
```

## DLP Compliance

All status propagation includes:

- **Context Tag:** `collab_status`
- **Symbolic Hash:** SHA256 of status payload
- **Anchor Tracking:** T1/SRB states included
- **Drift Monitoring:** Real-time drift detection

## Example Workflows

### Scheduled Health Check

```yaml
name: R2 Health Status
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Propagate health status
        uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-status-sync@main
        with:
          status_type: 'health'
          severity: 'info'
```

### Error Alert Propagation

```yaml
name: R2 Error Alert
on:
  workflow_run:
    workflows: ["CI/CD Pipeline"]
    types: [completed]
    branches: [main]

jobs:
  error-alert:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Propagate error status
        uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-status-sync@main
        with:
          status_type: 'error'
          severity: 'error'
          target_repository: 'AUo959/aurora-cloudbank-runtime'
```

### Performance Monitoring

```yaml
name: R2 Performance Status
on:
  push:
    branches: [main]

jobs:
  performance-status:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests and collect metrics
        run: pytest --benchmark-only
      
      - name: Propagate performance status
        uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-status-sync@main
        with:
          status_type: 'performance'
          severity: 'info'
          include_metrics: 'true'
```

## Troubleshooting

### Target Not Notified
**Symptom:** `target_notified` output is `false`  
**Cause:** Target repository access denied or doesn't exist  
**Solution:** Verify repository name format and permissions

### Invalid Status Type
**Symptom:** Action fails with validation error  
**Cause:** Unsupported status_type value  
**Solution:** Use only: `health`, `performance`, `error`, or `alert`

### Drift Detected in Status
**Symptom:** `drift_detected: true` in drift_status  
**Cause:** Symbolic drift between source and baseline  
**Solution:** Review drift_delta, consider re-baselining with full context sync

## Production Considerations

**Current Implementation:** Simulation mode for development/testing

**Production Enhancements (Future):**
1. GitHub API integration for issue/PR creation
2. Repository dispatch event triggering
3. Status check API updates
4. Webhook notifications to external systems
5. Encrypted payload transmission

## Integration with R2 Context Sync

Status sync complements context sync:

- **Context Sync** - Detailed telemetry data transfer (scheduled)
- **Status Sync** - Real-time operational status (event-driven)

Use both for complete R-2 agent observability across environments.

## Ethics Protocol: Picard_Delta_3

Adheres to Aurora's Picard_Delta_3 ethics framework:

1. **Status Transparency** - All status changes logged
2. **No False Alarms** - Severity levels validated
3. **Drift Accountability** - Drift status always included
4. **Audit Trail** - Complete DLP lineage tracking

## Related Documentation

- [R2 Agent Telemetry](../../../docs/R2_AGENT_TELEMETRY.md)
- [Collab-Sync Workflow](../../workflows/collab-sync.yml)
- [R2 Context Sync Action](../r2-context-sync/README.md)

## Version History

- **2.0.0** (2025-11-13) - Production-ready with multi-severity support
- **1.0.0** (2025-10-15) - Initial implementation

## Contact

**Team:** Aurora CloudBank Team  
**Repository:** AUo959/aurora-cloudbank-symbolic  
**Issues:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues
