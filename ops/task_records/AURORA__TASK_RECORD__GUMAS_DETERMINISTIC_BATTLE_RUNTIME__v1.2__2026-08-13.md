# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.2`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.1__2026-08-12.md`  
**Created:** `2026-08-13`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 3 — deterministic per-vessel T0 physical instantiation`  
**Admission code head:** `f00013245f58c15e6d56e3213a858df985b12147`

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control engagement around irregular Planetoid P17. CanonRec class/polity substitutions must change real simulation variables and consequences without changing combat-engine code. Authoritative state transitions execute before reporting; the reporter never decides outcomes.

## 2. Authority stack

1. immutable recovered `GUMAS-PACKAGE-V2` evidence;
2. separately versioned restored GUMAS aggregate tactical authority;
3. pinned CanonRec snapshot plus deterministic tactical-input resolver;
4. scenario/state adapter that instantiates but does not resolve combat;
5. bounded per-vessel physical/combat extension subordinate to GUMAS;
6. immutable event/state ledger;
7. factual read-only reporter.

Historical recovered source bytes remain immutable. Scenario-local simulation numbers do not become canon.

## 3. Accepted authority and identities

- recovered GUMAS tree SHA-256: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`;
- recovery package SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`;
- active restored runtime: `2.0.1-restored.2`;
- restored replay SHA-256: `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`;
- pinned CanonRec commit: `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
- CanonRec resolver: `1.0.1`;
- derivation rules: `canonrec-tactical-derivation-v1.1`;
- canonical JSON profile: `aurora-canonical-json-v1`;
- control resolved-manifest SHA-256: `cd8a22b8d8721106ab94f5f881685cbd8f58c95beeb8f2d86853e09fd61bdfdc`;
- alternate-class substitution manifest SHA-256: `d20cbe034f522d99f17311436a61cd47dd4602aacc3f4d82aaac1483d4ab9fae`.

## 4. Phase status

### Phase 0 — provenance and plan anchoring
**Status:** PASS / complete.

### Phase 1 — historical tactical restoration
**Status:** PASS / accepted.

The selected compatibility contract remains:

`CombatResolver.resolve_battle(CombatState, attacker_fleets, defender_fleets, topology_manager)`

Hardening completed on top of the initial restoration:

- automatic and explicit battle paths converge on one resolver contract;
- recovered ZIP materialization is hash-verified and atomic;
- historical `modules.gumas` import exposure is temporary and protected by the Python import lock;
- historical imports do not remain at `sys.path[0]` or persist as global `modules.gumas` entries;
- isolated subprocess regression removes ambient `PYTHONPATH` dependence.

Evidence:

- `simulation/runtime/gumas_v2_restored/GUMAS__RESTORATION_MANIFEST__v1.1__2026-08-13.json`;
- `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.1__2026-08-13.json`;
- focused workflow `GUMAS v2 Restoration`, run `31760439850`, job `94645445647`: success;
- repository workflow `Aurora CI (Minimal)`, run `31760439839`, job `94645484810`: full suite success.

### Phase 2 — deterministic CanonRec tactical-input resolution
**Status:** PASS / accepted.

Accepted properties:

- current CanonRec `entity_id` / `certainty` schema is handled directly;
- lifecycle `status: active` is not confused with canonical certainty;
- role/feature/doctrine matching is token/phrase-boundary aware rather than raw substring matching;
- `ai` no longer matches `rail`; `central` no longer matches `decentralized`;
- same snapshot + same roster resolves identically;
- Bastion class substitution changes real capability values through the same resolver path;
- Prime Construct authority traverses the same resolver path and resolves a distinct doctrine vector;
- Marshal/Sentinel doctrine is scope-contained: applicable Sentinel receives the two pinned scoped sources; generic Union classes do not inherit them;
- unsigned 64-bit seed encoding can be represented losslessly across JSON consumers;
- non-finite numbers are rejected from canonical JSON hashing.

Evidence:

- `simulation/receipts/GUMAS__RECEIPT__CANONREC_TACTICAL_RESOLUTION_PHASE2__v1.0__2026-08-13.json`;
- focused workflow `GUMAS CanonRec Resolution`, run `31760439826`, job `94645445525`: success;
- repository workflow `Aurora CI (Minimal)`, run `31760439839`, job `94645484810`: full suite success.

### Phase 3 — deterministic per-vessel T0 physical instantiation
**Status:** admitted / active.

The frozen baseline already supplies:

