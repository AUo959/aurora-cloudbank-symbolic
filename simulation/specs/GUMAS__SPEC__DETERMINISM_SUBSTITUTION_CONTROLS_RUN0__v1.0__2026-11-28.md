# GUMAS Phase 11: Determinism and Substitution Controls, and Run 0

**Contract ID:** `GUMAS_DETERMINISM_SUBSTITUTION_CONTROLS_RUN0_v1_0`
**Version:** `1.0.0`
**Date:** `2026-11-28`
**Package:** `simulation/runtime/gumas_battle_controls/`
**Supersedes the Phase-11 "contract-only" boundary in:** DTER v2.1
**Historical canon status of every output:** `non_canon_simulation_instance`

## 1. Purpose

Phase 11 does three things on the accepted Phase 0–10 runtime:

1. **Control A (same-input replay).** Prove that the exact admitted Run-0 setup produces byte-identical ledgers, terminal outcomes, reports and export receipts.
2. **Control B (class substitution).** Change only the versioned CanonRec class input. Prove that the change resolves to the declared physical deltas, and that the unchanged generic engine carries them through.
3. **Control C (polity substitution).** Change only the versioned CanonRec authority input. Prove that the change resolves to the declared doctrine and command deltas, and that the unchanged generic engine carries them through.

Run 0 is the first execution of the control setup. Control A is a second, independent execution of the same setup.

## 2. Corrections to accepted phases that Phase 11 depends on

### 2.1 Phase 9: continuation past macrostep 1 (defect fix)

Phase 7 consumes the semantic-normalized Phase-6 receipt (`normalize_phase6_receipt`). The committed state's `last_phase6_receipt_sha256` and the Phase-7 receipt's `phase6_receipt_sha256` therefore carry the **normalized** identity. Phase-9 `_validate_prior_checkpoint` compared that value against the **raw** receipt hash. The two match only when every unordered Phase-6 list is already in canonical order, so every real run failed at macrostep 2 with `current state does not retain prior Phase-6 receipt`. The one-step witness never reached the check, and the synthetic tests passed only because their lists were empty.

The fix recomputes the normalized identity from the validated raw receipt and requires that both the prior Phase-7 receipt and the current state bind it. The ledger still binds the raw receipt hash. Regression tests: `test_second_macrostep_accepts_semantic_normalized_phase6_identity` and `test_prior_phase7_binding_to_normalized_phase6_is_checked`.

### 2.2 Phase 4: authority-doctrine bridge (gap fix)

The pinned resolver derives a doctrine vector for every CanonRec authority (`resolve_authority(...)["doctrine_vector"]`), but no Phase 3 through 9 code consumed it. A polity substitution therefore could not reach any simulation variable, and Control C could never pass honestly.

Bridge:

- `initialize_run_context(..., authority_doctrine_by_side=...)` binds each side's `authority_id`, `authority_resolution_sha256`, `manifest_sha256`, and the integer Q1000 `doctrine_q1000` into the run identity. The binding fails closed if the side set differs from the baseline, if the T0 roster organization differs from `authority_id`, or if any doctrine value is outside the integers 0 to 1000.
- `decide(..., doctrine=...)` shifts commander attributes by `sign * (doctrine - 500) * weight / 1000`, rounded half-even and clamped to [0, 1000]. The weights are the fixed table `DOCTRINE_COMMANDER_BIAS` in `gumas_command_policy/coefficients.py`. The conditioned attributes replace `command_team_numeric.commander.attributes_q1000`, so Phase 8 surrender resolve sees the same commander as Phase 4. The receipt records the doctrine, its hash, the deltas, and the unconditioned attributes under `authority_doctrine`.
- With no doctrine, Phase 4 behaves exactly as v1.0. A neutral doctrine (all 500) yields zero deltas and identical orders.
- The Phase-10 reporter accepts the optional run-context field and fails closed if a decision's doctrine differs from the bound doctrine, or if a decision carries doctrine the run context never bound.

