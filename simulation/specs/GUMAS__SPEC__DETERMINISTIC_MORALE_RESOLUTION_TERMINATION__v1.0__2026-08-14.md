# GUMAS Deterministic Morale, Resolution, and Termination Specification v1.0

**Date:** 2026-08-14  
**Layer:** L2 tactical simulation  
**Status:** normative Phase-8 contract; no movement/weapons/reporting authority  
**Task:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**PR:** `#1506`

## Purpose

Define the deterministic transition from committed Phase-7 physical consequences plus accepted command-policy decisions into morale/cohesion change, ceasefire/disengagement state, physical withdrawal, surrender, combat incapacity, annihilation, hard-limit stalemate, and battle termination.

Phase 8 exists because realistic battles rarely continue until every ship is destroyed. It must permit a battle to stop for reasons that emerge from the simulated state while remaining fully deterministic and auditable.

Phase 8 is not a second commander and not a narrator. It may make existing command decisions and physical consequences legally consequential. It may not invent motives, rescore tactics, move vessels, create contacts, fire weapons, apply new physical damage, or narrate an outcome.

## Controlling inputs

A valid Phase-8 step requires:

1. accepted Phase-7 state and valid state SHA-256;
2. accepted Phase-7 receipt and source identities;
3. one accepted current Phase-4 command decision receipt for each participating fleet/side;
4. frozen baseline identities and side/fleet mapping;
5. P17-centered position/velocity state already committed by Phase 5;
6. frozen scenario bounds:
   - withdrawal boundary `20,000 km`;
   - hard duration `21,600 s` (`21,600,000 ms`);
   - no reinforcements or third-party intervention;
7. prior Phase-8 resolution state when evaluating persistent ceasefire offers or mutual-disengagement streaks;
8. versioned Phase-8 coefficients and source identity once implemented.

The authoritative integrated loop will later provide each current command receipt through the Phase-9 `LIVE_COMMAND_OBSERVATION_BRIDGE`. Phase-8 subsystem tests may use frozen command observations only as test fixtures; those fixtures are not authoritative Run-0 observations.

## Authority and provenance boundary

Phase 8 may consume:

- physical damage/disposition committed by Phase 7;
- numeric command decisions committed by Phase 4;
- current positions/velocities committed by Phase 5;
- frozen scenario termination bounds.

Phase 8 may not branch on:

- ship class name;
- polity/faction name;
- commander or lieutenant prose;
- narrative interpretation;
- unstated canon assumptions.

All Phase-8 morale, surrender, offer-persistence, withdrawal-threshold, and termination-precedence coefficients are `SCENARIO_LOCAL`. They are control mechanics, not promoted CanonRec facts.

## Numeric representation

All authoritative arithmetic uses integers/fixed point:

- morale/cohesion/readiness/ratios: q1000 integers;
- positions: integer micrometres;
- velocities: integer micrometres per second;
- time: integer milliseconds;
- canonical serialization: `aurora-canonical-json-v1`;
- rounding: deterministic round-half-even with accepted integer helpers;
- norm/boundary checks: exact integer squared-distance comparisons;
- outbound checks: exact integer dot product.

No ambient RNG, binary floating-point authority, wall-clock input, LLM inference, or process-randomized hash may affect Phase 8.

## Phase ordering

For each Phase-8 macrostep:

1. validate Phase-7 state/receipt identities;
2. validate both current Phase-4 command receipts and their policy source identity;
3. validate prior Phase-8 resolution state if present;
4. derive current-step physical shock from Phase-7 target receipts;
5. update vessel morale/cohesion simultaneously from pre-Phase-8 values;
6. derive side aggregate state from updated surviving vessels;
7. update ceasefire-offer state and negotiation signal;
8. update mutual-disengagement streak;
9. evaluate annihilation, ceasefire, stand-down/surrender, incapacity, withdrawal, and hard-limit predicates;
10. apply deterministic termination precedence;
11. emit engagement/protection state without rewriting Phase-7 physical disposition;
12. hash next state, resolution state, and Phase-8 receipt.

