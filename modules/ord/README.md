# ORD-Series Drone Fleet — Policy Family

The Orion Station autonomous MCP validation layer, policy side. Recovered
from the ORION_ORD Promotion Workbench v0.5.0 (2026-03-10) and integrated
per its own promotion queue:

| Component | Role |
|---|---|
| `ord_threshold_registry.py` | Governance-backed policy config seam (defaults mirror `governance/ORD_THRESHOLD_REGISTRY__v0.5.0__2026-03-10.json`) |
| `ord_policy_engine.py` | Dispatch core — builds `DispatchOrder`s from `MissionBrief`s (which drones fly for which mission risk/destination/sensitivity) |
| `ord_inspection_policy.py` | Inspection core — quarantine and sanitization decisions (ORD-3 Shadowfax doctrine) |
| `ord_receipts.py` | Audit support — canonical JSON + SHA-256 receipts |

The fleet **entity** layer (ORD-1 Gamma Swarm / ORD-2 Delta Scout /
ORD-3 Shadowfax registry accessors) already lives in `src/entities/fleet/`.
This package supplies the policy decisions those entities execute.

Security posture (review-fix lineage carried in from the workbench):
hostname-based destination authority checks, token-aware sensitivity
classification across nested parameters, URL-spoofing and keyword-boundary
regression tests (`tests/ord/`, marked `critical`).

Posture per the workbench: governance-backed policy-library candidate.
Wiring it into live MCP dispatch surfaces is a separate, explicit step.

Specs: `docs/ord/` (SPEC, RefactorPlan, TEST_VECTOR_SET, all v0.5.0).
Legacy recovered sources remain in workspace staging only
(`_staging/orion_ord_review_fix/package/staging/legacy_pack/`), per the
promotion queue.
