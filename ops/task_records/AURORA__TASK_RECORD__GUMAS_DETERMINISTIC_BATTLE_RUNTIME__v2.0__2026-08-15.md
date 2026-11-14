# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`
**Version:** `v2.0`
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.9__2026-08-15.md`
**Created:** `2026-08-15`
**Status:** `active`
**Owner / active worker:** `Aurora / Codex`
**Repository:** `AUo959/aurora-cloudbank-symbolic`
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`
**PR:** `#1506`
**Current phase:** `Phase 10 — deterministic factual reporter and evidence export contract`
**Phase-10 admission:** Phase 9 accepted on implementation head `689eb440114c3be9463a2e1228117d0e0af0aacb` after focused, one-step pinned-CanonRec, cross-phase, security/review, and repository-wide validation.

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control around Planetoid P17. CanonRec class/polity substitutions must change real simulation variables and consequences without battle-engine code changes. Authoritative state transitions execute before reporting; reporting never decides outcomes.

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
11. **active deterministic factual reporter and evidence export**;
12. later independent control/substitution acceptance and explicitly authorized execution.

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
- **Phase 10:** ACTIVE — deterministic factual reporting and evidence export from validated accepted artifacts only.
- **Phase 11 / Control A/B/C:** BLOCKED until Phase 10 acceptance.
- **Run 0:** BLOCKED pending all remaining gates and explicit owner execution authority.

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

## 5. Phase-9 acceptance boundary

Normative contract:

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER__v1.0__2026-08-15.md`

Accepted implementation identity:

- branch head: `689eb440114c3be9463a2e1228117d0e0af0aacb`;
- Phase-9 source bundle: `836eb5759b06f86fbe624158d799d2c5efc4cdb7c110cde8a76e7ea880292431`;
- focused workflow: `GUMAS Battle Orchestrator` run `31869097342`, `10 passed`, pinned-CanonRec one-step smoke success;
- repository workflow: `Aurora CI (Minimal)` run `31869097319`, `3704 passed`, accepted skips/xfails/xpasses;
- T0 roster: `11d22e6de49e18768a94b4a0f43170b70ae6b0fd901dafa6d610f7f1e180ff85`;
- one-step ledger entry: `e5fbf15363efe8786171229a8ee7bca99972ac24db44c013158f0835c0d9122a`;
- termination mode: `ongoing`;
- macrosteps executed: `1`;
- reporter invoked: `false`;
- Run 0 executed: `false`.

The witness proves integration and replay only. It is not a battle result and gives no authority to execute a second real macrostep.

## 6. Binding Phase-9 invariants

The `LIVE_COMMAND_OBSERVATION_BRIDGE` is now authoritative:

- own material/readiness/resource/position/capability state may be exact;
- enemy estimates may use only that side's prior Phase-6 contacts and attributable effects;
- unseen enemy hull, readiness, resources, morale, cohesion, class, polity, and command state remain inaccessible;
- cumulative battle-damage estimate is observation memory, not opponent-state access;
- closing pressure uses observed contact-distance history, not hidden velocity;
- prior Phase-8 negotiation signal is consumed through immediate ledger continuity;
- all 16 Phase-4 observation fields remain bounded integer q1000.

The authoritative macrostep remains:

`previous committed state`

→ validate run/roster/source/state/receipt/ledger identities
→ reject terminal prior checkpoint
→ derive side-local live observations
→ Phase 4 command policy
→ Phase 5 movement/P17 geometry
→ Phase 6 sensing/EW/targeting/fire
→ Phase 7 simultaneous damage/disposition
→ Phase 8 morale/resolution/termination
→ immutable Phase-9 ledger entry
→ stop if terminal, otherwise expose a checkpoint without executing it

No reporter or LLM exists in that path.

## 7. Mandatory Phase-10 reporting boundary

Phase 10 must be a pure projection over validated immutable artifacts. It may consume:

- Phase-9 run context and ledger entries;
- committed checkpoint state/receipts after their hashes and source identities validate;
- Phase-8 terminal outcome verbatim;
- sorted factual per-step deltas already committed by the accepted phase owners.

It may not:

- execute or request another macrostep;
- infer hidden enemy information;
- select tactics, targets, damage, morale, surrender, withdrawal, winner, or canon status;
- reinterpret Phase-8 outcome fields;
- feed any rendered value back into simulation state;
- use LLM prose as factual authority;
- read unvalidated or floating artifacts;
- claim Run 0.

## 8. Required Phase-10 outputs

The contract must define at least:

1. normalized machine-readable factual event stream;
2. per-macrostep evidence index linking every statement to a state/receipt/ledger hash;
3. deterministic human-readable summary generated from a fixed template/vocabulary;
4. terminal summary that copies Phase-8 outcome fields without winner reinterpretation;
5. redaction/publication profile distinct from simulation truth;
6. exporter receipt binding input ledger head, reporter source identity, normalized output hash, and rendered output hash;
7. regeneration rule proving the same ledger produces byte-identical output;
8. explicit `historical_canon_status = non_canon_simulation_instance` and `run0_executed = false` for the one-step acceptance witness.

## 9. Phase-10 acceptance gates

Phase 10 is not accepted until tests prove:

1. every reported fact maps to an accepted artifact field and hash;
2. reporter input mutation fails closed;
3. ledger reordering, gap, fork, or previous-hash mutation fails closed;
4. mapping insertion order is inert;
5. same ledger/checkpoint regenerates byte-identical normalized and rendered outputs;
6. hidden state absent from the accepted artifacts cannot appear in output;
7. changing a factual committed field changes only the corresponding factual projection;
8. terminal outcome is copied, not re-decided;
9. reporting has no imports/calls into transition execution;
10. no ambient RNG, floating authority, wall clock, network, LLM, or prose interpretation affects output;
11. real pinned-CanonRec one-step reporting smoke consumes the accepted Phase-9 witness only and does not execute a new step;
12. focused and repository-wide CI pass on the same implementation head.

## 10. Validation matrix

| Validation | State |
|---|---|
| restored aggregate replay | PASS |
| CanonRec control/substitution input resolution | PASS |
| T0 replay/symmetry | PASS |
| command policy replay/causality | PASS |
| movement/geometry replay | PASS |
| sensing/EW/weapons replay | PASS |
| damage/disposition replay | PASS |
| morale/resolution/termination replay | PASS |
| live command-observation replay and information boundary | PASS |
| authoritative macrostep and immutable ledger continuity | PASS |
| deterministic factual reporting/regeneration | ACTIVE |
| Control A same-input full-run replay | BLOCKED |
| Control B class substitution | BLOCKED |
| Control C polity substitution | BLOCKED |
| Run-0 receipt | BLOCKED |

## 11. Stop conditions

Stop rather than improvise if Phase 10 requires reporter feedback into state, hidden enemy access, narrative winner selection, LLM judgment, unvalidated input, mutable randomness, floating-point authority, wall-clock/network dependence, class/polity/side/prose special casing, altered frozen scenario bounds, another macrostep, or Run-0 execution.

## 12. Exact next action

Write and commit the Phase-10 deterministic factual reporter/evidence-export contract before implementation. The contract must specify schemas, fixed factual vocabulary/templates, artifact-to-statement provenance, ledger-chain validation, deterministic rendering, publication/redaction separation, and the acceptance matrix above.

Then implement the reporter as a pure separately versioned package with focused tests and a real pinned-CanonRec **one-step artifact reporting** smoke that consumes an already produced Phase-9 witness and never calls `execute_macrostep` itself.

## 13. Handoff anchor

Continuation must reference this DTER `v2.0`, PR `#1506` latest head, all Phase-1 through Phase-9 receipts, and the Phase-10 pure-reporting boundary.

**Run 0 remains blocked. No battle result is claimed.**
