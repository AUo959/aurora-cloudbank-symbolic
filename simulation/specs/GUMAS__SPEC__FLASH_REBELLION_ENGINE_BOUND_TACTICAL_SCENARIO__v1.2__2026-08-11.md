# GUMAS Flash-Rebellion Tactical Restoration and Control Scenario v1.2

**Scenario contract ID:** `GUMAS_FLASH_REBELLION_TACTICAL_RESTORATION_v1_2`  
**Layer:** L2  
**Anchor:** `EOS_SEED_ORION`  
**Ethics:** `Picard_Delta_3`  
**Status:** historical tactical source recovered; restoration and control integration pending

> **Lineage supersession note (2026-08-12):** Any statement in this v1.2 specification implying that a separate later 2026-02-16 tactical `engine.py` / `models.py` / `scenarios.py` revision remains missing is superseded by `simulation/recovery/GUMAS__RECOVERY__V2_TACTICAL_SOURCE_VERIFICATION__v1.1__2026-08-12.md` and `simulation/recovery/GUMAS__LINEAGE__V1_V2_V25_V3_REATTRIBUTION__v1.0__2026-08-12.md`. The recovered v2.0 package is treated as the complete surviving historical tactical implementation. `GUMAS_SIM_2.5` is not tactical authority. Restoration must explicitly resolve the three-way historical combat API disagreement before Run 0.

## Purpose

Define the controlled path from the recovered historical GUMAS v2.0 tactical authoring source to a deterministic, physically bounded Galactic Union fleet-engagement control run.

This specification does not create a second simulation authority. `GUMASEngine` / `GUMASState` remain the enclosing L2 authority. The recovered v2.0 tactical package supplies the historical fleet/combat design and implementation evidence. Because the recovered authoring revision contains combat-integration defects, the archival source must remain immutable and any executable restoration must be separately versioned, source-digested, tested, and bound to the flash-rebellion fixture through an explicit adapter.

The previously created standalone `GUMAS_TACTICAL_BATTLE_RESOLVER_v1`, its regression test, and its frozen battle receipt remain retired and non-authoritative.

## Recovery status

The source-recovery blocker is closed.

Independent verification established:

- Witness A SHA-256: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- Witness B SHA-256: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- Reunified recovery ZIP SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`
- Recovered `modules/gumas` tree digest: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`

All recovered module hashes agree across both historical witnesses. The package identifies itself as `GUMAS L2 Multi-Agent Galactic Simulation Package v2.0`, anchor `GUMAS-PACKAGE-V2`.

Recovered tactical interfaces include:

- `GUMASEngine`
- `FleetState`
- `CombatState`
- `CombatResolver`
- `TopologyManager`
- `EventType.FLEET_MOVEMENT`
- `EventType.FLEET_BATTLE`
- `calc_combat_outcome`
- Phase 8 fleet movement
- Phase 9 combat resolution

The exact later 2026-02-16 validated `engine.py` / `models.py` / `scenarios.py` revision remains unverified because the recovered authoring revision has different LOC counts for those three files. This sentence is retained only as historical text and is superseded by the lineage note above; the current recovery classification does **not** presume that such a later tactical revision existed.

See `simulation/recovery/GUMAS__RECOVERY__V2_TACTICAL_SOURCE_VERIFICATION__v1.1__2026-08-12.md` for the current hash, corrected-search, and defect record.

## Archival defects

The historical source is evidence and must not be repaired in place.

### Defect A — automatic combat phase lacks a CombatState

Recovered `GUMASEngine._combat_resolution_tick()` calls:

`CombatResolver.resolve_battle(combat=None, ...)`

Recovered `CombatResolver.resolve_battle()` immediately requires `combat.condition` for terrain modifiers and later requires `combat.location` to generate battle events.

Therefore a real contested-location automatic combat phase in this authoring revision is not executable as written.

### Defect B — explicit FLEET_BATTLE handler calls a missing method

Recovered `GUMASEngine._handle_fleet_battle()` calls `CombatResolver.resolve_combat(...)`.

Recovered `CombatResolver` defines `resolve_battle()` and does not define `resolve_combat()`.

Static method/call inventory confirms this is the only missing `CombatResolver` method referenced by the engine.

### Defect C — historical resolver contract disagreement

The corrected local forensic sweep reports a contemporaneous corrected deep-dive document specifying:

`resolve_battle(attackers, defenders, location) -> BattleResult`

That differs from both the recovered `combat.py` resolver signature and the recovered `engine.py` event-handler call. Restoration must therefore select and document an intended compatibility contract rather than simply rename `resolve_combat` to `resolve_battle`.

## Authority boundary

