# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`
**Version:** `v1.9`
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.8__2026-08-14.md`
**Created:** `2026-08-15`
**Status:** `active`
**Owner / active worker:** `Aurora / Codex`
**Repository:** `AUo959/aurora-cloudbank-symbolic`
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`
**PR:** `#1506`
**Current phase:** `Phase 9 — authoritative macrostep orchestrator and immutable ledger`
**Phase-9 admission:** Phase 8 accepted on branch head `34109c37f6f7548685559e1c13ba81c61510533b` after focused and repository-wide validation.

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control around Planetoid P17. CanonRec class/polity substitutions must change real simulation variables and consequences without battle-engine code changes. Authoritative state transitions execute before reporting; reporting never decides outcomes.

## 2. Authority stack

1. immutable recovered `GUMAS-PACKAGE-V2` evidence;
2. separately versioned restored GUMAS aggregate tactical authority;
3. pinned CanonRec snapshot + deterministic tactical-input resolver;
4. accepted deterministic per-vessel T0 constructor/calibration;
5. accepted deterministic command-team policy;
6. accepted movement/P17 geometry kernel;
7. accepted sensing/EW/targeting/effective-salvo layer;
8. accepted damage/readiness/physical-disposition layer;
9. accepted morale/resolution/termination layer;
10. **active Phase-9 authoritative step orchestrator + immutable ledger**;
11. later deterministic factual reporter.

Simulation outputs remain non-canon unless separately promoted through Git governance.

## 3. Accepted phase status

- **Phase 0:** PASS — provenance/planning anchored.
- **Phase 1:** PASS — recovered v2 combat contract restoration.
- **Phase 2:** PASS — deterministic CanonRec tactical resolution.
- **Phase 3:** PASS — deterministic 38-vessel T0 physical state.
- **Phase 4:** PASS — deterministic commander + six-lieutenant policy.
- **Phase 5:** PASS — bounded movement/P17 collision/occultation/withdrawal geometry.
- **Phase 6:** PASS — sensing/EW/targeting/effective-salvo effects.
- **Phase 7:** PASS — shield/armor/hull/readiness/physical disposition.
- **Phase 8:** PASS — morale/cohesion, ceasefire/disengagement, physical withdrawal, surrender, incapacity, annihilation, hard-limit stalemate, engagement/protection state, and deterministic termination.
- **Phase 9:** ACTIVE — live observations, ordered authoritative macrosteps, terminal short-circuiting, and immutable ledger continuity.
- **Phase 10+:** BLOCKED until Phase 9 acceptance.

## 4. Accepted receipts

The accepted implementation chain is:

1. `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.1__2026-08-13.json`
2. `simulation/receipts/GUMAS__RECEIPT__CANONREC_TACTICAL_RESOLUTION_PHASE2__v1.0__2026-08-13.json`
3. `simulation/receipts/GUMAS__RECEIPT__PHYSICAL_T0_PHASE3__v1.0__2026-08-13.json`
4. `simulation/receipts/GUMAS__RECEIPT__COMMAND_POLICY_PHASE4__v1.0__2026-08-13.json`
5. `simulation/receipts/GUMAS__RECEIPT__MOVEMENT_GEOMETRY_PHASE5__v1.0__2026-08-13.json`
6. `simulation/receipts/GUMAS__RECEIPT__SENSING_EW_TARGETING_WEAPONS_PHASE6__v1.0__2026-08-13.json`
7. `simulation/receipts/GUMAS__RECEIPT__DAMAGE_DISPOSITION_PHASE7__v1.0__2026-08-14.json`
8. `simulation/receipts/GUMAS__RECEIPT__MORALE_RESOLUTION_TERMINATION_PHASE8__v1.0__2026-08-15.json`

Phase-8 acceptance binds:

- branch head `34109c37f6f7548685559e1c13ba81c61510533b`;
- focused workflow `GUMAS Morale Resolution` run `31867481871`, `18 passed` plus pinned-CanonRec smoke;
- repository workflow `Aurora CI (Minimal)` run `31867481900`, `3626 passed` plus accepted skips/xfails/xpasses;
- CanonRec commit `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
- Phase-8 composite source `a848e798414d98b0840a5d2dc46b88f2d0a9cc4d76028d25a47beb207990277a`;
- first-step resolution receipt `5f31bcb6a7a1e2113e8a61e69b317997f101aa5215345814bd888f95b9163562`.

## 5. Phase-8 authority reconciliation remains binding

The sole normative Phase-8 implementation contract remains:

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_RESOLUTION_TERMINATION__v1.0__2026-08-14.md`

The decision remains:

`simulation/specs/GUMAS__DECISION__PHASE8_CONTRACT_RECONCILIATION__v1.0__2026-08-14.md`

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_WITHDRAWAL_TERMINATION__v1.0__2026-08-14.md` remains superseded historical design evidence. Its incompatible semantics must not enter Phase 9.

Phase 8 does not own position, velocity, shield, armor, hull, readiness, damage state, or physical disposition. Those remain Phase-7 authority. Phase 9 may orchestrate accepted phases but must not collapse their ownership boundaries.

## 6. Mandatory Phase-9 obligation

`LIVE_COMMAND_OBSERVATION_BRIDGE` is mandatory.

Synthetic/frozen command observations are permitted in bounded subsystem tests only. At each authoritative macrostep, the command observation must be derived deterministically from the previously committed battle state and verified receipts.

At minimum the bridge must derive q1000 values for:

- contact quality;
- uncertainty;
- relative advantage;
- own material damage;
- observed enemy material damage;
- logistics/resource strain;
- mobility margin;
- geometry opportunity;
- withdrawal viability;
- EW opportunity;
- carrier opportunity;
- repair need;
- enemy closing pressure;
- mission pressure;
- elapsed/time-limit pressure;
- the prior Phase-8 negotiation signal.

Every field must retain a deterministic derivation receipt. Unknown enemy state must remain uncertainty, not omniscient leakage.

## 7. Authoritative macrostep order

Phase 9 must commit exactly this order:

`previous committed state`

→ validate prior ledger head and accepted source identities
→ derive live command observation
→ Phase 4 command policy
→ Phase 5 movement/P17 geometry
→ Phase 6 sensing/EW/targeting/fire
→ Phase 7 simultaneous damage/disposition
→ Phase 8 morale/resolution/termination
→ immutable ledger entry
→ STOP when terminated, otherwise admit the next macrostep

If the prior accepted Phase-8 state is terminal, Phase 9 must fail closed before movement, sensing, firing, or damage. If the current Phase-8 result terminates the battle, the orchestrator must commit that terminal step and refuse any subsequent macrostep.

## 8. Immutable ledger requirements

Each ledger entry must bind at minimum:

- schema and orchestrator version;
- run/scenario identity without asserting canon status;
- macrostep index and elapsed milliseconds;
- previous ledger-entry SHA-256 or explicit genesis marker;
- previous committed state SHA-256;
- live-observation state and receipt SHA-256 by side;
- Phase-4 decision SHA-256 by side/fleet;
- Phase-5 state and receipt SHA-256;
- Phase-6 state and receipt SHA-256;
- Phase-7 state and receipt SHA-256;
- Phase-8 state, resolution, and receipt SHA-256;
- terminal outcome object;
- accepted source identities for every invoked phase;
- canonical JSON profile and ledger-entry SHA-256.

The ledger must be append-only by hash continuity. Reordering inputs, dictionary insertion order, or reporting regeneration must not change normalized ledger output.

## 9. Phase-9 acceptance gates

Phase 9 is not accepted until tests prove:

1. live observations are derived from committed state/receipts rather than the shared acceptance fixture;
2. same prior state + ledger head produces byte-identical observations, phase outputs, and ledger entry;
3. side/fleet mapping insertion order is inert;
4. observation values remain integer q1000 and bounded `[0,1000]`;
5. no hidden omniscient enemy material state enters the command observation;
6. prior negotiation signals are consumed exactly once in the next observation;
7. protected and invalid targets cannot be selected;
8. no reinforcement or third-party vessel can enter after T0;
9. terminal prior state prevents another macrostep;
10. terminal current step is committed exactly once and then stops;
11. every parent source/state/receipt hash is validated before use;
12. previous-ledger hash mutation fails closed;
13. phase source-identity drift fails closed;
14. no ambient mutable RNG, floating authority, prose input, or class/polity/side special casing exists;
15. reporting remains absent from the authoritative transition path;
16. a real pinned-CanonRec one-step smoke reproduces exactly without executing Run 0.

Focused CI and a clean repository-wide suite must pass on the same Phase-9 implementation head before Phase 9 can be sealed.

## 10. Validation matrix

| Validation | State |
|---|---|
| restored aggregate replay | PASS |
| CanonRec control/substitution | PASS |
| T0 replay/symmetry | PASS |
| command policy replay/causality | PASS |
| movement/geometry replay | PASS |
| sensing/EW/weapons replay | PASS |
| damage/disposition replay | PASS |
| morale/resolution/termination replay | PASS |
| integrated live command-observation replay | ACTIVE |
| immutable ledger continuity | ACTIVE |
| reporting regeneration | BLOCKED |
| Control A same-input replay | BLOCKED |
| Control B class substitution | BLOCKED |
| Control C polity substitution | BLOCKED |
| Run-0 receipt | BLOCKED |

## 11. Stop conditions

Stop rather than improvise if implementation requires conflicting canonical authority, synthetic observations in the authoritative loop, omniscient leakage into a side's observation, class/polity/side/prose special casing, LLM judgment, unpinned mutable randomness, floating-point authority, altered frozen scenario bounds, another step after termination, reporting feedback into state, or any bypass of a prior phase's source/state/receipt validation.

## 12. Exact next action

Write and commit a Phase-9 contract before implementation. The contract must define the live-observation schema and derivations, orchestrator boundary, ledger schema/hash continuity, terminal short-circuit, T0 roster freeze, fail-closed validation, and acceptance matrix above.

Then implement the contract as a separately versioned runtime with focused tests and a real one-step pinned-CanonRec smoke. The smoke may prove the integrated first step only; it must not iterate the battle or claim an outcome.

## 13. Handoff anchor

Continuation must reference this DTER `v1.9`, PR `#1506` latest head, all Phase-1 through Phase-8 receipts, and the Phase-9 `LIVE_COMMAND_OBSERVATION_BRIDGE` obligation.

**Run 0 remains blocked. No battle result is claimed.**
