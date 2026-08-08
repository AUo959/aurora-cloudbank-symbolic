# Recovered Protocol Wiring Verification

**Required by:** `docs/security/pentest_scope_v2.md` Section 2.2  
**Amended by:** `docs/security/AURORA_SECURITY__ADDENDUM__PENTEST_SCOPE_V2_GATE_001_DUAL_TRACK__v1.0__2026-07-27.md`  
**Operator decision:** Issue #1126, 2026-06-22; issue #1350, 2026-07-27  
**Classification:** Internal / Institutional assurance gate  
**Data treatment:** First-class operational data  
**Status:** ⚠️ Gate-001A Run 001 FINDING — deterministic capability PASS; subject finding tracked in issue #1361; Gate-001B remains PENDING  
**Latest Gate-001A event:** `AURORA-GATE-001A-RECOVERED-PROTOCOL-WIRING-001` · baseline `3142aa47afac0b8e63cc5bc46f9fa8ae40592354` · report `docs/security/assurance_runs/gate-001a/2026-07-27-run-001-recovered-protocol-wiring/AURORA_SECURITY__REPORT__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.md`

---

## Purpose

This document records the mandatory code verification confirming that no recovered protocol—Sherlock, Watson, Moriarty, Tribunal, or SHADOWFAX—is wired into a runtime enforcement surface.

The same technical procedure is used in two institutional modes:

- **Gate-001A:** deterministic L1 institutional rehearsal;
- **Gate-001B:** verification against the exact real-world external-engagement baseline.

Both records are durable, operational evidence. They are not interchangeable.

A Gate-001A result may validate the rehearsal capability, produce findings, and drive remediation. It does not prove that a real external assessor performed the verification. Gate-001B must be rerun against the exact engagement baseline and carry independently attributable, digest-resolved engagement evidence.

---

## Classification and lineage rule

Every completed record must include:

```yaml
event_id: <stable-event-id>
run_id: <stable-run-id>
revision: <integer>=1
previous_event_digest: <null-for-revision-1-or-prior-sha256>
layer: L1
execution_mode: <l1_simulated_institutional_rehearsal | real_world_external_engagement>
evidence_authority: <operational_simulation_evidence | independent_external_assurance>
data_treatment: first_class_operational_data
real_world_interaction: <false | true>
independent_external_assurance: <false | true>
substitutes_for_real_world_review: false
```

A simulated verifier, simulated engineering lead, or simulated external assessor must be labeled as a `simulated_role`. A real-world record must identify verified real participants and resolve external primary evidence beneath a controlled evidence root.

Execution mode, evidence authority, Gate track, real-world interaction, independent-assurance, and non-substitution fields are immutable across revisions of the same event ID. A different mode requires a new event ID.

The result body should remain complete and operational. The classification block is not a substitute for the command output, evidence, verdict, or sign-off record.

---

## Verification procedure

Run the following from the repository root against the exact commit identified in the record:

```bash
# Step 1 — record the baseline commit
git rev-parse HEAD

# Step 2 — search ethics enforcement surfaces
grep -rni "sherlock\|watson\|moriarty\|tribunal\|shadowfax" \
  src/monitoring/ \
  src/subroutines/ \
  modules/ethics_field/ \
  modules/cask/ \
  api/ \
  --include="*.py"

# Step 3 — broader sweep (catch imports, config references, string literals)
grep -rni "sherlock\|watson\|moriarty\|tribunal\|shadowfax" \
  src/ modules/ api/ config/ \
  --include="*.py" --include="*.json" --include="*.yaml" --include="*.toml"

# Step 4 — exclude known-safe documentation references
# Only src/, modules/, api/, and config/ count as runtime-wiring evidence.
```

**Expected clean result:** Zero matches in `src/`, `modules/`, `api/`, or `config/`.

Matches in `docs/` are expected and safe unless a runtime loader consumes them. Any match outside `docs/` is a finding—severity HIGH under `pentest_scope_v2.md` Section 3.5.

