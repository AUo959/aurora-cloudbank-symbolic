# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.6`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.5__2026-08-13.md`  
**Created:** `2026-08-13`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 7 — shield, armor, hull, system, and disposition transitions`  
**Phase-7 admission reference:** Phase-6 acceptance seal following validated code head `f6dfa0a2335ca1c25bf6749c0775f5bb95675e24`

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
8. Phase-7 damage/system/disposition layer;
9. later morale/withdrawal/surrender/termination layer;
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
- Phase-6 contract ID/version: `GUMAS_SENSING_EW_TARGETING_WEAPONS_v1_0` / `1.0.0`;
- Phase-6 source bundle SHA-256: `05e65b2ee5744809f22eeb1dd6cf5cbf637690d1fa16c177c3bbeedca74427e7`;
- accepted Phase-6 observation SHA-256: `bf8606c0ae9e682cefa2cda649e817d39dea57e36687b274d9f6c3892aa5f1f3`;
- accepted Phase-6 fire-control SHA-256: `43ec46c18f5f2efbd9ff029fb429445aa2b231086bd018c2a104c27804c64adc`;
- accepted Phase-6 next-state SHA-256: `393ffd735e01da4fe4ca2e35547ee457d626005f5e27add5d6f4e97ea7ca7479`;
- accepted Phase-6 receipt SHA-256: `3b84a912d1826846599dcd2c01ec763f2430af3da8931a03c01940f26faef775`.

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

Accepted implementation head: `f6dfa0a2335ca1c25bf6749c0775f5bb95675e24`.

Verified behavior:
- P17 line-of-sight and sensor range gate contacts;
- sensor/readiness/stealth calculations are deterministic and monotonic;
- EW attack/protection/deception are order-independent;
- target eligibility enforces committed hostile identification, range, ROE and protected disposition;
- deterministic complete-ship-ID tie-breaking;
- effective-salvo attempts use class-agnostic firepower/range/readiness values;
- stochastic shot uncertainty uses per-shot SHA-256 child material, not mutable/ambient RNG;
- firing consumes shooter ammunition/energy only;
- Phase 6 emits effect descriptors but does not apply damage;
- Phase-3 direct capability schema is consumed without changing accepted T0: direct q1000 keys are read as stored and sensors/mobility are recovered from the exact invertible accepted Phase-3 physical calibration;
- real pinned-CanonRec first-step witness: 440 contacts, 58 hostile-confirmed tracks, zero weapon attempts because no eligible confirmed target is yet within effective weapon range.

Evidence:
- `simulation/receipts/GUMAS__RECEIPT__SENSING_EW_TARGETING_WEAPONS_PHASE6__v1.0__2026-08-13.json`;
- focused `GUMAS Sensing EW Weapons` run `31767364701`, job `94665878398`: success;
- `Aurora CI (Minimal)` run `31767364715`, job `94665918498`: full suite success.

### Phase 7 — shield, armor, hull, system, and disposition transitions
**Status:** admitted / active.

Phase 7 consumes immutable Phase-6 effect descriptors and current physical/readiness state. It may apply deterministic shield depletion, armor/hull damage, bounded subsystem/readiness degradation, and physical combat disposition changes such as `combat_capable`, `degraded`, `disabled`, or `destroyed` where physically warranted.

Phase 7 must not decide morale, surrender, ceasefire, withdrawal success, battle termination, or reporting.

## 5. Phase-7 boundary

Phase 7 may produce:
- deterministic shield absorption/depletion;
- residual effect transfer into armor and hull;
- deterministic subsystem/readiness degradation linked to actual damage magnitude;
- updated damage-state/disposition classification;
- immutable per-effect damage receipts;
- next-state and damage-ledger hashes.

Phase 7 may not:
- invent incoming effects not emitted by Phase 6;
- use prose, class names or polity names as hidden modifiers;
- decide that a side surrenders or withdraws;
- end the battle;
- narrate outcomes.

## 6. Outstanding integrated-loop obligation

`LIVE_COMMAND_OBSERVATION_BRIDGE` is mandatory before Controls A/B/C and Run 0.

The Phase-4 and Phase-6 subsystem smokes intentionally use a frozen synthetic command-observation fixture so command-policy behavior can be tested independently. The authoritative battle loop must not do this.

In the integrated step orchestrator/ledger phase, every new command-policy observation must be derived deterministically from the previously committed state and receipts, including at minimum:
- committed contact quality/uncertainty;
- relative material/damage state;
- logistics/resource strain;
- mobility margin and geometry opportunity;
- withdrawal viability;
- EW opportunity;
- repair need;
- enemy closing pressure;
- mission/time pressure from the frozen scenario.

That adapter must be versioned, source-hashed, replay-tested, and included in run identity. No LLM inference or prose interpretation is allowed in authoritative command observations.

## 7. Non-negotiable invariants

- state machine first, story second;
- no LLM/model judgment inside authoritative transitions;
- identical complete inputs produce identical normalized next state;
- CanonRec substitutions affect damage only through accepted resolved/calibrated numeric state and effect descriptors;
- no class-name or polity-name behavior branches;
- disabled/surrendered/destroyed entities cannot be valid new targets;
- stable deterministic ordering/tie-breaking everywhere;
- archival GUMAS source remains immutable;
- no reinforcements or third parties;
- no battle result is claimed before Phase 12.

## 8. Remaining sequence

- **Phase 7:** shield/damage/system/disposition transitions;
- **Phase 8:** morale, withdrawal, surrender, ceasefire, termination;
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
| `V-11` damage/disposition replay | active | Phase 7 |
| `V-12` integrated command-observation/ledger replay | blocked | Phase 9 |
| `V-13` reporting regeneration | blocked | Phase 10 |
| `V-14` Control A | blocked | Phase 11 |
| `V-15` Control B | blocked | Phase 11 |
| `V-16` Control C | blocked | Phase 11 |
| `V-17` Run-0 receipt | blocked | Phase 12 |

## 10. Stop conditions

Stop rather than improvise on conflicting canonical authority; a material change to the frozen premise/roster; canon promotion; destructive/preservation-sensitive mutations; altered ethics/security authority; damage rules requiring class/polity-name special casing; any runtime judgment delegated to an LLM; any authoritative branch depending on unpinned floating/random behavior; or any attempt to treat the subsystem smoke's synthetic command observation as authoritative Run-0 input.

## 11. Exact next action

Before executable Phase-7 code, commit a versioned damage/disposition specification defining:

1. effect-descriptor validation and stable application order;
2. shield absorption/depletion equation;
3. armor absorption/degradation equation;
4. hull damage equation;
5. deterministic subsystem/readiness degradation driven by actual damage fraction;
6. damage-state and physical disposition thresholds;
7. simultaneous-effects semantics;
8. overkill/capacity clamping and fail-closed rules;
9. immutable damage receipt/state schemas;
10. same-input replay, insertion-order independence, monotonicity, zero-effect, shield-before-armor-before-hull, disabled/destroyed, and no-morale/no-termination acceptance tests.

Only after that specification is committed may Phase-7 executable code be introduced.

## 12. Handoff anchor

Any continuation must reference:
- this DTER `v1.6`;
- PR `#1506` latest head;
- Phase-1 through Phase-6 receipts;
- current phase `Phase 7`;
- `LIVE_COMMAND_OBSERVATION_BRIDGE` obligation in Section 6;
- exact next action in Section 11.

**Run 0:** blocked. No tactical outcome is claimed.
