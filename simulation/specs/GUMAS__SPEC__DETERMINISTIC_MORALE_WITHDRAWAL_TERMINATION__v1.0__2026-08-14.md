# GUMAS Deterministic Morale, Withdrawal, Surrender, Ceasefire, and Termination Specification v1.0

**Contract ID:** `GUMAS_MORALE_TERMINATION_v1_0`  
**Layer:** L2 tactical simulation  
**Phase:** 8  
**Date:** 2026-08-14  
**Status:** normative pre-implementation specification  
**DTER:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.7__2026-08-14.md`  
**PR:** `#1506`

## 1. Purpose

Convert already-committed physical consequences and command intent into deterministic morale/cohesion changes, withdrawal/control status, surrender, ceasefire, mutual disengagement, combat incapacity, and battle termination.

Phase 8 makes battles capable of ending for realistic reasons other than annihilation. It does not privilege peace and it does not force survival. A force may surrender, withdraw, disengage, become incapable, reach stalemate, or be annihilated according to state.

Phase 8 is a state transformer and termination classifier. It is not a movement engine, sensor model, weapon resolver, damage resolver, command-observation generator, or reporter.

## 2. Controlling inputs

A valid Phase-8 step requires:

1. an accepted Phase-7 state with valid deterministic state SHA-256;
2. the accepted Phase-7 step receipt that binds that state;
3. exactly one verified current command-policy receipt for every active fleet;
4. accepted movement geometry already embedded in vessel positions;
5. the frozen P17 withdrawal boundary `20,000 km`;
6. the frozen hard run duration `21,600 s`;
7. prior Phase-8 control memory if one exists in state;
8. the accepted Phase-4 command policy source identity;
9. versioned Phase-8 constants and source identity once implemented.

Phase 8 creates no new sensor contact, shot, effect descriptor, physical damage, velocity, or position.

## 3. Authority and provenance boundary

Canonical ship/polity differences reach Phase 8 only through accepted numeric state produced upstream: capacities, firepower, readiness, physical disposition, resources, and command-policy decisions.

Phase-8 morale/termination coefficients are `SCENARIO_LOCAL` control mechanics. They are not CanonRec facts and may not be promoted merely because a simulation uses them.

Forbidden authoritative inputs:

- class name;
- polity name;
- vessel role prose;
- commander or lieutenant prose characteristic;
- generated narrative;
- LLM inference;
- wall clock;
- mutable/global RNG.

## 4. Authoritative numeric representation

All authoritative arithmetic uses integers/fixed point.

- morale/cohesion/readiness/fractions/attributes: Q1000 integers `[0,1000]`;
- distance: integer micrometres from accepted movement state;
- elapsed time: integer milliseconds;
- deterministic round-half-even helper from accepted movement geometry;
- canonical JSON profile: `aurora-canonical-json-v1`;
- process-randomized `hash()` forbidden;
- ambient RNG forbidden;
- floating-point branches forbidden.

## 5. Physical disposition versus combat-control status

Phase 7 owns **physical disposition**:

- `combat_capable`
- `degraded`
- `disabled`
- `destroyed`

Phase 8 adds a separate **combat-control status** and never overwrites the physical meaning:

- `engaged`
- `withdrawn`
- `surrendered`
- `disabled`
- `destroyed`

Rules:

1. physical `destroyed` -> control `destroyed`;
2. physical `disabled` -> control `disabled` unless already surrendered;
3. a physically capable/degraded ship outside the withdrawal boundary -> control `withdrawn`;
4. a non-destroyed ship belonging to a surrendered side -> control `surrendered`;
5. otherwise -> control `engaged`.

`withdrawn` and `surrendered` are willingness/control states, not physical damage states.

Phase 9 must enforce target protection from control status without rewriting physical disposition. Accepted Phase-6 code is not modified in Phase 8.

## 6. New-consequence morale/cohesion model

Phase 8 updates morale/cohesion only from **new consequences committed in the current Phase-7 receipt**. Persistent old damage is not charged again every ten seconds.

### 6.1 Per-target new physical shock

For each Phase-7 target damage receipt:

- `new_hull_loss_q1000` = committed Phase-7 hull-loss fraction;
- `overall_readiness_loss_q1000` = absolute value of the committed `overall` readiness delta;
- `new_disposition_shock_q1000` is based only on a transition into a more severe physical state:
  - newly `degraded`: `150`;
  - newly `disabled`: `500`;
  - newly `destroyed`: `1000`;
  - no new severity transition: `0`.