- 19 vessels per side and stable ship-ID rules;
- side centroids and centroid velocities;
- formation radius `850 km`;
- stable lexicographic vessel ordering;
- Planetoid P17 triaxial ellipsoid and gravity parameters;
- rotation period `7.8 h`;
- integration step `10 s`;
- combat/withdrawal boundary `20,000 km`;
- initial readiness/supply/damage conditions.

Still required in Phase 3:

1. versioned physical calibration from dimensionless CanonRec-derived capability vectors plus explicit scenario-local calibration constants;
2. complete deterministic vessel-state schema;
3. deterministic formation-slot algorithm producing per-vessel position vectors from frozen centroids/radius/order;
4. deterministic initial per-vessel velocity vectors;
5. deterministic orientation/attitude representation;
6. initial shield/armor/system, energy/fuel/ammunition where modeled, sensor/EW readiness, morale/cohesion/readiness, command assignment, and disposition state;
7. complete Planetoid P17 rotational reference (`spin_axis_reference_frame`, `spin_axis_vector`, `phase_at_t0`) if rotation affects collision/occultation;
8. canonical normalized T0 snapshot plus SHA-256;
9. replay test proving identical fixture + resolver + calibration produces identical T0 snapshot;
10. mirrored/material symmetry test proving both control sides remain equal at T0.

## 5. Phase-3 constraints

The Phase-2 provenance audit remains controlling:

- canonical identity/text: `CANON_DIRECT`;
- applicable subgroup doctrine: `CANON_SCOPED_DOCTRINE`;
- dimensionless 0–1000 capability/doctrine vectors: `DERIVED_FROM_CANON`;
- existing baseline physical/combat numbers: `SCENARIO_LOCAL`.

No baseline numerical proxy may be promoted to canon. The required physical calibration table is itself scenario-local/versioned run-identity material. CanonRec substitutions must affect physical state through explicit calibration equations, never class-specific battle-engine branches.

The adapter/constructor may instantiate physical state but may not choose battle outcomes, targets, damage, withdrawal, surrender, or other later state transitions.

## 6. Non-negotiable invariants

- state machine first, story second;
- no LLM/model judgment inside authoritative transitions;
- identical complete inputs produce identical normalized outputs;
- canonical differences enter real simulation variables only through explicit provenance-preserving mappings;
- no process-randomized `hash()` for simulation decisions;
- deterministic iteration/tie-breaking is explicit;
- archival recovered source remains immutable;
- scenario-local values remain labeled and hashed;
- disabled/surrendered targets remain protected in later phases;
- no Run-0 reinforcements or third parties;
- battle outcome remains unclaimed until all later gates pass.

## 7. Remaining sequence

- **Phase 3:** complete deterministic T0 physical state;
- **Phase 4:** deterministic command-team policy;
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
| `V-01` restored aggregate contract | PASS | Phase-1 v1.1 receipt |
| `V-02` restored aggregate replay | PASS | `de55355d...` |
| `V-03` control CanonRec roster resolution | PASS | `cd8a22b8...` |
| `V-04` alternate-class substitution | PASS | `d20cbe03...` |
| `V-05` alternate polity/org resolver traversal | PASS | GU/Prime authority receipts |
| `V-06` T0 replay | active | Phase 3 |
| `V-07` physical invariants | blocked | later physical kernel |
| `V-08` command-policy replay | blocked | Phase 4 |
| `V-09` reporting regeneration | blocked | Phase 10 |
| `V-10` Control A | blocked | Phase 11 |
| `V-11` Control B | blocked | Phase 11 |
| `V-12` Control C | blocked | Phase 11 |
| `V-13` Run-0 receipt | blocked | Phase 12 |

## 9. Stop conditions

Stop rather than improvise on conflicting canonical authority, a material change to the frozen Run-0 premise or roster symmetry, canon promotion, destructive/preservation-sensitive mutations, altered ethics/security authority, or a required physical value that has neither an approved deterministic derivation nor an explicitly labeled scenario-local calibration/fallback.

## 10. Exact next action

Implement Phase 3 as one bounded extension package with three separately reviewable artifacts:

1. a versioned physical-calibration specification/table;
2. a deterministic T0 constructor and state schema;
3. replay + symmetry tests and a T0 receipt.

First mutation should define calibration/schema/formation semantics before any movement, targeting, weapons, damage, command-policy, or battle execution code is introduced.

## 11. Handoff anchor

Any continuation must reference:

- this task record `v1.2`;
- latest PR #1506 head;
- Phase-1 v1.1 receipt;
- Phase-2 v1.0 receipt;
- current phase `Phase 3`;
- the exact next action in Section 10.

**Run 0:** blocked. No tactical outcome is claimed.
