# GUMAS Deterministic Sensing, EW, Targeting, and Weapons Specification v1.0

**Date:** 2026-08-13  
**Layer:** L2 tactical simulation  
**Status:** normative Phase-6 contract; no damage/termination/reporting authority  
**Task:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**PR:** `#1506`

## Purpose

Define the deterministic bridge from accepted Phase-5 physical state plus accepted command-policy orders into observation, electronic-warfare, target-selection, and weapon-effect descriptors.

Phase 6 must make ship-class and polity substitutions matter through resolved/calibrated numeric capabilities. It may not branch on class names, polity names, prose, or model judgment.

Phase 6 does **not** apply shield, armor, hull, subsystem, morale, cohesion, surrender, ceasefire, or termination changes. Those remain later phases.

## Controlling inputs

A valid Phase-6 step requires:

1. accepted restored GUMAS runtime `2.0.1-restored.2`;
2. pinned CanonRec commit `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
3. accepted CanonRec control manifest SHA-256 `cd8a22b8d8721106ab94f5f881685cbd8f58c95beeb8f2d86853e09fd61bdfdc`;
4. accepted T0 SHA-256 `47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec`;
5. accepted command-policy bundle SHA-256 `8c9ba9d413945404e7648c8f427b660576b0e85887c7639a0944f56b38585b3f`;
6. accepted movement bundle SHA-256 `565ef76f94cef320a4e4e8a0cbf75a301270eeef4326975b4cf41681d46bab57`;
7. accepted physical movement-state input;
8. accepted command receipt for each active fleet;
9. frozen run seed material and deterministic child-random contract when a weapon draw is required.

Any identity change changes run identity.

## Canon/provenance boundary

Current CanonRec contains richer weapon prose for some classes, but the accepted tactical resolver does not yet expose a normalized cross-class weapon-family schema for every valid substitute class.

Therefore Phase 6 v1.0 uses one **effective-salvo abstraction** driven only by already accepted class-agnostic numeric fields:

- `firepower_milliunits`;
- `effective_weapon_range_m`;
- `sensor_range_m`;
- `capability_q1000.sensors`;
- `capability_q1000.electronic_warfare`;
- `capability_q1000.stealth`;
- `capability_q1000.mobility`;
- readiness/resource state.

This does not claim that all canonical vessels literally use the same weapon. It is a scenario-local numerical combat abstraction until CanonRec provides a normalized weapon-family contract across substitute rosters.

Future canonical weapon-family data may extend the resolver without changing the fundamental Phase-6 interface.

## Authoritative numeric representation

Authoritative Phase-6 arithmetic is integer/fixed-point.

- positions: integer micrometres from Phase 5;
- velocities: integer micrometres/second from Phase 5;
- ranges: integer micrometres;
- capability/readiness/quality/probability values: integer q1000;
- weapon effect: integer milliunits;
- deterministic random draw: integer q1000 derived from SHA-256 child material;
- canonical serialization: `aurora-canonical-json-v1`.

Python `hash()`, ambient randomness, wall-clock values, non-finite numbers, and platform-dependent floating branches are forbidden.

## Step ordering

For each Phase-6 macrostep:

1. validate input identities and stable vessel order;
2. build physical truth geometry from Phase-5 state;
3. generate raw sensor contacts;
4. resolve EW attack/protection/deception effects;
5. commit the observation/contact state;
6. evaluate target eligibility from committed contacts plus ROE;
7. select targets deterministically;
8. create weapon attempts for authorized shooters;
9. resolve deterministic shot/intercept exposure;
10. apply shooter resource expenditure only;
11. emit immutable Phase-7 effect descriptors;
12. hash observation state, fire-control state, and Phase-6 receipt.

Damage is not applied during this sequence.

## Sensor-contact model

A contact candidate exists only when:

- source and target are different vessels;
- source and target are not on the same side for Run 0;
- target is within source `sensor_range_m`;
- the Phase-5 P17 occultation function reports clear line of sight.

The simulation may know truth-side identity internally, but the targeting layer may act only on the committed contact classification.

### Range quality

Let:

`range_fraction_q1000 = clamp(round_half_even(distance_um * 1000 / sensor_range_um), 0, 1000)`

`range_quality_q1000 = 250 + round_half_even(750 * (1000 - range_fraction_q1000) / 1000)`

This gives a nonzero track-quality floor at the calibrated sensor boundary while still rewarding proximity.

### Raw contact quality

`raw_contact_q1000 = clamp(round_half_even(
    4 * sensors_q1000
  + 3 * range_quality_q1000
  + 3 * sensor_readiness_q1000
  - 5 * target_stealth_q1000
) / 10, 0, 1000)`

A contact with quality below `150` is not committed as an actionable track.

### Identity quality

Initial-combatant rosters are known before the flash-rebellion engagement, but same-polity identification can still be degraded by EW.

`identity_quality_q1000` begins at `raw_contact_q1000` and is modified separately by deceptive emissions.

Classification thresholds:

- `< 300`: `unknown`;
- `300..599`: `suspected_hostile`;
- `>= 600`: `hostile_confirmed`.

Weapon targeting requires `hostile_confirmed` unless a later versioned ROE explicitly allows otherwise.

## Electronic warfare

EW actions come only from accepted `ew_sensors` specialist intents:

- `PASSIVE_TRACK`;
- `PROTECT_NETWORK`;
- `ACTIVE_JAM`;
- `DECEPTIVE_EMISSIONS`.

Each vessel's EW strength is:

`ew_strength_q1000 = round_half_even(electronic_warfare_q1000 * ew_readiness_q1000 / 1000)`

EW range is scenario-local and equals the vessel's calibrated sensor range in Phase 6 v1.0.

### ACTIVE_JAM

For each visible enemy contact within EW range:

`jam_pressure = round_half_even(attacker_ew_strength * ew_range_quality / 1000)`

Defender protection:

- base: defender EW strength;
- `PROTECT_NETWORK`: protection multiplier `1250/1000`;
- otherwise multiplier `1000/1000`.

`net_jam = max(0, jam_pressure - protected_defender_ew)`

Track quality loses:

`round_half_even(net_jam * 500 / 1000)`.

### DECEPTIVE_EMISSIONS

Uses the same net-EW calculation, but applies primarily to identity:

- identity-quality loss multiplier: `650/1000`;
- track-quality loss multiplier: `150/1000`.

Phase 6 v1.0 does not create phantom vessels. Deception degrades classification of real tracks only.

### PASSIVE_TRACK

Adds no offensive EW pressure. It grants a deterministic self track-quality bonus of `+75 q1000` after EW resolution, capped at 1000.

### PROTECT_NETWORK

Adds no offensive EW pressure and only increases defensive EW protection as defined above.

All simultaneous EW contributions are accumulated by stable attacker `ship_id` order and summed before clamping so dictionary insertion order cannot affect results.

## Target eligibility

A target is eligible only when all are true:

1. target is an initial combatant on the opposing side;
2. target disposition is not `surrendered`, `disabled`, `destroyed`, or another later protected/noncombatant state;
3. committed contact classification is `hostile_confirmed`;
4. committed contact quality meets the tactical fire threshold;
5. target is within the shooter's `effective_weapon_range_m`;
6. P17 does not occult shooter-to-target line of sight at the authoritative phase;
7. shooter readiness/resources permit a firing attempt.

Fire thresholds by tactical intent:

- `HOLD_FIRE`: no target may be selected;
- `CONTROLLED_FIRE`: contact quality >= `650`;
- `MAX_EFFECT_FIRE`: contact quality >= `500`.

ROE remains: military targets only; disabled or surrendered vessels are not valid targets.

## Target selection

Target selection is numeric and class-agnostic.

For each eligible target:

`proximity_q1000 = clamp(1000 - round_half_even(distance_um * 1000 / weapon_range_um), 0, 1000)`

`threat_q1000 = clamp(round_half_even(target_firepower_milliunits * 1000 / 20000), 0, 1000)`

`target_score = 5 * contact_quality_q1000 + 3 * threat_q1000 + 2 * proximity_q1000`

Select highest score. Exact ties resolve to lexicographically smallest complete `ship_id`.

No role-name, class-name, polity-name, narrative, or hidden priority branch is allowed.

## Effective salvo

Phase 6 v1.0 authorizes at most one effective salvo per combat-capable vessel per macrostep.

Tactical intensity:

- `HOLD_FIRE`: 0;
- `CONTROLLED_FIRE`: 650 q1000;
- `MAX_EFFECT_FIRE`: 1000 q1000.

Logistics expenditure multiplier:

- `CONSERVE`: 600;
- `BALANCED_EXPENDITURE`: 800;
- `SURGE_EXPENDITURE`: 1000.

`salvo_intensity = round_half_even(tactical_intensity * logistics_multiplier / 1000)`

Shooter weapon readiness multiplies salvo intensity before effect calculation.

## Hit probability and deterministic child draw

Weapon uncertainty is permitted only through an order-independent labeled child draw.

Child material:

`AURORA::GUMAS::PHASE6::SHOT::{seed_u64_hex}::{macrostep_index}::{shooter_id}::{target_id}::{shot_ordinal}::{phase6_source_sha256}`

Compute SHA-256 over UTF-8 bytes. Interpret the first 8 bytes as unsigned big-endian integer.

`draw_q1000 = floor(u64 * 1000 / 2^64)`

No mutable RNG stream is consumed. Adding an unrelated shot cannot perturb another shot's draw.

### Hit chance

`range_margin_q1000 = proximity_q1000`

`weapon_readiness_q1000 = shooter.readiness_q1000.weapons`

`target_evasion_q1000 = target.capability_q1000.mobility`

If the target fleet's navigation intent is `EVASIVE_VECTOR`, add `150` to target evasion, capped at 1000.

`hit_chance_q1000 = clamp(
    50
  + round_half_even(500 * contact_quality_q1000 / 1000)
  + round_half_even(200 * range_margin_q1000 / 1000)
  + round_half_even(200 * weapon_readiness_q1000 / 1000)
  - round_half_even(250 * target_evasion_q1000 / 1000),
  25,
  975
)`

`hit = draw_q1000 < hit_chance_q1000`

The hit chance must be exposed in the receipt. The draw must be exposed so replay is auditable.

## Effect descriptor

A miss emits an attempt with `delivered_effect_milliunits = 0`.

For a hit:

`base_effect = round_half_even(
    shooter.firepower_milliunits
  * salvo_intensity_q1000
  * weapon_readiness_q1000
  / 1_000_000
)`

`impact_quality_q1000 = clamp(500 + round_half_even((hit_chance_q1000 - draw_q1000) / 2), 250, 1000)`

`delivered_effect_milliunits = round_half_even(base_effect * impact_quality_q1000 / 1000)`

Phase 6 emits this value only. Phase 7 decides how shields, armor, hull, and systems absorb or suffer it.

## Shooter resource expenditure

A firing attempt consumes self resources whether it hits or misses.

For `salvo_intensity_q1000 > 0`:

`ammo_cost_q1000 = max(1, round_half_even(12 * salvo_intensity_q1000 / 1000))`

`energy_cost_q1000 = max(1, round_half_even(8 * salvo_intensity_q1000 / 1000))`

If required resources are unavailable, the attempt is rejected fail-closed with reason `insufficient_resources`.

Resource decrements are part of the authoritative Phase-6 state and are included in its hash.

These costs are `SCENARIO_LOCAL` control calibration, not canon.

## Contact and weapon schemas

Each committed contact contains at minimum:

- observer `ship_id`;
- target truth `ship_id` for audit;
- distance;
- P17 line-of-sight status;
- raw contact quality;
- EW deltas by source;
- final track quality;
- final identity quality;
- classification;
- source physical-state SHA-256.

Each weapon attempt contains at minimum:

- deterministic attempt ID;
- shooter and selected target IDs;
- command decision SHA-256;
- contact receipt SHA-256;
- fire mode and salvo intensity;
- range/proximity;
- hit chance;
- child-draw material SHA-256 and `draw_q1000`;
- hit boolean;
- delivered effect milliunits;
- ammo/energy cost;
- rejection reason if not fired.

## State and receipts

Phase 6 emits:

1. `observation_state` hash;
2. `fire_control_state` hash;
3. updated shooter-resource state hash;
4. ordered weapon-attempt list;
5. ordered Phase-7 effect-descriptor list;
6. complete Phase-6 receipt hash;
7. source-bundle identity binding all executable modules and coefficient tables.

Wall-clock timestamps are excluded from authoritative hashes.

## Fail-closed conditions

Phase 6 stops before accepted output when:

- source state or required source identity is missing/mismatched;
- vessel IDs duplicate;
- required physical/capability/readiness/resource fields are missing/out of range;
- an EW or targeting mode is unknown;
- P17 occultation authority is unavailable;
- a reference uses an uncommitted contact;
- a protected target becomes eligible;
- class/polity-name special-casing is detected;
- child-draw material is incomplete;
- non-integer authoritative values enter the branch logic;
- replay or insertion-order tests diverge.

## Acceptance tests

Phase 6 is not accepted until all of the following pass:

1. same complete inputs -> identical contact, targeting, shot, resource, effect and receipt hashes;
2. vessel/order/map insertion order changes do not alter normalized output;
3. P17 occultation removes contacts and prevents weapon eligibility;
4. reducing target stealth cannot reduce observer contact quality;
5. increasing observer sensor capability/readiness cannot reduce contact quality;
6. increasing hostile EW cannot improve target contact quality;
7. `PROTECT_NETWORK` cannot worsen defensive contact quality under otherwise equal conditions;
8. weapon range gating is exact at and just outside the boundary;
9. `HOLD_FIRE` produces no weapon attempt;
10. protected/disabled/surrendered targets are never eligible;
11. target-score ties use complete `ship_id`;
12. higher calibrated firepower cannot reduce base effect under identical conditions;
13. higher target mobility cannot increase hit probability under identical conditions;
14. the labeled child draw is stable and independent of unrelated attempt insertion;
15. alternate CanonRec class substitution changes Phase-6 behavior only through resolved/calibrated numeric inputs;
16. no damage state changes occur in Phase 6;
17. real 38-vessel pinned-source smoke replays exactly.

## Phase boundary

Passing Phase 6 proves deterministic sensing, EW, target selection, firing attempts, self-resource expenditure, and attack-effect descriptors.

It does **not** authorize damage application, morale/disposition transitions, withdrawal/surrender/ceasefire resolution, battle termination, reporting, or Run 0.