A vessel that was already degraded/disabled is not charged that transition shock again.

### 6.2 Fleet shock

For each fleet:

`fleet_transition_shock_q1000 = round_half_even(sum(new_disposition_shock_q1000) / initial_fleet_vessel_count)`

Clamp `[0,1000]`.

This is intentionally vessel-count normalized but severity weighted. Material class differences already affect how likely each vessel is to reach those physical states.

### 6.3 Commander resilience mitigation

Read commander numeric attributes from the verified command receipt:

- `command_skill`
- `discipline`

`resilience_mitigation_q1000 = round_half_even((command_skill + discipline) * 150 / 1000)`

Equivalent weighted form:

`150*command_skill + 150*discipline`, each normalized by Q1000.

Maximum mitigation is `300`; command skill cannot erase physical consequences.

### 6.4 Morale pressure

For each non-destroyed vessel:

`raw_morale_pressure = 500*own_new_hull_loss + 200*own_overall_readiness_loss + 300*fleet_transition_shock`

Each weighted term is divided by 1000 using deterministic round-half-even.

`effective_morale_loss = round_half_even(raw_morale_pressure * (1000 - resilience_mitigation) / 1000)`

`morale_next = max(0, morale_before - effective_morale_loss)`

### 6.5 Cohesion pressure

`raw_cohesion_pressure = 200*own_new_hull_loss + 200*own_overall_readiness_loss + 600*fleet_transition_shock`

`effective_cohesion_loss = round_half_even(raw_cohesion_pressure * (1000 - resilience_mitigation) / 1000)`

`cohesion_next = max(0, cohesion_before - effective_cohesion_loss)`

No morale/cohesion recovery exists in Phase-8 v1.0. Recovery requires a separately versioned mechanic rather than hidden regeneration.

Zero new Phase-7 physical consequences therefore produce zero morale/cohesion loss.

## 7. Fleet aggregate state

For each fleet, Phase 8 deterministically computes:

- surviving vessel count;
- destroyed count;
- disabled count;
- withdrawn count;
- surrendered count;
- engaged count;
- mean morale Q1000 over non-destroyed vessels;
- mean cohesion Q1000 over non-destroyed vessels;
- current combat-effectiveness Q1000;
- active-vessel fraction Q1000;
- current centroid for engaged/mobile vessels where defined;
- current radial boundary state;
- current strategic posture and navigation intent.

### 7.1 Combat effectiveness

For each vessel not physically destroyed or disabled:

`hull_fraction = round_half_even(hull_current * 1000 / hull_max)`

`effective_firepower = firepower_milliunits * hull_fraction * weapons_readiness / 1_000_000`

Fleet nominal denominator is the sum of `firepower_milliunits` for all fleet vessels currently present in the state, treating that constant calibrated firepower as the 1000/1000 reference.

`combat_effectiveness_q1000 = round_half_even(sum(effective_firepower) * 1000 / sum(nominal_firepower))`

Destroyed/disabled vessels contribute zero effective firepower.

This preserves CanonRec-derived material differences without class-name branching.

## 8. Withdrawal semantics

The accepted movement layer already computes vessel position and the withdrawal boundary radius:

`P17_WITHDRAWAL_RADIUS_UM = 20_000_000_000_000`

A non-destroyed/non-disabled vessel is physically outside when:

`norm(position_um) > P17_WITHDRAWAL_RADIUS_UM`

Such a vessel receives control status `withdrawn` regardless of prose or side identity. Boundary exit is a physical fact.

A fleet achieves **successful withdrawal** when:

1. at least one non-destroyed vessel survives;
2. every surviving mobile vessel (`combat_capable` or `degraded`) is outside the withdrawal boundary;
3. no surviving mobile vessel remains engaged inside the battle volume.

Destroyed/disabled vessels left behind do not prevent a mobile force from withdrawing; they remain losses/stragglers.

If both fleets satisfy successful withdrawal in the same committed state, classify the result as `mutual_disengagement` rather than assign a winner.

Successful withdrawal does not automatically imply a unique victor because the frozen rebel and loyalist objectives can both interpret a rebel exit as partial/full objective satisfaction. Phase 8 therefore sets `victor_side_id = null` for withdrawal; scenario-objective interpretation belongs to later factual reporting.

## 9. Ceasefire handshake semantics

