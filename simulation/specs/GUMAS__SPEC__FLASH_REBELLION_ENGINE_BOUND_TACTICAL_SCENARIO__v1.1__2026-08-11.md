# GUMAS Flash-Rebellion Engine-Bound Tactical Scenario v1.1

**Scenario contract ID:** `GUMAS_FLASH_REBELLION_ENGINE_BOUND_v1_1`  
**Layer:** L2  
**Anchor:** `EOS_SEED_ORION`  
**Ethics:** `Picard_Delta_3`  
**Status:** scenario/integration specification; no historical canon promotion

## Purpose

Define a deterministic, physically bounded fleet-engagement fixture that executes under the existing GUMAS simulation authority rather than introducing a second tactical engine.

The authoritative simulation object is `GUMASEngine`. CanonRec retains the primary source bundle for the engine core and its seeded-reproducibility contract. The later GUMAS validation package documents fleet movement, `FLEET_BATTLE`, `CombatResolver`, terrain modifiers, and the expanded lifecycle as the intended tactical extension surface. This fixture binds to those GUMAS interfaces; it must not fall back to an independent resolver if an integration path is unavailable in a particular checkout.

The previous standalone `GUMAS_TACTICAL_BATTLE_RESOLVER_v1` framing is retired by this revision.

## Authority and implementation boundary

1. **Simulation authority:** `GUMASEngine` owns run identity, seed, state lifecycle, event ordering, ethics callback, and audit history.
2. **Core state authority:** `GUMASState` remains the enclosing L2 state model.
3. **Scenario construction:** the flash-rebellion fixture is supplied as explicit scenario state/configuration, not as a competing engine.
4. **Tactical extension:** fleet movement and battle resolution bind to the GUMAS fleet/combat subsystem documented by the validated v2 architecture. If the active checkout does not expose that extension surface, execution is blocked pending integration; no replacement resolver is silently substituted.
5. **Canon authority:** CanonRec remains authoritative for class identities, roles, naming admission, and any later promotion of simulation outcomes.
6. **Runtime observations:** officers, vessel instances, tactical decisions, damage, and outcomes remain non-canon simulation-instance data unless explicitly reconciled and promoted.

## Canon boundary

A committed baseline is authoritative only as a reusable **test fixture**. Scenario-local officers, vessel IDs, numerical coefficients, and run outcomes are not L2 history merely because they are version-controlled.

New scenario-local names generated under `GUMAS_NAMING_PROTOCOL_v0.1` must be rechecked against the current CanonRec naming registry before canon admission.

## Engine binding

The fixture maps onto the existing GUMAS lifecycle as follows:

- `GUMASEngine(seed=...)` establishes the deterministic RNG root.
- `init_scenario(state=...)` receives or adapts the scenario-specific GUMAS state.
- fleet movement is evaluated inside the GUMAS movement phase/extension surface;
- fleet engagements are evaluated through the GUMAS combat subsystem rather than prose-side arbitration;
- significant mutations remain ethics-checkable through the existing `ethics_callback`/Picard_Delta_3 path;
- ordered state changes and events remain part of the GUMAS audit trail;
- final tactical output is attached to the run receipt/state export without promoting the result into CanonRec.

The fixture may require an adapter between the present core `GUMASState` dataclasses and the later fleet/combat state model. That adapter is integration plumbing, not a new simulation authority.

## Determinism contract

A run identity is:

`(engine_version, tactical_extension_version, scenario_adapter_version, baseline_sha256, seed_u64)`

Requirements:

1. The GUMAS seed is the root of all stochastic-looking behavior.
2. Child RNG streams, if required by the tactical extension, are derived deterministically from labeled SHA-256 material.
3. Entity iteration order is stable and explicit.
4. Python process-randomized `hash()` is forbidden for simulation decisions.
5. Wall-clock time, network state, external APIs, and unrecorded human choices cannot affect resolution.
6. Every material mutation emits an ordered event/state-change record.
7. Normalized output uses canonical JSON with sorted keys and SHA-256 checksums.
8. Two executions with identical run identity must produce equivalent normalized event sequences and final-state checksums.

## Physical model

The battle volume is centered on a rotating irregular planetoid represented for collision and occultation by a triaxial ellipsoid. Gravity is a point-mass approximation using the configured mass.

- Translation is Newtonian within the tactical extension.
- Fixed numerical step is baseline-defined; default 10 s.
- Ships obey class-specific acceleration caps.
- No instantaneous relocation is permitted.
- FTL is disabled inside the configured battle volume by scenario rule.
- Ellipsoid collision is terminal unless a controlled-landing rule is explicitly defined.
- Line-of-sight is blocked when the observer-target segment intersects the ellipsoid.
- Withdrawal requires physically crossing the configured boundary with a viable command chain.
- Geometry is binding; narrative preference cannot override collision, occlusion, range, or maneuver constraints.

CanonRec ship-class records define qualitative class identity and role. The numerical acceleration, shield, hull, sensor, stealth, range, and combat coefficients in the fixture remain **scenario-local proxies**, not new canonical ship specifications.

## Force instantiation

