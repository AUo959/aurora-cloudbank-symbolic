# GUMAS Deterministic Live Observation, Orchestrator, and Ledger Specification v1.0

**Date:** 2026-08-15
**Layer:** L2 tactical simulation
**Status:** normative Phase-9 implementation contract; Run 0 remains blocked
**Task:** `TASK-20260812-gumas-deterministic-battle-runtime`
**DTER:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.9__2026-08-15.md`
**PR:** `#1506`

## Purpose

Phase 9 turns the accepted Phase-3 through Phase-8 subsystems into one deterministic authoritative macrostep. It supplies the mandatory `LIVE_COMMAND_OBSERVATION_BRIDGE`, invokes each existing owner in order, commits an immutable hash-linked ledger entry, and refuses any transition after termination.

Phase 9 is orchestration authority only. It may derive side-local numeric observations and validate/sequence accepted phase boundaries. It may not alter Phase-4 policy coefficients, perform Phase-5 movement, create Phase-6 effects, apply Phase-7 damage, decide Phase-8 termination, narrate events, or promote a simulation result to canon.

The Phase-9 one-step smoke is an integration witness, not Run 0. It must stop after one macrostep and may not claim a battle outcome.

## 1. Controlling inputs

A genesis macrostep requires:

1. the accepted deterministic T0 snapshot;
2. its initialized Phase-5 movement state at `macrostep_index == 0`;
3. the frozen v1.2 P17 baseline;
4. the pinned CanonRec-resolved T0 provenance already embedded in the T0 snapshot;
5. the baseline `seed_u64`;
6. no prior Phase-6, Phase-7, or Phase-8 artifact;
7. no prior live-observation receipt or ledger entry.

A continuation macrostep requires:

1. the previously committed Phase-8 next state;
2. the immediately preceding Phase-6 receipt;
3. the immediately preceding Phase-7 receipt;
4. the immediately preceding Phase-8 resolution state and receipt;
5. the preceding live-observation receipt for each side;
6. the immediately preceding Phase-9 ledger entry;
7. the same frozen baseline, seed, run identity, and T0 roster identity.

Genesis artifacts must be absent together. Continuation artifacts must be present together. A mixed or partial checkpoint fails closed.

## 2. Numeric and serialization profile

All authoritative values use integers:

- command inputs, capability, readiness, resources, and ratios: q1000;
- positions: integer micrometres;
- velocities: integer micrometres per second;
- time: integer milliseconds;
- hashes: lower-case SHA-256 hex;
- canonical JSON: UTF-8, sorted keys, separators `(',', ':')`, `ensure_ascii=false`, `allow_nan=false`;
- rounding: round-half-even using the accepted integer helper.

Definitions used below:

- `RHE(n/d)`: round-half-even integer division;
- `CLAMP(x)`: `max(0, min(1000, x))`;
- `MEAN(values)`: `RHE(sum(values) / count(values))`, or `0` for an empty list;
- `FRACTION(current, maximum)`: `CLAMP(RHE(current * 1000 / maximum))`, with positive maximum required.

No binary floating-point authority, ambient RNG, wall-clock input, LLM inference, prose interpretation, dictionary insertion order, class-name branch, polity branch, or side-name branch may affect a result.

## 3. Frozen roster and run identity

### 3.1 Roster record

At genesis, build one sorted record per T0 vessel containing exactly:

- `ship_id`;
- `side_id`;
- `fleet_id`;
- `baseline_class_id`;
- `canonrec_class_id`;
- `organization_id`.

`t0_roster_sha256 = SHA256(canonical_json(roster_records))`.

Every step must prove that the current state contains exactly the same vessel IDs and that all six identity fields remain unchanged. Missing, duplicated, added, renamed, side-swapped, fleet-swapped, class-swapped, or organization-swapped vessels fail closed. No reinforcement or third party can enter after T0.

### 3.2 Run identity

The Phase-9 run identity contains:

- `historical_canon_status = non_canon_simulation_instance`;
- `baseline_id` and version;
- canonical baseline SHA-256;
- `source_t0_sha256`;
- `t0_roster_sha256`;
- unsigned 64-bit `seed_u64`;
- accepted Phase-4 through Phase-8 source identities;
- Phase-9 source identity.

The run identity is hashed and repeated by hash in every ledger entry. It is simulation provenance, not canon promotion.

## 4. Side-local knowledge boundary

The bridge has two distinct information classes.

### 4.1 Exact own-state authority

A side may read the following fields for its own frozen vessels from the previously committed state:

