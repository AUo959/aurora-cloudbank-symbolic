# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v2.1`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v2.0__2026-08-15.md`  
**Created:** `2026-08-15`  
**Status:** `active`  
**Owner / active worker:** `Aurora / unassigned continuation`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 11 — authority-safe determinism/substitution controls contract and refusing preflight`  
**Phase-11 admission:** Phase 10 accepted on implementation head `635e97e05790c5d2efae6d66141bc3c1450e3d43` after focused, real pinned-CanonRec one-step reporting, cross-phase, source-boundary, and provisioned repository-wide validation.

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control around Planetoid P17. CanonRec class/polity substitutions must change real simulation variables and consequences without battle-engine code changes. Authoritative state transitions execute before reporting; reporting never decides outcomes.

The immediate task is not battle execution. It is to specify the final independent determinism and substitution controls, encode their evidence/identity matrix, and build a preflight that refuses execution unless the owner separately opens the execution gate.

## 2. Accepted authority stack

1. immutable recovered `GUMAS-PACKAGE-V2` evidence;
2. separately versioned restored GUMAS aggregate tactical authority;
3. pinned CanonRec snapshot + deterministic tactical-input resolver;
4. deterministic per-vessel T0 constructor/calibration;
5. deterministic command-team policy;
6. bounded movement/P17 geometry kernel;
7. sensing/EW/targeting/effective-salvo layer;
8. damage/readiness/physical-disposition layer;
9. morale/resolution/termination layer;
10. live command-observation bridge, authoritative macrostep orchestrator, and immutable ledger;
11. deterministic factual reporter, evidence index, fixed renderer, and leakage-safe evidence export;
12. **active contract-only independent determinism/substitution controls**;
13. later explicitly authorized control execution and separately authorized Run 0.

Simulation outputs remain non-canon unless separately promoted through Git governance.

## 3. Phase status

- **Phase 0:** PASS — provenance/planning anchored.
- **Phase 1:** PASS — recovered v2 combat contract restoration.
- **Phase 2:** PASS — deterministic CanonRec tactical resolution.
- **Phase 3:** PASS — deterministic 38-vessel T0 physical state.
- **Phase 4:** PASS — deterministic commander + six-lieutenant policy.
- **Phase 5:** PASS — bounded movement/P17 collision/occultation/withdrawal geometry.
- **Phase 6:** PASS — sensing/EW/targeting/effective-salvo effects.
- **Phase 7:** PASS — shield/armor/hull/readiness/physical disposition.
- **Phase 8:** PASS — morale/cohesion, ceasefire/disengagement, withdrawal, surrender, incapacity, annihilation, stalemate, protection, and termination.
- **Phase 9:** PASS — side-local live observations, ordered authoritative macrosteps, frozen roster, terminal short-circuiting, and immutable hash-linked ledger.
- **Phase 10:** PASS — validated factual projection, statement-level evidence index, fixed rendering, public redaction profile, exporter receipt, and leakage-safe observation/order pairs.
- **Phase 11 contract/preflight:** ACTIVE — specifications and fail-closed preflight only.
- **Control A/B/C execution:** BLOCKED pending the committed Phase-11 contract and explicit owner execution authority.
- **Run 0:** BLOCKED pending all remaining gates and a separate explicit owner execution decision.

## 4. Accepted receipt chain

1. `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.1__2026-08-13.json`
2. `simulation/receipts/GUMAS__RECEIPT__CANONREC_TACTICAL_RESOLUTION_PHASE2__v1.0__2026-08-13.json`
3. `simulation/receipts/GUMAS__RECEIPT__PHYSICAL_T0_PHASE3__v1.0__2026-08-13.json`
4. `simulation/receipts/GUMAS__RECEIPT__COMMAND_POLICY_PHASE4__v1.0__2026-08-13.json`
5. `simulation/receipts/GUMAS__RECEIPT__MOVEMENT_GEOMETRY_PHASE5__v1.0__2026-08-13.json`
6. `simulation/receipts/GUMAS__RECEIPT__SENSING_EW_TARGETING_WEAPONS_PHASE6__v1.0__2026-08-13.json`
7. `simulation/receipts/GUMAS__RECEIPT__DAMAGE_DISPOSITION_PHASE7__v1.0__2026-08-14.json`
8. `simulation/receipts/GUMAS__RECEIPT__MORALE_RESOLUTION_TERMINATION_PHASE8__v1.0__2026-08-15.json`
9. `simulation/receipts/GUMAS__RECEIPT__LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_PHASE9__v1.0__2026-08-15.json`
10. `simulation/receipts/GUMAS__RECEIPT__FACTUAL_REPORTER_EVIDENCE_EXPORT_PHASE10__v1.0__2026-08-15.json`

## 5. Phase-10 acceptance boundary

Normative contract:

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_FACTUAL_REPORTER_EVIDENCE_EXPORT__v1.0__2026-08-15.md`

