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

## Custody review, 2026-11-23

Codex verified the raw `SRB_SHADOWFAX_Stillness_v1.0.zip` Git blob
`7ead99def0f8e22c97358913bba197184a01f5c2` at
commit `06ea38edadf3167cbe57b4e49340946d6ac1c972`. Its 7,595,909 bytes,
11 ZIP members, and SHA-256 match the historical artifact inventory.
The ZIP contains general governance, continuity, and registry material.
Custody review did not identify a member attributable to the standalone
SHADOWFAX protocol. The internal path and hash, and the full custody
verification fields, remain pending. The wiring block remains in force
and [#1361](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1361)
tracks ORD-3 lineage. [Artifact inventory](../../../.repohealth/artifacts_manifest.json)

The control-plane inventory identifies candidate archives for the other
protocols, including the Aurora 2.5 ethics bundles and
`MORIARTY_Operational_Pack_v1.zip`. The inventory supplies expected digests.
Custody still requires the archive bytes, a uniquely attributable member
for each protocol, and the archive and member SHA-256 digests calculated
from those bytes. Sherlock, Watson, Moriarty, and Tribunal therefore
remain pending in the live manifest.
[Control-plane archive inventory](https://github.com/AUo959/Aurora_ORIONCORE_Directory_Main/blob/6f28f881fb5eddf5c974b98e35f697183539bb54/catalog/archive_inventory.jsonl)