1. **Archival authority:** recovered v2.0 source tree SHA-256 `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9` plus the two witness archives are immutable historical evidence.
2. **Historical implementation identity:** `GUMAS-PACKAGE-V2` is the recovered tactical implementation. Generic `GUMASEngine` / `GUMASState` names alone are insufficient lineage identifiers.
3. **Restoration authority:** an executable restoration must be a new version, never an in-place mutation of the recovered archive.
4. **Adapter authority:** the scenario adapter translates the control fixture into restored GUMAS tactical state; it does not resolve combat itself.
5. **Canon authority:** CanonRec governs ship-class identity and any later promotion of simulation observations.
6. **Run authority:** no tactical result is authoritative until the complete run identity is pinned and replay validation passes.

## Restoration scope

The smallest acceptable restoration should preserve historical formulas and semantics wherever possible while correcting only the integration defects necessary to make the tactical path coherent and testable.

At minimum, restoration work must decide and document:

1. how a `CombatState` is created for co-located opposing fleets;
2. how battlefield condition is derived or supplied deterministically;
3. which historical resolver contract becomes the compatibility target and why;
4. how the explicit `FLEET_BATTLE` handler maps into that contract;
5. how battle events are recorded into the existing GUMAS audit/event lifecycle;
6. how deterministic ordering is enforced for fleets and combat pairs;
7. how historical RNG behavior is preserved or explicitly versioned;
8. how the recovered aggregate fleet model is extended or adapted for the physically bounded per-vessel control fixture without allowing a second resolver to emerge.

Any behavior not present in the historical tactical engine but required by the physical control fixture must be identified as an explicit restoration/extension, not retroactively attributed to GUMAS v2.0.

## Determinism contract

A complete Run-0 identity must include:

`(engine_version, engine_source_digest, tactical_version, tactical_source_digest, scenario_adapter_version, scenario_adapter_source_digest, baseline_sha256, seed_u64)`

Requirements:

1. the scenario seed is the root of all stochastic-looking behavior;
2. process-randomized `hash()` is forbidden for simulation decisions;
3. child RNG streams, if introduced, use labeled cryptographic derivation;
4. vessel, fleet, combat-pair, and event iteration order is explicit and stable;
5. wall clock, network state, external APIs, and unrecorded human choices cannot affect resolution;
6. raw audit timestamps may exist but are excluded from normalized deterministic state hashing;
7. every material tactical mutation is represented in ordered state/event output;
8. two runs with identical complete identity must produce equivalent normalized output and final checksum.

## Physical control fixture

The control remains two materially identical 19-vessel Galactic Union task forces around Planetoid P17:

- 1 Judicator
- 3 Aegis
- 1 Palisade
- 2 Sentinel
- 1 Obsidian
- 4 Vanguard
- 6 Peregrine
- 1 Reliant

The historical v2.0 model is aggregate fleet-at-topology-node combat. The physical control fixture adds per-vessel geometry, collision/occlusion, acceleration limits, targeting eligibility, damage/disposition, withdrawal geometry, and deterministic officer effects as a separately versioned bounded extension subordinate to restored GUMAS authority.

## Command model

Each side has one commander and six lieutenant roles:

- tactical
- navigation
- EW/sensors
- carrier operations
- engineering/damage control
- logistics/support

Recorded attributes remain scenario input. A restored/extended implementation must define a versioned deterministic policy mapping those attributes and current state into tactical choices. Prose characteristics are explanatory only.

## Run-0 gates

Before execution:

1. recovered archival source and witnesses are preserved unchanged;
2. restoration version and source digest are pinned;
3. the chosen combat compatibility contract passes Phase 9 and explicit `FLEET_BATTLE` tests;
4. fixture adapter is versioned and source-digested;
5. complete per-vessel T0 state is explicit or deterministically derived;
6. planetoid rotational reference state is pinned if rotation affects geometry;
7. commander/lieutenant policy is executable and deterministic;
8. collision, occlusion, acceleration, protected-target, withdrawal, no-reinforcement, and termination invariants pass;
9. two independent runs with identical complete identity produce equivalent normalized event/state output and final checksum.

## Output contract

A completed control run records:

- recovered archival tree digest;
- restoration version and source digest;
- adapter version and source digest;
- baseline ID and SHA-256;
- seed;
- T0 material-equivalence check;
- ordered GUMAS event/state-change log;
- per-vessel final state;
- aggregate GUMAS fleet state;
- remaining combat power by side;
- losses by class;
- elapsed simulated time;
- termination mode;
- victor, if one exists under the termination rules;
- unresolved objectives;
- normalized final-state SHA-256;
- `historical_canon_status: non_canon_simulation_instance`.

## Control-run status

`BLOCKED_PENDING_TACTICAL_RESTORATION_AND_FIXTURE_INTEGRATION`