Accepted implementation and witness identity:

- branch head: `635e97e05790c5d2efae6d66141bc3c1450e3d43`;
- Phase-10 source bundle: `ca6c4c61e91c9ab87578aafb1308910539fd56e3e8c4cee38b0502022af3942a`;
- focused workflow: `GUMAS Factual Reporter` run `31870997151`, `10 passed`, real pinned-CanonRec one-step reporting smoke success;
- repository workflow: `Aurora CI (Minimal)` run `31870997221`, `3714 passed`, accepted skips/xfails/xpasses;
- required status context: `CI Check`, passed;
- external advisory integrations: Codacy app and SonarCloud failed but are not branch-protection requirements;
- input ledger head: `e5fbf15363efe8786171229a8ee7bca99972ac24db44c013158f0835c0d9122a`;
- truth normalized report: `d0a06b970b1f2e72ee349d0a45cee52024dfacd8da19b9a9a3d5d65abe68820f`;
- truth rendered report: `b414221d5bd4c1d7f4ee1d9527e687f96415eeeca29651ba3eeed75679f7b4e7`;
- public normalized report: `a2de14d90169c7571671b521ba18abbf80059c68401e5b3fbe6ec49657a0bbbc`;
- public rendered report: `39f48ae18a7b8973e01317b8639229110d25e8d1da6c19b6536ef1187e5ea23c`;
- termination mode: `ongoing`;
- transition reporter invoked: `false`;
- Run 0 executed: `false`.

The smoke produced exactly one accepted Phase-9 witness, then replayed the pure reporter over copies of that artifact packet. The authoritative reporter imported or called no transition function. The witness is integration evidence, not a battle result and not authority to continue the exact scenario.

## 6. Binding Phase-10 boundary

The reporter is a pure projection over a caller-anchored, validated, complete Phase-9 genesis-to-head artifact chain. It:

- recomputes all artifact identities and cross-links before projection;
- keeps the raw Phase-6 receipt distinct from the accepted semantic-normalized identity consumed by Phase 7;
- exposes only facts deliberately present in accepted receipts, resolution state, run context, and ledger;
- maps every rendered statement to evidence references;
- copies terminal outcome fields without choosing or reinterpreting a winner;
- derives the public profile by deterministic whitelist projection from simulation truth;
- emits byte-identical normalized, evidence, rendered, and exporter-receipt output for the same input;
- cannot execute a macrostep, mutate simulation state, access hidden opponent state, or feed a report back into the transition path.

No LLM, narrative prose, ambient randomness, floating-point authority, wall clock, network, or canon promotion participates in reporting.

## 7. Native-model value without authority leakage

Phase 10 creates an evidence-grounded bridge to the proposed Aurora-native state model:

```text
validated side-local command_observation
  -> accepted deterministic command_order
  -> authoritative state-transition receipts
  -> normalized factual consequences
  -> evidence references and fixed factual rendering
```

The `command_observation -> command_order` pair is a leakage-safe supervised example because the observation is exactly the information available to that side at decision time. The subsequent receipt chain can support transition prediction, consequence modeling, critic/evaluator training, and provenance-aware factual rendering.

This is corpus infrastructure, not model authority. Dataset admission, split policy, training, evaluation, deployment, command substitution, and any state feedback each require separate contracts. Rendered prose is never a training label for physical truth unless its underlying evidence references are retained and validated.

## 8. Phase-11 contract-only boundary