- physical current and maximum shield/armor/hull;
- readiness;
- resources;
- position and velocity;
- capability q1000 values;
- physical disposition.

### 4.2 Enemy-observation authority

A side may learn about an opposing vessel only when the immediately preceding accepted Phase-6 receipt contains a contact whose observer belongs to the side and whose target is that opposing vessel.

For each opposing target, select one best contact by this descending key:

1. `contact_quality_q1000`;
2. `identity_quality_q1000`;
3. ascending `observer_ship_id` as the final deterministic tie-break.

The side may consume from that selected contact only:

- target and observer IDs;
- distance;
- contact quality;
- identity quality;
- classification;
- contact SHA-256.

For Phase-5 motion reference construction only, the selected target ID authorizes resolving that target's position from the exact state bound by the Phase-6 receipt. This is a narrow track-position projection. It does not authorize reading enemy hull, readiness, resources, morale, cohesion, capability, role, class, or command fields.

Enemy material damage may be learned only when all are true:

1. the target has a selected side-local contact;
2. the preceding Phase-6 receipt contains an effect on that target;
3. the effect source vessel belongs to the observing side;
4. the preceding Phase-7 target receipt binds the same effect ID;
5. the Phase-7 receipt reports `new_hull_loss_q1000` for that target.

No opposing raw vessel field may be used to compute a command observation. This negative information-flow rule is mandatory and must have a focused mutation test.

## 5. Live command observation v1.0

Emit one object per side with exactly the 16 fields accepted by Phase 4:

- `contact_quality`;
- `relative_advantage`;
- `own_damage`;
- `enemy_damage_estimate`;
- `logistics_strain`;
- `mobility_margin`;
- `geometry_opportunity`;
- `withdrawal_viability`;
- `mission_pressure`;
- `time_pressure`;
- `negotiation_signal`;
- `ew_opportunity`;
- `carrier_opportunity`;
- `repair_need`;
- `enemy_closing_pressure`;
- `uncertainty`.

All fields are integer q1000 and every term is recorded in a side-local derivation receipt.

### 5.1 Exact own-state metrics

For the side's frozen vessel roster:

`material_health = FRACTION(sum(current shield + current armor + current hull), sum(max shield + max armor + max hull))`

`own_damage = 1000 - material_health`

`resource_margin = MEAN(all fuel, energy, ammunition, and supply q1000 values across own vessels)`

`logistics_strain = 1000 - resource_margin`

For each own vessel, `active = 1` only when disposition is `combat_capable` or `degraded`; otherwise its active mobility contribution is zero.

`mobility_margin = MEAN(active * propulsion_readiness_q1000 for every frozen own vessel)`

`readiness_margin = MEAN(overall readiness and damage-control readiness for every frozen own vessel)`

`readiness_deficit = 1000 - readiness_margin`

`repair_need = CLAMP(RHE((500 * own_damage + 500 * readiness_deficit) / 1000))`

`fuel_margin = MEAN(fuel_q1000 across own vessels)`

For each active own vessel:

`boundary_progress = CLAMP(RHE(norm(position_um) * 1000 / withdrawal_boundary_um))`

`withdrawal_progress = MEAN(boundary_progress for active own vessels)`

`withdrawal_viability = CLAMP(RHE((600 * mobility_margin + 200 * fuel_margin + 200 * withdrawal_progress) / 1000))`

For each own vessel:

`ew_effective = RHE(electronic_warfare_q1000 * ew_readiness_q1000 / 1000)`

`own_ew_margin = MEAN(ew_effective values)`

For each own vessel:

`carrier_effective = RHE(carrier_projection_q1000 * min(overall_readiness, energy_resource, supply_resource) / 1000)`

`carrier_opportunity = MEAN(carrier_effective values)`

### 5.2 Side-local contact metrics

Let `enemy_roster_count` be the frozen number of opposing vessels. Unseen targets contribute zero.

`contact_quality = RHE(sum(best contact quality by target) / enemy_roster_count)`

`identity_quality = RHE(sum(best identity quality by target) / enemy_roster_count)`

`uncertainty = 1000 - RHE((contact_quality + identity_quality) / 2)`

For each selected contact, use the selected observer's own effective weapon range:

`target_geometry = CLAMP(1000 - RHE(contact_distance_um * 1000 / observer_weapon_range_um))`

`geometry_opportunity = RHE(sum(target_geometry by contacted target) / enemy_roster_count)`

`ew_opportunity = CLAMP(RHE((600 * uncertainty + 400 * own_ew_margin) / 1000))`

### 5.3 Cumulative attributable enemy-damage estimate

