# GUMAS Deterministic Battle Runtime Implementation Plan v1.0

**Date:** 2026-08-12  
**Layer:** L2 tactical simulation  
**Status:** pre-implementation execution plan  
**Authority:** owner-approved implementation intent; no Run-0 execution authority  
**Related PR:** #1506

## Purpose

Commit the intended implementation sequence before executable restoration or battle-runtime work begins.

The objective is to turn the recovered GUMAS v2.0 tactical lineage plus CanonRec into a deterministic, stepwise, physically bounded battle runtime whose state transitions determine events and whose reporting layer only describes already-committed simulation results.

The Run-0 scenario remains unchanged: equal-strength, medium-sized Galactic Union fleets around an irregular planetoid, flash-rebellion context, initial combatants only, deterministic commander/lieutenant teams, no required annihilation outcome, and realistic withdrawal/surrender/ceasefire/mission-kill termination paths.

## Non-negotiable runtime invariant

**The battle is a state machine first and a report second.**

At every step:

1. authoritative state is read;
2. deterministic decisions and physical/combat effects are resolved;
3. a new immutable state is committed;
4. the new state and emitted events are hashed;
5. only then may the reporting layer narrate what occurred.

The reporting layer must never decide, modify, improvise, or retroactively reconcile combat outcomes.

No LLM/model judgment is permitted inside authoritative state transitions.

## Authority stack

```text
Pinned scenario fixture
        ↓
Pinned CanonRec snapshot
        ↓
Deterministic CanonRec tactical-input resolver
        ↓
Resolved tactical manifest + provenance
        ↓
Scenario/state adapter
        ↓
Restored GUMAS v2.0 aggregate tactical authority
        ↓
Bounded per-vessel physical/combat extension
        ↓
Immutable event/state ledger
        ↓
Deterministic factual battle reporter
```

The CanonRec resolver resolves inputs; it does not resolve combat. The scenario adapter instantiates state; it does not resolve combat. Restored GUMAS plus the bounded physical extension determine what happens.

## Determinism requirements

### 1. Replay determinism

The same complete run identity must produce equivalent normalized state/event output and the same final checksum.

Run identity includes at minimum:

- scenario fixture hash;
- deterministic seed;
- recovered/restored GUMAS source digest;
- bounded-extension source digest;
- CanonRec commit/ref and material source hashes;
- CanonRec resolver source digest;
- resolved tactical-manifest hash;
- command-policy version/digest;
- physics/combat configuration digest;
- timestep/integration configuration;
- deterministic RNG stream layout.

### 2. Canon-resolution determinism

The same CanonRec snapshot and roster must always resolve to the same tactical manifest.

Qualitative-to-numeric translation must be implemented as explicit, versioned deterministic rules. Runtime interpretation such as "this class seems faster" or "this polity is probably more aggressive" is forbidden.

### 3. Causal determinism

A changed canonical class, vessel, organization, or polity must alter the simulation only through explicit resolved properties and policies.

Every consequential resolved value must preserve a traceable chain:

```text
CanonRec fact/source
    ↓
resolved/derived tactical parameter
    ↓
authoritative simulation variable
    ↓
decision or physical/combat consequence
    ↓
emitted event
    ↓
later state
```

If a class/polity substitution changes only labels or narration, the implementation fails acceptance.

### 4. Reporting determinism

The authoritative factual report must be generated from the immutable event ledger, not from free-form inference.

Given the same ledger, the factual report must communicate the same events in the same order. Optional stylistic renderings may exist later but can never replace the authoritative event-derived report.

## State-step lifecycle

Each authoritative tactical step will use a fixed phase order. Phase order itself is versioned and part of run identity.

Proposed v1 step order:

1. load immutable State N;
2. update deterministic environmental/planetoid geometry;
3. resolve sensor visibility, line of sight, occultation, and track quality;
4. evaluate command team state and deterministic command policies;
5. generate legal orders;
6. resolve movement/propulsion integration within class-specific limits;
7. resolve electronic warfare/countermeasures;
8. resolve targeting eligibility and firing decisions;
9. resolve weapon effects, shields, armor, subsystem and disposition damage;
10. resolve boarding/sabotage only when supported by resolved doctrine/capability and legal geometry;
11. update crew/system readiness, morale/cohesion, supply/ammunition/energy where modeled;
12. evaluate withdrawal, surrender, ceasefire, disengagement, mission-kill, and command-collapse conditions;
13. evaluate battle termination;
14. commit State N+1;
15. hash State N+1 and its ordered event batch;
16. emit the factual step report from committed events only.

No phase may observe partially committed results from a later phase. Tie-breaking and iteration order must be explicit and stable.