Phase 11 may now define, but not execute, three independent controls:

- **Control A — same-input exact replay:** prove byte-identical ledger, termination, report, and exporter identities from the exact admitted setup.
- **Control B — class substitution:** change only the versioned CanonRec class input, prove the permitted resolved physical deltas, and require the unchanged generic engine to propagate those deltas.
- **Control C — polity substitution:** change only the versioned CanonRec polity input, prove the permitted resolved doctrine/command/resource deltas, and require the unchanged generic engine to propagate those deltas.

The contract must separate four identities for every control:

1. source and CanonRec input identity;
2. resolved tactical-input identity;
3. T0/run/ledger identity;
4. reporter/export identity.

It must define allowed-delta and forbidden-delta matrices, engine-source equality requirements, termination comparison semantics, evidence packaging, and a refusal receipt for missing authority.

## 9. Why real controls remain blocked

Control A is a complete replay of the exact Run-0 setup and may reveal the full outcome. Controls B and C are also complete battle executions and may reveal comparative outcomes. Labeling them “validation” does not remove their execution or result authority implications.

Therefore:

- synthetic and structurally reduced fixtures may test the future harness;
- static contract/schema validation may proceed;
- a preflight may prove inputs and then refuse execution;
- no exact-scenario Control A/B/C transition loop may start without explicit owner execution authority;
- authority for controls does not automatically authorize Run 0;
- authority for Run 0 does not promote its result into canon.

## 10. Phase-11 acceptance gates

The contract/preflight lane is not accepted until tests prove:

1. control identity, source pins, frozen roster, and scenario bounds are explicit;
2. allowed and forbidden input/state deltas are machine-checkable;
3. transition and reporter source bundles must remain identical across controls;
4. same-input replay comparison is byte-level and covers every ledger/export artifact;
5. class/polity substitutions enter only through the pinned CanonRec resolver;
6. generic engine code has no class, polity, side-name, or prose special case;
7. preflight refuses absent, expired, mismatched, or wrong-scope authority;
8. control execution authority and Run-0 authority are separate capabilities;
9. outputs remain non-canon and publication-gated;
10. no refusal path executes a macrostep or discloses an outcome.

Actual Control A/B/C acceptance remains undefined until the owner authorizes execution and the committed contract specifies the resulting execution receipt.

## 11. Validation matrix

| Validation | State |
|---|---|
| restored aggregate replay | PASS |
| CanonRec input resolution | PASS |
| T0 replay/symmetry | PASS |
| command policy replay/causality | PASS |
| movement/geometry replay | PASS |
| sensing/EW/weapons replay | PASS |
| damage/disposition replay | PASS |
| morale/resolution/termination replay | PASS |
| live observation and immutable ledger | PASS |
| factual reporting, evidence, regeneration | PASS |
| leakage-safe observation/order export | PASS |
| Phase-11 control contract/schema | ACTIVE |
| authority-refusing preflight | ACTIVE |
| Control A same-input full replay | BLOCKED |
| Control B class substitution | BLOCKED |
| Control C polity substitution | BLOCKED |
| Run-0 receipt | BLOCKED |

## 12. Stop conditions

Stop rather than improvise if Phase 11 would execute the exact scenario, reveal an unapproved result, conflate control and Run-0 authority, permit a substitution outside CanonRec, change engine source between controls, admit hidden state, use narrative comparison as evidence, weaken identity checks, alter frozen scenario bounds, or promote output into canon.

## 13. Exact next action

Write and commit the Phase-11 determinism/substitution-controls contract and machine-checkable schemas. Implement only a fail-closed preflight and synthetic/reduced-fixture contract tests. The preflight must emit a refusal receipt when execution authority is absent.

Do not execute Control A, Control B, Control C, another exact-scenario macrostep, or Run 0. Return to the owner with the completed contract/preflight evidence and request a separate execution decision.

## 14. Handoff anchor

Continuation must reference this DTER `v2.1`, PR `#1506` latest head, all Phase-1 through Phase-10 receipts, and the Phase-11 contract-only boundary.

**Phases 0–10 are accepted. Real controls and Run 0 remain blocked. No battle result is claimed.**
