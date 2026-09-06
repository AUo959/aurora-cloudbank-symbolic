# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**Version:** `v1.3`  
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.2__2026-08-13.md`  
**Created:** `2026-08-13`  
**Status:** `active`  
**Owner / active worker:** `Aurora / ChatGPT GitHub workstream`  
**Repository:** `AUo959/aurora-cloudbank-symbolic`  
**Branch:** `agent/gumas-flash-rebellion-battle-baseline`  
**PR:** `#1506`  
**Current phase:** `Phase 4 — deterministic command-team policy`  
**Phase-4 admission reference:** `e4f3337da2810d92e87d00eddfcfd5a929995ae5`

---

## 1. Objective

Build a repeatable, deterministic, physically bounded, stepwise GUMAS battle runtime for the frozen Galactic Union flash-rebellion control engagement around Planetoid P17. CanonRec class/polity substitutions must alter real simulation variables and consequences without battle-engine code changes. Authoritative state transitions execute before reporting; reporting never decides outcomes.

## 2. Authority stack

1. immutable recovered `GUMAS-PACKAGE-V2` evidence;
2. separately versioned restored GUMAS aggregate tactical authority;
3. pinned CanonRec snapshot plus deterministic tactical-input resolver;
4. scenario/state adapter and deterministic T0 constructor;
5. bounded per-vessel physical/combat extension subordinate to GUMAS;
6. deterministic command-team policy using frozen numeric officer attributes;
7. immutable event/state ledger;
8. factual read-only reporter.

Historical recovered source bytes remain immutable. Scenario-local numbers and simulation outcomes remain non-canon unless separately promoted through Git governance.

## 3. Accepted identities