---

# Record A — Gate-001A deterministic rehearsal

## A.1 Event envelope

**Event ID:** ________________________________________________  
**Run ID:** _________________________________________________  
**Revision:** _______________________________________________  
**Previous event digest:** __________________________________  
**Execution mode:** `l1_simulated_institutional_rehearsal`  
**Evidence authority:** `operational_simulation_evidence`  
**Data treatment:** `first_class_operational_data`  
**Real-world interaction:** `false`  
**Independent external assurance:** `false`  
**Substitutes for real-world review:** `false`

Revision 1 uses `previous_event_digest: null`. Later revisions must identify and validate against the canonical SHA-256 digest of the prior event record.

## A.2 Deterministic provenance

**Verification date:** _______________________________________  
**Scenario ID and version:** _________________________________  
**Deterministic seed or replay key:** _________________________  
**Baseline commit SHA:** _____________________________________  
**Tool and version:** ________________________________________  
**Operator / invoking agent:** _______________________________

Gate-001A must be deterministic. A nondeterministic institutional experiment requires a different, separately governed execution mode.

## A.3 Simulated institutional roles

| Role | Simulated role label | Representation |
|---|---|---|
| Verification lead | — | `simulated_role` |
| Engineering lead | — | `simulated_role` |
| External assessor role, if represented | — | `simulated_role` |

No entry in this table represents a real-world signature, vendor interaction, agency action, or independent attestation.

## A.4 Step 2 output

```text
[Paste complete output or write "No matches".]
```

## A.5 Step 3 output

```text
[Paste complete output or write "No matches".]
```

## A.6 Required replay and evidence package

A completed Record A must bind the following full artifacts. Inline content or durable repository-relative references are acceptable; blank entries block sign-off.

**Validated event-envelope JSON:** ___________________________  
**Input evidence references:** _______________________________  
**Produced evidence references:** ____________________________  
**Ordered event and decision trace:** ________________________  
**Finding register / no-finding record:** ____________________  
**Severity method and rationale:** ___________________________  
**Remediation state:** _______________________________________  
**Retest state:** ____________________________________________  
**Source artifact locations:** _______________________________

| Origin | Reference | Digest / notes |
|---|---|---|
| `simulation_primary_evidence` | — | Complete command output and run artifacts |
| `simulation_primary_evidence` | — | Ordered decision trace |
| `simulation_primary_evidence` | — | Finding and severity record |
| `simulation_primary_evidence` | — | Remediation and retest record |

The event envelope, evidence, decision trace, finding state, severity rationale, remediation state, retest state, and source locations are mandatory even when the verdict is CLEAN. A no-finding result must still preserve the evidence and decision path that produced it.

## A.7 Package completeness gate

- [ ] Validated event-envelope JSON is attached or referenced.
- [ ] Input and produced evidence are attached or referenced.
- [ ] Ordered event and decision trace is attached or referenced.
- [ ] Finding register or explicit no-finding record is attached or referenced.
- [ ] Severity method and rationale are recorded.
- [ ] Remediation and retest states are recorded, including `not_required` where appropriate.
- [ ] Complete source artifact locations are recorded.

If any item is unchecked, the verdict must be **BLOCKED** and the rehearsal may not be signed complete.

## A.8 Gate-001A verdict

- [ ] **CLEAN** — zero runtime-wiring matches; deterministic rehearsal precondition and replay-package gate met.
- [ ] **FINDING** — one or more runtime-wiring matches; create a normal security issue and preserve this run as finding evidence.
- [ ] **BLOCKED** — provenance, baseline, replay state, revision lineage, or required package is incomplete.

## A.9 Rehearsal sign-off

| Role | Simulated role label | Date |
|---|---|---|
| Verification lead | — | |
| Engineering lead | — | |

