# Single-Worker Constraint for Monitoring & Ethics Modules

## Overview

Aurora CloudBank's monitoring, ethics, and audit modules maintain **in-process state** that is not synchronized across multiple uvicorn workers. Running the API with `WEB_CONCURRENCY > 1` will cause state divergence between workers.

## Affected Modules

| Module | In-process state |
|--------|-----------------|
| `src/monitoring/monitoring_system.py` | `baselines`, `interventions`, `last_intervention_time` |
| `src/monitoring/drift_detector.py` | `baselines`, `alerts` |
| `src/monitoring/ethics_engine.py` | `violations`, loaded rules |
| `src/monitoring/audit_logger.py` | `entries` (in-memory mirror) |

## Symptoms of Multi-Worker Deployment

- **Baselines diverge**: a baseline established in worker A is invisible to worker B.
- **Intervention cooldowns bypass**: cooldowns tracked in worker A do not prevent re-fires in worker B.
- **Ethics violation counts mismatch** across workers.
- **Audit log entries** are written to disk by whichever worker handles the request; other workers do not reload from disk automatically.

## Recommended Deployment

Run with a **single uvicorn worker**:

```bash
# Explicit single worker (recommended)
WEB_CONCURRENCY=1 uvicorn api.aurora_api:app --host 0.0.0.0 --port 8000

# Or equivalently
uvicorn api.aurora_api:app --workers 1 --host 0.0.0.0 --port 8000
```

To scale horizontally, run **multiple single-worker instances** behind a load balancer. Each node independently maintains its own monitoring state. Cross-node state coordination (e.g. via Redis) is tracked in issue #810.

## Startup Warning

If `WEB_CONCURRENCY > 1` is detected at startup, the API emits:

```
WARNING: WEB_CONCURRENCY=N detected. The monitoring, ethics, and audit modules use
in-process state that is NOT shared across uvicorn workers. Run with WEB_CONCURRENCY=1
...
```

This is a non-fatal warning. The API will still start, but the above state-divergence issues apply.

## Future Work

Issue [#810](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/810) tracks externalizing shared state to Redis to enable true multi-worker deployments.