No new movement, sensing, firing, or damage occurs inside Phase 8.

# 1. Physical shock and morale/cohesion

## 1.1 Side physical metrics

For each side, derive from Phase-7 target damage receipts:

`fleet_hull_loss_q1000 = round_half_even(sum(new hull loss) * 1000 / sum(max hull of side vessels at Phase-7 start))`

`new_incapacity_q1000 = round_half_even(newly disabled-or-destroyed vessel count * 1000 / side vessel count at Phase-7 start)`

For each vessel:

`local_hull_loss_q1000 = target receipt new_hull_loss_q1000, else 0`

A vessel counts as newly incapacitated only when its Phase-7 physical disposition changes from `combat_capable` or `degraded` to `disabled` or `destroyed` during the current Phase-7 step.

## 1.2 Battle shock

Scenario-local v1.0 fleet shock:

`battle_shock_q1000 = round_half_even((700 * fleet_hull_loss_q1000 + 300 * new_incapacity_q1000) / 1000)`

Clamp to `[0,1000]`.

If both fleet hull loss and new incapacity are zero, battle shock is exactly zero.

## 1.3 Specialist dissent coupling

The accepted command receipt already computes each specialist's deterministic `dissent_q1000`. Phase 8 does not recompute dissent.

`mean_dissent_q1000 = round_half_even(sum(specialist dissent_q1000) / specialist count)`

`shock_coupled_dissent_q1000 = round_half_even(mean_dissent_q1000 * battle_shock_q1000 / 1000)`

Therefore officer disagreement alone cannot erode cohesion during a physically quiet step.

## 1.4 Vessel morale update

Scenario-local v1.0 morale loss:

`morale_loss_q1000 = round_half_even((500 * local_hull_loss_q1000 + 300 * fleet_hull_loss_q1000 + 200 * new_incapacity_q1000) / 1000)`

`morale_next = max(0, morale_prior - morale_loss_q1000)`

Morale never increases in Phase 8 v1.0. Recovery belongs to a future separately versioned mechanic.

## 1.5 Vessel cohesion update

Scenario-local v1.0 cohesion loss:

`cohesion_loss_q1000 = round_half_even((400 * fleet_hull_loss_q1000 + 300 * new_incapacity_q1000 + 300 * shock_coupled_dissent_q1000) / 1000)`

`cohesion_next = max(0, cohesion_prior - cohesion_loss_q1000)`

All vessel morale/cohesion losses are calculated from the same pre-Phase-8 snapshot and applied simultaneously.

Destroyed vessels retain stored morale/cohesion values for provenance but are excluded from later active fleet aggregates.

## Quiet-step invariant

If:

- `fleet_hull_loss_q1000 == 0`; and
- `new_incapacity_q1000 == 0`,

then:

- `battle_shock_q1000 == 0`;
- `morale_loss_q1000 == 0` for every vessel;
- `cohesion_loss_q1000 == 0` for every vessel,

regardless of officer dissent.

This prevents artificial morale drift when nothing adverse actually happens.

# 2. Aggregate side state

For each side after morale/cohesion update:

- `surviving_ship_ids`: physical disposition != `destroyed`;
- `mobile_ship_ids`: disposition in `{combat_capable, degraded}` and propulsion readiness >= 150;
- `combat_effective_ship_ids`: disposition in `{combat_capable, degraded}` and weapons readiness >= 150;
- `disabled_ship_ids`: disposition == `disabled`;
- `destroyed_ship_ids`: disposition == `destroyed`;
- `fleet_morale_q1000`: round-half-even mean morale of surviving ships, or `0` if none;
- `fleet_cohesion_q1000`: round-half-even mean cohesion of surviving ships, or `0` if none;
- `combat_effective_fraction_q1000`: combat-effective count / surviving count, or `0` if none;
- `surviving_hull_fraction_q1000`: sum current hull / sum maximum hull for surviving ships, or `0` if none.

