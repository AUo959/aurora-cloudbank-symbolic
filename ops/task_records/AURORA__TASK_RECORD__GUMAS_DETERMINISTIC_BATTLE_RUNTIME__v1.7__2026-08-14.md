# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.7`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.6__2026-08-13.md`  
**Created:** `2026-08-14`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 8 — morale, withdrawal, surrender, ceasefire, disengagement, incapacity, and termination`  
**Phase-8 admission reference:** Phase-7 acceptance seal following validated code head `c2cd8ef8044c0caec73f820ba28b97613a7440bd`

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control around Planetoid P17. CanonRec class/polity substitutions must alter real simulation variables and consequences without battle-engine code changes. Authoritative transitions execute before reporting; reporting never decides outcomes.

## 2. Authority stack

1. immutable recovered `GUMAS-PACKAGE-V2` evidence;
2. separately versioned restored GUMAS aggregate tactical authority;
3. pinned CanonRec snapshot plus deterministic tactical-input resolver;
4. deterministic per-vessel T0 constructor and physical calibration;
5. deterministic command-team policy producing orders only;
6. accepted bounded per-vessel movement/geometry kernel subordinate to GUMAS;
7. accepted sensing/EW/targeting/effective-salvo layer;
8. accepted shield/armor/hull/readiness/physical-disposition layer;
9. Phase-8 morale/withdrawal/surrender/ceasefire/disengagement/termination layer;
10. authoritative step orchestrator plus immutable event/state ledger;
11. factual read-only reporter.

Historical recovered source bytes remain immutable. Scenario-local values and simulation outcomes remain non-canon unless separately promoted through Git governance.

## 3. Accepted identities

- recovered GUMAS tree SHA-256: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`;
- restored runtime: `2.0.1-restored.2`;
- restored replay SHA-256: `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`;
- pinned CanonRec commit: `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
- resolved control manifest SHA-256: `cd8a22b8d8721106ab94f5f881685cbd8f58c95beeb8f2d86853e09fd61bdfdc`;
- physical calibration SHA-256: `94a6cd7ec934d3fd4a382af051e1a6bb5994ecb5d2bf6b906102367c28592cf6`;
- accepted T0 SHA-256: `47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec`;
- command policy bundle SHA-256: `8c9ba9d413945404e7648c8f427b660576b0e85887c7639a0944f56b38585b3f`;
- movement source bundle SHA-256: `565ef76f94cef320a4e4e8a0cbf75a301270eeef4326975b4cf41681d46bab57`;
- accepted one-step movement-state SHA-256: `c947b95b3e6a38c6676c4a197c5351f017734aebd56ecdf48ab0324311dd1c74`;
- Phase-6 source bundle SHA-256: `05e65b2ee5744809f22eeb1dd6cf5cbf637690d1fa16c177c3bbeedca74427e7`;
- accepted Phase-6 next-state SHA-256: `393ffd735e01da4fe4ca2e35547ee457d626005f5e27add5d6f4e97ea7ca7479`;
- accepted raw Phase-6 receipt SHA-256: `3b84a912d1826846599dcd2c01ec763f2430af3da8931a03c01940f26faef775`;
- Phase-7 contract ID/version: `GUMAS_DAMAGE_DISPOSITION_v1_0` / `1.0.0`;
- Phase-7 damage-core bundle SHA-256: `ff5d94f98b0742b3d81a3230827b640777870dea8c3a6c1011d9e0e1c81dcad1`;
- Phase-7 semantic-normalizer bundle SHA-256: `ad9f5ad8217813db66796cd2960d0788e140bfae1fe7ad2ce263695be2ccfefe`;
- Phase-7 composite source SHA-256: `bbe6d1663ddf32b651db957434f6b1c6e86d56456c9bd93cffd8b8ecf972ed5a`;
- accepted Phase-7-bound normalized Phase-6 receipt SHA-256: `cb1c2337d22aa17883fae8a203286337a95313114c4f645f974111e68bf10259`;
- accepted Phase-7 next-state SHA-256: `701ee047f86a8f3f29c7d57f5820214daf3fd60891160235ce533db9b63ea473`;
- accepted Phase-7 damage-ledger SHA-256: `d2842b8e0f519b9c4ea759fb7ca4ac255ceb3865fd3924be9ca8f4928d2a38f4`;
- accepted Phase-7 receipt SHA-256: `ab0ecdbdcbbb6edc78378e312a60d77b98b1b755a174d0b7466f630713bb0c2b`.

## 4. Phase status

### Phase 0 — provenance and plan anchoring
**Status:** PASS / complete.

### Phase 1 — historical tactical restoration
**Status:** PASS / accepted.  
Evidence: `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.1__2026-08-13.json`.

### Phase 2 — deterministic CanonRec tactical-input resolution
**Status:** PASS / accepted.  
Evidence: `simulation/receipts/GUMAS__RECEIPT__CANONREC_TACTICAL_RESOLUTION_PHASE2__v1.0__2026-08-13.json`.

### Phase 3 — deterministic per-vessel T0 physical instantiation
**Status:** PASS / accepted.  
Evidence: `simulation/receipts/GUMAS__RECEIPT__PHYSICAL_T0_PHASE3__v1.0__2026-08-13.json`.

### Phase 4 — deterministic command-team policy
**Status:** PASS / accepted.  
Evidence: `simulation/receipts/GUMAS__RECEIPT__COMMAND_POLICY_PHASE4__v1.0__2026-08-13.json`.

### Phase 5 — bounded movement and geometry
**Status:** PASS / accepted.  
Evidence: `simulation/receipts/GUMAS__RECEIPT__MOVEMENT_GEOMETRY_PHASE5__v1.0__2026-08-13.json`.

### Phase 6 — sensing, EW, targeting, and weapons
**Status:** PASS / accepted.  
Evidence: `simulation/receipts/GUMAS__RECEIPT__SENSING_EW_TARGETING_WEAPONS_PHASE6__v1.0__2026-08-13.json`.

### Phase 7 — shield, armor, hull, system, and disposition transitions
**Status:** PASS / accepted.

Accepted implementation head: `c2cd8ef8044c0caec73f820ba28b97613a7440bd`.

Verified behavior:
- Phase-6 raw provenance is validated before semantic normalization;
- semantically unordered Phase-6 lists are canonicalized before Phase-7 state binding;
- simultaneous effects are insertion-order independent;
- shield absorbs before armor and armor before hull;
- armor uses fixed integer 850/1000 absorption efficiency and deterministic integer ceiling;
- hull is clamped non-negative and overkill is recorded;
- only new hull penetration can shock internal readiness;
- higher damage-control readiness cannot increase readiness degradation;
- greater hull loss cannot reduce readiness degradation;
- physical `disabled` remains distinct from `destroyed`;
- morale and cohesion are untouched;
- duplicate effects and effects against already-destroyed targets fail closed;
- actual Phase-6-produced effect descriptors cross the Phase-7 boundary successfully;
- accepted first-step Run-0 witness has zero Phase-6 effects and therefore an exact no-damage Phase-7 transition.

Evidence:
- `simulation/receipts/GUMAS__RECEIPT__DAMAGE_DISPOSITION_PHASE7__v1.0__2026-08-14.json`;
- focused `GUMAS Damage Disposition` run `31847120622`, job `94915720078`: 10 focused tests + pinned-CanonRec smoke success;
- `Aurora CI (Minimal)` run `31847120609`, job `94915767503`: full repository suite success.

### Phase 8 — morale, withdrawal, surrender, ceasefire, disengagement, incapacity, and termination
**Status:** admitted / active.

Phase 8 consumes committed Phase-7 state/receipts, verified command decisions, committed movement/boundary state, and frozen scenario time/objective bounds. It may update morale/cohesion from newly committed consequences, make existing command intents legally consequential, and determine whether a valid termination class has been reached.

Phase 8 must not move vessels, create contacts, fire weapons, apply new physical damage, synthesize future command observations, or narrate outcomes.

## 5. Phase-8 boundary

Frozen scenario facts already available to Phase 8:
- withdrawal boundary: `20,000 km` from P17;
- hard run duration: `21,600 s`;
- no reinforcements;
- no external mediation;
- no third-party intervention;
- command-policy strategic intents already include `DISENGAGE` and `CEASEFIRE_PROBE`;
- navigation intent already includes `WITHDRAW_VECTOR`;
- permitted termination classes are mutual ceasefire/stand-down, successful withdrawal, surrender, mutual disengagement, combat incapacity, hard-time-limit/stalemate, and annihilation if it emerges naturally.

Phase 8 must preserve the distinction between **physical ability** from Phase 7 and **willingness/control status** from Phase 8. `disabled` is not automatically `surrendered`; withdrawal intent is not successful withdrawal until geometry proves boundary exit.

## 6. Outstanding integrated-loop obligation

`LIVE_COMMAND_OBSERVATION_BRIDGE` remains mandatory before Controls A/B/C and Run 0.

The authoritative Phase-9 step orchestrator must derive every new command-policy observation deterministically from the previously committed state and receipts, including contact quality/uncertainty, relative material state, logistics strain, mobility/geometry opportunity, withdrawal viability, EW opportunity, repair need, enemy closing pressure, and mission/time pressure.

No LLM inference or prose interpretation is allowed in authoritative command observations.

## 7. Non-negotiable invariants

- state machine first, story second;
- no LLM/model judgment inside authoritative transitions;
- identical complete inputs produce identical normalized next state;
- CanonRec substitutions influence Phase 8 only through accepted numeric state/consequences, never class/polity names;
- withdrawal requires physical boundary evidence;
- surrender requires explicit deterministic criteria and is not equivalent to physical disablement;
- ceasefire requires deterministic command-state agreement, not narrator intervention;
- disabled/surrendered/destroyed/protected entities cannot become valid new deliberate targets;
- annihilation is reachable but never privileged;
- no reinforcements or third parties;
- no battle result is claimed before Phase 12.

## 8. Remaining sequence

- **Phase 8:** morale, withdrawal, surrender, ceasefire, disengagement, incapacity, termination;
- **Phase 9:** authoritative step orchestrator + immutable event/state ledger, including `LIVE_COMMAND_OBSERVATION_BRIDGE`;
- **Phase 10:** deterministic factual reporter;
- **Phase 11:** Controls A/B/C;
- **Phase 12:** admit and execute Run 0.

## 9. Validation matrix

| ID | Validation | State |
|---|---|---|
| `V-01` restored aggregate contract | PASS | Phase 1 |
| `V-02` restored aggregate replay | PASS | `de55355d...` |
| `V-03` control CanonRec resolution | PASS | `cd8a22b8...` |
| `V-04` alternate class substitution | PASS | Phase 2 |
| `V-05` alternate polity/org traversal | PASS | Phase 2 |
| `V-06` T0 replay | PASS | `47d31a29...` |
| `V-07` T0 symmetry/proxy-independence | PASS | Phase 3 |
| `V-08` command-policy replay/causality | PASS | Phase 4 |
| `V-09` movement/geometry replay | PASS | `c947b95b...` |
| `V-10` sensing/EW/targeting/weapons replay | PASS | `3b84a912...` |
| `V-11` damage/disposition replay | PASS | `ab0ecdbd...` |
| `V-12` morale/termination replay | active | Phase 8 |
| `V-13` integrated command-observation/ledger replay | blocked | Phase 9 |
| `V-14` reporting regeneration | blocked | Phase 10 |
| `V-15` Control A | blocked | Phase 11 |
| `V-16` Control B | blocked | Phase 11 |
| `V-17` Control C | blocked | Phase 11 |
| `V-18` Run-0 receipt | blocked | Phase 12 |

## 10. Stop conditions

Stop rather than improvise on conflicting canonical authority; a material change to the frozen premise/roster; canon promotion; destructive/preservation-sensitive mutations; altered ethics/security authority; Phase-8 rules requiring class/polity/prose special casing; any runtime judgment delegated to an LLM; any unpinned floating/random branch; a withdrawal result without committed geometry evidence; a ceasefire/surrender result not derivable from committed command/state inputs; or any attempt to treat subsystem smoke fixtures as authoritative Run-0 observations.

## 11. Exact next action

Before executable Phase-8 code, commit a versioned morale/withdrawal/surrender/ceasefire/termination specification defining:

1. authoritative Phase-8 input validation and source binding;
2. morale/cohesion updates driven only by newly committed physical/command consequences;
3. explicit separation between physical disposition and control/willingness status;
4. successful withdrawal semantics using the accepted `20,000 km` boundary and committed geometry;
5. surrender eligibility/scoring/thresholds from accepted numeric state and commander attributes;
6. ceasefire proposal/acceptance semantics using existing deterministic command-policy intent;
7. mutual-disengagement state/streak semantics;
8. combat-incapacity semantics;
9. hard-time-limit/stalemate semantics at `21,600 s`;
10. deterministic termination precedence and victor/objective-result rules, including cases where no single victor is implied;
11. protected-target consequences for surrendered/withdrawn entities without modifying accepted physical disposition semantics;
12. immutable Phase-8 state/receipt schemas and source identities;
13. replay, insertion-order independence, no-new-damage, no-prose/no-RNG, morale monotonicity, boundary, ceasefire, surrender, disengagement, incapacity, stalemate, and non-annihilation acceptance tests.

Only after that specification is committed may Phase-8 executable code be introduced.

## 12. Handoff anchor

Any continuation must reference:
- this DTER `v1.7`;
- PR `#1506` latest head;
- Phase-1 through Phase-7 acceptance receipts;
- current phase `Phase 8`;
- `LIVE_COMMAND_OBSERVATION_BRIDGE` obligation in Section 6;
- exact next action in Section 11.

**Run 0:** blocked. No tactical outcome is claimed.