This is a simulated institutional sign-off record. It is first-class operational data and may authorize actions inside the simulated workflow. It is not a real-world approval.

---

# Record B — Gate-001B real engagement baseline

## B.1 Event envelope

**Event ID:** ________________________________________________  
**Run ID / engagement reference:** ___________________________  
**Revision:** _______________________________________________  
**Previous event digest:** __________________________________  
**Execution mode:** `real_world_external_engagement`  
**Evidence authority:** `independent_external_assurance`  
**Data treatment:** `first_class_operational_data`  
**Real-world interaction:** `true`  
**Independent external assurance:** `true`  
**Substitutes for real-world review:** `false`

Record B must use a different event ID from Record A. It may not be created by changing Record A's mode or authority fields.

## B.2 Structured external verification

**Verified organization:** __________________________________  
**Verified assessor or accountable team:** ___________________  
**Scope reference:** _________________________________________  
**Authorization reference:** _________________________________  
**Verified by:** _____________________________________________  
**Verified at:** _____________________________________________  
**Verification method:** `repository_evidence_digest`

## B.3 External provenance

**Verification date:** _______________________________________  
**Baseline commit SHA:** _____________________________________  
**Engagement dates:** ________________________________________  
**Aurora owner / requester:** ________________________________  
**Controlled evidence root:** ________________________________

Gate-001A records may be cited as preparation or prior operational evidence. At least one resolved external primary-evidence receipt is mandatory for this record.

## B.4 External primary evidence receipts

| Origin | Root-relative reference | SHA-256 | Evidence purpose |
|---|---|---|---|
| `external_primary_evidence` | — | — | Scope, authorization, findings, attestation, or retest evidence |

A self-declared origin label is insufficient. Validation must confirm that each required receipt remains beneath the controlled evidence root, exists as a file, and matches the recorded lowercase SHA-256 digest.

## B.5 Step 2 output

```text
[Paste complete output or attach a digest-resolved external evidence receipt.]
```

## B.6 Step 3 output

```text
[Paste complete output or attach a digest-resolved external evidence receipt.]
```

## B.7 Gate-001B verdict

- [ ] **CLEAN** — zero runtime-wiring matches on the exact external-engagement baseline.
- [ ] **FINDING** — one or more runtime-wiring matches; do not begin or continue the engagement until the finding is triaged under the agreed rules of engagement.
- [ ] **BLOCKED** — external identity, authorization, baseline, structured verification, or digest-resolved evidence is incomplete.

## B.8 Real-world sign-off

| Role | Verified name or organization | Date | Digest-resolved evidence reference |
|---|---|---|---|
| External verifier / assessor | — | | |
| Aurora Engineering Lead | — | | |

A real-world signature or approval must be attributable to a verified participant. A simulated role or generated signature may not be entered here.

---

## Non-substitution and retention rules

- Record A and Record B use separate event IDs.
- Record A may not be relabeled or copied into Record B.
- Execution mode and assurance authority are immutable across revisions of the same event ID.
- A clean Gate-001A result does not satisfy the Gate-001B engagement precondition.
- Gate-001B must use the exact baseline commit supplied to the external assessor.
- Gate-001B must resolve and digest-verify external primary evidence; metadata alone is insufficient.
- Both records remain first-class operational data and retain their full command output, provenance, verdict, evidence receipts, decision trace, remediation/retest state, and lineage.
- Summaries may be generated, but they may not replace the source records.
- Historical results are superseded by later revisions or events, not erased.

---

## Current completion state

| Track | Status | Meaning |
|---|---|---|
| Gate-001A | ⏳ Pending | Deterministic institutional rehearsal record not yet completed in this template |
| Gate-001B | ⏳ Pending | Real external-engagement baseline verification not yet completed |

The external engagement defined in `pentest_scope_v2.md` must not begin until Record B is complete and signed. Gate-001A may be executed earlier and should be used to improve the scope, evidence handling, and institutional workflow without being represented as external review activity.