No class or role weighting is allowed in v1.0. A later version may introduce normalized crew/tonnage semantics only through an explicit versioned calibration.

# 3. Ceasefire offers and negotiation signal

## 3.1 Offer creation

Current strategic posture `CEASEFIRE_PROBE` creates or refreshes an offer.

Scenario-local offer lifetime:

`CEASEFIRE_OFFER_TTL_MACROSTEPS = 3`

At macrostep `N`, a newly created offer expires after macrostep `N + 3` unless refreshed.

## 3.2 Offer persistence / rescission

- `CEASEFIRE_PROBE`: create/refresh offer;
- `PRESS`: immediately rescind that side's outstanding offer;
- `HOLD`, `POSITIONAL_MANEUVER`, or `DISENGAGE`: preserve an existing unexpired offer without refreshing it;
- expired offers are removed deterministically.

## 3.3 Negotiation signal

For the next Phase-9 command-observation synthesis:

`negotiation_signal_q1000_by_side[side] = 1000` if the opposing side has an active offer, else `0`.

Phase 8 emits this field; Phase 9 later owns feeding it into the next authoritative command observation.

## 3.4 Mutual ceasefire

A mutual ceasefire exists when both sides have active offers after the current Phase-8 offer update.

Mutual ceasefire is terminal after all current-step Phase-7 damage has already been committed.

Outcome:

- `termination_mode = mutual_ceasefire`;
- no single victor;
- all surviving vessels become protected from deliberate new targeting in later orchestration;
- physical disposition fields remain unchanged.

A unilateral offer alone never terminates battle.

# 4. Mutual disengagement

A single simultaneous `DISENGAGE` selection is not enough to terminate combat by itself. Mutual disengagement requires observable persistence and absence of fresh weapon effect.

Scenario-local rule:

`MUTUAL_DISENGAGE_REQUIRED_STREAK = 2`

The streak increments only when, for the current macrostep:

- both sides' strategic posture is `DISENGAGE`; and
- Phase 7 received zero Phase-6 effect descriptors.

Otherwise the streak resets to zero.

At streak `>= 2`:

- `termination_mode = mutual_disengagement`;
- no single victor;
- all surviving ships are protected;
- physical dispositions remain unchanged.

# 5. Physical withdrawal

## 5.1 Boundary

Frozen P17 withdrawal radius:

`WITHDRAWAL_BOUNDARY_UM = 20,000 km = 20,000,000,000,000 um`

P17 center is the origin of the accepted inertial tactical frame.

For a mobile vessel with integer position `p=(x,y,z)` and velocity `v=(vx,vy,vz)`:

`outside_or_at_boundary = x^2 + y^2 + z^2 >= WITHDRAWAL_BOUNDARY_UM^2`

`outbound = x*vx + y*vy + z*vz > 0`

A vessel is `withdrawn_mobile` only when both predicates are true.

## 5.2 Side withdrawal intent

A side has withdrawal intent only when its current strategic posture is `DISENGAGE`.

Navigation intent `WITHDRAW_VECTOR` is recorded as supporting command evidence but is not an additional success requirement because committed physical boundary/outbound state is authoritative.

Crossing the boundary without `DISENGAGE` does not count as battle withdrawal. `DISENGAGE` without physical exit does not count as successful unilateral withdrawal.

## 5.3 Success threshold

Scenario-local threshold:

`WITHDRAWAL_SUCCESS_FRACTION_Q1000 = 700`

`withdrawn_mobile_fraction_q1000 = withdrawn_mobile_count / mobile_ship_count`

A side successfully withdraws when:

- strategic posture == `DISENGAGE`;
- `mobile_ship_count > 0`;
- `withdrawn_mobile_fraction_q1000 >= 700`.

Disabled/destroyed vessels are excluded from the mobile denominator. Surviving non-mobile vessels left inside the battle volume are listed explicitly as `stranded_or_abandoned_ship_ids`.

## 5.4 Withdrawal outcome

Successful unilateral withdrawal is terminal for this limited-combatant battle.

