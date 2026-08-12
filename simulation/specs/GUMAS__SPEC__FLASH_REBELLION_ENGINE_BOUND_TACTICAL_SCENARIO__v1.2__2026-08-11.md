# GUMAS Flash-Rebellion Tactical Restoration and Control Scenario v1.2

**Scenario contract ID:** `GUMAS_FLASH_REBELLION_TACTICAL_RESTORATION_v1_2`  
**Layer:** L2  
**Anchor:** `EOS_SEED_ORION`  
**Ethics:** `Picard_Delta_3`  
**Status:** historical tactical source recovered; restoration and control integration pending

## Purpose

Define the controlled path from the recovered historical GUMAS v2.0 tactical source to a deterministic, physically bounded Galactic Union fleet-engagement control run.

This specification does not create a second simulation authority. The recovered v2.0 package identified by anchor `GUMAS-PACKAGE-V2` and recovered `modules/gumas` tree SHA-256 `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9` is the historical tactical restoration base. Because the recovered source contains combat-integration defects, the archival source must remain immutable and any executable restoration must be separately versioned, source-digested, tested, and bound to the flash-rebellion fixture through an explicit adapter.

The previously created standalone `GUMAS_TACTICAL_BATTLE_RESOLVER_v1`, its regression test, and its frozen battle receipt remain retired and non-authoritative.

## CanonRec input-resolution invariant

This control fixture is a control case, not a hardcoded one-off battle engine.

Canonical roster and polity/organization data must resolve through:

`simulation/specs/GUMAS__SPEC__CANONREC_TACTICAL_INPUT_RESOLUTION__v1.0__2026-08-12.md`

The Run-0 prompt and roster remain unchanged. The resolver contract establishes that a future valid CanonRec class/polity roster can replace the control roster without changing GUMAS combat code. CanonRec defines canonical identity and scoped capabilities; versioned derivation rules convert qualitative canon into numerical simulation parameters where needed; scenario-local values are explicit fallbacks only.

The complete run identity must therefore pin the CanonRec commit/snapshot, material CanonRec source hashes, resolver version/source digest, and resolved tactical-input manifest SHA-256 in addition to engine/restoration/adapter/baseline identity.

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

The previous hypothesis of a separate missing later tactical core trio is retired unless contrary executable evidence appears. The corrected forensic search found no second tactical implementation. See the recovery verification and lineage records for the evidence boundary between independently re-hashed artifacts and local forensic findings.

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

A contemporaneous corrected deep-dive found by the local forensic sweep reportedly documents a third API contract, `resolve_battle(attackers, defenders, location) -> BattleResult`. Restoration must therefore deliberately select and document the compatibility contract rather than perform a casual method rename.

## Authority boundary

1. **Archival authority:** the recovered v2.0 source and two witness archives are immutable historical evidence.
2. **Historical tactical restoration base:** `GUMAS-PACKAGE-V2`, recovered tree digest `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`.
3. **Executable simulation authority:** a separately versioned restoration derived from that recovered package.
4. **Canon authority:** CanonRec governs ship/polity identity, scoped technology/doctrine, and any later promotion of simulation observations.
5. **Canon resolver authority:** the deterministic CanonRec resolver translates pinned canonical sources into a resolved tactical-input manifest; it does not resolve combat.
6. **Scenario adapter authority:** the adapter translates the control fixture and resolved CanonRec manifest into restored GUMAS tactical state; it does not resolve combat.
7. **Run authority:** no tactical result is authoritative until the complete run identity is pinned and replay validation passes.

## Restoration scope

The smallest acceptable restoration should preserve historical formulas and semantics wherever possible while correcting only the integration defects necessary to make the tactical path coherent and testable.

At minimum, restoration work must decide and document:

1. how a `CombatState` is created for co-located opposing fleets;
2. how battlefield condition is derived or supplied deterministically;
3. the intended compatibility contract among the three historical combat API signatures;
4. how battle events are recorded into the existing GUMAS audit/event lifecycle;
5. how deterministic ordering is enforced for fleets and combat pairs;
6. how historical RNG behavior is preserved or explicitly versioned;
7. how the recovered aggregate fleet model is extended or adapted for the physically bounded per-vessel control fixture without allowing a second resolver to emerge;
8. how the CanonRec resolved-input manifest maps canonical/derived class properties into aggregate and per-vessel tactical state.