Phase 11 always binds doctrine, so Run 0 and every control run with it.

### 2.3 Phase 5 and Phase 9: range-seeking `POSITION_FOR_ADVANTAGE` (gap fix)

The first complete Run 0 and controls passed every comparison, but every run was a non-engagement: zero weapon attempts in 2,160 macrosteps. The fleets start about 12,100 km apart, outside every effective weapon range (at most 5,636 km). The only navigation intent the policy chose, `POSITION_FOR_ADVANTAGE`, burned along the planetoid tangent and had no term that closes range. Both fleets accelerated apart and lost sensor contact.

Fix: Phase 9 now builds a motion reference for `POSITION_FOR_ADVANTAGE` from the side-local contact centroid, the mean contacted-target velocity, and a standoff of 800/1000 of the fleet's shortest active effective weapon range. Phase 5 steers to that standoff and matches the track velocity (movement spec, amendment 2026-11-28). Without a contact, the v1.0 tangent rule still applies. No variant, side, class or authority is named. The evidence from the non-engaging runs was replaced by a re-run on the fixed engine.

## 3. Identity layers

Every run receipt keeps these four layers separate:

| Layer | Fields |
|---|---|
| Source and CanonRec input | `baseline_sha256`, `calibration_sha256`, `source_set_sha256`, `canonrec_commit` |
| Resolved tactical input | `resolved_manifest_sha256`, `authority_resolution_sha256`, `authority_doctrine_by_side` |
| T0, run and ledger | `t0_sha256`, `initial_state_sha256`, `t0_roster_sha256`, `run_identity_sha256`, `ledger_genesis_sha256`, `ledger_head_sha256`, `ledger_chain_sha256`, `final_state_sha256` |
| Reporter and export | per profile: `normalized_report_sha256`, `rendered_report_sha256`, `evidence_index_sha256`, `export_receipt_sha256` |

`engine_source_identity` records the Phase 4–9 accepted source identities, the Phase-10 reporter identity, the Phase-11 package identity, and the SHA-256 of the resolver and T0 constructor sources.

## 4. Variants and the allowed-delta matrix

Each variant applies one declared edit to deep copies of the three frozen control documents. Then `check_input_deltas` diffs every JSON leaf against the control files. Any differing path outside the variant's allowed prefixes fails closed before a macrostep runs.

| Variant | Declared edit | Allowed baseline paths | Allowed calibration paths | Allowed source-set paths |
|---|---|---|---|---|
| `control` | none | none | none | none |
| `class_substitution` | per side, one `CLASS-PEREGRINE-01` becomes one `CLASS-BASTION-01` (`cls_bastion`). This is the source set's own `substitution_witness`, so 19 vessels per side and mirror symmetry still hold | `/fleet_template/composition` | `/identity_mapping/baseline_class_to_canonrec/CLASS-BASTION-01`, `/authority_boundary/control_manifest_sha256` | none |
| `polity_substitution` | operating authority `org_galactic_union` becomes `org_union_naval_forces`, whose source is appended to the source set. It is Union-bound, so every control class still binds and hardware is unchanged | none | `/identity_mapping/organization_id`, `/authority_boundary/control_manifest_sha256` | `/sources` |

`control_manifest_sha256` is re-bound to the manifest that the unchanged pinned resolver produces for the variant. The control variant must reproduce the accepted pin `cd8a22b8…` and the accepted T0 `47d31a29…`.