## Implementation sequence

### Phase 0 — Preserve and pin historical authority

- Keep recovered GUMAS v2.0 archival bytes immutable.
- Preserve both historical witness ZIPs and recovery manifests.
- Pin recovered tree digest and package anchor in restoration metadata.
- Do not patch archival files in place.

**Exit criterion:** restoration source tree can be proven to derive from the verified archival digest.

### Phase 1 — Restore the historical GUMAS combat contract

- Create a separately versioned restored GUMAS v2.0 implementation under a tracked path.
- Resolve the historical three-way combat API disagreement deliberately.
- Construct valid `CombatState` instead of passing `None`.
- Provide compatibility for explicit `FLEET_BATTLE` without inventing an independent combat authority.
- Add focused regression tests for Phase 9 and explicit fleet-battle dispatch.

**Exit criterion:** the aggregate historical combat path executes deterministically under tests and preserves a documented restoration diff from archival source.

### Phase 2 — Implement deterministic CanonRec tactical-input resolution

- Pin a CanonRec snapshot by commit/ref.
- Resolve canonical class/vessel/polity/organization identities.
- Apply scope-safe doctrine inheritance.
- Implement versioned qualitative-to-numeric derivation rules.
- Mark every value as `CANON_DIRECT`, `CANON_SCOPED_DOCTRINE`, `DERIVED_FROM_CANON`, or `SCENARIO_LOCAL`.
- Emit a canonical resolved tactical manifest with source paths/hashes.
- Fail closed when required inputs cannot be resolved.

**Exit criterion:** same CanonRec snapshot + same roster produces byte-equivalent normalized manifest; alternate valid class/polity substitutions traverse the same resolver code path.

### Phase 3 — Define deterministic per-vessel T0 state

For every initial combatant, define or deterministically derive:

- vessel ID;
- class/polity/organization references;
- position vector;
- velocity vector;
- orientation/attitude representation;
- formation slot;
- initial shield/armor/system states;
- fuel/energy/ammunition values where modeled;
- sensor/EW readiness;
- command assignment;
- initial morale/cohesion/readiness;
- damage/disposition state.

Planetoid state must include a complete deterministic physical reference, including spin axis and rotational phase if rotation affects collision or occultation.

**Exit criterion:** fixture + resolver + deterministic T0 constructor yields an identical complete state snapshot on repeat.

### Phase 4 — Implement deterministic command-team policy

- Convert commander and lieutenant attributes into explicit versioned policy functions.
- Define command roles, decision inputs, legal actions, scoring functions, thresholds, and tie-breaking.
- Preserve command friction, initiative, aggression, caution, doctrine adherence, morale effects, and specialist influence only through explicit equations/rules.
- No prose interpretation at runtime.

**Exit criterion:** identical state produces identical orders; controlled officer-attribute changes produce explainable, traceable policy differences.

### Phase 5 — Implement bounded movement and geometry

- Fixed timestep or other explicitly versioned deterministic integrator.
- Class-resolved acceleration/turning/propulsion limits.
- Irregular-planetoid collision geometry.
- Occultation and line-of-sight calculations.
- Bounded engagement volume and withdrawal geometry.
- Stable numerical precision/rounding policy.

**Exit criterion:** movement, collision, occlusion, and withdrawal tests are reproducible across identical runs.

### Phase 6 — Implement sensing, EW, targeting, and weapons

- Deterministic track-quality and sensor-state transitions.
- Canon-derived/scenario-derived EW capabilities.
- Explicit target eligibility and prioritization policies.
- Range/geometry/occlusion restrictions.
- Deterministic RNG streams only where modeled uncertainty is intentional.
- Stable target and event ordering.

**Exit criterion:** same state/seed yields identical detection, targeting, EW, and firing outcomes.

### Phase 7 — Implement shield, damage, system, and disposition transitions

- Shield-energy and reactor interaction where applicable.
- Armor/hull/subsystem damage.
- Mission-kill/disabling states distinct from destruction.
- Boarding/sabotage only when capability, doctrine, geometry, and surviving personnel permit it.
- Damage must feed later maneuver, sensors, weapons, command, and withdrawal state.

**Exit criterion:** damage effects propagate causally into future state rather than existing as isolated score changes.

### Phase 8 — Implement morale, withdrawal, surrender, ceasefire, and termination

- Explicit deterministic decision functions for disengagement and surrender.
- Battles are not forced to annihilation.
- Resolution modes include, at minimum where physically/logically applicable: withdrawal, mutual disengagement, surrender, ceasefire, command collapse, mission kill, capture, destruction, or bounded stalemate/time-limit result.
- No reinforcements or third-party intervention in Run 0.

