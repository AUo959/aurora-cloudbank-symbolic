# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.8`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.7__2026-08-14.md`  
**Created:** `2026-08-14`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 8 — morale, resolution, and termination`  
**Phase-8 admission:** Phase-7 accepted on code head `c2cd8ef8044c0caec73f820ba28b97613a7440bd`.

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
9. **active Phase-8 morale/resolution/termination contract**;
10. later authoritative step orchestrator + immutable ledger;
11. later deterministic factual reporter.

Simulation outputs remain non-canon unless separately promoted through Git governance.

## 3. Phase-8 authority reconciliation

Two v1.0 Phase-8 design files were committed concurrently. This is resolved by:

`simulation/specs/GUMAS__DECISION__PHASE8_CONTRACT_RECONCILIATION__v1.0__2026-08-14.md`

The sole normative Phase-8 implementation contract is:

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_RESOLUTION_TERMINATION__v1.0__2026-08-14.md`

The concurrently committed:

`simulation/specs/GUMAS__SPEC__DETERMINISTIC_MORALE_WITHDRAWAL_TERMINATION__v1.0__2026-08-14.md`

is retained as historical design evidence but is superseded for implementation/validation. Runtime code must not mix incompatible thresholds or semantics from the superseded file.

## 4. Accepted phase status

- **Phase 0:** PASS — provenance/planning anchored.
- **Phase 1:** PASS — recovered v2 combat contract restoration.
- **Phase 2:** PASS — deterministic CanonRec tactical resolution.
- **Phase 3:** PASS — deterministic 38-vessel T0 physical state.
- **Phase 4:** PASS — deterministic commander + six-lieutenant policy.
- **Phase 5:** PASS — bounded movement/P17 collision/occultation/withdrawal geometry.
- **Phase 6:** PASS — sensing/EW/targeting/effective-salvo effects.
- **Phase 7:** PASS — shield/armor/hull/readiness/physical disposition.
- **Phase 8:** ACTIVE — morale, ceasefire/disengagement, physical withdrawal, surrender, incapacity, annihilation, hard-limit stalemate, termination.
- **Phase 9+:** blocked until Phase 8 acceptance.

Phase-7 evidence:

`simulation/receipts/GUMAS__RECEIPT__DAMAGE_DISPOSITION_PHASE7__v1.0__2026-08-14.json`

Accepted Phase-7 head: `c2cd8ef8044c0caec73f820ba28b97613a7440bd`.

## 5. Phase-8 governing invariants

- State machine first, story second.
- No LLM/model judgment inside authoritative transitions.
- No class-name, polity-name, role-prose, officer-prose, or narrative branches.
- Integer/fixed-point arithmetic only; ambient RNG and floating authority forbidden.
- Physical disposition remains owned by Phase 7 and is not rewritten.
- Quiet physical steps cannot create morale/cohesion decay merely from officer dissent.
- Ceasefire comes only from committed `CEASEFIRE_PROBE` decisions.
- `PRESS` rescinds that side's outstanding ceasefire offer.
- Surrender requires compatible command posture plus the complete numeric predicate; disablement alone is not surrender.
- Withdrawal requires committed `DISENGAGE` intent plus exact P17 boundary/outbound geometry.
- Unilateral withdrawal does not automatically create a victor label.
- Annihilation is reachable but is not privileged.
- No movement, sensing, firing, new damage, or reporting occurs inside Phase 8.
- If Phase 8 terminates the battle, Phase 9 must not execute another combat macrostep.

## 6. Frozen bounds / interfaces

- P17 withdrawal radius: `20,000 km` / `20,000,000,000,000 um`.
- hard duration: `21,600 s` / `21,600,000 ms`.
- no reinforcements, external mediation, or third-party intervention.
- strategic command vocabulary already includes `DISENGAGE` and `CEASEFIRE_PROBE`.
- movement state already supplies integer position/velocity for exact withdrawal tests.
- Phase-7 receipt supplies current-step hull loss/incapacity evidence.
- Phase-4 receipt supplies normalized commander attributes, specialist dissent, posture, and current observation.

## 7. Outstanding integrated-loop obligation

`LIVE_COMMAND_OBSERVATION_BRIDGE` remains mandatory in Phase 9 before Controls A/B/C or Run 0.

The authoritative orchestrator must derive each next command observation from committed state/receipts, including contact quality/uncertainty, material state, logistics strain, mobility/geometry opportunity, withdrawal viability, EW opportunity, repair need, enemy closing pressure, mission/time pressure, and Phase-8 negotiation signals.

Phase-8 subsystem tests may use frozen observation fixtures only as tests. They are not authoritative Run-0 observations.

## 8. Validation matrix

| Validation | State |
|---|---|
| restored aggregate replay | PASS |
| CanonRec control/substitution | PASS |
| T0 replay/symmetry | PASS |
| command policy replay/causality | PASS |
| movement/geometry replay | PASS |
| sensing/EW/weapons replay | PASS |
| damage/disposition replay | PASS |
| morale/resolution/termination replay | ACTIVE |
| integrated command-observation/ledger replay | BLOCKED |
| reporting regeneration | BLOCKED |
| Control A same-input replay | BLOCKED |
| Control B class substitution | BLOCKED |
| Control C polity substitution | BLOCKED |
| Run-0 receipt | BLOCKED |

## 9. Stop conditions

Stop rather than improvise if implementation requires conflicting canonical authority, class/polity/prose special casing, LLM judgment, unpinned randomness/floating behavior, altered frozen scenario bounds, a withdrawal result without disengagement + outbound boundary evidence, surrender without command posture + full predicate, a winner for a no-winner termination class, mutation of Phase-7 physical state, or use of synthetic subsystem observations as authoritative Run-0 input.

## 10. Exact next action

Implement the reconciled Phase-8 contract as a bounded versioned runtime with:

1. source-bound constants/kernel identity;
2. Phase-7 and Phase-4 receipt validation;
3. deterministic current-step fleet shock and morale/cohesion update;
4. ceasefire offer persistence/rescission + negotiation signals;
5. effect-free bilateral disengagement streak;
6. exact squared-distance + outbound-dot-product withdrawal evidence;
7. surrender predicate tied to `CEASEFIRE_PROBE`/`DISENGAGE` and numeric commander/physical state;
8. combat-incapacity, annihilation, hard-limit predicates;
9. exact termination precedence;
10. top-level engagement/protection state without rewriting physical disposition;
11. deterministic resolution-state/receipt hashes;
12. all 34 contract acceptance tests plus real pinned-CanonRec first-step smoke;
13. focused CI + full repository suite on the same implementation head.

Only after those gates pass may Phase 8 be sealed and DTER advance to Phase 9.

## 11. Handoff anchor

Continuation must reference this DTER `v1.8`, PR `#1506` latest head, Phase-1 through Phase-7 receipts, the Phase-8 reconciliation decision, the normative `MORALE_RESOLUTION_TERMINATION` v1.0 contract, and `LIVE_COMMAND_OBSERVATION_BRIDGE` obligation.

**Run 0 remains blocked. No battle result is claimed.**