The fixture instantiates two materially identical 19-vessel Galactic Union task forces from one shared template:

- 1 Judicator
- 3 Aegis
- 1 Palisade
- 2 Sentinel
- 1 Obsidian
- 4 Vanguard
- 6 Peregrine
- 1 Reliant

Stable vessel IDs are generated deterministically. Carrier fighters, bombers, repair drones, and embedded craft remain parent capabilities unless separately enumerated at T0; they cannot become implicit reinforcements.

## Command model

Each side has one commander and six lieutenant roles:

- tactical
- navigation
- EW/sensors
- carrier operations
- engineering/damage control
- logistics/support

Commanders and lieutenants use recorded bounded attributes. Both sides have normalized nominal competence but different attribute distributions, allowing asymmetric decisions without an asymmetric hidden capability budget.

Decision effects must be derived from recorded attributes plus current engine state. Prose descriptions are explanatory only and cannot override computed state.

## Detection and geometry

Track quality may depend on:

- sensor range;
- target signature/stealth proxy;
- planetoid occultation;
- EW/sensor performance;
- formation dispersion;
- previously confirmed tracks.

Loss of present line-of-sight may increase uncertainty but does not instantly erase previously observed motion.

## Combat extension requirements

A valid firing opportunity requires all of the following:

1. target is not destroyed, surrendered, or otherwise protected from deliberate fire;
2. target is within the effective-range proxy;
3. a valid track exists;
4. line-of-fire is not blocked by the planetoid;
5. firing unit remains combat-capable.

The GUMAS combat extension should combine surviving fleet strength, range, geometry, tactical leadership, commander coordination, EW information advantage, supply/morale state, damage, and seeded allocation/noise.

Damage proceeds through explicit vessel state. The fixture uses:

`undamaged → damaged → mission_kill → destroyed`

Surrender is a separate protected state. Reliant support and carrier repair capabilities may recover only bounded recoverable damage; destroyed ships or catastrophic system losses cannot be restored.

## Morale and termination

After each engagement window the command model considers remaining combat power, flagship status, mobility, recent loss rate, command cohesion, casualty aversion, aggression, negotiation openness, and objective status.

Permitted termination modes:

1. **Ceasefire / stand-down** — mutually accepted by the two combatant commands.
2. **Withdrawal** — a force crosses the boundary and pursuit cannot sustain effective interception.
3. **Surrender** — continued resistance is irrational and escape is unavailable.
4. **Mutual disengagement** — effective fire ceases for the configured interval while separation increases.
5. **Combat incapacity** — one side has no combat-capable vessels.
6. **Hard time limit** — unresolved combat ends as disengagement/stalemate, never as an invented victory.

Annihilation is possible but is neither required nor rewarded.

## Flash-rebellion constraints

- both formations originate from the Galactic Union;
- combatants are frozen at T0;
- no reinforcements enter;
- no third party intervenes;
- no narrator injects rescue, mediation, or a replacement objective;
- authenticated combatant communication may carry demands, surrender, or ceasefire proposals;
- disabled or surrendered vessels are protected from further deliberate fire.

## Output contract

A completed run records:

- GUMAS engine version / source lineage;
- tactical extension and adapter versions;
- baseline ID and SHA-256;
- seed;
- initial material-equivalence check;
- ordered GUMAS event/state-change log;
- per-vessel final state;
- remaining combat power by side;
- losses by class;
- elapsed simulated time;
- termination mode;
- victor, if one exists under the termination rule;
- unresolved objectives;
- normalized final-state SHA-256;
- `historical_canon_status: non_canon_simulation_instance`.

## Validation gate

Before this fixture is promoted from configuration to an executable tactical control, all of the following must pass:

- existing GUMAS core seed reproducibility remains green;
- the tactical adapter binds to GUMAS rather than creating a parallel engine;
- same seed + same baseline produces identical normalized event/state output and checksum in two independent executions;
- changed seed changes stochastic allocations without changing T0 material conditions;
- mirrored fleets are materially equal at T0;
- planetoid occultation blocks illegal fire;
- acceleration and withdrawal bounds are enforced;
- protected ships are not targeted;
- no reinforcement appears after T0;
- ceasefire, withdrawal, surrender, mutual disengagement, incapacity, and annihilation are reachable from valid state;
- outcome is not hard-coded to faction, commander, or narrative intent.

## Source lineage

Primary repository authorities:

- CanonRec `L2_GUMAS_ENGINE__API_REFERENCE__v1.0.md` — public `GUMASEngine`/`GUMASState` contract.
- CanonRec `ORION__L2_GUMAS_ENGINE__SOURCE_BUNDLE__v1.1__NAMING_INTEGRATED__2026-02-09.md` — embedded engine source and seeded execution lineage.
- CanonRec `L2_GUMAS_SHIP_REGISTRY__v1.0.md` and ship-class records — class identity/role authority.
- CloudBank `modules/gumas/naming.py` — deterministic scenario-local naming implementation.

The later validated GUMAS architecture package is implementation evidence for the fleet/combat extension surface. Where that package and an active checkout differ, the difference is an integration/versioning question; it is not evidence that GUMAS itself is absent.