**Exit criterion:** termination is generated by state and policy, never chosen by reporter or operator after the fact.

### Phase 9 — Implement immutable event/state ledger

Each step writes an ordered event batch containing sufficient machine-readable facts to reconstruct why State N became State N+1.

Each event will include stable identifiers and provenance such as:

- run ID;
- step/tick;
- phase;
- event sequence;
- actor/target IDs where applicable;
- causal input references;
- pre/post values where relevant;
- RNG stream/counter reference when randomness is used;
- authoritative result;
- state/event hash linkage.

**Exit criterion:** normalized ledger can be replay-audited and the final state can be causally traced through ordered events.

### Phase 10 — Implement deterministic factual battle reporter

- Reporter consumes committed events only.
- One report segment per step/tick or configured reporting interval.
- Clearly distinguish observed fact from derived summary.
- Never introduce unlogged maneuvers, dialogue, damage, motives, or outcomes.
- Preserve vessel IDs/names and command attribution.

**Exit criterion:** identical ledger produces equivalent authoritative report output.

### Phase 11 — Determinism and substitution validation

#### Control A — identical replay

Run the exact Run-0 setup twice with identical inputs.

Required result:

- identical resolved manifest;
- identical T0 state;
- identical ordered normalized event ledger;
- identical normalized per-step states;
- identical termination mode/result;
- identical final checksum.

#### Control B — single class substitution

Replace exactly one control ship class with a different valid CanonRec class while keeping all other eligible inputs and the seed fixed.

Required result:

- resolver identifies the exact changed canonical inputs;
- changed capabilities enter real simulation variables;
- consequences are traceable through state/events;
- no engine-code change occurs;
- no requirement that the victor change.

#### Control C — polity/organization substitution

Replace one side with a different valid CanonRec organization/polity and valid roster.

Required result:

- same resolver/adapter/engine path;
- scoped doctrine/technology changes alter only applicable variables/policies;
- no hard-coded faction branch is required;
- full replay determinism remains intact.

### Phase 12 — Admit Run 0

Only after Phases 0-11 pass:

- freeze all run-identity inputs;
- calculate baseline/run hashes;
- execute the initial flash-rebellion battle without intervention;
- emit the complete stepwise factual battle record and final disposition;
- preserve the result as the control receipt for future parameterized reruns.

## RNG design requirements

A single global sequence must not allow unrelated feature additions to perturb all later random outcomes.

Use named deterministic RNG streams or a counter-based equivalent for domains such as:

- sensing;
- EW;
- targeting uncertainty;
- weapons effects;
- damage effects;
- morale/command uncertainty, if any;
- boarding/sabotage, if any.

Stream identity, seed derivation, and counter/order rules are part of run identity.

Adding a new unrelated calculation must not silently reorder existing RNG consumption.

## Numerical determinism requirements

Before Run 0, explicitly pin:

- units;
- timestep;
- integration method;
- coordinate frame;
- floating-point/decimal policy;
- rounding/quantization points;
- ordering of vessels, targets, effects, and events;
- collision tolerance;
- equality/tie thresholds;
- serialization format for hashes.

Canonical JSON or another explicitly specified normalization must be used wherever checksums depend on serialized state.

## CanonRec substitution invariant

The simulator must not contain ship-class- or polity-specific combat branches merely to make substitutions work.

A different valid canonical force changes:

- resolved inputs;
- resulting state capabilities;
- legal actions;
- decision policy inputs;
- physical/combat consequences;

It does **not** require a different battle engine.

Exceptions are allowed only for genuinely unique canonical mechanics and must still enter through explicit capability interfaces rather than hard-coded scenario identity checks.

## Safety / integrity boundaries

- No archival recovered source is modified in place.
- No mass deletion or deduplication action is part of this implementation.
- No narrative output may mutate simulation state.
- No manual outcome correction is permitted inside a deterministic run.
- If an invariant fails, the run fails closed and is not promoted as a baseline.
- Any implementation shortcut that cannot preserve provenance and replay identity must remain outside Run 0.

## Definition of operational capability

The runtime is operational only when the following statement is executable fact:

> Given a pinned CanonRec snapshot, a valid roster, a frozen scenario, a fixed seed, and pinned simulator source/configuration, Aurora can resolve canonical capabilities, instantiate complete physical state, advance the battle one deterministic step at a time, commit an auditable event/state ledger, and report the unfolding battle strictly from those committed events. Repeating the same run reproduces the same authoritative result; substituting a different canonical class or polity changes the battle only through explicit, traceable canonical inputs and deterministic rules.

Until that definition is satisfied, PR #1506 remains pre-Run-0 and no simulated outcome is authoritative.
