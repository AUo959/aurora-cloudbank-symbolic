# Runtime Mapping Design — Recovered Protocols

**Status:** Planning artifact — documentation only
**Authority:** Operator + Aurora joint decision required before any mapping is activated
**Ref:** Issue [#1151](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1151) | PROTOCOL_PROMOTION_PLAN.md Section 7–8
**Updated:** 2026-06-24

---

## Purpose

This document describes the **design intent** for how each recovered ethics protocol would map to runtime enforcement surfaces once all promotion gates are met. It is a planning document, not an authorization. No protocol listed here is currently wired to any runtime surface.

The authoritative gate list governing when wiring may begin is in `recovered_protocol_manifest.json` under `wiring_gate`. This document expands on the rationale and sequencing behind those gates.

---

## Runtime Surfaces

Four surfaces exist in the Orion Station ethics architecture that recovered protocols may eventually connect to:

### `EthicsEngine`

| Property | Value |
|---|---|
| Current status | **Not wired to any recovered protocol** |
| Function | Core ethics evaluation — assesses proposed actions against ethical anchors before execution |
| Layer | L1 operational decision layer |
| Pre-conditions for wiring | Custody verified + pentest signed + Section 7 tests passing + implementation issue approved |

### `ethics_gate`

| Property | Value |
|---|---|
| Current status | **Not wired to any recovered protocol** |
| Function | Binary gate — allows or blocks an action based on EthicsEngine output |
| Layer | L1, inline with action dispatch |
| Pre-conditions for wiring | Same as EthicsEngine; must not be wired without EthicsEngine mapping also reviewed |

### `compliance_monitor`

| Property | Value |
|---|---|
| Current status | **Not wired to any recovered protocol** |
| Function | Continuous background monitoring — flags drift, anomalies, and doctrine violations |
| Layer | L1/L2 boundary observer |
| Pre-conditions for wiring | Custody verified + pentest signed + Section 7 tests passing + implementation issue approved; additionally requires L1/L2 boundary isolation confirmed |

### `geometric_ethics`

| Property | Value |
|---|---|
| Current status | **Not wired to any recovered protocol** |
| Function | Spatial/relational ethics reasoning — evaluates multi-agent and cross-layer ethical geometry |
| Layer | L3 framework layer (Axiomera, Caelion, Sentari, Velatrix) |
| Pre-conditions for wiring | Same as EthicsEngine; L3 framework authority must be confirmed prior to wiring |

---

## Protocol-to-Surface Mapping Table

This table describes **intended eventual mapping only**. All entries are conditional on all promotion gates being met. "Eligible" means the protocol's design is compatible with that surface — it does not mean wiring is authorized.

| Protocol | EthicsEngine | ethics_gate | compliance_monitor | geometric_ethics | Notes |
|---|---|---|---|---|---|
| **Sherlock** | Eligible (evidence input) | Not eligible (investigation ≠ enforcement) | Eligible (traceability feed) | Eligible (doctrine verification) | Sherlock produces inputs and reports; it does not enforce. Must never be wired to ethics_gate directly. |
| **Watson** | Eligible (context input) | Not eligible (briefing ≠ gate decision) | Eligible (context correlation) | Not eligible | Watson moderates and correlates; it does not adjudicate. ethics_gate wiring explicitly excluded. |
| **Moriarty** | Eligible (anomaly signal) | **Conditional** (quarantine recommendation only, not auto-enforce) | Eligible (anomaly detection feed) | Eligible (anchor validation) | **HARD BLOCK**: containment boundaries must be tested before any ethics_gate wiring is considered. Quarantine must remain a recommendation, not an automatic gate action, until tests pass. |
| **Tribunal** | Not eligible (adjudication is post-hoc, not pre-action) | Not eligible | Eligible (ruling record feed) | Eligible (dispute record) | Tribunal reviews decisions already made. It must not sit inline on the action dispatch path. |
| **SHADOWFAX** | **Blocked** | **Blocked** | **Blocked** | **Blocked** | Standalone bundle not located — HARD BLOCK on all surface mapping until bundle is found and hash-verified. |

---

## Gate Ordering

Every protocol must pass these gates **in order** before any surface mapping is activated. Gates are per-protocol — Sherlock passing all gates does not unblock Moriarty.

### Gate 1 — Custody Resolution

- `source_package_name` and `source_package_sha256` verified
- `internal_file_path` and `internal_file_sha256` verified
- `verification_date` and `reviewer_or_agent_surface` recorded
- `unresolved_blockers` empty (or all HARD BLOCKs resolved with operator sign-off)
- `promotion_decision` updated to `approved_for_schema_promotion` by operator
- **Output:** fixture updated, live manifest updated, `docs/security/recovered_protocol_wiring_verification.md` updated

### Gate 2 — Pentest and Test Plan

- `docs/security/pentest_scope_v2.md` complete and signed (Section 11 signatures on file)
- Section 7 test plan items in PROTOCOL_PROMOTION_PLAN.md passing for this protocol
- For Moriarty specifically: containment boundary tests passing (see #1152)
- For Tribunal specifically: appeal record requirement tests passing (see #1153)
- **Output:** test results recorded, pentest report linked in implementation issue

### Gate 3 — Implementation Issue Approval

- A follow-up implementation issue exists (per PROTOCOL_PROMOTION_PLAN.md Section 8)
- Issue is approved by operator before work begins
- `promotion_decision` updated to `approved_for_runtime_wiring` in manifest and fixture
- **Output:** implementation issue open and approved; this document updated with surface mapping decisions

---

## Special Cases

### Moriarty — Containment Boundary Tests Required

Moriarty's `ethics_gate` eligibility is conditional on containment boundary tests passing. The risk without those tests: a quarantine recommendation wired directly to `ethics_gate` could act as automatic enforcement, bypassing the appeal path that the manifest requires. Until #1152 tests are designed and passing:

- Moriarty may be considered for `EthicsEngine` and `compliance_monitor` input feeds only
- `ethics_gate` wiring remains blocked
- Any containment action must remain a **recommendation to a human reviewer**, not an automated gate

### SHADOWFAX — Bundle Location Required

SHADOWFAX has no eligible surface mapping until the standalone bundle is located and hash-verified. This is not a documentation gap — the source material itself is unlocated. The `missing_dependency` classification in the fixture and manifest reflects this. Until the bundle is found:

- No surface mapping design for SHADOWFAX may be finalized
- The `blocked_pending_bundle_location` promotion decision is schema-enforced and cannot be changed without operator approval
- When the bundle is located, Gate 1 custody resolution applies in full before any mapping discussion

---

## Non-Goals

This document does **not**:

- Authorize wiring any protocol to any runtime surface
- Define implementation code for EthicsEngine, ethics_gate, compliance_monitor, or geometric_ethics
- Replace the wiring gate in `recovered_protocol_manifest.json` — that gate remains authoritative
- Claim custody hashes are verified
- Make promotion decisions on behalf of the operator
- Describe L2-to-L1 state promotion (separate concern, out of scope)

---

## Relationship to Other Section 8 Artifacts

| Artifact | Role |
|---|---|
| `recovered_protocol_manifest.json` | Authoritative custody state and wiring gate |
| `schemas/custody_record.schema.json` | Validates custody_record fields (#1149) |
| `schemas/recovered_protocol_manifest.schema.json` | Validates full manifest (#1149) |
| `fixtures/*.fixture.json` | Canonical sanitized examples per protocol (#1150) |
| `runtime_mapping_design.md` | **This document** — surface mapping design intent (#1151) |
| `tests/moriarty_containment_tests.md` | Containment boundary test plan (#1152) |
| `tests/tribunal_appeal_tests.md` | Appeal record requirement test plan (#1153) |
| `docs/security/recovered_protocol_wiring_verification.md` | Grep verification output slot (Q-0003a) |
