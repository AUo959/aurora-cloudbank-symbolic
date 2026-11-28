# GUMAS Deterministic Damage and Physical Disposition Specification v1.0

**Date:** 2026-08-13  
**Layer:** L2 tactical simulation  
**Status:** normative Phase-7 contract; no morale/termination/reporting authority  
**Task:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**PR:** `#1506`

## Purpose

Define the deterministic transition from accepted Phase-6 attack-effect descriptors into shield depletion, armor loss, hull loss, subsystem/readiness degradation, damage state, and **physical** combat disposition.

Phase 7 is a damage-state transformer. It may determine whether a vessel is physically combat-capable, degraded, disabled, or destroyed. It may not decide morale, surrender, ceasefire, withdrawal success, battle termination, or narrative interpretation.

## Controlling inputs

A valid Phase-7 step requires:

1. accepted Phase-6 source bundle SHA-256 `05e65b2ee5744809f22eeb1dd6cf5cbf637690d1fa16c177c3bbeedca74427e7`;
2. accepted current physical state with valid state SHA-256;
3. accepted Phase-6 receipt and `fire_control_state_sha256`;
4. unique immutable Phase-6 effect descriptors;
5. existing calibrated maximum/current shield, armor, and hull milliunits;
6. existing readiness and direct support/endurance capability state;
7. versioned Phase-7 coefficients and source identity once implemented.

Phase 7 creates no incoming effect on its own. If Phase 6 emits no effect descriptors, Phase 7 must preserve damage state exactly apart from its own receipt metadata.

## Provenance boundary

Shield, armor, and hull **capacities** already derive from CanonRec tactical capability through the accepted Phase-3 calibration. Phase 7 therefore treats those capacities as authoritative material inputs.

Phase-7 absorption, shock, and disposition coefficients are `SCENARIO_LOCAL` control mechanics. Their appearance in a simulation does not promote them to canon.

No class name, polity name, role prose, weapon prose, or officer prose may alter a damage equation.

## Authoritative numeric representation

All authoritative arithmetic uses integers/fixed point:

- incoming effect: integer milliunits;
- shield/armor/hull current and maximum: integer milliunits;
- fractions/readiness/capabilities: integer q1000;
- canonical serialization: `aurora-canonical-json-v1`;
- rounding: deterministic round-half-even using the already accepted integer helper.

Ambient/global randomness and platform-dependent floating branches are forbidden.

## Application ordering

For each Phase-7 macrostep:

1. validate physical state and Phase-6 receipt identities;
2. validate every effect descriptor and reject duplicate `effect_id` values;
3. group effects by `target_ship_id`;
4. sort source effect descriptors lexicographically by `effect_id` for receipts only;
5. compute aggregate incoming effect per target as the exact integer sum;
6. apply the aggregate simultaneously through shield → armor → hull;
7. compute aggregate hull-shock readiness degradation from actual new hull loss;
8. recompute damage state and physical disposition;
9. preserve morale/cohesion unchanged;
10. commit vessel states in complete `ship_id` lexicographic order;
11. hash damage state and Phase-7 receipt.

Because layer absorption uses the aggregate per target, input effect-list insertion order cannot change the physical result.

## Layer model

### Shield

Shield absorption is one-for-one in common milliunits:

`shield_absorbed = min(incoming_effect, shield_current)`

`shield_next = shield_current - shield_absorbed`

`residual_after_shield = incoming_effect - shield_absorbed`

There is **no implicit shield regeneration in Phase 7 v1.0**. Current CanonRec-derived defensive technology already affects capacity. Time-dependent regeneration requires its own future normalized canonical/scenario contract rather than being invented inside damage application.

### Armor

Armor is ablative and has a fixed scenario-local absorption efficiency:

`ARMOR_ABSORPTION_EFFICIENCY_Q1000 = 850`

Effective absorbable energy from current armor is:

`armor_effect_capacity = round_half_even(armor_current * 850 / 1000)`

`armor_absorbed = min(residual_after_shield, armor_effect_capacity)`

Armor integrity consumed to absorb that effect is:

`armor_integrity_loss = min(armor_current, ceil(armor_absorbed * 1000 / 850))`

The authoritative implementation must provide an integer ceiling helper; binary floating arithmetic is forbidden.

`armor_next = armor_current - armor_integrity_loss`

`residual_after_armor = residual_after_shield - armor_absorbed`

Armor cannot produce energy or absorb more than the incoming residual.

### Hull

Hull damage is one-for-one in common milliunits:

`hull_loss = min(residual_after_armor, hull_current)`

`hull_next = hull_current - hull_loss`

`overkill = residual_after_armor - hull_loss`

Overkill is recorded but may not create negative hull or spill into another vessel.

## Damage fractions

For each material layer:

`fraction_q1000 = round_half_even(current * 1000 / maximum)`

Clamp to `[0,1000]`.

New hull-loss fraction for the current macrostep:

`new_hull_loss_q1000 = round_half_even(hull_loss * 1000 / hull_maximum)`

## Subsystem/readiness shock

Only **new hull loss** can directly degrade internal subsystem readiness in Phase 7 v1.0. Shield or armor-only damage does not silently reduce internal systems.

Damage-control readiness mitigates but cannot eliminate shock:

`damage_control_mitigation_q1000 = round_half_even(prior_damage_control_readiness * 250 / 1000)`

`unmitigated_shock_q1000 = new_hull_loss_q1000`

`effective_shock_q1000 = round_half_even(unmitigated_shock_q1000 * (1000 - damage_control_mitigation_q1000) / 1000)`

