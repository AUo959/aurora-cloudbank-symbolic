# Recovered Ethics Protocols — Review Intake

**Status:** Recovery and promotion planning only.  
**Issue:** #993  
**Runtime posture:** No runtime enforcement wiring is authorized by this document.

## Purpose

This folder records the review path for recovered ethics-layer protocols before any of them are promoted into CloudBank runtime behavior.

The recovered protocol suite includes:

- **Sherlock** — investigation, audit, traceability, causal mapping, transparency reporting, and doctrine verification.
- **Watson** — context retention, rigidity moderation, evidence correlation, and operator-readable briefing.
- **Moriarty** — anomaly containment, quarantine, review-only translation, ethics audit, anchor validation, and rollback-over-compromise posture.
- **Tribunal** — dispute, appeal, memory-sovereignty, narrative-integrity, drift-threshold, and containment-action adjudication.
- **SHADOWFAX** — stillness, pause, supervisory review, paradox escalation, and boundary-instability oversight.

## Canon warning

Recovered files and uploaded packages are useful source evidence, but they are not implementation canon until promoted through Git with review.

The current folder does **not** claim that recovered protocols are complete, sealed runtime canon, or safe to wire directly into enforcement. It provides a controlled path for inventory, custody review, schema review, integration-boundary review, and test planning.

## Separation-of-duties contract

| Protocol | Allowed role | Must not do |
|---|---|---|
| Sherlock | Investigate, reconstruct, trace, verify, and report | Mutate subject state, enforce containment, adjudicate appeals |
| Watson | Preserve context, correlate evidence, moderate rigidity, brief operators | Alter Sherlock logs, enforce containment, adjudicate disputes |
| Moriarty | Contain anomaly-class boundary risk under oversight | Treat containment as narrative escalation, adjudicate its own actions, bypass appeal |
| Tribunal | Adjudicate disputes, appeals, and containment questions | Perform primary investigation or secretly enforce containment |
| SHADOWFAX | Pause, stillness, supervisory escalation, boundary-conflict review | Bypass evidence, erase review paths, convert instability into proof |

## Current implementation boundaries

Recovered protocol work must be reviewed against existing CloudBank ethics infrastructure before runtime wiring:

- `src/monitoring/ethics_engine.py`
- `src/monitoring/ethics_gate.py`
- `src/subroutines/ethics_compliance_monitor.py`
- `modules/ethics_field/geometric_ethics.py`
- `modules/symbolic_core/model_validation.py`
- CASK issue #780 / PR #941 if still relevant at the time of integration

## Promotion rule

The first accepted PR for #993 should remain documentation/schema planning only.

Runtime implementation should occur only in follow-up issues after reviewers accept:

1. artifact inventory and custody status,
2. protocol schemas,
3. separation-of-duties contract,
4. integration boundaries,
5. test plan,
6. rollback and appeal requirements.

See `PROTOCOL_PROMOTION_PLAN.md` for the detailed plan.
