# ORD_THRESHOLD_REGISTRY__v0.5.0__2026-03-10

Status: draft_governance_candidate  
Anchor: EOS_SEED_ORION  
Ethics: Picard_Delta_3

## Purpose

This registry externalizes the main ORD thresholds so dispatch and inspection logic stop hiding governance decisions in code.

## Controlled values

- `reconnaissance_threshold = 0.40`
- `inspection_threshold = 0.40`
- `secure_transport_threshold = 0.40`
- `drift_threshold = 0.005`
- `quantum_seal_threshold = 0.60`
- `quarantine_violation_count = 3`

## Why this matters

v0.4.0 still worked, but the thresholds lived inside code like tiny policy goblins wearing fake moustaches. This pass moves them into reviewable governance.

## Rules

1. Code may consume this registry.
2. Code may not silently redefine these values.
3. Threshold changes require a version bump and receipt note.
4. Drift + ethics failure remains an explicit escalation path.
5. Restricted-sensitivity markers force secure transport consideration.
6. Sensitivity markers should be matched on token boundaries over structured keys and values, not arbitrary substrings.

## Open follow-up

Threshold ownership should be assigned to a named review function before any L1-adjacent deployment use.
