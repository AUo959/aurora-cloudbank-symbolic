# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.1`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.0__2026-08-12.md`  
**Created:** `2026-08-12`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 2 — deterministic CanonRec resolver and resolved tactical manifest`  
**Controlling revision:** `this file v1.1 + latest PR #1506 head`

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control engagement around irregular planetoid P17. CanonRec polity/class substitutions must change real simulation variables and consequences without changing combat-engine code. Every state transition executes before any battle report is rendered.

## 2. Acceptance statement

The task is complete only when the recovered GUMAS v2 tactical lineage remains preserved; restored aggregate combat is deterministic; CanonRec inputs resolve deterministically with per-value provenance; all control vessels receive deterministic physical T0 state; command staff produce deterministic orders; sensing, maneuver, EW, targeting, damage, withdrawal/surrender, and termination advance as a bounded state machine; events/states are hash-auditable; reporting is read-only; Controls A/B/C pass; and only then Run 0 executes.

## 3. Authority and source inputs

### Independently verified

- recovered historical authority: `GUMAS-PACKAGE-V2`;
- recovered tree SHA-256: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`;
- recovery package SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`;
- restored aggregate runtime: `2.0.1-restored.1`;
- Phase-1 implementation commit: `79efdb2dbdfaec790efc8b42155eae94d067c1bd`;
- Phase-1 replay SHA-256: `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`;
- Phase-1 receipt: `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.0__2026-08-12.json`;
- baseline: `simulation/baselines/gumas/GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json`;
- battle specification: `simulation/specs/GUMAS__SPEC__FLASH_REBELLION_ENGINE_BOUND_TACTICAL_SCENARIO__v1.2__2026-08-11.md`;
- CanonRec resolution contract: `simulation/specs/GUMAS__SPEC__CANONREC_TACTICAL_INPUT_RESOLUTION__v1.0__2026-08-12.md`;
- implementation plan: `simulation/plans/GUMAS__PLAN__DETERMINISTIC_BATTLE_RUNTIME_IMPLEMENTATION__v1.0__2026-08-12.md`.

### Owner decisions

- Run-0 prompt and equal 19-vessel GU-vs-GU roster remain unchanged;
- no reinforcements or third-party intervention;
- realistic non-annihilation outcomes are valid;
- class/polity substitution must be causally meaningful and deterministic;
- runtime executes each step before reporting;
- handoffs do not replace committed execution structure.

## 4. Scope

### In scope

Restored GUMAS aggregate authority, deterministic CanonRec resolution, scenario adapter, physical per-vessel extension, deterministic command policy, state/event ledger, factual reporting, controls A/B/C, and Run 0 after all gates.

### Out of scope

Changing the control prompt without owner instruction; editing recovered archival bytes; treating scenario-local coefficients as canon; allowing an LLM/reporter to decide outcomes; adding reinforcements; automatic canon promotion; integrating FORGE v3 without separate approval.

### Protected / immutable surfaces

Recovered GUMAS v2 bytes/witnesses, pinned CanonRec records for a run, final frozen Run-0 baseline, and raw executed event ledgers.

## 5. Current state and known gaps

### Completed

- Phase 0 provenance/plan anchoring;
- Phase 1 historical tactical restoration;
- automatic Phase 9 and explicit `FLEET_BATTLE` converge on recovered `CombatResolver.resolve_battle(CombatState, ...)`;
- historical package is reassembled from lossless segments and SHA-256 verified before import;
- full GitHub repository test suite passed on restoration commit;
- Run 0 has no claimed result.

### Open gaps

- no executable deterministic CanonRec resolver/manifest yet;
- tactical coefficients have not all been classified by provenance;
- no physical T0 vessel instantiation;
- no officer command policy;
- no per-step physical battle kernel/event ledger/report;
- Controls A/B/C not yet executed.

## 6. Planned mutations

| Surface | Intended change | Constraint |
|---|---|---|
| CanonRec resolver | pinned deterministic identity/doctrine/class resolution | no runtime LLM inference |
| resolved tactical manifest | canonicalized hashed values + source provenance | every value classified |
| derivation tables | deterministic qualitative-to-numeric mappings | explicit version/digest |
| tests | control roster, alternate class, alternate polity/org, scope leakage, replay | no engine edits for substitutions |
| later adapter/physics | only after Phase-2 gate | adapter may not resolve combat |

## 7. Execution sequence and gates

### Phase 0 — Provenance and plan anchoring
**Status:** complete.

### Phase 1 — Historical tactical restoration
**Status:** complete / PASS.

Evidence:
- commit `79efdb2dbdfaec790efc8b42155eae94d067c1bd`;
- receipt `GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.0__2026-08-12.json`;
- Aurora CI Minimal run `31566442227`, job `94019102643`: full suite success;
- normalized replay SHA-256 `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`.

### Phase 2 — CanonRec resolver and resolved tactical manifest

Actions:
1. pin the live CanonRec commit used for development;
2. inspect actual polity/org/class/doctrine schemas;
3. implement strict resolution precedence and scope rules;
4. implement only explicit versioned derivations needed to produce numeric tactical inputs;
5. label every resolved value `CANON_DIRECT`, `CANON_SCOPED_DOCTRINE`, `DERIVED_FROM_CANON`, or `SCENARIO_LOCAL`;
6. canonicalize/hash the resolved manifest;
7. test all eight Run-0 classes + GU organization;
8. prove one alternate class and one alternate polity/org traverse the same API without GUMAS engine changes;
9. prove Marshal-specific doctrine does not leak into generic GU resolution;
10. replay identical resolver input and require identical manifest hash.

