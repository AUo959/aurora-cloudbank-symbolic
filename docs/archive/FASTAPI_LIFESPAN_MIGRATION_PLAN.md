# FastAPI Lifespan Migration Plan

Version: 1.0.0  
Context Tag: lifespan_migration_plan  
Generated: 2025-11-24T00:00:00Z (UTC placeholder)

## Purpose
Establish a unified, explicit FastAPI lifespan context (`lifespan(app)`) to coordinate startup and shutdown operations for Aurora CloudBank Symbolic. This consolidates initialization logic, ensures graceful teardown, and embeds Data Lineage Protocol (DLP) tagging for operational integrity.

## Current State (Baseline)
`api/aurora_api.py` already defines an `@asynccontextmanager` lifespan function performing:
- Telemetry initialization (`get_telemetry`, `get_r2_telemetry`)
- HALO/PAS Drift Controller startup/stop
- Shutdown telemetry snapshot export
This plan formalizes and extends that pattern with anchor, memory, quantum, and ledger hooks.

## Objectives
1. Centralize subsystem startup (telemetry, memory manager, insight ledger, thread bridges, quantum simulator, event coordination) with optional dependency guards.
2. Introduce structured DLP export manifests at shutdown (e.g. `lifespan_shutdown_manifest.json`).
3. Enforce UTC timestamp usage via `utc_now()` from `src/core/time_utils.py` for all lifecycle events.
4. Provide hooks for future: maintenance scanners, security audits, cache warmers.
5. Minimize blocking work on the event loop—use background tasks for long-running warmups.

## Startup Sequence (Proposed)
| Step | Component | Action | Optional | DLP Tag |
|------|-----------|--------|----------|---------|
| 1 | Telemetry | Initialize and record feature baseline | No | `lifespan_start_telemetry` |
| 2 | Insight Ledger | `initialize_ledger()` if available | Yes | `lifespan_start_ledger` |
| 3 | AuMemManager | Pre-warm memory seal / health check | Yes | `lifespan_start_memory` |
| 4 | Quantum Simulator | Enumerate backends & cache response | Yes | `lifespan_start_quantum` |
| 5 | Thread Transfer Bridges (v1/v2) | Initialize predictive drift layers | Yes | `lifespan_start_thread_bridge` |
| 6 | Event Coordination | Validate registry & reactive listeners | Yes | `lifespan_start_coordination` |
| 7 | HALO/PAS Controller | Start drift monitoring loop | Yes | `lifespan_start_halo_pas` |
| 8 | Crew Agents | Load baseline agent state (t1/srb anchors) | Yes | `lifespan_start_agents` |
| 9 | Health Snapshot | Emit initial health summary to log | No | `lifespan_start_health` |

All steps wrapped in try/except; failures logged with WARN without aborting application startup (graceful degradation).

## Shutdown Sequence (Proposed)
| Step | Component | Action | Ordering | DLP Tag |
|------|-----------|--------|----------|---------|
| 1 | HALO/PAS Controller | Stop monitoring loop | Early | `lifespan_stop_halo_pas` |
| 2 | Event Coordination | Flush pending events | Early | `lifespan_stop_coordination` |
| 3 | Quantum Simulator | Export active session summaries | Mid | `lifespan_stop_quantum` |
| 4 | AuMemManager | Seal memory state & write integrity manifest | Mid | `lifespan_stop_memory` |
| 5 | Insight Ledger | Flush audit buffers | Mid | `lifespan_stop_ledger` |
| 6 | Telemetry | Final metrics snapshot + lineage seal | Late | `lifespan_stop_telemetry` |
| 7 | Export Master Manifest | Aggregate all collected seals | Final | `lifespan_shutdown_export` |

## Master Shutdown Manifest Structure
```jsonc
{
  "context_tag": "lifespan_shutdown_export",
  "timestamp_utc": "<utc_now ISO>",
  "components": {
    "telemetry": {"operations": <int>, "features_tracked": <int>, "seal": "<sha256>"},
    "memory": {"total_memories": <int>, "seal": "<sha256>"},
    "quantum": {"states": <int>, "entanglements": <int>, "seal": "<sha256>"},
    "ledger": {"entries": <int>, "seal": "<sha256>"},
    "coordination": {"sessions": <int>, "seal": "<sha256>"}
  },
  "aggregate_seal": "<sha256 over sorted component seals>"
}
```

## Error Handling Strategy
- Non-critical subsystem failures log `WARNING` with component tag.
- Critical telemetry or security initialization failure logs `ERROR` but continues (system remains observable via fallback logger).
- Shutdown exceptions are caught individually; manifest includes `errors` array if present.

## Concurrency & Performance
- Long-running warmups (large memory pre-load, quantum backend enumeration) executed via `asyncio.create_task` post-yield if feasible.
- All blocking I/O minimized during startup to keep initial response latency low.

## Security & Integrity
- No secrets logged; redact tokens and credentials.
- All exported manifests hashed (sha256) and optionally signed via GPG key (`aurora-public-key.asc`) in a future phase.
- Telemetry snapshot uses sanitized request/session IDs (see `sanitize_request_id`, `sanitize_session_id`).

## Implementation Outline (Diff-Friendly)
1. Extend existing `lifespan` function: add guarded initialization blocks (e.g. `if INSIGHT_LEDGER_AVAILABLE and initialize_ledger:`).
2. Introduce helper `_export_shutdown_manifest()` near end of file.
3. Use `utc_now()` for all new timestamps.
4. Keep changes surgical: do not refactor unrelated route code.
5. Add minimal log lines with structured placeholders (no f-strings with dynamic data prone to injection).

## Testing Plan
| Test Type | Focus | Method |
|-----------|-------|--------|
| Unit | `_export_shutdown_manifest()` structure | Direct function call with mocked components |
| Integration | Startup/Shutdown sequence | Spin app with TestClient and ensure logs & manifest file appear |
| Regression | Existing routes unaffected | Smoke test key endpoints (`/health`, `/agent/tools`) |

## Rollout Strategy
Phase 1: Documentation & code patch (no new tests)  
Phase 2: Add unit tests for manifest export  
Phase 3: Add integration tests & optional GPG signing  
Phase 4: Expand shutdown cleanup (cache flush, async task cancellation)  

## Acceptance Criteria
- Lifespan includes all proposed startup/shutdown hooks (best-effort for optional modules).
- UTC timestamps only (no naive `datetime.utcnow()` left in new code).
- Shutdown manifest generated when all major components available (skips gracefully if not).
- Codacy analysis passes with zero new issues.

## Open Questions / Future Enhancements
- Should memory sealing invoke a differential export to reduce manifest size? (Future optimization)
- Add Prometheus exporter integration inside lifespan? (Phase after telemetry stabilization)
- Consider configurable timeout for graceful shutdown tasks.

## Summary
This migration formalizes lifecycle management, improving reliability, observability, and data lineage integrity while aligning with ongoing UTC standardization. Implementation can proceed immediately with minimal risk due to guarded optional imports.

---
Generated by Aurora Agent (lifespan plan).