- recovered GUMAS tree SHA-256: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`;
- recovery package SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`;
- restored runtime: `2.0.1-restored.2`;
- restored replay SHA-256: `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`;
- pinned CanonRec commit: `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
- CanonRec resolver: `1.0.1`;
- derivation rules: `canonrec-tactical-derivation-v1.1`;
- canonical JSON profile: `aurora-canonical-json-v1`;
- resolved control manifest SHA-256: `cd8a22b8d8721106ab94f5f881685cbd8f58c95beeb8f2d86853e09fd61bdfdc`;
- physical calibration version: `1.0`;
- physical calibration SHA-256: `94a6cd7ec934d3fd4a382af051e1a6bb5994ecb5d2bf6b906102367c28592cf6`;
- T0 constructor version: `1.0.0`;
- T0 constructor source SHA-256: `01dd9f1ed08ebc1822e42c28d038e2fff742fe8d0421c342198fbebf56208f6f`;
- accepted normalized T0 SHA-256: `47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec`;
- canonical T0 snapshot file SHA-256: `b9c249ceb3c8ac6c67396046aa6cbfe04d65cc0fb9b6a175d3772113ca3e9968`.

## 4. Phase status

### Phase 0 — provenance and plan anchoring
**Status:** PASS / complete.

### Phase 1 — historical tactical restoration
**Status:** PASS / accepted.

Selected compatibility contract:

`CombatResolver.resolve_battle(CombatState, attacker_fleets, defender_fleets, topology_manager)`

Primary evidence:
- `simulation/receipts/GUMAS__RECEIPT__V2_COMBAT_RESTORATION_PHASE1__v1.1__2026-08-13.json`.

### Phase 2 — deterministic CanonRec tactical-input resolution
**Status:** PASS / accepted.

Accepted behavior includes boundary-aware rule matching, current CanonRec schema support, scoped doctrine containment, lossless u64 seed representation, class substitution through the same resolver, and deterministic canonical hashing.

Primary evidence:
- `simulation/receipts/GUMAS__RECEIPT__CANONREC_TACTICAL_RESOLUTION_PHASE2__v1.0__2026-08-13.json`.

### Phase 3 — deterministic per-vessel T0 physical instantiation
**Status:** PASS / accepted.

Accepted on implementation head `d8214ee7f289169a6a322459bb927061f6e525b6` and sealed at `e4f3337da2810d92e87d00eddfcfd5a929995ae5`.

Verified properties:
- all 38 vessels receive complete deterministic T0 physical state;
- exact 19/19 material symmetry is preserved;
- positions and velocities are exact sign mirrors between sides;
- formation centroids are preserved;
- class-agnostic CanonRec-derived capability vectors drive physical calibration;
- obsolete baseline proxy coefficients are causally inert;
- P17 spin axis, reference frame, period, phase and handedness are pinned;
- same complete inputs reproduce byte-equivalent canonical T0 output;
- constructor source identity is part of run identity.

Evidence:
- `simulation/receipts/GUMAS__RECEIPT__PHYSICAL_T0_PHASE3__v1.0__2026-08-13.json`;
- `simulation/baselines/gumas/GUMAS__INDEX__FLASH_REBELLION_T0_REPRODUCIBILITY__v1.0__2026-08-13.json`;
- focused `GUMAS Physical T0` workflow run `31762064025`, job `94650331791`: success;
- `Aurora CI (Minimal)` run `31762064059`, job `94650378556`: full suite success.

### Phase 4 — deterministic command-team policy
**Status:** admitted / active.

The frozen baseline supplies one commander and six specialist lieutenants per side. Their numeric attributes are authoritative scenario inputs for command behavior. Human-readable `characteristic` prose is descriptive only and MUST NOT participate in authoritative decisions.

Phase 4 must define and prove:
1. a versioned command observation schema derived only from committed simulation state;
2. a finite legal action vocabulary for each decision domain;
3. explicit equations mapping commander attributes and specialist attributes into action scores/thresholds;
4. explicit specialist influence and commander-alignment behavior;
5. deterministic conflict resolution between commander intent and specialist recommendation;
6. explicit lexicographic or otherwise versioned tie-breaking;
7. no hidden LLM/model judgment and no process-randomized `hash()`;
8. no prose-characteristic input to scoring;
9. deterministic replay: same observation + same command team = identical decision receipt;
10. causal sensitivity: controlled attribute changes produce traceable, intended score/decision changes;
11. side differences arise from the frozen numeric teams, not hard-coded loyalist/rebel branches;
12. policy output issues orders only; later physical/combat phases remain responsible for consequences.

## 5. Phase-4 design boundary

Phase 4 may choose or recommend **orders**, but it may not yet implement movement, sensing, weapons, damage, morale transitions, surrender, ceasefire resolution, or termination. Those remain later phases.

Policy inputs must be normalized tactical observations rather than future-state guesses. Where later phases have not yet produced a signal, the observation schema must accept an explicit neutral/unavailable value rather than inventing one.

Commander attributes:
- `command_skill`
- `aggression`
- `casualty_aversion`
- `adaptability`
- `deception`
- `discipline`
- `negotiation_openness`
- `initiative`

Specialist attributes:
- `domain_skill`
- `initiative`
- `discipline`
- `stress_tolerance`
- `risk_tolerance`
- `commander_alignment`

Specialist roles:
- `tactical`
- `navigation`
- `ew_sensors`
- `carrier_ops`
- `engineering`
- `logistics`

## 6. Non-negotiable invariants

- state machine first, story second;
- no LLM/model judgment inside authoritative transitions;
- identical complete inputs produce identical normalized outputs;
- officer differences must create traceable causal differences where their domains are relevant;
- class/polity differences continue to enter through CanonRec-derived state, never side-specific code;
- deterministic iteration and tie-breaking are explicit;
- archival recovered source remains immutable;
- scenario-local values remain labeled and hashed;
- policy cannot bypass later physical constraints;
- no Run-0 reinforcements or third parties;
- no battle result is claimed before Phase 12.

## 7. Remaining sequence

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
| `V-06` T0 replay | PASS | `47d31a29...` |
| `V-07` T0 symmetry/proxy-independence | PASS | Phase-3 receipt |
| `V-08` command-policy replay | active | Phase 4 |
| `V-09` reporting regeneration | blocked | Phase 10 |
| `V-10` Control A | blocked | Phase 11 |
| `V-11` Control B | blocked | Phase 11 |
| `V-12` Control C | blocked | Phase 11 |
| `V-13` Run-0 receipt | blocked | Phase 12 |

## 9. Stop conditions

Stop rather than improvise on conflicting canonical authority; a material change to the frozen Run-0 premise or roster symmetry; canon promotion; destructive/preservation-sensitive mutations; altered ethics/security authority; an officer behavior that cannot be traced to frozen numeric attributes and committed state; or a required command input that would require prose/LLM interpretation.

## 10. Exact next action

Before executable command-policy code, commit a versioned Phase-4 command-policy specification defining:

1. normalized command observation schema;
2. legal action vocabulary by decision domain;
3. exact commander/specialist scoring equations;
4. specialist influence/alignment rules;
5. deterministic tie-breaking and decision-receipt schema;
6. replay and causal-sensitivity acceptance tests.

Only after that specification is committed may the pure deterministic policy module and tests be implemented.

## 11. Handoff anchor

Any continuation must reference:
- this DTER `v1.3`;
- PR `#1506` and its latest head;
- Phase-1, Phase-2 and Phase-3 receipts;
- current phase `Phase 4`;
- exact next action in Section 10.

**Run 0:** blocked. No tactical outcome is claimed.
