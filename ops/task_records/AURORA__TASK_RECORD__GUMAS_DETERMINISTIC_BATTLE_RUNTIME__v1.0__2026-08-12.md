# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.0`  
**Created:** `2026-08-12`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**Queue ID:** `none currently linked`  
**Issue:** `none currently linked`  
**PR:** `#1506`  
**Creation context:** created after the pre-implementation plan commit and before restoration/runtime implementation  
**Controlling revision:** `this file v1.0 + PR #1506 head`

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for a medium-sized Galactic Union flash-rebellion fleet engagement around an irregular planetoid, while preserving the recovered historical GUMAS v2.0 tactical lineage and making CanonRec polity/class substitution meaningful without changing combat-engine code.

The simulator must execute each state transition first and only then report the unfolding battle from the committed event/state ledger.

## 2. Acceptance statement

This task is complete only when:

- the recovered GUMAS v2.0 tactical source is preserved unchanged as archival authority evidence;
- a separately versioned restored GUMAS tactical runtime resolves the historical combat integration defects;
- the Run-0 fixture resolves its polity/class inputs through a deterministic CanonRec resolver with provenance;
- every class/polity difference used by the simulation has a traceable causal path from canonical input to numerical/behavioral state to battle consequence;
- complete per-vessel deterministic T0 physical state is defined;
- commander/lieutenant attributes feed a deterministic command policy;
- battle state advances stepwise under bounded movement, sensing, targeting, EW, weapons, shielding/damage, withdrawal/surrender, and termination rules;
- each authoritative state transition and event is hashed/auditable;
- the reporting layer describes committed events but cannot decide outcomes;
- identical inputs replay identically;
- changing one canonical class or organization/polity changes only resolved inputs and consequent simulation behavior, not combat-engine code;
- Control A/B/C acceptance tests pass;
- only then may Run 0 execute and produce an authoritative control receipt.

## 3. Authority and source inputs

### Independently verified

