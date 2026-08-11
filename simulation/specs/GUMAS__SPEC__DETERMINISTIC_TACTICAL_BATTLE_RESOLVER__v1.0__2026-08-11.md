# GUMAS Deterministic Tactical Battle Resolver v1.0

**Resolver ID:** `GUMAS_TACTICAL_BATTLE_RESOLVER_v1`  
**Layer:** L2  
**Anchor:** `EOS_SEED_ORION`  
**Ethics:** `Picard_Delta_3`  
**Status:** additive simulation specification; no historical canon promotion

## Purpose

Provide a repeatable tactical engagement resolver for bounded fleet actions when the full galaxy-scale GUMAS engine is unnecessary or unavailable. The resolver is deliberately narrow: initial combatants, physical geometry, finite maneuver, deterministic command decisions, combat damage, and realistic termination.

This specification is an additive tactical harness. It does not replace THREADCORE, CanonRec, the GUMAS political simulation, or the missing `modules/gumas/engine.py` currently referenced by the retained CanonRec source bundle.

## Canon boundary

A committed baseline is authoritative as a reusable **test fixture**. Scenario-local officers, vessel IDs, and run outcomes remain simulation-instance data unless explicitly reconciled and promoted through CanonRec. New scenario-local names generated under `GUMAS_NAMING_PROTOCOL_v0.1` must be rechecked against a current CanonRec registry before any canon admission.

## Determinism contract

1. A run is identified by `(resolver_version, baseline_sha256, seed_u64)`.
2. All stochastic-looking variation uses one explicit `random.Random(seed_u64)` stream or labeled child streams derived with SHA-256.
3. Entity iteration order is stable and lexicographic by ID.
4. Python's process-randomized `hash()` is forbidden.
5. Wall-clock time, network state, external APIs, and unrecorded human choices are forbidden during resolution.
6. Every state mutation emits an ordered event record.
7. Normalized output is canonical JSON with sorted keys and a SHA-256 checksum.
8. Same inputs must produce the same normalized event sequence and final state.

## Physical model

The battle volume is centered on a rotating irregular planetoid represented for collision and occultation by a triaxial ellipsoid. Gravity is a point-mass approximation using the body's configured mass.

- Translation is Newtonian.
- Numerical step: baseline-defined fixed step; default 10 s.
- Ships have class-specific acceleration caps.
- No instantaneous relocation is allowed.
- FTL is disabled inside the configured battle volume by scenario rule.
- Collision with the ellipsoid is terminal unless the scenario explicitly defines controlled landing.
- Line-of-sight is blocked when the segment between observer and target intersects the ellipsoid.
- A force exits combat by crossing the configured withdrawal boundary with a viable command chain.
- The planetoid's gravity, occlusion, and collision surface are physical constraints; dramatic needs never override them.

The present CanonRec ship-class records define roles and qualitative capabilities, not hard accelerations, shield capacities, or weapon ranges. Therefore numerical class coefficients in a baseline are explicitly **scenario-local proxies**, not new canonical ship specifications.

## Force instantiation

A fleet baseline specifies class counts. The resolver instantiates stable vessel IDs in class order, then lexicographic ID order. Both sides may share the same template to guarantee equal material strength.

Carrier fighters, bombers, repair drones, and embedded craft are treated as capabilities of their parent carrier unless separately enumerated in the baseline. This prevents accidental reinforcement through unbounded small-craft spawning.

## Command model

Each side has one commander and six lieutenant roles:

- tactical
- navigation
- EW/sensors
- carrier operations
- engineering/damage control
- logistics/support

Commanders carry bounded attributes in `[0,1]` describing skill and decision style. Lieutenants carry domain skill, initiative, discipline, stress tolerance, risk tolerance, and commander alignment.

Nominal competence can be normalized across sides while distributions remain different. This lets equal fleets diverge through command style without quietly giving one side a larger hidden capability budget.

Decision scoring must be derived from recorded attributes and current state. No prose-only override may change a decision after scoring.

## Detection and geometry

Detection state depends on:

- sensor range
- target signature/stealth proxy
- planetoid occultation
- EW/sensor lieutenant performance
- current formation dispersion
- prior confirmed tracks

Loss of line-of-sight may degrade a track but does not erase previously observed motion instantaneously. The resolver may keep bounded track uncertainty.

## Combat resolution

Combat is resolved in deterministic engagement windows. A firing opportunity requires:

1. target is not destroyed or surrendered;
2. target is inside the firing unit's effective range proxy;
3. a valid track exists;
4. line-of-fire is not blocked by the planetoid;
5. the firing unit is not mission-killed.

Effectiveness combines:

- surviving class combat power
- range factor
- geometry/occlusion factor
- tactical lieutenant skill
- commander coordination
- EW information advantage
- damage and morale penalties
- seeded allocation/noise from the recorded RNG stream

Damage applies to shields first and hull second. Hull damage reduces combat power and mobility. Damage states are:

`undamaged → damaged → mission_kill → destroyed`

A surrendered vessel is removed from target selection immediately.

Reliant support and carrier repair drones may restore limited recoverable damage during lulls, bounded by their configured repair factor. They may not restore destroyed vessels or erase catastrophic system loss.

## Morale, withdrawal, ceasefire, and surrender

Battles are not extermination contests by default.

After each engagement window, each commander evaluates:

- remaining combat power fraction
- flagship status
- mobility/escape corridor
- recent casualty/damage rate
- command cohesion
- casualty aversion
- aggression
- negotiation openness
- objective status

Legal termination modes:

1. **Ceasefire / stand-down** — both commanders accept.
2. **Withdrawal** — one force crosses the withdrawal boundary and pursuit cannot maintain effective interception.
3. **Surrender** — continued resistance is irrational and escape is unavailable.
4. **Mutual disengagement** — no effective fire for the configured interval while separation increases.
5. **Combat incapacity** — one side has no combat-capable vessels.
6. **Hard time limit** — unresolved engagement terminates as an operational disengagement/stalemate, not an invented victory.

Annihilation remains possible if tactical circumstances genuinely produce it, but there is no bonus for fighting to the last ship.

## Flash-rebellion constraints

For the baseline flash rebellion:

- both formations originate from the Galactic Union;
- neither side receives reinforcements;
- no third party intervenes;
- no narrator injects a rescue, mediator, or new objective;
- authenticated communication between the two commands may be used for demands, surrender, or ceasefire;
- disabled or surrendered vessels are protected from further deliberate fire.

## Output contract

A completed run should export:

- baseline ID and SHA-256
- resolver version
- seed
- initial force totals
- ordered event log
- per-vessel final state
- side-level remaining combat power
- losses by class
- elapsed simulated time
- termination mode
- victor, if any
- unresolved objectives
- final-state SHA-256
- explicit `historical_canon_status: non_canon_simulation_instance`

## Required validation before promotion to a general tactical tool

- same seed + same baseline produces identical event log and checksum;
- changed seed changes stochastic allocations without changing initial conditions;
- mirrored equal fleets remain materially equal at T0;
- planetoid occultation blocks illegal fire;
- acceleration and withdrawal bounds are enforced;
- disabled/surrendered ships are not targeted;
- no reinforcement enters after T0;
- ceasefire, withdrawal, surrender, mutual disengagement, and annihilation are all reachable;
- outcome is not hard-coded to any faction or commander;
- the full GUMAS-engine source drift is tracked separately rather than hidden by this harness.
