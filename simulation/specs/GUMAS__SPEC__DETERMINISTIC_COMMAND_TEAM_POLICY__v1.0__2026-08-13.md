# GUMAS Deterministic Command-Team Policy v1.0

**Contract ID:** `GUMAS_COMMAND_POLICY_v1_0`  
**Layer:** L2  
**Phase:** 4  
**Status:** normative pre-implementation specification  
**DTER:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.3__2026-08-13.md`

## 1. Purpose

Convert the frozen numeric attributes of each fleet commander and six specialist lieutenants into deterministic, auditable orders. The command policy chooses orders only. It does not move ships, determine sensor truth, resolve weapons, apply damage, decide surrender acceptance, or narrate results.

The policy must satisfy one governing rule:

> If officer attributes or committed tactical observations differ, any changed decision must be traceable through explicit arithmetic. If they do not differ, the policy may not invent a difference.

Human-readable `characteristic` prose in the scenario baseline is descriptive metadata only and is forbidden as an authoritative input.

## 2. Numeric policy

All authoritative policy arithmetic uses signed integers and Q1000 normalized values.

- normalized values: integer `[0, 1000]`;
- weights: signed integer basis points;
- weighted term: `round_half_even(value_q1000 * weight / 1000)`;
- final scores: signed integers; no implicit clamp unless stated;
- no binary-float arithmetic inside scoring;
- no non-finite values;
- no process-randomized `hash()`;
- no RNG in command policy v1.0;
- input parsing from baseline decimals uses decimal text and `ROUND_HALF_EVEN` to Q1000.

Policy version and policy source digest are required run-identity inputs once implementation exists.

## 3. Authoritative officer inputs

### Commander

- `command_skill`
- `aggression`
- `casualty_aversion`
- `adaptability`
- `deception`
- `discipline`
- `negotiation_openness`
- `initiative`

### Every specialist lieutenant

- `domain_skill`
- `initiative`
- `discipline`
- `stress_tolerance`
- `risk_tolerance`
- `commander_alignment`

Specialist assignments are fixed identifiers:

- `tactical`
- `navigation`
- `ew_sensors`
- `carrier_ops`
- `engineering`
- `logistics`

No side name, officer name, prose characteristic, or faction label may directly alter a score.

## 4. Normalized command observation schema

A `CommandObservationV1` is a committed-state projection. Every field is Q1000 `[0,1000]` unless otherwise noted.

| Field | Meaning |
|---|---|
| `contact_quality` | confidence/quality of usable hostile contact |
| `relative_advantage` | normalized own tactical advantage; `500` means approximate parity |
| `own_damage` | fraction-like aggregate combat damage burden |
| `enemy_damage_estimate` | currently supportable estimate from committed sensing state |
| `logistics_strain` | ammunition/fuel/supply/energy strain |
| `mobility_margin` | available maneuver capability relative to current demands |
| `geometry_opportunity` | usable P17 cover/flank/occlusion opportunity |
| `withdrawal_viability` | ability to execute a viable withdrawal if ordered |
| `mission_pressure` | pressure to continue pursuing the side's frozen operational objective |
| `time_pressure` | urgency created by elapsed time / shrinking opportunity |
| `negotiation_signal` | committed evidence of an opposing willingness to communicate/de-escalate |
| `ew_opportunity` | supportable electronic-warfare opportunity |
| `carrier_opportunity` | supportable small-craft/carrier opportunity |
| `repair_need` | aggregate recoverable repair/damage-control need |
| `enemy_closing_pressure` | committed evidence that hostile geometry is closing dangerously |
| `uncertainty` | unresolved tactical uncertainty; high values penalize irreversible actions |

Before later phases produce a field, callers must supply the explicit neutral value `500`, except absent positive signals (`negotiation_signal`, `carrier_opportunity`, `ew_opportunity`, `repair_need`) which use `0`. Unknown values may not be filled by prose/model inference.

## 5. Strategic action vocabulary

The fleet commander chooses exactly one strategic posture per command decision epoch:

- `HOLD`
- `PRESS`
- `POSITIONAL_MANEUVER`
- `DISENGAGE`
- `CEASEFIRE_PROBE`

This vocabulary is deliberately small. Later phases translate these postures into physically legal orders and may reject an order that cannot be executed under physical constraints.

## 6. Strategic scoring equations

Let every symbol below be Q1000. `parity = 1000 - min(1000, abs(relative_advantage - 500) * 2)`.

Each score is the sum of weighted terms. The coefficient tables are normative.

### `HOLD`

| Input | Weight |
|---|---:|
| commander `discipline` | +220 |
| commander `command_skill` | +180 |
| commander `casualty_aversion` | +130 |
| `uncertainty` | +170 |
| `contact_quality` | -100 |
| `mission_pressure` | -90 |
| `enemy_closing_pressure` | +100 |
| `own_damage` | +90 |

### `PRESS`

| Input | Weight |
|---|---:|
| commander `aggression` | +240 |
| commander `initiative` | +180 |
| commander `command_skill` | +130 |
| commander `discipline` | +70 |
| `relative_advantage` | +160 |
| `contact_quality` | +130 |
| `mission_pressure` | +120 |
| `enemy_damage_estimate` | +80 |
| commander `casualty_aversion` | -170 |
| `own_damage` | -180 |
| `logistics_strain` | -120 |
| `uncertainty` | -110 |

### `POSITIONAL_MANEUVER`

| Input | Weight |
|---|---:|
| commander `adaptability` | +220 |
| commander `deception` | +190 |
| commander `initiative` | +120 |
| commander `command_skill` | +100 |
| `geometry_opportunity` | +190 |
| `mobility_margin` | +150 |
| `ew_opportunity` | +90 |
| `uncertainty` | +50 |
| `own_damage` | -90 |
| `logistics_strain` | -70 |

### `DISENGAGE`

| Input | Weight |
|---|---:|
| commander `casualty_aversion` | +240 |
| `own_damage` | +230 |
| `logistics_strain` | +170 |
| `withdrawal_viability` | +190 |
| `enemy_closing_pressure` | +100 |
| `uncertainty` | +70 |
| commander `aggression` | -150 |
| commander `initiative` | -80 |
| `mission_pressure` | -170 |
| `relative_advantage` | -120 |

### `CEASEFIRE_PROBE`

| Input | Weight |
|---|---:|
| commander `negotiation_openness` | +280 |
| commander `casualty_aversion` | +150 |
| commander `command_skill` | +80 |
| `negotiation_signal` | +260 |
| `own_damage` | +110 |
| `logistics_strain` | +90 |
| `parity` | +110 |
| commander `aggression` | -130 |
| `mission_pressure` | -100 |
| `uncertainty` | -60 |

No action receives a side-specific bonus.

## 7. Specialist competence and independence

For each specialist:

`competence = 350*domain_skill + 150*initiative + 150*discipline + 200*stress_tolerance + 150*risk_tolerance`, with each weighted term divided by 1000 using the numeric policy.

`independence = 1000 - commander_alignment`.

`effective_voice = 700*competence + 300*commander_alignment`, normalized by the same weighted-term rule.

Interpretation:

- domain skill/stress/discipline determine whether advice is technically credible;
- initiative/risk tolerance affect how strongly the specialist pushes an available option;
- commander alignment determines how readily the specialist reinforces commander posture;
- low alignment never creates randomness; it allows technically strong specialists to exert more independent pressure in their domain.

## 8. Specialist action vocabularies

### Tactical
- `HOLD_FIRE`
- `CONTROLLED_FIRE`
- `MAX_EFFECT_FIRE`

### Navigation
- `HOLD_VECTOR`
- `POSITION_FOR_ADVANTAGE`
- `EVASIVE_VECTOR`
- `WITHDRAW_VECTOR`

### EW / Sensors
- `PASSIVE_TRACK`
- `PROTECT_NETWORK`
- `ACTIVE_JAM`
- `DECEPTIVE_EMISSIONS`

### Carrier Ops
- `HOLD_CRAFT`
- `SCREEN_FLEET`
- `COMMIT_STRIKE_CRAFT`

### Engineering
- `BALANCED_POWER`
- `REINFORCE_DEFENSE`
- `PRIORITIZE_PROPULSION`
- `DAMAGE_CONTROL_SURGE`

### Logistics
- `CONSERVE`
- `BALANCED_EXPENDITURE`
- `SURGE_EXPENDITURE`

The policy returns these as intent. Later phases determine whether the action can be executed and what it causes.

## 9. Specialist domain pressures

Specialist recommendations are based on committed observation plus the selected strategic posture.

For every specialist action, implementation must expose a score breakdown with:

- `observation_terms`;
- `attribute_terms`;
- `strategic_compatibility_term`;
- `alignment_term`;
- `independent_safety_term` where applicable.

Normative directional requirements:

- Tactical: higher `risk_tolerance`, `initiative`, `contact_quality`, and `PRESS` compatibility lower the bar for stronger fire intent; higher uncertainty lowers it.
- Navigation: higher `domain_skill` and `mobility_margin` increase positioning capability; high risk tolerance favors `POSITION_FOR_ADVANTAGE`; damage/closing pressure and withdrawal viability favor `EVASIVE_VECTOR`/`WITHDRAW_VECTOR`.
- EW/Sensors: higher domain skill, EW opportunity, deception-compatible commander posture and risk tolerance favor active/deceptive EW; uncertainty/contact weakness favors passive tracking/protection.
- Carrier Ops: higher carrier opportunity, domain skill and risk tolerance favor craft commitment; damage/logistics strain and low risk tolerance favor holding/screening.
- Engineering: repair need favors `DAMAGE_CONTROL_SURGE`; closing pressure/low mobility can favor propulsion; damage threat favors defense. Engineering may push back on an unsafe commander posture when competence is high and alignment is low.
- Logistics: logistics strain and low risk tolerance favor conservation; high mission pressure plus available reserves can favor surge. Logistics may constrain aggressive posture but never directly cancels a commander order in Phase 4.

Exact specialist coefficient tables must live in the implementation as versioned immutable data and be covered by snapshot/hash tests. Any coefficient change is a policy-version change.

## 10. Commander-specialist reconciliation

Phase 4 uses deterministic advisory reconciliation rather than personality prose.

1. Score strategic postures from Section 6.
2. Choose strategic posture using Section 11 tie-breaking.
3. Score each specialist's finite action set.
4. Apply strategic compatibility bonus/penalty.
5. Apply specialist alignment reinforcement.
6. Apply independent safety pressure proportional to `competence * independence` only in that specialist's domain.
7. Choose one specialist intent per role.
8. Emit one `CommandDecisionReceiptV1`.

Specialists do not secretly mutate the strategic posture. If a high-competence, low-alignment specialist strongly disagrees, the receipt records a deterministic `dissent_q1000` and the later execution layer can use that as an explicit command-friction input. There is no hidden override.

## 11. Tie-breaking

Scores are sorted by:

1. descending integer score;
2. ascending stable action ID (ASCII lexicographic order).

Thus ties are deterministic and do not consume RNG.

Role iteration order is fixed:

`tactical`, `navigation`, `ew_sensors`, `carrier_ops`, `engineering`, `logistics`.

## 12. Decision receipt schema

`CommandDecisionReceiptV1` must include at minimum:

- policy ID/version/source digest;
- baseline ID/version/hash;
- side/fleet ID;
- decision epoch integer;
- observation canonical hash;
- command-team numeric input canonical hash;
- strategic score table with term-level arithmetic;
- selected strategic posture;
- per-role specialist score tables;
- selected intent per role;
- per-role `dissent_q1000`;
- tie-break trace where a tie exists;
- final canonical decision SHA-256;
- explicit `prose_inputs_used: false`;
- explicit `rng_used: false`.

Receipts are causal evidence. They are not narrative.

## 13. Acceptance tests

Phase 4 cannot pass without all of the following:

1. **Replay:** same observation + same team yields byte-identical normalized decision receipt.
2. **Order independence:** map/dict insertion ordering cannot change a decision.
3. **Side neutrality:** identical numeric teams and observations produce identical action IDs regardless of side label.
4. **Aggression sensitivity:** increasing commander aggression while holding other inputs fixed cannot decrease the raw `PRESS` score and cannot increase the raw `CEASEFIRE_PROBE` score.
5. **Casualty sensitivity:** increasing casualty aversion cannot decrease raw `DISENGAGE`/`CEASEFIRE_PROBE` scores and cannot increase raw `PRESS` score.
6. **Negotiation sensitivity:** increasing negotiation openness cannot decrease raw `CEASEFIRE_PROBE` score.
7. **Adaptability/deception sensitivity:** increasing those attributes cannot decrease raw `POSITIONAL_MANEUVER` score.
8. **Specialist domain sensitivity:** changing one specialist's domain skill affects only that role's specialist scoring/dissent, not unrelated specialist raw attribute terms.
9. **Alignment sensitivity:** decreasing commander alignment increases potential independent-domain dissent for otherwise identical specialists.
10. **Prose inertness:** altering/removing `characteristic` text produces identical command decisions.
11. **No hidden randomness:** policy has no RNG calls and receipt says `rng_used: false`.
12. **Frozen control divergence:** when given at least one discriminating tactical observation, the existing loyalist and rebel command teams produce any differences solely from their frozen numeric attributes; the receipt must expose the arithmetic.
13. **Full-suite regression:** repository-wide tests remain green.

## 14. Non-goals

Phase 4 does not:

- execute movement;
- compute collision/occlusion;
- decide sensor truth;
- select actual weapon targets;
- resolve shots or damage;
- make surrender or ceasefire legally effective;
- terminate battle;
- generate prose;
- promote simulation output to canon.

## 15. Promotion gate

A command-policy implementation may advance to Phase 5 only when:

- this contract is implemented as a pure deterministic module;
- coefficient/source identity is pinned;
- focused replay/sensitivity tests pass;
- a control command-policy receipt is committed or reproducibly indexed;
- `Aurora CI (Minimal)` full suite passes on the accepted code head;
- DTER is versioned forward.

**Run 0 remains blocked.**
