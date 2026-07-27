# Recovered Protocol Wiring Verification

**Required by:** `docs/security/pentest_scope_v2.md` Section 2.2  
**Amended by:** `docs/security/AURORA_SECURITY__ADDENDUM__PENTEST_SCOPE_V2_GATE_001_DUAL_TRACK__v1.0__2026-07-27.md`  
**Operator decision:** Issue #1126, 2026-06-22; issue #1350, 2026-07-27  
**Classification:** Internal / Institutional assurance gate  
**Data treatment:** First-class operational data  
**Status:** ⏳ PENDING — Gate-001A and Gate-001B records are maintained separately

---

## Purpose

This document records the mandatory code verification confirming that no recovered protocol—Sherlock, Watson, Moriarty, Tribunal, or SHADOWFAX—is wired into a runtime enforcement surface.

The same technical procedure is used in two institutional modes:

- **Gate-001A:** deterministic L1 institutional rehearsal;
- **Gate-001B:** verification against the exact real-world external-engagement baseline.

Both records are durable, operational evidence. They are not interchangeable.

A Gate-001A result may validate the rehearsal capability, produce findings, and drive remediation. It does not prove that a real external assessor performed the verification. Gate-001B must be rerun against the exact engagement baseline and carry independently attributable engagement provenance.

---

## Classification rule

Every completed record must include:

```yaml
layer: L1
execution_mode: <l1_simulated_institutional_rehearsal | real_world_external_engagement>
evidence_authority: <operational_simulation_evidence | independent_external_assurance>
data_treatment: first_class_operational_data
real_world_interaction: <false | true>
independent_external_assurance: <false | true>
substitutes_for_real_world_review: false
```

A simulated verifier, simulated engineering lead, or simulated external assessor must be labeled as a `simulated_role`. A real-world record must identify verified real participants or controlled external evidence.

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
**Execution mode:** `l1_simulated_institutional_rehearsal`  
**Evidence authority:** `operational_simulation_evidence`  
**Data treatment:** `first_class_operational_data`  
**Real-world interaction:** `false`  
**Independent external assurance:** `false`  
**Substitutes for real-world review:** `false`

## A.2 Deterministic provenance

**Verification date:** _______________________________________  
**Scenario ID and version:** _________________________________  
**Deterministic seed or replay key:** _________________________  
**Baseline commit SHA:** _____________________________________  
**Tool and version:** ________________________________________  
**Operator / invoking agent:** _______________________________

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

## A.6 Gate-001A verdict

- [ ] **CLEAN** — zero runtime-wiring matches; deterministic rehearsal precondition met.
- [ ] **FINDING** — one or more runtime-wiring matches; create a normal security issue and preserve this run as finding evidence.
- [ ] **BLOCKED** — provenance, baseline, or replay state is incomplete.

## A.7 Rehearsal sign-off

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
**Execution mode:** `real_world_external_engagement`  
**Evidence authority:** `independent_external_assurance`  
**Data treatment:** `first_class_operational_data`  
**Real-world interaction:** `true`  
**Independent external assurance:** `true`  
**Substitutes for real-world review:** `false`

## B.2 External provenance

**Verification date:** _______________________________________  
**Baseline commit SHA:** _____________________________________  
**Verified organization or assessor:** _______________________  
**Scope / authorization reference:** _________________________  
**Controlled evidence reference:** ___________________________  
**Aurora owner / requester:** ________________________________

Gate-001A records may be cited as preparation or prior operational evidence. At least one external primary-evidence reference is mandatory for this record.

## B.3 Step 2 output

```text
[Paste complete output or attach an attributable controlled evidence reference.]
```

## B.4 Step 3 output

```text
[Paste complete output or attach an attributable controlled evidence reference.]
```

## B.5 Gate-001B verdict

- [ ] **CLEAN** — zero runtime-wiring matches on the exact external-engagement baseline.
- [ ] **FINDING** — one or more runtime-wiring matches; do not begin or continue the engagement until the finding is triaged under the agreed rules of engagement.
- [ ] **BLOCKED** — external identity, authorization, baseline, or attributable evidence is incomplete.

## B.6 Real-world sign-off

| Role | Verified name or organization | Date | Evidence reference |
|---|---|---|---|
| External verifier / assessor | — | | |
| Aurora Engineering Lead | — | | |

A real-world signature or approval must be attributable to a verified participant. A simulated role or generated signature may not be entered here.

---

## Non-substitution and retention rules

- Record A and Record B use separate event IDs.
- Record A may not be relabeled or copied into Record B.
- A clean Gate-001A result does not satisfy the Gate-001B engagement precondition.
- Gate-001B must use the exact baseline commit supplied to the external assessor.
- Both records remain first-class operational data and retain their full command output, provenance, verdict, and lineage.
- Summaries may be generated, but they may not replace the source records.
- Historical results are superseded by later runs, not erased.

---

## Current completion state

| Track | Status | Meaning |
|---|---|---|
| Gate-001A | ⏳ Pending | Deterministic institutional rehearsal record not yet completed in this template |
| Gate-001B | ⏳ Pending | Real external-engagement baseline verification not yet completed |

The external engagement defined in `pentest_scope_v2.md` must not begin until Record B is complete and signed. Gate-001A may be executed earlier and should be used to improve the scope, evidence handling, and institutional workflow without being represented as external review activity.