Gate to exit:
- control roster and required substitutions resolve deterministically through one interface with complete provenance and no combat-engine changes.

**Status:** active / next action.

### Phase 3 — Deterministic T0 physical instantiation
**Status:** blocked on Phase 2.

### Phase 4 — Stepwise battle state machine
**Status:** blocked on Phase 3.

### Phase 5 — Acceptance Controls A/B/C
**Status:** blocked on Phase 4.

### Phase 6 — Run 0
**Status:** blocked on Phases 2–5.

## 8. Invariants and non-negotiables

- state machine first, story second;
- reporter never changes state or decides events;
- identical complete inputs produce identical authoritative outputs;
- canonical differences must enter real simulation variables when canon distinguishes them;
- every causal substitution trace is recoverable: `CanonRec fact → resolved parameter → simulation variable → decision/physics → event/state`;
- no free-form qualitative judgment at runtime;
- canon-to-number derivations are explicit, versioned, deterministic, and hashed;
- adapters translate/instantiate but do not become combat authority;
- archival recovered source is immutable;
- scenario-local values remain labeled;
- no reinforcements/third parties in Run 0;
- realistic termination before annihilation is valid;
- non-causal timestamps never contaminate deterministic hashes;
- blocking invariant failure fails closed.

## 9. Validation and acceptance tests

| ID | Validation | State |
|---|---|---|
| `V-01` restored aggregate contract | PASS | Phase-1 receipt |
| `V-02` restored aggregate replay | PASS | `de55355d...` |
| `V-03` control CanonRec roster resolution | pending | Phase 2 |
| `V-04` alternate-class substitution | pending | Phase 2 |
| `V-05` alternate polity/org substitution | pending | Phase 2 |
| `V-06` T0 replay | blocked | Phase 3 |
| `V-07` physical invariants | blocked | Phase 4 |
| `V-08` command-policy replay | blocked | later phase |
| `V-09` reporting read-only regeneration | blocked | later phase |
| `V-10` Control A | blocked | Phase 5 |
| `V-11` Control B | blocked | Phase 5 |
| `V-12` Control C | blocked | Phase 5 |
| `V-13` Run-0 receipt | blocked | Phase 6 |

## 10. Stop conditions and owner decisions

Stop rather than improvise on conflicting CanonRec authority, ambiguous scope/inheritance, an unresolvable required numeric property without authorized fallback, a material architecture departure, any change to Run-0 premise/roster symmetry, canon promotion, destructive/preservation-sensitive changes, or altered ethics/security authority.

## 11. Rollback and recovery

All implementation is additive on draft PR #1506. Revert the scoped phase commit(s) while retaining recovery/receipt/history records. Never delete failed deterministic receipts needed for lineage. Any run whose pinned code/config/canon identity changes is invalidated rather than silently reinterpreted.

## 12. Decision and plan-delta log

| Date / commit | Decision | Consequence |
|---|---|---|
| 2026-08-11 | no parallel tactical resolver | historical GUMAS remains authority |
| 2026-08-12 | recovered v2 package is tactical restoration base | v2.5 no longer tactical authority |
| `e2609cda...` | pre-implementation plan committed | implementation gated by plan |
| `03273353...` | DTER v1.0 committed | durable task reference established |
| `79efdb2d...` | restore shipped `resolve_battle(CombatState,...)` contract via subclass | Phase 1 executable restoration |
| 2026-08-12 | historical ZIP imported only after decoded SHA-256 verification | preserved-byte boundary fails closed |
| 2026-08-12 | full repository suite passed | advance to Phase 2 |

## 13. Evidence and receipts

- Phase-1 implementation: `79efdb2dbdfaec790efc8b42155eae94d067c1bd`;
- Phase-1 receipt: `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.0__2026-08-12.json`;
- Aurora CI Minimal: run `31566442227`, job `94019102643`, conclusion `success`;
- full test suite, critical tests, syntax, OPAL2, and container hash validation: PASS;
- replay digest: `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`.

## 14. Current status and next action

**Current phase:** `Phase 2 — deterministic CanonRec resolver and resolved tactical manifest`  
**Completed gates:** `Phase 0, Phase 1`  
**Open blocker:** `CanonRec schemas/snapshot must be freshly pinned and inspected before resolver code is written`  
**Owner decision required:** `no, unless CanonRec authority conflicts`  
**Exact next action:** `read current CanonRec repository head plus GU organization, all eight Run-0 ship-class records, applicable fleet/cross-cutting doctrine, and at least one alternate class/polity; then implement the deterministic resolver against those actual schemas.`

## 15. Handoff anchor

Any continuation must reference:
- this task record path/version (`v1.1`);
- latest PR #1506 head;
- current phase `Phase 2`;
- Phase-1 receipt;
- exact next action from Section 14;
- unresolved authority conflicts, if any.

## 16. Completion record

**Final status:** pending.  
**Run 0:** blocked.  
**Residual follow-ups:** physical instantiation, state machine, command policy, ledger/reporting, Controls A/B/C.  
**Successor record:** none; continue this DTER until a material objective/authority change requires v1.2.