Record:

- `termination_mode = successful_withdrawal`;
- `withdrawn_side_id`;
- `local_control_side_id = opposing side` if that side still has surviving assets in/near the battle volume;
- `stranded_or_abandoned_ship_ids`;
- `victor_side_id = null` by default.

This no-false-winner rule is intentional. The frozen loyalist objective includes driving rebels from P17, while the rebel objective includes breaking containment and retaining freedom of maneuver. A physical withdrawal can therefore satisfy different factual aspects of both objectives; Phase 8 records what happened rather than imposing an authorial winner label.

# 6. Surrender / stand-down

Surrender is willingness/control state, not physical disposition.

## 6.1 Eligible command posture

A side may surrender only when its current strategic posture is one of:

- `CEASEFIRE_PROBE`;
- `DISENGAGE`.

This prevents Phase 8 from inventing surrender contrary to a command decision.

## 6.2 Commander resolve modifier

Use the already normalized numeric commander attributes embedded in the accepted command receipt:

- `command_skill`;
- `discipline`;
- `casualty_aversion`;
- `negotiation_openness`.

No prose is read.

`commander_resolve_q1000 = round_half_even((command_skill + discipline + (1000 - casualty_aversion) + (1000 - negotiation_openness)) / 4)`

Scenario-local surrender threshold:

`surrender_threshold_q1000 = 500 + round_half_even(commander_resolve_q1000 * 250 / 1000)`

Thus threshold is bounded `[500,750]`. A disciplined, highly skilled, casualty-tolerant, negotiation-closed commander requires greater objective pressure before surrender becomes valid; the opposite profile reaches the threshold sooner. This does not select the strategic posture—the Phase-4 command policy already did that.

## 6.3 Surrender pressure

Read `withdrawal_viability` from the current accepted command receipt's normalized observation.

`withdrawal_failure_q1000 = 1000 - withdrawal_viability`

`combat_deficit_q1000 = 1000 - combat_effective_fraction_q1000`

`hull_deficit_q1000 = 1000 - surviving_hull_fraction_q1000`

`morale_deficit_q1000 = 1000 - fleet_morale_q1000`

`cohesion_deficit_q1000 = 1000 - fleet_cohesion_q1000`

Scenario-local pressure:

`surrender_pressure_q1000 = round_half_even((300*combat_deficit + 250*hull_deficit + 200*morale_deficit + 100*cohesion_deficit + 150*withdrawal_failure) / 1000)`

## 6.4 Surrender predicate

A side meets surrender conditions only if all are true:

- eligible strategic posture;
- at least one surviving vessel;
- opposing side has at least one combat-effective vessel;
- successful withdrawal has not already occurred;
- `combat_effective_fraction_q1000 <= 500`;
- `fleet_morale_q1000 <= 450`;
- `surrender_pressure_q1000 >= surrender_threshold_q1000`.

If both sides independently satisfy the predicate in the same simultaneous Phase-8 step, classify `mutual_stand_down` with no victor rather than creating two contradictory winners.

Unilateral surrender:

- `termination_mode = surrender`;
- surrendered side recorded;
- opposing side is `victor_side_id`;
- every surviving surrendered vessel is protected from deliberate targeting;
- physical disposition remains unchanged.

# 7. Combat incapacity

A side is combat-incapacitated when:

- at least one vessel survives; and
- `combat_effective_ship_ids` is empty.

Unilateral incapacity terminates battle:

- `termination_mode = combat_incapacity`;
- incapacitated side recorded;
- opposing side is victor if it has surviving combat-effective assets.

If both sides are simultaneously incapacitated:

- `termination_mode = mutual_incapacity`;
- no victor;
- all surviving ships protected.

Incapacity is not surrender and does not rewrite vessel physical dispositions.

# 8. Annihilation

A side is annihilated when it has zero surviving vessels.

Because Phase-7 effects are simultaneous, mutual annihilation is valid.