Phase 8 uses the existing Phase-4 strategic posture `CEASEFIRE_PROBE`. It does not create a second negotiation model.

### 9.1 Offer state

When a fleet emits `CEASEFIRE_PROBE`, Phase 8 records/renews a deterministic ceasefire offer valid for:

`CEASEFIRE_OFFER_TTL_STEPS = 3`

The offer expiry is stored as a macrostep index. Expired offers are removed before handshake evaluation.

### 9.2 Acceptance

A mutual ceasefire/stand-down becomes effective when both opposing fleets have non-expired committed ceasefire offers.

This can occur:

- because both choose `CEASEFIRE_PROBE` in the same command epoch; or
- because one previously committed an offer and the other commits `CEASEFIRE_PROBE` before expiry.

Phase 9's `LIVE_COMMAND_OBSERVATION_BRIDGE` must expose an active opposing offer as a deterministic positive `negotiation_signal`; Phase 8 itself does not synthesize the next command observation.

No narrator, external mediator, or LLM can accept a ceasefire.

## 10. Surrender semantics

Surrender is distinct from physical disablement and uses a hard material gate plus a deterministic willingness score.

### 10.1 Hard eligibility gate

A fleet is surrender-eligible only if:

`combat_effectiveness_q1000 <= 350`

and at least one of:

- mean morale `<= 450`;
- active-vessel fraction `<= 350`.

A fleet above this hard gate cannot surrender regardless of commander personality.

### 10.2 Surrender pressure score

From current aggregate state plus commander numeric attributes and the command receipt's already-normalized observation:

- incapacity pressure = `1000 - combat_effectiveness`;
- morale pressure = `1000 - mean_morale`;
- cohesion pressure = `1000 - mean_cohesion`;
- commander casualty aversion;
- commander negotiation openness;
- commander aggression;
- commander discipline;
- mission pressure from the verified command observation.

Score terms:

- incapacity pressure: `+350`;
- morale pressure: `+200`;
- cohesion pressure: `+150`;
- casualty aversion: `+150`;
- negotiation openness: `+100`;
- aggression: `-80`;
- discipline: `-50`;
- mission pressure: `-80`.

Each term is `round_half_even(value_q1000 * weight / 1000)`.

Surrender occurs when the hard gate is true and:

`SURRENDER_THRESHOLD = 500`

If both sides independently surrender in the same committed step, termination class remains `surrender` but `victor_side_id = null`.

Surrendered ships receive control status `surrendered`; physical disposition remains unchanged.

## 11. Mutual disengagement semantics

Phase 8 tracks a deterministic mutual-disengagement streak.

A step qualifies when:

1. both active fleets select strategic posture `DISENGAGE`;
2. neither fleet has terminated via surrender/ceasefire/withdrawal/incapacity/annihilation;
3. current fleet-centroid separation is greater than or equal to the previous qualifying separation.

The first qualifying step initializes streak `1` and stores separation.

A non-qualifying step resets the streak to `0`.

`MUTUAL_DISENGAGEMENT_STREAK_STEPS = 3`

At streak `3`, terminate as `mutual_disengagement` with no unique victor.

## 12. Combat incapacity

A fleet is physically combat-incapable when it has no vessel with physical disposition in:

- `combat_capable`;
- `degraded`.

If exactly one side is combat-incapable and the other retains at least one active combat vessel, terminate as `combat_incapacity` and the active side is the victor.

If both sides are combat-incapable, terminate as `combat_incapacity` with `victor_side_id = null`.

Disabled vessels are survivors, not destroyed vessels.

## 13. Annihilation

A fleet is annihilated when every vessel is physically `destroyed` / hull current zero.

If exactly one fleet is annihilated, terminate as `annihilation` and the surviving side is victor.

If both fleets are annihilated in the same committed state, terminate as `annihilation` with no victor.

Annihilation is checked because it can occur; it receives no positive weighting or preference.

## 14. Hard time limit / stalemate

Accepted movement authority fixes:

`MAX_RUN_DURATION_MS = 21_600_000`

If elapsed simulation time reaches the hard limit and no higher-precedence termination condition has already applied, terminate as `hard_time_stalemate` with no victor.

Phase 8 never extrapolates beyond the accepted state to guess what would happen later.

## 15. Deterministic termination precedence

After morale/control state is updated, evaluate in this exact order:

1. `annihilation`;
2. `surrender`;
3. `mutual_ceasefire`;
4. `successful_withdrawal`;
5. `combat_incapacity`;
6. `mutual_disengagement`;
7. `hard_time_stalemate`;
8. otherwise battle remains active.