Subsystem loss weights are scenario-local and class-neutral:

- propulsion: `900/1000` of effective shock;
- weapons: `900/1000`;
- sensors: `700/1000`;
- EW: `700/1000`;
- damage control: `800/1000`;
- overall: `600/1000`.

For each field:

`readiness_loss = round_half_even(effective_shock_q1000 * field_weight / 1000)`

`readiness_next = max(0, prior_readiness - readiness_loss)`

All reductions are calculated from the **pre-Phase-7 readiness snapshot** and applied simultaneously, so effect order cannot feed back through damage control inside the same macrostep.

Support/endurance already contribute to accepted material capacities. They are not applied a second time here.

## Damage-state classification

Damage state describes physical damage only.

- `undamaged`: shield, armor, and hull all at maximum;
- `shield_damaged`: shield below maximum; armor and hull at maximum;
- `armor_damaged`: armor below maximum; hull at maximum;
- `hull_damaged`: hull fraction > 600 q1000;
- `major_damage`: hull fraction > 300 and <= 600;
- `critical_damage`: hull fraction > 0 and <= 300;
- `destroyed`: hull fraction == 0.

The most severe applicable state wins.

## Physical disposition classification

Disposition in Phase 7 describes physical ability, not willingness.

- `destroyed` if hull current == 0;
- `disabled` if any of:
  - hull fraction <= 150;
  - overall readiness < 150;
  - both propulsion and weapons readiness < 150;
- `degraded` if any of:
  - hull fraction < 600;
  - propulsion readiness < 500;
  - weapons readiness < 500;
  - sensors readiness < 500;
  - EW readiness < 500;
  - damage-control readiness < 500;
- otherwise `combat_capable`.

A disabled vessel is not destroyed. Later phases may permit rescue, recovery, surrender, or drift according to separate rules.

Morale and cohesion are unchanged by Phase 7; Phase 8 may react to committed physical damage afterward.

## Effect validation

Each Phase-6 effect descriptor must contain:

- `effect_id`;
- `attempt_id`;
- `source_ship_id`;
- `target_ship_id`;
- positive integer `delivered_effect_milliunits`;
- integer `impact_quality_q1000` in `[0,1000]`;
- `source_state_sha256`.

The target must exist in the current state. Source may already have changed disposition after Phase 6; this does not retroactively erase an already committed simultaneous effect.

An effect targeting a vessel already `destroyed` at the **start** of the Phase-7 step is rejected fail-closed as invalid input; Phase 6 should never have created it.

## Damage receipt schema

For every target with one or more incoming effects, emit one aggregate deterministic damage receipt containing at minimum:

- target `ship_id`;
- ordered source `effect_id` list;
- total incoming effect;
- shield before/absorbed/after;
- armor before/effect absorbed/integrity lost/after;
- hull before/lost/after;
- overkill;
- new hull-loss q1000;
- readiness before/delta/after;
- damage state before/after;
- physical disposition before/after;
- morale before/after assertion showing no Phase-7 mutation;
- cohesion before/after assertion showing no Phase-7 mutation;
- receipt SHA-256.

Vessels with no incoming effect remain byte-equivalent in all material/damage/readiness/morale/cohesion fields.

## Phase-7 state

The next state preserves the accepted movement/Phase-6 physical-state schema and adds only provenance/reference fields required to bind the Phase-7 source and receipt.

The next state hash covers updated:

- shield/armor/hull current values;
- readiness;
- damage state;
- physical disposition;
- unchanged morale/cohesion;
- parent state identity;
- Phase-7 source identity;
- damage receipt identity.

## Fail-closed conditions

Phase 7 fails before accepted output when:

- prior state hash is invalid;
- Phase-6 receipt/effect identity is invalid or mismatched;
- duplicate effect IDs exist;
- effect target is absent;
- delivered effect is non-positive/non-integer;
- impact quality is outside q1000 bounds;
- current capacity exceeds maximum or is negative;
- required readiness is missing/out of bounds;
- an incoming effect targets a vessel already destroyed before the step;
- any material layer becomes negative;
- morale or cohesion changes inside Phase 7;
- replay or insertion-order tests diverge.

## Acceptance tests

Phase 7 is not accepted until all of the following pass:

1. same state + same effect set -> identical next-state and damage-receipt hashes;
2. shuffled effect insertion order -> identical normalized output;
3. zero effects -> material/damage/readiness/morale/cohesion state unchanged;
4. shield absorbs before armor;
5. armor absorbs before hull;
6. exact shield-depletion boundary is deterministic;
7. exact armor-depletion boundary is deterministic;
8. hull never becomes negative; overkill is recorded;
9. higher shield capacity cannot increase downstream armor/hull loss under equal effect;
10. higher armor capacity cannot increase hull loss under equal residual effect;
11. no hull penetration -> no subsystem/readiness shock;
12. greater hull loss cannot reduce readiness degradation under otherwise equal conditions;
13. higher prior damage-control readiness cannot increase subsystem degradation;
14. destroyed classification occurs exactly at hull zero;
15. disabled is distinct from destroyed;
16. morale/cohesion remain unchanged;
17. protected/previously destroyed target effects fail closed;
18. real-source pipeline can consume Phase-6 effect descriptors when they eventually exist;
19. the current first-step Run-0 witness with zero Phase-6 effects produces an exact no-damage transition.

## Phase boundary

Passing Phase 7 proves deterministic material damage and physical disposition transitions only.

It does **not** authorize morale, withdrawal, surrender, ceasefire, battle termination, integrated command-observation synthesis, reporting, or Run 0.
