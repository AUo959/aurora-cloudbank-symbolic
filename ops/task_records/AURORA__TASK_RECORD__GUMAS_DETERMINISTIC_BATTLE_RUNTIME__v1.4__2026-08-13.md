# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.4`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.3__2026-08-13.md`  
**Created:** `2026-08-13`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 5 — bounded movement and geometry`  
**Phase-5 admission reference:** `60bb9d4846104e8bc54dd3ed673d5fd424f24150`

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control around Planetoid P17. CanonRec class/polity substitutions must alter real simulation variables and consequences without battle-engine code changes. Authoritative transitions execute before reporting; reporting never decides outcomes.

## 2. Authority stack

1. immutable recovered `GUMAS-PACKAGE-V2` evidence;
2. separately versioned restored GUMAS aggregate tactical authority;
3. pinned CanonRec snapshot plus deterministic tactical-input resolver;
4. deterministic per-vessel T0 constructor and physical calibration;
5. deterministic command-team policy producing orders only;
6. bounded per-vessel movement/geometry kernel subordinate to GUMAS;
7. later sensing/combat/damage/disposition layers;
8. immutable event/state ledger;
9. factual read-only reporter.

Historical recovered source bytes remain immutable. Scenario-local values and simulation outcomes remain non-canon unless separately promoted through Git governance.

## 3. Accepted identities

- recovered GUMAS tree SHA-256: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`;
- restored runtime: `2.0.1-restored.2`;
- restored replay SHA-256: `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`;
- pinned CanonRec commit: `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
- resolved control manifest SHA-256: `cd8a22b8d8721106ab94f5f881685cbd8f58c95beeb8f2d86853e09fd61bdfdc`;
- physical calibration SHA-256: `94a6cd7ec934d3fd4a382af051e1a6bb5994ecb5d2bf6b906102367c28592cf6`;
- T0 constructor source SHA-256: `01dd9f1ed08ebc1822e42c28d038e2fff742fe8d0421c342198fbebf56208f6f`;
- accepted T0 SHA-256: `47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec`;
- command policy ID/version: `GUMAS_COMMAND_POLICY_v1_0` / `1.0.0`;
- command policy bundle SHA-256: `8c9ba9d413945404e7648c8f427b660576b0e85887c7639a0944f56b38585b3f`;
- policy module SHA-256: `fa8cd517dec187ee0792b9d4fceac4a5f7a6ce9c5df59affe11600b56afd3f21`;
- policy coefficient table SHA-256: `c318548f9b43477f1d081c3fac3eec7d8b94c03cfb8adbdc55a64fe6f4c82eee`.

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

Evidence:
- `simulation/receipts/GUMAS__RECEIPT__PHYSICAL_T0_PHASE3__v1.0__2026-08-13.json`;
- accepted normalized T0 SHA-256 `47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec`.

### Phase 4 — deterministic command-team policy
**Status:** PASS / accepted.

Accepted implementation head: `4e6027e218decf9ea4f92121436c2ba8d9ecdd7e`.

Verified behavior:
- fixed-point deterministic policy with no RNG;
- no side-specific behavioral branches;
- human-readable officer characteristics and names are causally inert;
- command-team insertion order and observation-map insertion order are inert;
- commander attribute monotonicity tests pass;
- specialist domain-skill effects are role-local;
- lower commander alignment can create explicit deterministic dissent;
- policy identity binds both executable policy bytes and coefficient-table bytes;
- same observation produces `POSITIONAL_MANEUVER` for the frozen loyalist team and `PRESS` for the frozen rebel team entirely through their different numeric attributes;
- command output contains orders only; no movement/combat consequence is applied.

Evidence:
- `simulation/receipts/GUMAS__RECEIPT__COMMAND_POLICY_PHASE4__v1.0__2026-08-13.json`;
- focused `GUMAS Command Policy` run `31764360847`, job `94657059129`: success;
- `Aurora CI (Minimal)` run `31764360860`, job `94657100680`: full suite success.

### Phase 5 — bounded movement and geometry
**Status:** admitted / active.

Phase 5 converts already-committed T0 state plus command orders into physically legal deterministic position/velocity/attitude transitions. It does not sense targets, resolve EW, select weapon targets, fire weapons, apply damage, decide surrender, or narrate results.

Required Phase-5 surfaces:
1. authoritative fixed-point integration state and timestep semantics;
2. deterministic conversion of strategic/navigation/engineering intents into requested acceleration vectors subject to vessel acceleration caps;
3. point-mass P17 gravity using the frozen gravitational parameter;
4. rotating triaxial P17 body geometry using the Phase-3 pinned spin/phase reference;
5. deterministic collision/intersection checks against P17;
6. deterministic line-segment occultation geometry against the rotating triaxial body;
7. deterministic range/separation/closing-rate calculations;
8. battle-volume and withdrawal-boundary geometry, without yet deciding whether withdrawal terminates combat;
9. explicit physical rejection/clamping of impossible command intents rather than silently granting them;
10. one-step and multi-step replay checks with canonical state hashes;
11. no RNG and no floating-point-dependent authoritative branch behavior;
12. class effects enter only through Phase-3 calibrated physical values such as `max_accel_mm_s2`, never class-name branches.

## 5. Phase-5 boundary

Phase 5 may update:
- vessel position;
- vessel velocity;
- authoritative attitude if needed for commanded acceleration;
- deterministic geometric relationship fields derived from positions/P17;
- movement resource usage only if specified before implementation and causally tied to movement.

Phase 5 may not yet update:
- sensor contact truth;
- EW success/failure;
- target eligibility or targeting decisions;
- shots, shields, armor, hull or system damage;
- morale/cohesion;
- surrender/ceasefire effectiveness;
- battle termination;
- narrative/reporting.

## 6. Non-negotiable invariants

- state machine first, story second;
- no LLM/model judgment inside authoritative transitions;
- identical complete inputs produce identical normalized next state;
- impossible orders are constrained by physics rather than rewritten narratively;
- acceleration limits come from the same class-agnostic CanonRec-derived physical calibration accepted in Phase 3;
- deterministic iteration/tie-breaking is explicit;
- P17 geometry uses the pinned scenario-local rotational reference from Phase 3;
- archival GUMAS source remains immutable;
- no reinforcements or third parties;
- no battle result is claimed before Phase 12.

## 7. Remaining sequence

- **Phase 5:** bounded movement and geometry;
- **Phase 6:** sensing, EW, targeting, weapons;
- **Phase 7:** shield/damage/system/disposition transitions;
- **Phase 8:** morale, withdrawal, surrender, ceasefire, termination;
- **Phase 9:** immutable event/state ledger;
- **Phase 10:** deterministic factual reporter;
- **Phase 11:** Controls A/B/C;
- **Phase 12:** admit and execute Run 0.

## 8. Validation matrix

| ID | Validation | State |
|---|---|---|
| `V-01` restored aggregate contract | PASS | Phase 1 |
| `V-02` restored aggregate replay | PASS | `de55355d...` |
| `V-03` control CanonRec resolution | PASS | `cd8a22b8...` |
| `V-04` alternate class substitution | PASS | `d20cbe03...` |
| `V-05` alternate polity/org traversal | PASS | Phase 2 |
| `V-06` T0 replay | PASS | `47d31a29...` |
| `V-07` T0 symmetry/proxy-independence | PASS | Phase 3 |
| `V-08` command-policy replay/causality | PASS | Phase 4 |
| `V-09` movement/geometry replay | active | Phase 5 |
| `V-10` reporting regeneration | blocked | Phase 10 |
| `V-11` Control A | blocked | Phase 11 |
| `V-12` Control B | blocked | Phase 11 |
| `V-13` Control C | blocked | Phase 11 |
| `V-14` Run-0 receipt | blocked | Phase 12 |

## 9. Stop conditions

Stop rather than improvise on conflicting canonical authority; a material change to the frozen premise or roster; canon promotion; destructive/preservation-sensitive mutations; altered ethics/security authority; a movement rule that would require class-name special casing; or authoritative geometry that depends on unpinned floating implementation behavior.

## 10. Exact next action

Before executable movement code, commit a versioned Phase-5 movement/geometry specification defining:

1. authoritative units and fixed-point/integer arithmetic;
2. timestep and integration algorithm;
3. P17 point-mass gravity equation and quantization;
4. command-order-to-acceleration translation and physical clamping;
5. rotating triaxial transform;
6. collision and occultation algorithms;
7. range/closing/withdrawal geometry;
8. canonical movement-step receipt/state-hash schema;
9. one-step, multi-step, symmetry, acceleration-cap, collision, occultation and replay acceptance tests.

Only after that specification is committed may Phase-5 executable kernel code be introduced.

## 11. Handoff anchor

Any continuation must reference:
- this DTER `v1.4`;
- PR `#1506` latest head;
- Phase-1 through Phase-4 receipts;
- current phase `Phase 5`;
- exact next action in Section 10.

**Run 0:** blocked. No tactical outcome is claimed.