- unilateral annihilation -> opposing surviving side is victor;
- mutual annihilation -> no victor;
- annihilation is reachable but never forced or preferred by the simulation.

# 9. Hard time limit / stalemate

Frozen hard limit:

`HARD_LIMIT_MS = 21,600,000`

The predicate becomes true exactly when:

`elapsed_ms >= HARD_LIMIT_MS`

If no higher-precedence terminal condition applies at that step:

- `termination_mode = hard_limit_stalemate`;
- `stalemate = true`;
- no victor;
- no invented sudden disengagement or surrender.

# 10. Deterministic termination precedence

Evaluate all predicates from the same committed post-morale snapshot, then select exactly one outcome in this precedence order:

1. `mutual_annihilation` / unilateral `annihilation`;
2. `mutual_ceasefire`;
3. `mutual_stand_down`;
4. `mutual_incapacity` / unilateral `combat_incapacity`;
5. unilateral `surrender`;
6. `mutual_disengagement`;
7. `successful_withdrawal`;
8. `hard_limit_stalemate`;
9. otherwise `ongoing`.

When the same-precedence unilateral predicate is true for both sides, use the corresponding mutual class rather than side-ID tie-breaking.

The precedence represents physical finality and negotiated stop-state semantics, not narrative importance.

# 11. Engagement and protected-target state

Phase 8 must not overwrite Phase-7 `disposition`, because that field describes physical capability.

Instead emit top-level control state:

`engagement_status_by_side` values:

- `engaged`;
- `ceasefire`;
- `disengaged`;
- `surrendered`;
- `withdrawn`;
- `incapacitated`;
- `annihilated`.

Also emit sorted `protected_ship_ids`.

Protection rules:

- mutual ceasefire: all surviving ships protected;
- mutual disengagement: all surviving ships protected;
- mutual stand-down: all surviving ships protected;
- unilateral surrender: all surviving surrendered-side ships protected;
- incapacity: surviving incapacitated-side ships protected;
- successful withdrawal: battle is terminal; surviving withdrawn-side ships and stranded disabled ships are recorded separately;
- destroyed ships remain invalid targets by Phase-7/Phase-6 rules.

Phase 9 must enforce this protection state before any future Phase-6 targeting call. If Phase 8 says `terminated=true`, Phase 9 must not run another combat macrostep.

# 12. Phase-8 resolution state

Versioned resolution state must include at minimum:

- schema / contract / version / source identity;
- parent Phase-7 state SHA-256;
- parent Phase-7 receipt SHA-256;
- current command decision SHA-256 by fleet/side;
- macrostep index and elapsed milliseconds;
- side aggregate metrics;
- battle shock by side;
- mean specialist dissent and shock-coupled dissent by side;
- active ceasefire offer + expiry by side;
- negotiation signal q1000 by side;
- mutual-disengagement streak;
- withdrawal geometry receipt by side;
- surrender pressure/threshold receipt by side;
- annihilation/incapacity predicates;
- engagement status by side;
- protected ship IDs;
- terminal outcome object;
- resolution-state SHA-256.

The next physical state may update only:

- vessel `morale_q1000`;
- vessel `cohesion_q1000`;
- Phase-8 provenance/reference fields.

It may not mutate position, velocity, shield, armor, hull, readiness, damage state, or physical disposition.

# 13. Terminal outcome schema

At minimum:

- `terminated: bool`;
- `termination_mode`;
- `victor_side_id: string | null`;
- `local_control_side_id: string | null`;
- `withdrawn_side_ids: []`;
- `surrendered_side_ids: []`;
- `incapacitated_side_ids: []`;
- `annihilated_side_ids: []`;
- `stalemate: bool`;
- `reason_code`;
- numeric/identity evidence references only.

Phase 8 must not write narrative prose into authoritative outcome fields.

# 14. Fail-closed conditions

Phase 8 fails before accepted output when:

- Phase-7 state or receipt hash/identity is invalid;
- current command receipt hash or command-policy source identity is invalid;
- command fleet/side mapping conflicts with the frozen baseline;
- required commander numeric attributes are missing/out of q1000 bounds;
- required strategic posture is unknown;
- prior resolution-state hash is invalid;
- vessel side/fleet identity is ambiguous;
- morale/cohesion is missing or outside q1000 bounds;
- physical state required for withdrawal is missing/non-integer;
- withdrawal boundary differs from frozen `20,000 km`;
- hard limit differs from frozen `21,600 s`;
- a side is declared withdrawn without both disengagement intent and boundary/outbound evidence;
- a side is declared surrendered without the complete deterministic predicate;
- a winner is assigned for mutual ceasefire, mutual disengagement, mutual stand-down, mutual incapacity, mutual annihilation, hard-limit stalemate, or ordinary unilateral withdrawal;
- Phase 8 mutates position/velocity/material/readiness/physical disposition;
- replay or insertion-order tests diverge.

# 15. Acceptance tests

Phase 8 is not accepted until all of the following pass:

1. same Phase-7 state/receipt + same command receipts + same prior resolution state -> identical next-state/resolution/receipt hashes;
2. command-receipt mapping insertion order -> identical normalized output;
3. quiet step with no hull loss/incapacity -> morale/cohesion exactly unchanged;
4. specialist dissent with zero battle shock -> cohesion unchanged;
5. greater local hull loss cannot improve that vessel's morale under otherwise equal conditions;
6. greater fleet hull loss cannot improve side morale/cohesion;
7. more new incapacity cannot improve side morale/cohesion;
8. unilateral `CEASEFIRE_PROBE` -> active offer but no termination;
9. offer persists exactly for configured TTL unless refreshed/rescinded;
10. `PRESS` rescinds own offer;
11. overlapping bilateral offers -> `mutual_ceasefire`, no victor;
12. one `DISENGAGE` step -> no mutual-disengagement termination;
13. two qualifying effect-free bilateral `DISENGAGE` steps -> `mutual_disengagement`, no victor;
14. `DISENGAGE` inside 20,000 km -> no successful withdrawal;
15. outside boundary but inward/non-outbound velocity -> no withdrawal;
16. outside/outbound without `DISENGAGE` -> no withdrawal;
17. exact 700/1000 mobile withdrawal threshold is deterministic;
18. unilateral successful withdrawal -> terminal, local control recorded, no default victor;
19. surrender cannot occur under `PRESS`, regardless of damage;
20. surrender cannot occur while physical/morale pressure criteria are unmet;
21. commander resolve changes surrender threshold monotonically as specified;
22. simultaneous bilateral surrender predicates -> `mutual_stand_down`, no victor;
23. disabled is not automatically surrendered;
24. unilateral combat incapacity -> terminal and opponent victor only when opponent remains combat-effective;
25. mutual incapacity -> no victor;
26. unilateral annihilation -> terminal and surviving opponent victor;
27. mutual annihilation -> no victor;
28. hard limit triggers exactly at `21,600,000 ms`, not one millisecond earlier;
29. earlier valid terminal predicate outranks hard-limit stalemate;
30. Phase 8 never mutates position, velocity, shield, armor, hull, readiness, damage state, or physical disposition;
31. protected ship IDs are complete and deterministically sorted;
32. no class/polity/prose branch, ambient RNG, or floating authority exists;
33. first real Run-0 control step remains ongoing with unchanged morale/cohesion because Phase 7 recorded no physical shock;
34. Phase-9 integration contract can consume `negotiation_signal_q1000_by_side`, protected entities, engagement status, and terminal outcome without interpretation.

# Phase boundary

Passing Phase 8 proves deterministic morale/cohesion consequences and deterministic battle-resolution/termination semantics only.

It does **not** authorize the integrated battle loop, future command-observation synthesis, immutable event orchestration, reporting, Controls A/B/C, or Run 0.

The next phase must build the authoritative step orchestrator and ledger, including `LIVE_COMMAND_OBSERVATION_BRIDGE`, before any battle is allowed to unfold beyond subsystem tests.