- `simulation/recovery/GUMAS__RECOVERY__V2_TACTICAL_SOURCE_VERIFICATION__v1.1__2026-08-12.md`
- `simulation/recovery/GUMAS__LINEAGE__V1_V2_V25_V3_REATTRIBUTION__v1.0__2026-08-12.md`
- recovered `GUMAS-PACKAGE-V2` tree SHA-256: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`
- witness A SHA-256: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- witness B SHA-256: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- `simulation/baselines/gumas/GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json`
- `simulation/specs/GUMAS__SPEC__FLASH_REBELLION_ENGINE_BOUND_TACTICAL_SCENARIO__v1.2__2026-08-11.md`
- `simulation/specs/GUMAS__SPEC__CANONREC_TACTICAL_INPUT_RESOLUTION__v1.0__2026-08-12.md`
- `simulation/plans/GUMAS__PLAN__DETERMINISTIC_BATTLE_RUNTIME_IMPLEMENTATION__v1.0__2026-08-12.md`
- CanonRec ship-class and polity/organization records pinned per run.

### External forensic evidence

- `simulation/recovery/GUMAS__RCA__TACTICAL_SOURCE_DEDUP_MISCLASSIFICATION__v1.0__2026-08-12.md` records Addendum D's owner-device primary-source findings about basename-based deduplication and preservation failure; the local dedup manifests themselves are not yet imported into this GitHub workstream.

### Owner decisions

- battle prompt remains the original equal-strength GU-vs-GU flash-rebellion control around an irregular planetoid;
- battle is limited to initial combatants; no reinforcements/third-party intervention;
- realistic resolution includes retreat, surrender, disengagement, ceasefire, mission kill, or destruction; battles need not run to annihilation;
- initial conditions are a frozen baseline for future reruns;
- future CanonRec class/polity substitutions must meaningfully change the simulated system and remain deterministic in their own right;
- each simulation step must execute before the battle report is generated;
- committed pre-implementation intent plus a durable task-reference structure is required for work of this class.

## 4. Scope

### In scope

- historical v2 tactical restoration derived from recovered source;
- deterministic CanonRec resolution and provenance manifest;
- scenario adapter into restored GUMAS state;
- deterministic per-vessel physical tactical extension;
- command-team deterministic decision policy;
- event-sourced state ledger and hashes;
- factual deterministic reporting surface;
- reproducibility and substitution tests;
- Run-0 control execution only after all gates pass.

### Out of scope

- changing the original Run-0 battle premise or roster without owner instruction;
- retroactively modifying recovered archival v2 source;
- treating scenario-local coefficients as canon;
- allowing the reporter/LLM to decide battle outcomes;
- adding reinforcements or external intervention;
- promoting simulated events into L2 canon automatically;
- wiring FORGE v3.0 into the restored v2 runtime without separate owner approval and validation.

### Protected / immutable surfaces

- recovered historical GUMAS v2.0 bytes and witness archives;
- CanonRec source records used for a pinned run;
- frozen Run-0 baseline once its final pre-run hash is established;
- raw event ledger for an executed run.

## 5. Current state and known gaps

### Current state

- historical tactical source recovery is complete and independently hash-verified;
- lineage confusion around `GUMAS_SIM_2.5` has been corrected;
- Run-0 fixture and tactical integration specification exist;
- CanonRec input-resolution contract exists;
- pre-implementation runtime plan is committed;
- no replacement standalone battle resolver remains in the PR;
- no authoritative Run-0 outcome exists.

### Known gaps / blockers

1. recovered combat API is internally inconsistent:
   - Phase 9 passes `combat=None` to `resolve_battle(...)`, which dereferences combat state;
   - explicit `FLEET_BATTLE` calls undefined `resolve_combat(...)`;
   - contemporaneous documentation reports a third incompatible resolver signature;
2. no separately versioned restored executable tactical runtime yet;
3. no executable CanonRec resolver yet;
4. current numerical tactical coefficients have not all been classified as direct canon / scoped canon / derived / scenario-local;
5. no complete per-vessel T0 state-instantiation implementation yet;
6. no deterministic officer command-policy implementation yet;
7. no stepwise physical tactical runtime/event ledger/reporting implementation yet;
8. no Control A/B/C execution proof yet.

## 6. Planned mutations

Expected surfaces are defined primarily by the committed implementation plan. At minimum the work is expected to add separately versioned runtime, resolver/adapter, state/event schemas, tests, and receipts without altering archival recovered source.

| Surface | Intended change | Authority / rationale | Risk |
|---|---|---|---|
| restored GUMAS runtime path | minimal compatibility restoration around recovered v2 contract | recovered source + explicit restoration spec | high |
| CanonRec resolver | deterministic canonical input resolution with provenance | CanonRec substitution contract | high |
| scenario adapter | instantiate runtime state only; never resolve battle itself | authority-boundary invariant | medium |
| physical tactical layer | deterministic per-vessel bounded state evolution | original battle requirement | high |
| command policy | deterministic mapping from officer attributes + state to orders | original battle requirement | high |
| event/state ledger | append authoritative transitions/events + hashes | determinism/audit requirement | medium |
| reporter | render committed events only | narrative-authority boundary | medium |
| tests/receipts | replay, substitution, causal trace, physical invariants | acceptance contract | medium |

Unexpected mutation surfaces must be entered into the decision/plan-delta log before or with implementation.

## 7. Execution sequence and gates

### Phase 0 — Provenance and plan anchoring

Actions:
- recover/verify tactical source;
- correct lineage;
- define baseline/spec/CanonRec contract;
- commit implementation plan and this DTER.

Gate to exit:
- authoritative historical base, control fixture, execution plan, and durable task record are all explicit.

**Status:** complete.

### Phase 1 — Historical tactical restoration

Actions:
- preserve archival source untouched;
- choose/document the smallest coherent combat compatibility contract;
- create separately versioned restored runtime;
- regression-test Phase 9 and explicit `FLEET_BATTLE` paths;
- characterize deterministic RNG/event behavior.

Gate to exit:
- aggregate restored combat executes deterministically without relying on the physical extension.

**Status:** next.

### Phase 2 — CanonRec resolver and resolved tactical manifest

Actions:
- resolve polity/org/class data from pinned CanonRec snapshot;
- enforce scope/inheritance rules;
- implement deterministic canon-to-number derivations where needed;
- classify all current tactical coefficients;
- produce hashed resolved-input manifest.

Gate to exit:
- control roster plus at least one alternate class and one alternate organization/polity resolve through the same interface without combat-engine changes.

**Status:** pending.

### Phase 3 — Deterministic T0 physical instantiation

Actions:
- instantiate every vessel's position, velocity, orientation, formation slot, system state, and applicable physical parameters;
- pin planetoid reference frame/rotation state;
- hash State 0.

Gate to exit:
- repeated instantiation from identical inputs produces byte/normalized-equivalent State 0.

**Status:** pending.

### Phase 4 — Stepwise battle state machine

Authoritative order per step:

1. read immutable State N;
2. sensing/detection;
3. command-team decision evaluation;
4. order generation;
5. movement/propulsion integration;
6. EW/countermeasure resolution;
7. targeting/weapons resolution;
8. shield/armor/system/damage resolution;
9. crew/morale/command consequences as modeled;
10. withdrawal/surrender/disengagement evaluation;
11. termination evaluation;
12. commit State N+1;
13. hash State N+1 and authoritative events;
14. only then render the factual battle report.

Gate to exit:
- all transitions satisfy physical, causal, provenance, and determinism invariants.

**Status:** pending.

### Phase 5 — Acceptance tests

- **Control A:** identical control run twice → identical normalized state/event hashes and result.
- **Control B:** change exactly one canonical ship class → resolver delta is explicit and consequent behavioral/physical differences are traceable; no engine-code change.
- **Control C:** change organization/polity → applicable canonical doctrine/technology changes propagate through the same resolver/adapter/runtime; no engine-code change.

Gate to exit:
- all three controls pass plus CI/invariant tests.

**Status:** pending.

### Phase 6 — Run 0

Actions:
- freeze source/config/canon/run identity;
- execute battle stepwise to a valid termination condition;
- emit immutable raw ledger, normalized deterministic receipt, and unfolding factual report.

Gate to exit:
- Run 0 receipt verifies against pinned inputs/code/hashes.

**Status:** blocked until Phases 1–5 pass.

## 8. Invariants and non-negotiables

- **state machine first, story second**;
- reporter never decides what happened;
- same complete input identity produces same authoritative output;
- canonical substitutions alter real state/decision variables when canon distinguishes them;
- every meaningful substitution has a traceable causal chain: `CanonRec fact → resolved parameter → simulation variable → decision/physics consequence → event/state`;
- no silent runtime qualitative judgment by an LLM;
- all canon-to-number derivations are explicit, versioned, deterministic, and hashed;
- adapters translate/instantiate but do not become combat authority;
- archival recovered source is immutable;
- scenario-local values remain labeled scenario-local;
- no reinforcements/third-party intervention in Run 0;
- realistic termination is permitted before annihilation;
- adding unrelated features must not casually perturb existing RNG streams; RNG consumption design must be stable and scoped;
- raw audit timestamps or other non-causal metadata must not contaminate normalized deterministic hashes;
- failure of a blocking invariant fails closed.

## 9. Validation and acceptance tests

| ID | Validation | Expected result | Evidence / receipt |
|---|---|---|---|
| `V-01` | restored aggregate combat contract | Phase 9 + explicit battle path execute coherently | pending |
| `V-02` | restored combat replay | identical input/seed → identical normalized output | pending |
| `V-03` | CanonRec control roster resolution | all eight control classes + GU scope resolve with provenance | pending |
| `V-04` | class substitution | alternate class changes resolved inputs/behavior without engine edit | pending |
| `V-05` | organization/polity substitution | scoped doctrine/technology changes propagate without engine edit | pending |
| `V-06` | T0 instantiation replay | identical manifest/seed → identical State 0 | pending |
| `V-07` | physical invariants | collision/occlusion/acceleration/range/withdrawal constraints hold | pending |
| `V-08` | command policy replay | same state/officers → same orders | pending |
| `V-09` | narrative authority | report can be regenerated from ledger and never changes state | pending |
| `V-10` | Control A | exact replay equivalence | pending |
| `V-11` | Control B | causal class-delta trace | pending |
| `V-12` | Control C | causal polity/org-delta trace | pending |
| `V-13` | Run-0 final receipt | hashes/config/code/canon/result verify | blocked |

## 10. Stop conditions and owner decisions

Stop rather than improvise if:

- recovered historical evidence contradicts the chosen restoration contract materially;
- restoration would require rewriting archival source rather than deriving a separately versioned implementation;
- CanonRec authority is ambiguous or conflicting for a required property;
- a requested numerical parameter cannot be derived deterministically and no scenario-local fallback has been explicitly authorized;
- physical requirements demand a materially different simulation architecture than the committed plan;
- a change would alter the original Run-0 battle premise, roster symmetry, or reinforcement boundary;
- a change would promote simulation output into canon;
- a destructive or preservation-sensitive mutation becomes necessary;
- security/ethics/canon authority boundaries change.

## 11. Rollback and recovery

### Recovery points

- recovered v2 witness hashes and archive package are preserved independently;
- PR #1506 is draft;
- no authoritative control result has been promoted;
- runtime implementation will be additive/separately versioned.

### Rollback procedure

- revert implementation commits on the scoped branch;
- retain archival/recovery records and superseded plan/history for lineage;
- invalidate any run receipt whose pinned source/config no longer matches;
- do not delete failed/superseded deterministic receipts if they are needed to explain lineage.

## 12. Decision and plan-delta log

| Date / commit | Decision or delta | Evidence / reason | Authority | Consequence |
|---|---|---|---|---|
| 2026-08-11 | Do not create a parallel tactical resolver | recovered GUMAS authority exists | owner + audit | standalone resolver/frozen outcome retired |
| 2026-08-12 | Recovered v2.0 becomes historical tactical restoration base | two hash-identical witnesses + recovered package | verified recovery evidence | `GUMAS_SIM_2.5` no longer tactical authority |
| 2026-08-12 | Treat v2 disappearance as deduplication/preservation failure, not intentional retirement | Addendum D RCA | owner-device forensic evidence | preserve v2 lineage; audit destructive dedup assumptions |
| 2026-08-12 | CanonRec substitutions must change real simulation behavior deterministically | owner requirement | owner | resolver/provenance/causal-trace acceptance tests required |
| 2026-08-12 | Simulation executes each state step before reporting | owner requirement | owner | event/state ledger is authoritative; reporter is read-only |
| `e2609cda44786eb197d29cf555f25c2c573a4880` | Commit implementation intent before runtime work | owner SOP requirement | owner | runtime implementation remains blocked until plan anchored |
| 2026-08-12 | Add DTER structure as durable reference in addition to plan/handoff | owner SOP clarification | owner | this record becomes controlling task index for #1506 |

## 13. Evidence and receipts

### Key commits

- `e2609cda44786eb197d29cf555f25c2c573a4880` — committed deterministic battle runtime implementation plan before runtime implementation.

### Key hashes

- recovered v2 tree: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`
- witness A: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- witness B: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- recovery package: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`

### CI / tests / replay

- planning/recovery/specification CI has been largely green across prior heads;
- executable restoration/runtime validation has not yet begun and no Run-0 result is valid yet.

## 14. Current status and next action

**Current phase:** `Phase 1 — Historical tactical restoration`  
**Completed gates:** `source recovery; lineage correction; baseline/specification; CanonRec substitution contract; pre-implementation plan; durable task record`  
**Open blockers:** `three-way historical combat API inconsistency; no restored runtime yet`  
**Owner decision required:** `no additional decision required to begin the already-approved minimal restoration phase; stop if restoration crosses a listed owner boundary`  
**Exact next action:** `inspect the recovered v2 combat/engine/model interfaces together, specify the minimal restored CombatState/resolver compatibility contract, commit that restoration design/tests, then implement the smallest separately versioned restoration without modifying archival bytes.`

## 15. Handoff anchor

Any handoff for this task must reference:

- task record: `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.0__2026-08-12.md`
- task record version: `v1.0`
- controlling PR: `#1506`
- implementation plan: `simulation/plans/GUMAS__PLAN__DETERMINISTIC_BATTLE_RUNTIME_IMPLEMENTATION__v1.0__2026-08-12.md`
- current phase: `Phase 1 — Historical tactical restoration`
- exact next action: `define and validate minimal restored combat compatibility contract before implementation expansion`
- unresolved blocker: `three incompatible historical combat API contracts`

The handoff supplements this task record and linked authority set; it does not replace them.

## 16. Completion record

**Final status:** `pending`  
**Merge / closing PR:** `#1506 (draft)`  
**Final controlling commit:** `pending`  
**Validation result:** `pending`  
**Residual risks / follow-ups:** `pending`  
**Successor task record(s):** `none yet`