Any behavior not present in the historical tactical engine but required by the physical control fixture must be identified as an explicit restoration/extension, not retroactively attributed to GUMAS v2.0.

## Determinism contract

A complete Run-0 identity must include:

`(engine_version, engine_source_digest, tactical_version, tactical_source_digest, canonrec_commit, canon_resolver_version, canon_resolver_source_digest, canon_resolution_manifest_sha256, scenario_adapter_version, scenario_adapter_source_digest, baseline_sha256, seed_u64)`

Requirements:

1. the scenario seed is the root of all stochastic-looking behavior;
2. process-randomized `hash()` is forbidden for simulation decisions;
3. child RNG streams, if introduced, use labeled cryptographic derivation;
4. vessel, fleet, combat-pair, source-resolution, and event iteration order is explicit and stable;
5. wall clock, network state, moving branch heads, external APIs, and unrecorded human choices cannot affect resolution;
6. raw audit timestamps may exist but are excluded from normalized deterministic state hashing;
7. every material tactical mutation is represented in ordered state/event output;
8. every resolved tactical input records provenance as direct canon, scoped canon doctrine, deterministic derivation, or scenario-local fallback;
9. two runs with identical complete identity must produce equivalent normalized output and final checksum.

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

The currently recorded numerical class coefficients are provisional simulation values. Before Run 0, the CanonRec resolver must classify each as `CANON_DIRECT`, `CANON_SCOPED_DOCTRINE`, `DERIVED_FROM_CANON`, or `SCENARIO_LOCAL`, and produce a deterministic resolved-input manifest. This classification step does not change the frozen roster or prompt.

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

## Canonical substitution validation

The resolver/adapter boundary must prove that future roster changes are data changes, not engine changes.

Before Run 0 or before declaring the architecture substitution-capable, validation must demonstrate:

1. all eight current Galactic Union control class refs resolve through CanonRec;
2. Galactic Union organization identity resolves through CanonRec;
3. Marshal-specific doctrine does not leak onto generic Galactic Union vessels unless explicitly inherited;
4. at least one alternate canonical class (for example Bastion or Dreadraider) can replace a control class without modifying combat-engine code;
5. at least one different canonical organization/polity can traverse the same resolver/adapter interface where sufficient canon exists;
6. direct CANON class/entity records override superseded staging/registry prose;
7. qualitative canon maps deterministically through a pinned derivation rule when a numeric simulation parameter is required;
8. missing required data fails closed unless an explicit scenario-local fallback exists;
9. changing the CanonRec snapshot changes the resolved-manifest/run identity;
10. identical CanonRec snapshot + roster + resolver version produces byte-equivalent canonical resolved manifests.

## Validation gates before Run 0

All of the following must pass:

1. recovered archival source and witnesses remain hash-identical and untouched;
2. restoration code is separately versioned and source-digested;
3. both recovered combat-integration defects and the selected compatibility contract have explicit regression tests;
4. aggregate historical combat formulas are characterized before any physical extension modifies their inputs;
5. CanonRec snapshot, resolver, source hashes, and resolved tactical-input manifest are pinned;
6. fixture adapter produces deterministic T0 tactical state;
7. planetoid collision and occlusion tests pass;
8. acceleration and withdrawal bounds pass;
9. protected-target rules pass;
10. no reinforcement can appear after T0;
11. command attributes produce deterministic decisions;
12. ceasefire, withdrawal, surrender, disengagement, incapacity, and annihilation are all reachable from valid state without hard-coded outcomes;
13. mirrored T0 material symmetry is verified;
14. same complete run identity produces identical normalized event/state output and final checksum twice;
15. a changed seed changes only stochastic allocations and not frozen T0 material conditions;
16. no result from the retired standalone resolver is used as validation evidence;
17. canonical roster substitution succeeds through the same resolver/adapter contract without engine modification.

## Output contract

A completed control run must record:

- archival source witness hashes;
- restored engine/tactical source versions and digests;
- CanonRec commit SHA and material source hashes;
- CanonRec resolver version/source digest;
- resolved tactical-input manifest and SHA-256;
- provenance class and derivation rule for each resolved tactical value;
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

`BLOCKED_PENDING_TACTICAL_RESTORATION_CANON_RESOLUTION_AND_FIXTURE_INTEGRATION`

The blocker is no longer source provenance. The blockers are controlled restoration, deterministic CanonRec input resolution, and deterministic physical integration.