`polity_prime_construct` (the source set's second authority witness) is **not** used. CanonRec binds every control class to `galactic_union`, so the pinned resolver correctly refuses to let the Prime Construct field them. Substituting it would require a hardware change too, which would no longer be a polity-only control.

Forbidden in every variant: any change to seed, scenario bounds, side geometry, command teams, calibration equations, the CanonRec commit, the engine source, or any field not listed above. No engine module may name a variant, a substituted class or authority, or a side. `test_engine_sources_do_not_special_case_variants` enforces this.

## 5. Execution authority

Execution requires a committed authority record (`aurora://simulation/gumas/phase11_execution_authority/v1.0`) with exactly these fields: `schema`, `authority_id`, `phase11_contract_id`, `granted_by`, `granted_on`, `expires_on`, `evidence`, `capabilities`, `scope`, `canon_promotion_authorized`, `publication_authorized`, and `authority_sha256`. The record is sealed by `authority_sha256`.

- Capabilities are separate: `gumas_battle_controls_execution` and `gumas_run0_execution`. Granting one does not grant the other.
- Scope must equal repository `AUo959/aurora-cloudbank-symbolic`, baseline `SIM-L2-FR-P17-EQUAL-001`, version `1.2`.
- `canon_promotion_authorized` must be `false`. Authority to run never promotes output.
- `evidence` must cite the owner's decision.
- The preflight compares `granted_on <= as_of <= expires_on`, where `as_of` is supplied by the caller. It reads no wall clock.

A refusal returns `aurora://simulation/gumas/phase11_refusal_receipt/v1.0` with `macrosteps_executed = 0`, `outcome_disclosed = false`, and `run0_executed = false`. `controls_cli.py preflight` exits 3 on refusal. CI asserts that refusal when no authority is supplied.

## 6. Run semantics

`run_to_termination` calls the accepted `execute_macrostep` from T0 until Phase 8 returns `terminated = true`. Phase 8 remains the sole termination authority. The 6-hour hard limit (2,160 macrosteps) is Phase 8's. The harness's `MAX_MACROSTEPS = 2,200` is only a fail-closed guard. The complete genesis-to-head chain then goes to the accepted Phase-10 reporter under both `simulation_truth_v1` and `public_summary_v1`.

## 7. Comparison semantics

- **Control A passes** iff the Run-0 and replay receipts are identical except for `authority`, `run0_executed` and their own seal, and the canonical-byte digests of every ledger entry, the full packet chain, and both complete report exports are identical.
- **Control B passes** iff the engine source identity and CanonRec commit are identical, only `cls_peregrine` and `cls_bastion` counts change, the authority is identical, the aggregate capability vector changes, T0 changes, the first ledger entry changes, and the ledger head changes.
- **Control C passes** iff the engine source identity and CanonRec commit are identical, roster counts and every class capability vector are identical, the authority and bound doctrine change, the first-step conditioned commander attributes change, T0 changes (organization id), the first ledger entry changes, and the ledger head changes.
- Terminal outcomes are **reported side by side, never required to differ**. A substitution that leaves the outcome unchanged is a valid result. The harness never picks a winner. It copies Phase-8 `terminal_outcome` verbatim.

## 8. Evidence and regeneration

`execute_controls` runs four independent processes (Run 0, replay, B, C) and seals `aurora://simulation/gumas/phase11_controls_evidence/v1.0`. The evidence holds the Run-0 receipt, three control receipts, the A/B/C comparison blocks, `all_controls_passed`, and `evidence_sha256`. It raises if any control fails.

`controls_cli.py execute --verify <committed evidence>` regenerates everything from the pinned inputs and fails unless the result is byte-identical to the committed file. The `GUMAS Battle Controls` workflow runs that regeneration whenever both the authority record and the evidence file are committed.

## 9. Boundaries that remain

- Outputs are non-canon. Promotion needs separate Git governance.
- `publication_authorized = false`. Rendered prose is not published outside the repository.
- No LLM, ambient RNG, floating-point authority, wall clock, or network participates in transitions, reporting, or comparison.
- Known Phase-2 derivation limit, recorded and not changed here: `cls_aegis` (role text "Frontline combat, planetary defense, fleet support") resolves to the `logistics_support` role profile because "support" matches before "combatant". The derivation is deterministic and accepted, but it understates Aegis firepower. Fixing it is a versioned Phase-2 change that would invalidate every downstream identity, so it is a follow-up.
