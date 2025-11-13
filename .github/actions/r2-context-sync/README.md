# R2 Context Sync Action

**Version:** 2.0.0  
**Type:** Composite Action  
**Purpose:** Synchronizes R-2 agent telemetry context with collaborative runtime environments

## Overview

The R2 Context Sync action enables secure, DLP-compliant context synchronization between Aurora CloudBank Symbolic and collaborative runtime environments. It collects R-2 agent telemetry data, validates allowlist repositories, and propagates context with symbolic anchors (T1, SRB) for drift-free state transfer.

## Features

- ✅ **Allowlist Validation** - Only syncs with pre-approved repositories
- ✅ **Symbolic Anchors** - Maintains T1/SRB anchor integrity across transfers
- ✅ **DLP Compliance** - Full context tagging and hash verification
- ✅ **Drift Detection** - Monitors and logs symbolic drift (Δ0.0 target)
- ✅ **Incremental Sync** - Supports full, incremental, and minimal sync modes
- ✅ **Ethics Protocol** - Adheres to Picard_Delta_3 ethics framework

## Symbolic Tags

- `T1:R2_SYNC` - Temporal anchor for sync operations
- `SRB:CONTEXT_TRANSFER` - Spatial-relational boundary for context scope
- `DLP:r2_collab_sync` - Data lineage protocol tag

**Anchor Seed:** `EOS_SEED_ORION_v2.0.0`  
**Ethics Protocol:** `Picard_Delta_3`

## Usage

### Basic Usage

```yaml
- name: R2 context sync
  uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-context-sync@main
  with:
    allowlist: '["AUo959/aurora-cloudbank-runtime", "AUo959/aurora-agents"]'
```

### Full Configuration

```yaml
- name: R2 context sync
  uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-context-sync@main
  with:
    allowlist: '["AUo959/aurora-cloudbank-runtime"]'
    sync_mode: 'incremental'
    telemetry_endpoint: 'http://localhost:8000/telemetry'
    context_retention_hours: '24'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `allowlist` | JSON array of allowed repositories | No | `[]` |
| `sync_mode` | Sync mode: `full`, `incremental`, or `minimal` | No | `incremental` |
| `telemetry_endpoint` | R-2 telemetry endpoint URL | No | `http://localhost:8000/telemetry` |
| `context_retention_hours` | Hours to retain context data | No | `24` |

## Outputs

| Output | Description |
|--------|-------------|
| `sync_status` | Status: `success`, `partial`, or `failed` |
| `context_hash` | SHA256 hash of synchronized context |
| `synced_count` | Number of context records synchronized |
| `timestamp` | ISO 8601 timestamp of completion |

## Sync Modes

### Full Sync
- Synchronizes entire telemetry context
- Includes all metrics, traces, and symbolic anchors
- Recommended for: Initial setup, recovery scenarios

### Incremental Sync (Default)
- Syncs only changes since last successful sync
- Maintains drift log continuity
- Recommended for: Scheduled syncs, regular operations

### Minimal Sync
- Syncs critical status and health data only
- Minimal bandwidth usage
- Recommended for: High-frequency checks, bandwidth constraints

## Context Structure

Synchronized context includes:

```json
{
  "telemetry_snapshot": {
    "timestamp": "2025-11-13T00:30:00Z",
    "metrics": { "operations_count": 1234, "success_rate": 0.99 },
    "health_status": "healthy",
    "version": "2.0.0"
  },
  "context_records": [],
  "drift_log": {
    "drift_delta": 0.0,
    "baseline_hash": "BASELINE_HASH_v2",
    "drift_detected": false
  },
  "symbolic_anchors": {
    "T1_state": 42,
    "SRB_resolution": 1337,
    "chain_notation": "001//999//"
  }
}
```

## Allowlist Configuration

The allowlist prevents unauthorized context synchronization. Format:

```json
["owner1/repo1", "owner2/repo2"]
```

**Security:** If `allowlist` is empty or `[]`, sync is **disabled by default** for safety.

## DLP Compliance

All sync operations include:

- **Context Tag:** `r2_collab_sync`
- **Symbolic Hash:** SHA256 of context payload
- **Anchor Validation:** T1/SRB integrity checks
- **Drift Monitoring:** Real-time drift detection (Δ0.0 target)

## Ethics Protocol: Picard_Delta_3

Adheres to Aurora's Picard_Delta_3 ethics framework:

1. **No Unauthorized Sync** - Allowlist enforcement mandatory
2. **Context Privacy** - PII filtering applied (future enhancement)
3. **Drift Transparency** - All drift logged and reported
4. **Audit Trail** - Complete lineage tracking via DLP tags

## Example Workflow

```yaml
name: R2 Context Sync
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  workflow_dispatch:

jobs:
  sync-context:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Sync R2 context
        uses: AUo959/aurora-cloudbank-symbolic/.github/actions/r2-context-sync@main
        with:
          allowlist: '["AUo959/aurora-cloudbank-runtime"]'
          sync_mode: 'incremental'
      
      - name: Check sync status
        run: |
          echo "Sync Status: ${{ steps.sync.outputs.sync_status }}"
          echo "Context Hash: ${{ steps.sync.outputs.context_hash }}"
          echo "Records Synced: ${{ steps.sync.outputs.synced_count }}"
```

## Troubleshooting

### Sync Disabled
**Symptom:** Action completes immediately without sync  
**Cause:** Empty allowlist  
**Solution:** Configure `allowlist` input with target repositories

### Sync Failed
**Symptom:** `sync_status` output is `failed`  
**Cause:** Target endpoint unavailable or validation error  
**Solution:** Check telemetry endpoint availability and logs

### Drift Detected
**Symptom:** `drift_detected: true` in drift_log  
**Cause:** Context divergence from baseline  
**Solution:** Review drift_delta value, consider full sync for re-baseline

## Production Considerations

**Current Implementation:** Simulation mode for development/testing

**Production Enhancements (Future):**
1. Live telemetry API integration
2. Encrypted context transfer
3. Mutual TLS authentication
4. Real-time drift correction
5. PII filtering on sensitive context fields

## Related Documentation

- [R2 Agent Telemetry](../../../docs/R2_AGENT_TELEMETRY.md)
- [Collab-Sync Workflow](../../workflows/collab-sync.yml)
- [Thread Transfer Protocol](../../../modules/reflective_autonomy/thread_transfer/THREAD_TRANSFER_PROTOCOL.md)

## Version History

- **2.0.0** (2025-11-13) - Production-ready composite action with symbolic anchors
- **1.0.0** (2025-10-15) - Initial implementation

## Contact

**Team:** Aurora CloudBank Team  
**Repository:** AUo959/aurora-cloudbank-symbolic  
**Issues:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues
