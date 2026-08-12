# GUMAS Flash-Rebellion Engine-Bound Tactical Scenario v1.2

**Scenario contract ID:** `GUMAS_FLASH_REBELLION_ENGINE_BOUND_v1_2`  
**Layer:** L2  
**Anchor:** `EOS_SEED_ORION`  
**Ethics:** `Picard_Delta_3`  
**Status:** source-lineage-gated control specification; no historical canon promotion

## Purpose

Define a deterministic, physically bounded Galactic Union fleet-engagement control fixture without introducing a second simulation authority.

The verified simulation authority is the existing `GUMASEngine` / `GUMASState` core. The historical GUMAS v2 documentation describes a later fleet/combat design containing `FleetState`, `CombatState`, `CombatResolver`, `FLEET_MOVEMENT`, `FLEET_BATTLE`, terrain/topology logic, and an expanded lifecycle. The source-lineage recovery pass performed for this scenario did **not** recover executable source for those tactical modules.

Accordingly, this revision treats the v2 tactical material as **documented design evidence**, not verified executable implementation. The fixture remains blocked from control-run execution until the actual tactical source is recovered and cryptographically identified, or the owner explicitly authorizes a new versioned GUMAS tactical implementation.

The previously created standalone `GUMAS_TACTICAL_BATTLE_RESOLVER_v1`, its regression test, and its frozen battle receipt are retired and are not authoritative evidence for any future run.

## Source-recovery finding

The supplied artifact `GUMAS_SIM_2.5.zip` was inspected directly.

- archive SHA-256: `6d91d36104b2da89d66e37f6b9b97691470762d4793763784988fb8db84db8c5`
- executable Python files present: `engine.py`, `models.py`, `formulas.py`, `scenarios.py`
- those files match the separately supplied core source set
- documented tactical files such as `combat.py` and `topology.py` are absent from the supplied archive
- the archive documentation nevertheless describes a larger v2 implementation with `CombatResolver`, `FLEET_BATTLE`, additional formulas, and an expanded tick lifecycle

Recovery searches also found no executable tactical module artifact in the uploaded File Library, current indexed CloudBank or CanonRec source, indexed branches, PRs, or unique-symbol commit history. Historical records do show local `GUMAS_SIM_2.0` / `GUMAS_SIM_2.5` project trees existed outside the live repository, but path references alone are not implementation evidence.

**Classification:** `partial_implementation_core_verified_tactical_source_missing`.

This classification follows the Aurora/GUMAS salvage rule that operational claims require verifiable implementation evidence; unsupported runtime claims remain quarantined rather than silently reconstructed.

## Authority and implementation boundary

1. **Simulation authority:** `GUMASEngine` owns the deterministic RNG root, enclosing state lifecycle, event ordering, ethics callback, and audit history.
2. **Core state authority:** the verified `GUMASState` is the enclosing L2 state model.
3. **Scenario fixture:** the flash-rebellion baseline is currently control input, not yet a native tactical `GUMASState`.
4. **Tactical source:** the documented v2 fleet/combat surface is non-executable evidence until its source is recovered or superseded by an explicitly approved new GUMAS version.
5. **Adapter:** any future adapter is integration plumbing only; it must not become a parallel battle engine.
6. **Fail closed:** if verified tactical source and adapter are unavailable, no battle executes.
7. **Canon authority:** CanonRec governs ship-class identity, role, naming admission, and any later promotion of simulation results.
8. **Runtime observations:** officers, vessel instances, tactical choices, damage, surrender, withdrawal, and outcomes remain `non_canon_simulation_instance` unless explicitly reconciled and promoted.

## Canon boundary

The baseline is a **versioned control fixture**, not a canonical historical battle.

Scenario-local officers, vessel IDs, numerical coefficients, tactical decisions, and outcomes do not become L2 history merely because they are version-controlled. Scenario-local names generated under `GUMAS_NAMING_PROTOCOL_v0.1` must be checked against a pinned CanonRec snapshot before any canon-admission request.

## Verified core binding

The verified core supports the following binding contract:

- `GUMASEngine(seed=...)` establishes the stochastic root;
- `init_scenario(state=...)` accepts an explicit `GUMASState`;
- significant mutations remain ethics-checkable through the existing callback / Picard_Delta_3 boundary;
- ordered state changes remain auditable through GUMAS tick history;
- raw audit output may contain non-causal wall-clock timestamps and must not be confused with the deterministic simulation projection used for replay checksums.

The core seeded-reproducibility smoke test was executed twice for 12 turns using the fixture seed. After removing wall-clock timestamp fields, normalized state matched with SHA-256:

`2821c009fae89bc3a77ed2e4551e002d3df565e07d20ad039e007423ccbcfbe8`

This validates the verified **core** RNG/state invariant only. It does not validate tactical combat, fleet movement, the planetoid fixture, or the command teams.

## Tactical binding gate

A tactical run may begin only when one of these paths is satisfied:

- **Recovery path:** the historical tactical source is recovered, reviewed, cryptographically identified, and shown to implement the documented fleet/combat contract; or
- **New-version path:** the owner explicitly authorizes a new versioned GUMAS tactical implementation derived from verified requirements and clearly distinguished from recovered historical code.

Neither path may silently reuse the retired standalone resolver.

## Determinism contract

A valid control-run identity must pin:

`(engine_version, engine_source_digest, tactical_version, tactical_source_digest, scenario_adapter_version, scenario_adapter_source_digest, baseline_sha256, seed_u64)`

`baseline_sha256` is SHA-256 over the UTF-8 encoding of parsed baseline data rendered as canonical JSON with recursively sorted object keys, separators exactly `,` and `:`, no added whitespace, and `ensure_ascii=false`.

Requirements:

1. The GUMAS seed is the root of all stochastic-looking behavior.
2. Child RNG streams, if any, are deterministically derived from labeled SHA-256 material.
3. Vessel IDs follow `{SIDE3}-{CLASS_TOKEN}-{NN}` and instantiated vessels resolve in lexicographic `ship_id` order.
4. Python process-randomized `hash()` is forbidden for simulation decisions.
5. Wall-clock time, network state, external APIs, and unrecorded human choices cannot affect causal resolution.
6. Every material mutation emits an ordered event/state record.
7. Raw audit output and deterministic normalized output are separate artifacts.
8. Two executions with identical complete run identity must produce equivalent normalized event sequences and final-state checksums.
9. A run is invalid while any required source digest is unavailable.

## Physical model requirements

The battle volume is centered on an irregular planetoid represented for collision and occultation by a triaxial ellipsoid with point-mass gravity.

The frozen fixture currently provides:

- semiaxes `190 × 135 × 90 km`;
- density `3100 kg/m³`;
- mass and gravitational parameter derived consistently from those dimensions;
- 20,000 km combat / withdrawal boundary;
- 10 s requested integration step;
- 21,600 s maximum duration;
- FTL disabled inside the battle volume.

Before a control run, the rotating-body model must also pin the spin-axis reference frame, spin-axis vector, and rotational phase at T0 if rotation affects collision or occultation. Otherwise the ellipsoid must explicitly be declared fixed in the simulation frame.

Geometry is binding: narrative preference cannot override collision, occultation, range, acceleration, or withdrawal constraints.

## T0 force instantiation

Each side uses the same 19-vessel template:

- 1 Judicator
- 3 Aegis
- 1 Palisade
- 2 Sentinel
- 1 Obsidian
- 4 Vanguard
- 6 Peregrine
- 1 Reliant

Both sides begin with the same scenario-local nominal combat-power proxy of `89.7`, readiness `1.0`, supply `1.0`, and no initial damage.

The present fixture freezes fleet centroids, centroid velocities, formation radius, composition, and deterministic vessel IDs. It does **not yet** freeze each vessel's complete T0 state. Before control execution, either:

- every vessel must receive explicit position, velocity, and any required attitude/orientation state; or
- a versioned deterministic formation-instantiation algorithm must derive those per-vessel states from the frozen centroids and template.

Carrier fighters, bombers, repair drones, and other embedded craft remain parent capabilities unless separately enumerated at T0; they cannot become implicit reinforcements.

## Command model

Each side has one commander and six lieutenant roles:

- tactical
- navigation
- EW/sensors
- carrier operations
- engineering/damage control
- logistics/support

The fixture records bounded attributes and descriptive characteristics for every officer. These values are currently **input data, not executable behavior**.

Before the control run, a versioned deterministic command-policy contract must map recorded attributes plus current tactical state into allowed actions, including maneuver, fire control, risk acceptance, repair priorities, withdrawal, surrender, and ceasefire decisions. Prose descriptions remain explanatory only and cannot override computed state.

## Tactical behavior requirements

The recovered or newly approved GUMAS tactical implementation must enforce at minimum:

- physically bounded movement with class acceleration caps;
- planetoid collision and line-of-sight occultation;
- sensor/track state rather than omniscient targeting;
- target-range and line-of-fire checks;
- exclusion of destroyed, surrendered, and otherwise protected units from deliberate targeting;
- explicit vessel damage state: `undamaged → damaged → mission_kill → destroyed`;
- surrender as a separate protected disposition;
- bounded repair that cannot resurrect destroyed vessels or catastrophic systems;
- supply, morale, command cohesion, EW, geometry, range, and surviving strength as combat inputs;
- deterministic seeded allocation/noise;
- no reinforcements, external rescue, narrator intervention, or third-party mediation.

## Resolution modes

The battle may terminate through any state-valid result, including:

1. mutual ceasefire / stand-down;
2. withdrawal beyond the battle boundary when effective interception cannot be sustained;
3. surrender;
4. mutual disengagement with effective fire ceased and separation increasing;
5. combat incapacity;
6. hard-time-limit stalemate/disengagement;
7. annihilation, if the deterministic state actually reaches it.

Annihilation is neither required nor rewarded. A hard time limit never manufactures a victor.

## Output contract

A completed control run records:

- engine version and exact source digest;
- tactical version and exact source digest;
- adapter version and exact source digest;
- baseline ID and SHA-256;
- seed;
- initial material-equivalence check;
- T0 per-vessel states;
- ordered GUMAS causal event/state-change log;
- raw audit log, including non-causal audit timestamps if emitted;
- deterministic normalized projection excluding non-causal fields;
- per-vessel final state;
- remaining combat power by side;
- losses by class;
- elapsed simulated time;
- termination mode;
- victor only when the termination rule establishes one;
- unresolved objectives;
- normalized final-state SHA-256;
- `historical_canon_status: non_canon_simulation_instance`.

## Validation gate

Before the fixture becomes an executable control, all of the following must pass:

- verified GUMAS core seed reproducibility remains green;
- tactical executable source is recovered and identified, or an owner-approved new GUMAS version exists;
- scenario adapter binds to GUMAS without parallel-engine fallback;
- all engine/tactical/adapter/baseline source digests are pinned;
- per-vessel T0 state is explicit or deterministically derived;
- planetoid rotational state/reference frame is complete;
- command attributes are mapped through a deterministic versioned policy;
- same complete run identity reproduces normalized events and final-state checksum twice;
- changed seed changes stochastic allocations without changing frozen T0 material conditions;
- mirrored fleets are materially equal at T0;
- occultation blocks illegal fire;
- acceleration and withdrawal bounds are enforced;
- protected units are not targeted;
- no reinforcement appears after T0;
- ceasefire, withdrawal, surrender, disengagement, incapacity, and annihilation are reachable through valid state transitions rather than hard-coded outcomes;
- no result is hard-coded to faction, commander, or narrative intent.

## Source lineage

Verified implementation authorities:

- CanonRec `L2_GUMAS_ENGINE__API_REFERENCE__v1.0.md` — public core `GUMASEngine` / `GUMASState` contract.
- CanonRec `ORION__L2_GUMAS_ENGINE__SOURCE_BUNDLE__v1.1__NAMING_INTEGRATED__2026-02-09.md` — embedded verified core source lineage.
- supplied `GUMAS_SIM_2.5.zip` — directly inspected archive; contains only the four executable core Python modules listed above plus documentation/validation material.
- CloudBank `modules/gumas/naming.py` — deterministic scenario-local naming implementation.

Canon authorities:

- CanonRec individual CANON ship-class records for Judicator, Aegis, Palisade, Sentinel, Obsidian, Vanguard, Peregrine, and Reliant.
- CanonRec `L2_NAMING_ADMISSION_POLICY__v1.0__2026-07-22.md` for name promotion boundaries.
- the older aggregate `L2_GUMAS_SHIP_REGISTRY__v1.0.md` is retained as historical provenance where individual CANON records now govern.

Documented-but-unverified tactical evidence:

- `GUMAS_ENGINE_ARCHITECTURE_SUMMARY.md`
- `COMPREHENSIVE_ENGINE_AUDIT.md`
- associated validation/checklist material describing the larger v2 tactical architecture

Those documents support the existence of a **design/claim set**. Without the corresponding executable files, they do not establish an operational `CombatResolver`.

## Recovery disposition

The source-lineage pass found no recoverable executable tactical module in the currently accessible project surfaces. The appropriate disposition is therefore:

**Preserve the verified GUMAS core. Preserve the documented tactical requirements. Quarantine claims of an already-operational v2 combat engine until source is recovered. Do not invent a replacement silently. Keep PR #1506 draft and the battle control run blocked.**
