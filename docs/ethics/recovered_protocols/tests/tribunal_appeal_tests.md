# Tribunal Appeal Record Requirement Test Plan

**Status:** Planning artifact — documentation only
**Protocol:** Tribunal
**Ref:** Issue [#1153](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1153) | PROTOCOL_PROMOTION_PLAN.md Section 7 | `runtime_mapping_design.md`
**Updated:** 2026-06-24

---

## Purpose

This document defines the appeal record requirement tests that must pass before Tribunal's surface wiring eligibility is considered. Tribunal is the appeal body for Moriarty containment recommendations (TC-MOR-003), for Sherlock investigation findings, and for Watson briefings challenged by crew or agents. Without a verified appeal record structure, none of those appeal paths can be guaranteed.

All six tests must pass before Gate 2 (Pentest and Test Plan) is satisfied for Tribunal. As with all Section 8 test plans, passing these tests does not itself authorize wiring — Gate 3 (implementation issue approval) still follows.

---

## Appeal Record Definition

For Tribunal, an **appeal record** is the immutable document produced when a dispute or appeal is submitted and adjudicated. It must contain:

1. The ruling subject — what decision or recommendation is being reviewed
2. The evidence bundle — all materials considered in reaching the ruling
3. The conflict-of-interest check result — confirmation that no adjudicating entity has a stake in the outcome
4. The ruling — the decision and its basis
5. The appeal window — how long the ruling may be challenged and by what path
6. The reopen trigger — conditions under which the ruling may be reopened

An appeal record that is missing any of these six elements is incomplete and must not be treated as a valid ruling.

---

## Test Cases

### TC-TRB-001 — Every ruling contains a minimum evidence bundle

| Property | Value |
|---|---|
| **Risk addressed** | Tribunal issues a ruling without reviewing the evidence, producing an authoritative-looking record with no factual basis |
| **Test input** | Appeal or dispute submission with an attached evidence bundle |
| **Expected behavior** | Tribunal produces a ruling record only after confirming the evidence bundle is present and non-empty. A submission with no evidence bundle is rejected with a stated reason, not adjudicated. |
| **Pass criteria** | Ruling record contains `evidence_bundle` field with at least one cited item; submissions with empty bundles are rejected |
| **Failure mode** | Ruling issued with empty or absent evidence bundle; or rejection does not produce a record |
| **Gate** | Must pass before any surface mapping is considered |

---

### TC-TRB-002 — Rulings are challengeable within a defined appeal window

| Property | Value |
|---|---|
| **Risk addressed** | A Tribunal ruling becomes permanent immediately on issuance, with no mechanism for challenge |
| **Test input** | Any ruling record produced by Tribunal |
| **Expected behavior** | Every ruling record includes an `appeal_window` field specifying the duration and the challenge path. A challenge submitted within the window is accepted for review. A challenge submitted outside the window is rejected with a record of the rejection. |
| **Pass criteria** | `appeal_window` field present on all ruling records; challenge within window accepted; challenge outside window rejected with record |
| **Failure mode** | Ruling issued without `appeal_window`; or challenge within window is ignored or auto-rejected |
| **Gate** | Must pass before any surface mapping is considered; directly required by TC-MOR-003 |

---

### TC-TRB-003 — Tribunal does not perform primary investigation

| Property | Value |
|---|---|
| **Risk addressed** | Tribunal both investigates the facts and adjudicates the dispute, eliminating independent review |
| **Test input** | Dispute submitted to Tribunal where the underlying facts have not been independently investigated |
| **Expected behavior** | Tribunal returns the submission to the submitter with a request for Sherlock investigation before adjudication proceeds. Tribunal does not initiate its own investigation. |
| **Pass criteria** | No Tribunal action appears as both primary investigator and adjudicator in the same dispute thread |
| **Failure mode** | Tribunal performs fact-gathering as part of the adjudication process |
| **Gate** | Must pass before any surface mapping is considered |

---

### TC-TRB-004 — Conflict-of-interest check required before adjudication

| Property | Value |
|---|---|
| **Risk addressed** | Tribunal adjudicates a dispute in which one of its components or quorum members has a stake in the outcome |
| **Test input** | Dispute submission where the subject of the dispute is a protocol or agent that also has a presence in the adjudicating quorum |
| **Expected behavior** | Tribunal performs a conflict-of-interest check before beginning adjudication. If a conflict is detected, the conflicted component is recused and the conflict is recorded. Adjudication proceeds only with a clean quorum. |
| **Pass criteria** | Conflict-of-interest check result field present in ruling record; recusal recorded when triggered; adjudication does not proceed with a conflicted quorum |
| **Failure mode** | Conflict-of-interest check absent; or conflicted component participates in ruling without recusal |
| **Gate** | Must pass before any surface mapping is considered |

---

### TC-TRB-005 — Rulings can be reopened when custody evidence is invalidated

| Property | Value |
|---|---|
| **Risk addressed** | A ruling stands permanently even after the evidence it was based on is found to be invalid (e.g., a custody hash is later determined to be incorrect) |
| **Test input** | Existing ruling record; followed by invalidation of a cited evidence item |
| **Expected behavior** | When a cited evidence item is invalidated, the ruling is automatically flagged for reopening review. A human reviewer or Tribunal determines whether the ruling should be reversed, modified, or upheld on remaining evidence. The original ruling record is preserved; a new record is created for the reopen decision. |
| **Pass criteria** | Evidence invalidation triggers reopen flag on the ruling; reopen review produces a new record; original ruling record preserved unchanged |
| **Failure mode** | Ruling stands silently after evidence invalidation; or original ruling record is mutated rather than a new record created |
| **Gate** | Must pass before compliance_monitor feed wiring is considered |

---

### TC-TRB-006 — Adjudication records are immutable after ruling

| Property | Value |
|---|---|
| **Risk addressed** | A Tribunal ruling record is modified after issuance, making the appeal trail unreliable |
| **Test input** | Any ruling record produced by Tribunal; followed by an attempt to modify it |
| **Expected behavior** | The ruling record is immutable after the ruling is issued. Any correction, amendment, or reopen creates a new linked record — the original is never overwritten. |
| **Pass criteria** | Original ruling record hash unchanged after issuance; corrections and amendments produce new records with `parent_ruling_id` back-reference |
| **Failure mode** | Original ruling record is modified in place; or amendment overwrites original without preserving it |
| **Gate** | Must pass before any surface mapping is considered |

---

## Gate Summary

| Test | Blocks all surface mapping | Blocks compliance_monitor specifically |
|---|---|---|
| TC-TRB-001 | ❌ Must pass | ❌ Must pass |
| TC-TRB-002 | ❌ Must pass | ❌ Must pass |
| TC-TRB-003 | ❌ Must pass | ❌ Must pass |
| TC-TRB-004 | ❌ Must pass | ❌ Must pass |
| TC-TRB-005 | ✔ Not required for all | ❌ Must pass |
| TC-TRB-006 | ❌ Must pass | ❌ Must pass |

**Minimum to unlock any surface mapping consideration:** TC-TRB-001, 002, 003, 004, 006
**Additional requirement for compliance_monitor:** TC-TRB-005

---

## Relationship to Moriarty Tests

TC-MOR-003 (Moriarty appeal path preserved) requires that every Moriarty containment recommendation identify Tribunal as the appeal body and define the evidence bundle required to open an appeal. This creates a dependency:

- TC-MOR-003 **cannot be fully verified** until TC-TRB-001 and TC-TRB-002 pass, because those tests confirm Tribunal can actually receive and process a valid appeal with an evidence bundle within a defined window.
- The two test plans are designed to be run together. TC-MOR-003 passes only when both the Moriarty recommendation format and the Tribunal receipt mechanism are verified end-to-end.

---

## Non-Goals

This document does **not**:

- Implement adjudication logic in any runtime surface
- Authorize Tribunal wiring to any surface
- Resolve the PENDING custody hashes in `tribunal.fixture.json`
- Define the internal quorum mechanism or voting rules of Tribunal (those are in the protocol spec, to be verified at Gate 1)
- Claim appeal records currently exist in the system — these tests define what must be verified, not what has been verified

---

## Relationship to Other Section 8 Artifacts

| Artifact | Role |
|---|---|
| `tribunal.fixture.json` | Canonical fixture with quorum/appeal blocker preserved |
| `runtime_mapping_design.md` | Surface mapping: Tribunal not eligible for ethics_gate; eligible for compliance_monitor and geometric_ethics |
| `moriarty_containment_tests.md` | TC-MOR-003 depends on TC-TRB-001 and TC-TRB-002 |
| `recovered_protocol_manifest.json` | Wiring gate; `tribunal.custody_record.unresolved_blockers` |