Each live-observation receipt stores `enemy_damage_estimate_q1000_by_target` for the complete opposing roster.

At genesis every target value is `0`.

On continuation:

`estimate_next[target] = CLAMP(estimate_prior[target] + attributable_new_hull_loss_q1000[target])`

Targets without current side-local contact or attributable current loss retain the prior estimate. The side-level value is:

`enemy_damage_estimate = MEAN(estimate_next for the complete opposing roster)`

The cumulative estimate is an observation-memory value. It is not permitted to read the opponent's actual cumulative hull state.

### 5.4 Closing pressure

Each live-observation receipt stores the selected contact distance by target. Compare the current selected contact from the preceding Phase-6 receipt with the prior live-observation receipt's stored distance for the same target:

`closing[target] = CLAMP(RHE((prior_distance - current_distance) * 1000 / prior_distance))` when `current_distance < prior_distance`; otherwise `0`.

`enemy_closing_pressure = RHE(sum(closing[target]) / enemy_roster_count)`.

A new contact, lost contact, stationary range, or increasing range contributes zero. No hidden enemy velocity may be read.

### 5.5 Relative, mission, time, and negotiation terms

`relative_advantage = CLAMP(500 + RHE((enemy_damage_estimate - own_damage) / 2))`

`time_pressure = CLAMP(RHE(elapsed_ms * 1000 / hard_limit_ms))`

Phase-9 v1.0 uses one side-neutral scenario-local urgency floor:

`MISSION_PRESSURE_FLOOR_Q1000 = 500`

`mission_pressure = max(MISSION_PRESSURE_FLOOR_Q1000, time_pressure)`

At genesis, `negotiation_signal = 0`.

On continuation, `negotiation_signal` is the current side's value from the immediately preceding validated Phase-8 resolution state. The receipt records that resolution SHA-256 and macrostep. Ledger continuity prevents the same Phase-8 resolution from being consumed for two different decision epochs.

## 6. Live-observation receipt

Each side receipt must bind:

- schema/version and Phase-9 source identity;
- run identity and roster SHA-256;
- side/fleet and decision epoch;
- source committed-state SHA-256;
- source preceding Phase-6, Phase-7, and Phase-8 hashes, or explicit genesis markers;
- prior live-observation receipt SHA-256, or genesis marker;
- sorted selected-contact evidence and contact-memory distances;
- sorted attributable-damage evidence;
- complete cumulative enemy-damage memory;
- exact own-state aggregate terms;
- exact field derivation terms;
- normalized 16-field observation;
- observation SHA-256;
- `enemy_raw_material_state_used = false`;
- `prose_inputs_used = false`;
- `ambient_rng_used = false`;
- `floating_authority_used = false`;
- receipt SHA-256.

Receipt hashing excludes only its own receipt-hash field.

## 7. Motion-reference bridge

Convert each Phase-4 command receipt through the accepted Phase-5 `order_from_command_receipt` boundary.

When a fleet's navigation intent is not `EVASIVE_VECTOR`, a motion reference is optional and v1.0 omits it.

When navigation intent is `EVASIVE_VECTOR`:

1. at least one selected side-local opposing contact is required;
2. resolve only those contacted target positions from the state bound by the preceding Phase-6 receipt;
3. set reference position to the round-half-even centroid of those positions;
4. set confidence to the round-half-even mean selected contact quality;
5. bind source state and Phase-6 receipt SHA-256;
6. use `reference_kind = phase9_side_local_contact_centroid`.

`EVASIVE_VECTOR` without a side-local contact fails closed. The orchestrator may not substitute the real opposing fleet centroid.

## 8. Authoritative macrostep

One macrostep executes exactly:

1. validate baseline, seed, run identity, T0 roster, current state hash, and checkpoint completeness;
2. validate the preceding ledger entry and all parent artifact hashes/source identities;
3. if the preceding Phase-8 outcome is terminal, fail closed before command or movement;
4. derive both side-local live observations and receipts;
5. invoke Phase 4 once per side/fleet with `decision_epoch = current_state.macrostep_index`;
6. construct Phase-5 orders and permitted side-local motion references;
7. invoke Phase 5 movement;
8. invoke Phase 6 sensing/EW/targeting/fire with the frozen seed;
9. invoke Phase 7 simultaneous damage/disposition;
10. invoke Phase 8 morale/resolution/termination with the preceding resolution state;
11. validate that every phase's parent hash equals the immediately preceding artifact;
12. commit one Phase-9 ledger entry;
13. return the new checkpoint and `can_continue = not terminal_outcome.terminated`.

