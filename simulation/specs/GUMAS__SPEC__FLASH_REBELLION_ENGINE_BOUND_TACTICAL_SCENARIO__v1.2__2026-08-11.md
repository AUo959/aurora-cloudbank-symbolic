# GUMAS Flash-Rebellion Tactical Restoration and Control Scenario v1.2

**Scenario contract ID:** `GUMAS_FLASH_REBELLION_TACTICAL_RESTORATION_v1_2`  
**Layer:** L2  
**Anchor:** `EOS_SEED_ORION`  
**Ethics:** `Picard_Delta_3`  
**Status:** historical tactical source recovered; restoration and control integration pending

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

The exact later 2026-02-16 validated `engine.py` / `models.py` / `scenarios.py` revision remains unverified because the recovered authoring revision has different LOC counts for those three files. This does not negate recovery of the historical tactical subsystem; it limits claims about the later validation run.

See `simulation/recovery/GUMAS__RECOVERY__V2_TACTICAL_SOURCE_VERIFICATION__v1.0__2026-08-12.md` for the independent hash and defect record.

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

## Authority boundary

1. **Archival authority:** the recovered v2.0 source and two witness archives are immutable historical evidence.
2. **Simulation authority:** `GUMASEngine` remains the enclosing L2 engine authority.
3. **Restoration authority:** an executable restoration must be a new version, never an in-place mutation of the recovered archive.
4. **Adapter authority:** the scenario adapter translates the control fixture into restored GUMAS tactical state; it does not resolve combat itself.
5. **Canon authority:** CanonRec governs ship-class identity and any later promotion of simulation observations.
6. **Run authority:** no tactical result is authoritative until the complete run identity is pinned and replay validation passes.

## Restoration scope

The smallest acceptable restoration should preserve historical formulas and semantics wherever possible while correcting only the integration defects necessary to make the tactical path coherent and testable.

At minimum, restoration work must decide and document:

1. how a `CombatState` is created for co-located opposing fleets;
2. how battlefield condition is derived or supplied deterministically;
3. whether the explicit `FLEET_BATTLE` handler is redirected to `resolve_battle()` or receives a compatibility wrapper;
4. how battle events are recorded into the existing GUMAS audit/event lifecycle;
5. how deterministic ordering is enforced for fleets and combat pairs;
6. how historical RNG behavior is preserved or explicitly versioned;
7. how the recovered aggregate fleet model is extended or adapted for the physically bounded per-vessel control fixture without allowing a second resolver to emerge.

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

No reinforcements, third-party intervention, or narrator-driven rescue may enter after T0.

The battle volume remains physically bounded. The triaxial planetoid is a real collision/occlusion object rather than narrative terrain flavor.

Before execution the fixture still requires either explicit per-vessel T0 state vectors or a versioned deterministic formation-instantiation algorithm, plus complete planetoid rotational reference state if body rotation affects collision or occultation.

## Historical model versus control extension

Recovered GUMAS v2.0 is an aggregate fleet-at-node tactical model:

- `FleetState` contains aggregate strength, technology, morale, location node, movement target/ETA, supply, and experience;
- Phase 8 moves fleets between topology nodes;
- `CombatResolver` computes aggregate fleet outcome from strength, tactical skill, technology/AI proxy, terrain, supply, and morale;
- losses are applied as aggregate fractional reductions to fleet strength and morale.

The requested flash-rebellion control is more physically explicit: per-vessel position, velocity, geometry, occlusion, acceleration limits, targeting eligibility, damage/disposition, withdrawal boundary, and commander/lieutenant decision effects.

Therefore the restoration must not pretend those per-vessel mechanics already existed in historical GUMAS. They are a **bounded tactical extension of GUMAS authority**, derived from and subordinate to the recovered engine rather than a replacement engine.

## Command model

Each side retains one commander plus six lieutenant roles:

- tactical
- navigation
- EW/sensors
- carrier operations
- engineering/damage control
- logistics/support

Recorded attributes must feed a deterministic executable policy. Character prose is explanatory only.

The command-policy layer must expose and version the equations/thresholds mapping attributes plus current tactical state to actions such as maneuver posture, target priority, EW allocation, repair priority, withdrawal, surrender, ceasefire proposal, and ceasefire acceptance.

## Combat and termination

The restored/extended GUMAS tactical path must preserve realistic non-annihilation outcomes.

Permitted termination classes remain:

1. mutual ceasefire / stand-down;
2. successful withdrawal beyond the control boundary;
3. surrender;
4. mutual disengagement;
5. combat incapacity;
6. hard time limit / stalemate;
7. annihilation if it emerges from valid state, without being privileged.

Disabled or surrendered vessels are protected from deliberate targeting.

## Validation gates before Run 0

All of the following must pass:

1. recovered archival source and witnesses remain hash-identical and untouched;
2. restoration code is separately versioned and source-digested;
3. both recovered combat-integration defects have explicit regression tests;
4. aggregate historical combat formulas are characterized before any physical extension modifies their inputs;
5. fixture adapter produces deterministic T0 tactical state;
6. planetoid collision and occlusion tests pass;
7. acceleration and withdrawal bounds pass;
8. protected-target rules pass;
9. no reinforcement can appear after T0;
10. command attributes produce deterministic decisions;
11. ceasefire, withdrawal, surrender, disengagement, incapacity, and annihilation are all reachable from valid state without hard-coded outcomes;
12. mirrored T0 material symmetry is verified;
13. same complete run identity produces identical normalized event/state output and final checksum twice;
14. a changed seed changes only stochastic allocations and not frozen T0 material conditions;
15. no result from the retired standalone resolver is used as validation evidence.

## Output contract

A completed control run must record:

- archival source witness hashes;
- restored engine/tactical source versions and digests;
- adapter version and source digest;
- baseline ID and canonical SHA-256;
- seed;
- complete T0 state checksum;
- material-symmetry receipt;
- ordered normalized event/state log;
- per-vessel final state;
- aggregate fleet final state;
- remaining combat power by side;
- losses and dispositions by class;
- elapsed simulated time;
- termination mode;
- victor only when implied by the termination rule;
- unresolved objectives;
- final normalized SHA-256;
- `historical_canon_status: non_canon_simulation_instance`.

## Current status

`BLOCKED_PENDING_TACTICAL_RESTORATION_AND_FIXTURE_INTEGRATION`

The blocker is no longer source provenance. The blocker is now controlled restoration plus deterministic physical integration.