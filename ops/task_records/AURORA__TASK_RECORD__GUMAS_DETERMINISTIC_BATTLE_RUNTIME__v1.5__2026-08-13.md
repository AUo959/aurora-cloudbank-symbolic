# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.5`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.4__2026-08-13.md`  
**Created:** `2026-08-13`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 6 — sensing, EW, targeting, and weapons`  
**Phase-6 admission reference:** Phase-5 acceptance seal commit created after validated code head `9d89f64866ed6d884c9830574c1cd60b76b121f9`

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
7. Phase-6 sensing/EW/targeting/weapons layer;
8. later damage/disposition/termination layers;
9. immutable event/state ledger;
10. factual read-only reporter.

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
- movement contract ID/version: `GUMAS_MOVEMENT_GEOMETRY_v1_0` / `1.0.0`;
- movement source bundle SHA-256: `565ef76f94cef320a4e4e8a0cbf75a301270eeef4326975b4cf41681d46bab57`;
- accepted initial movement-state SHA-256: `6b5e6b195aa8f7f839d69c1ba8e89f4a9b74db7946035f11a4a9c2e79581548d`;
- accepted one-step movement-state SHA-256: `c947b95b3e6a38c6676c4a197c5351f017734aebd56ecdf48ab0324311dd1c74`;
- accepted movement receipt SHA-256: `5977f48a5d32a19cf87a6c3caa8d11f26c83c1021957df0474adb982cd0444e0`.

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

Accepted implementation head: `9d89f64866ed6d884c9830574c1cd60b76b121f9`.

Verified behavior:
- 10-second macrostep with deterministic 100-ms substeps;
- integer/fixed-point authoritative movement state;
- P17 point-mass gravity;
- pinned rotating triaxial P17 transform;
- swept collision and segment occultation geometry;
- command orders translated into physically capped thrust without class-name branches;
- impossible reference-dependent maneuvers fail closed;
- same one-step inputs replay exactly;
- command-map insertion order is inert;
- 100-macrostep replay is exact;
- real pinned-CanonRec 38-vessel smoke produces deterministic movement with zero collisions;
- no RNG and no floating-point authoritative branch behavior.

Evidence:
- `simulation/receipts/GUMAS__RECEIPT__MOVEMENT_GEOMETRY_PHASE5__v1.0__2026-08-13.json`;
- `simulation/baselines/gumas/GUMAS__INDEX__FLASH_REBELLION_MOVEMENT_STEP_REPRODUCIBILITY__v1.0__2026-08-13.json`;
- focused `GUMAS Movement Geometry` run `31765543911`, job `94660577608`: success;
- `Aurora CI (Minimal)` run `31765543826`, job `94660620186`: full suite success.

### Phase 6 — sensing, EW, targeting, and weapons
**Status:** admitted / active.

Phase 6 consumes already-committed physical state and command orders. It may determine what each vessel can physically observe, how EW modifies observation quality, which targets are legally/physically eligible, and which weapon attempts occur. It must not yet apply shield, armor, hull, system, morale, cohesion, surrender, ceasefire, or termination state changes.

## 5. Phase-6 boundary

Phase 6 may produce:
- deterministic line-of-sight and range-gated sensor contacts;
- contact-quality/confidence state derived from sensor, stealth, geometry, readiness, and EW inputs;
- deterministic EW effects and counter-effects;
- target eligibility and target-selection receipts constrained by command intent and rules of engagement;
- weapon firing attempts, shot/beam/munition records, and deterministic intercept/hit or exposure results;
- immutable effect descriptors for Phase 7 to consume.

Phase 6 may not:
- apply shield depletion;
- apply armor/hull/system damage;
- alter morale/cohesion;
- decide surrender/withdrawal success/ceasefire acceptance;
- terminate the battle;
- narrate outcomes.

## 6. Non-negotiable invariants

- state machine first, story second;
- no LLM/model judgment inside authoritative transitions;
- identical complete inputs produce identical normalized next state;
- CanonRec substitutions affect sensing/EW/weapons only through resolved/calibrated capabilities;
- no class-name or polity-name behavior branches;
- P17 occultation must use the accepted Phase-5 geometry kernel;
- protected/disabled/surrendered targets must be ineligible once those states exist;
- target selection and tie-breaking must use stable deterministic ordering;
- stochastic weapon behavior, if any is required, must use labeled deterministic child RNG streams derived from the frozen run seed and event identity; Phase 6 must not use ambient/global randomness;
- archival GUMAS source remains immutable;
- no reinforcements or third parties;
- no battle result is claimed before Phase 12.

## 7. Remaining sequence

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
| `V-09` movement/geometry replay | PASS | `c947b95b...` |
| `V-10` sensing/EW/targeting/weapons replay | active | Phase 6 |
| `V-11` reporting regeneration | blocked | Phase 10 |
| `V-12` Control A | blocked | Phase 11 |
| `V-13` Control B | blocked | Phase 11 |
| `V-14` Control C | blocked | Phase 11 |
| `V-15` Run-0 receipt | blocked | Phase 12 |

## 9. Stop conditions

Stop rather than improvise on conflicting canonical authority; a material change to the frozen premise or roster; canon promotion; destructive/preservation-sensitive mutations; altered ethics/security authority; any sensing/EW/weapon rule that would require class-name or polity-name special casing; any runtime judgment delegated to an LLM; or any authoritative branch that depends on unpinned floating/random behavior.

## 10. Exact next action

Before executable Phase-6 code, commit a versioned sensing/EW/targeting/weapons specification defining:

1. authoritative contact and observation schema;
2. sensor range, line-of-sight, stealth and readiness equations;
3. EW attack/defense/countermeasure equations and scope;
4. deterministic contact-quality thresholds and degraded-contact behavior;
5. target eligibility, ROE, stable ordering and tie-breaking;
6. command-policy-to-targeting/fire-control mapping;
7. weapon family abstraction driven by CanonRec-derived firepower/range rather than class names;
8. deterministic hit/intercept/exposure resolution and any labeled child-RNG contract if unavoidable;
9. effect-descriptor schema passed forward to Phase 7 without applying damage;
10. same-input replay, occultation, stealth, EW monotonicity, range, protected-target, substitution-causality and order-independence acceptance tests.

Only after that specification is committed may Phase-6 executable code be introduced.

## 11. Handoff anchor

Any continuation must reference:
- this DTER `v1.5`;
- PR `#1506` latest head;
- Phase-1 through Phase-5 receipts;
- current phase `Phase 6`;
- exact next action in Section 10.

**Run 0:** blocked. No tactical outcome is claimed.