Rationale: irreversible physical destruction cannot be undone by a simultaneous later willingness label; explicit surrender/ceasefire precede generic incapacity/disengagement; withdrawal is a physically completed action; the hard clock is last-resort termination.

## 16. Termination receipt

Phase 8 emits a deterministic receipt containing at minimum:

- Phase-8 contract/version/source identity;
- prior state SHA-256;
- Phase-7 receipt SHA-256;
- current command decision SHA-256 by fleet;
- prior and next Phase-8 control-memory hashes;
- per-vessel morale/cohesion before/delta/after;
- per-vessel physical disposition and combat-control status;
- fleet aggregate metrics;
- ceasefire-offer state;
- surrender eligibility and term-level score breakdown;
- mutual-disengagement streak/separation evidence;
- withdrawal boundary evidence;
- termination evaluation trace in precedence order;
- final `terminated` boolean;
- termination class or `null`;
- `victor_side_id` or `null`;
- explicit `movement_applied: false`;
- explicit `damage_applied: false`;
- explicit `rng_used: false`;
- explicit `prose_inputs_used: false`;
- receipt SHA-256.

The next state hash must bind morale/cohesion, combat-control status, control memory, source identity, and termination state.

## 17. Fail-closed conditions

Phase 8 fails before accepted output when:

- Phase-7 state hash is invalid;
- Phase-7 receipt hash/source identity is invalid or does not bind the state;
- command receipts do not exactly cover active fleets;
- command policy source identity is wrong;
- commander numeric attributes/observation are missing or out of Q1000 bounds;
- vessel material/current capacities are invalid;
- a required physical disposition is unknown;
- elapsed time exceeds the hard scenario maximum;
- prior Phase-8 control memory has an invalid hash/schema;
- ceasefire offer expiry is malformed;
- fleet membership is ambiguous;
- any position/morale/cohesion/readiness value is malformed;
- any authoritative branch requires prose, class names, polity names, external input, floating behavior, or RNG.

## 18. Acceptance tests

Phase 8 is not accepted until all of the following pass:

1. same complete inputs -> byte-identical normalized next state and receipt;
2. command-map/vessel insertion order cannot change output;
3. zero new Phase-7 damage -> zero morale/cohesion loss;
4. greater new hull loss cannot improve resulting morale under otherwise equal inputs;
5. greater fleet transition shock cannot improve cohesion under otherwise equal inputs;
6. stronger command-skill/discipline resilience cannot increase morale/cohesion loss;
7. physically disabled is not automatically surrendered;
8. surrender cannot occur outside the hard eligibility gate;
9. eligible surrender crosses threshold deterministically and marks control status without changing physical disposition;
10. high aggression/mission pressure can keep an otherwise damaged force from crossing surrender threshold;
11. a unilateral ceasefire probe does not terminate immediately;
12. reciprocal non-expired ceasefire offers terminate as mutual ceasefire;
13. expired ceasefire offers do not terminate;
14. a vessel outside `20,000 km` is deterministically marked withdrawn;
15. successful fleet withdrawal requires every surviving mobile vessel outside the boundary;
16. simultaneous successful withdrawal by both fleets becomes mutual disengagement/no victor;
17. one-sided combat incapacity yields the active side as victor;
18. mutual combat incapacity yields no victor;
19. one-sided annihilation yields the surviving side as victor;
20. annihilation remains reachable without being forced;
21. three qualifying mutual-disengagement steps terminate; a broken streak resets;
22. hard limit at exactly `21,600,000 ms` terminates as stalemate if nothing else already applies;
23. no movement, sensor, weapon, or physical-damage field changes inside Phase 8;
24. no RNG, floating authority, prose input, class-name branch, or polity-name branch;
25. Run-0 first-step zero-damage state remains active unless committed command/control inputs independently satisfy a valid termination rule;
26. full repository suite remains green.

## 19. Phase boundary

Passing Phase 8 proves deterministic willingness/control-state evolution and battle termination semantics only.

It does **not** authorize the complete battle run yet. Phase 9 must still integrate all accepted subsystems into one authoritative step loop, implement `LIVE_COMMAND_OBSERVATION_BRIDGE`, enforce target protection for Phase-8 control status, and commit the immutable state/event ledger.

Only after orchestration, reporting, Controls A/B/C, and Run-0 admission may a battle result be claimed.