The current terminal macrostep is committed exactly once. Any attempt to execute from its checkpoint fails before Phase 4.

## 9. Source-identity validation

Phase 9 must compute current source identities directly from the installed Phase-4 through Phase-9 modules. It must compare them with every supplied state, receipt, prior resolution, run identity, and prior ledger entry before invocation.

Source drift fails closed. Updating an accepted phase therefore requires a new receipt/run identity and cannot silently continue an old ledger.

The orchestrator may call existing private source-identity helpers solely to validate the accepted implementation until those helpers receive a separately accepted public boundary. It may not duplicate their source hashes as constants.

## 10. Immutable ledger entry v1.0

Each entry contains:

- `schema = aurora://simulation/gumas/phase9_ledger_entry/v1.0`;
- Phase-9 contract/version/source identity;
- `historical_canon_status = non_canon_simulation_instance`;
- run-identity SHA-256;
- T0 roster SHA-256;
- macrostep index and start/end elapsed milliseconds;
- previous ledger-entry SHA-256, or `GENESIS`;
- previous committed-state SHA-256;
- live-observation state and receipt SHA-256 by side;
- Phase-4 decision SHA-256 by fleet;
- Phase-5 state and receipt SHA-256;
- Phase-6 state and receipt SHA-256;
- Phase-7 state and receipt SHA-256;
- Phase-8 next-state, resolution-state, and receipt SHA-256;
- terminal outcome object;
- accepted Phase-4 through Phase-9 source identities;
- `reporter_invoked = false`;
- `run0_executed = false`;
- canonical JSON profile;
- ledger-entry SHA-256.

The entry hash excludes only `ledger_entry_sha256`.

For continuation, validate:

- the prior entry's own hash;
- prior entry run/roster identities;
- prior entry Phase-8 next-state SHA-256 equals the supplied current state SHA-256;
- prior entry Phase-6/7/8 artifact hashes equal supplied checkpoint hashes;
- new macrostep index is prior macrostep index plus one;
- new previous-entry hash equals the prior entry hash.

Ledger entries are append-only values. Phase 9 provides no update or delete operation.

## 11. Terminal and reporting boundary

The authoritative terminal value is only `Phase8ResolutionState.terminal_outcome`.

Phase 9 may copy that object into its ledger and expose `can_continue`. It may not reinterpret the winner, local control, surrender, withdrawal, ceasefire, incapacity, annihilation, or stalemate fields.

No reporter is invoked inside the transition path. Phase 10 may later regenerate factual output solely from validated immutable ledger/checkpoint artifacts. Reporting must not feed values back into a state transition.

## 12. Acceptance matrix

Phase 9 is accepted only when focused tests prove:

1. genesis observation is derived from own T0 state with no synthetic control observation;
2. continuation observation uses only accepted prior contacts and attributable effects;
3. mutation of unseen enemy hull/readiness/resources cannot change the opposing side's observation;
4. mutation of own material/readiness/resources changes the appropriate own observation monotonically;
5. contact loss increases or preserves uncertainty and cannot improve geometry opportunity;
6. cumulative enemy-damage memory changes only from contacted, attributable effects;
7. negotiation signal is bound to exactly one immediately preceding Phase-8 resolution;
8. all 16 fields are integer q1000 and bounded;
9. same checkpoint produces byte-identical observations, phase outputs, and ledger entry;
10. side/fleet mapping insertion order is inert;
11. state, receipt, ledger, roster, and source-identity mutation each fail closed;
12. added/removed/swapped vessels fail closed;
13. `EVASIVE_VECTOR` cannot use an unobserved enemy centroid;
14. protected/invalid targets remain ineligible through accepted Phase 6;
15. a terminal prior state prevents another macrostep;
16. a terminal current step is committed once and cannot be continued;
17. no ambient RNG, floating authority, prose input, class/polity/side special case, or reporter exists in the transition path;
18. a real pinned-CanonRec one-step smoke replays exactly and stops after one step;
19. focused CI and the repository-wide suite pass on the same implementation head.

## 13. Run-0 prohibition

Phase-9 development and acceptance may:

- construct the real pinned T0 state;
- derive the genesis live observations;
- execute exactly one integrated macrostep;
- replay that one step for equality;
- emit a non-canon integration receipt.

It may not loop until termination, publish a battle result, name a winner, generate a narrative, claim canon status, or mark Run 0 complete.

**Run 0 remains blocked pending separate Phase-9 acceptance, later reporting/control gates, owner review, and explicit execution authority.**
