# L1L2_SYSTEM__ORD_DroneDispatch__SPEC__v0.5.0__2026-03-10

Status: draft_specification  
Anchor: EOS_SEED_ORION  
Ethics: Picard_Delta_3  
Source basis: `staging/legacy_pack/SOURCE__Recovered__ORD_DroneDispatch__v0.1__2026-03-10.py`

## Purpose

ORD Drone Dispatch is a policy-governed mission router for assigning pre-flight and post-flight controls around a payload operation.

This v0.5.0 pass promotes a clearer architecture statement: **ORD is a deterministic policy family governed by an external threshold registry, plus adapter boundaries and receipts.**

## Stable module family

- `modules/ord/ord_policy_engine.py`
- `modules/ord/ord_inspection_policy.py`
- `modules/ord/ord_receipts.py`
- `modules/ord/ord_threshold_registry.py`

## New governance seam

Threshold ownership now lives in `governance/ORD_THRESHOLD_REGISTRY__v0.5.0__2026-03-10.json`.

Controlled values:
- reconnaissance threshold
- inspection threshold
- secure transport threshold
- drift threshold
- quantum seal threshold
- quarantine violation count

This is the main architectural improvement over v0.4.0. Dispatch and inspection logic now consume reviewable governance values instead of quietly embedding them.

## Canonical system statement

ORD SHOULD be treated as a **policy orchestration layer with pure decision cores, a governance-backed threshold registry, and environment adapters**.

## Hard invariants

- **No L1/L2 bleed:** symbolic identities are metadata, not operational dependencies.
- **Ethics before integration:** inspection must be able to block integration.
- **Governance before threshold drift:** threshold values must be reviewable outside runtime logic.
- **Pure-policy separability:** dispatch and inspection decisions must run without network access.
- **Receipt discipline:** mission-level output must be serializable into audit-friendly records.
- **Adapter isolation:** environment-specific bridges belong behind interfaces.
- **Deterministic ordering:** normalized action lists and serializations must be stable.

## Promotion posture

Promote now as:
- architecture reference
- specification candidate
- governance-backed policy-library candidate
- testable dispatch and inspection core

Do not promote yet as:
- station control software
- autonomous L1 deployment artifact
- validated perimeter security product

## Open decisions

1. Whether sensitivity classes should remain `STANDARD / CONFIDENTIAL / RESTRICTED` or expand.
2. Whether Wisp remains a transport-only role or becomes a packaging-policy family.
3. Which threshold changes require dual approval versus single-owner review.
4. Which inspection findings must be adapter-provided instead of inferred from payload metadata.
