# GUMAS Phase-8 Contract Reconciliation Decision v1.0

**Date:** 2026-08-14  
**Task:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**PR:** `#1506`  
**Status:** binding Phase-8 authority decision

## Decision

Two Phase-8 v1.0 specifications were committed concurrently:

1. `simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_WITHDRAWAL_TERMINATION__v1.0__2026-08-14.md`
2. `simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_RESOLUTION_TERMINATION__v1.0__2026-08-14.md`

The second specification, `GUMAS__SPEC__DETERMINISTIC_MORALE_RESOLUTION_TERMINATION__v1.0__2026-08-14.md`, is the **single normative Phase-8 implementation contract**.

The first specification is preserved as historical design evidence but is **superseded for implementation and validation**. No executable Phase-8 code may mix its incompatible thresholds or state semantics into the normative contract unless a later explicitly versioned amendment changes the authority.

## Why the resolution/termination contract prevails

The selected contract better preserves the committed simulator invariants:

- **Commander agency:** surrender is possible only when the current deterministic command posture is `CEASEFIRE_PROBE` or `DISENGAGE`; Phase 8 cannot invent surrender contrary to the command policy.
- **Physical withdrawal:** successful withdrawal requires `DISENGAGE` plus committed P17 boundary and outbound-velocity evidence; position alone is insufficient.
- **Partial-fleet realism:** withdrawal is evaluated against an explicit `700/1000` mobile-force threshold and records stranded/abandoned assets rather than requiring every mobile survivor to cross simultaneously.
- **Quiet-step morale integrity:** specialist dissent cannot erode cohesion by itself; dissent couples only to real battle shock.
- **Ceasefire continuity:** offers persist deterministically, `PRESS` rescinds them, and Phase 8 emits the opposing-offer negotiation signal for the later live command-observation bridge.
- **Control-state separation:** Phase-7 physical disposition is never rewritten. Phase 8 emits side engagement/protection state and sorted protected ship IDs for Phase-9 enforcement.
- **No false victory:** unilateral withdrawal records physical outcome/local control without automatically inventing a victor.
- **Deterministic geometry:** withdrawal uses exact integer squared-distance and outbound dot-product predicates.

## Preserved useful intent from the superseded contract

The following ideas are already represented by, or are compatible with, the selected contract and remain required:

- physical disposition remains separate from willingness/control state;
- raw upstream provenance must validate before Phase-8 output is accepted;
- stable canonical ordering is mandatory;
- withdrawal/surrender/ceasefire must be factual state transitions, not narrative interpretations;
- no class/polity/prose branching, ambient RNG, or floating-point authority;
- Phase 8 never moves vessels, fires weapons, applies damage, or reports the battle;
- Run 0 remains blocked until the integrated Phase-9 loop, reporter, and Controls A/B/C pass.

## Implementation rule

All Phase-8 constants, tests, runtime behavior, acceptance receipts, and DTER references MUST trace to:

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_RESOLUTION_TERMINATION__v1.0__2026-08-14.md`

If implementation discovers a genuine defect or ambiguity in that contract, stop and version the contract forward before changing runtime behavior. Do not silently borrow a conflicting rule from the superseded specification.
