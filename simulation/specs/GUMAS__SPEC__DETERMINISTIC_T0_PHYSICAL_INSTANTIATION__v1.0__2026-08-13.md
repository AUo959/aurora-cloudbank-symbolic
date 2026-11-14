# GUMAS Deterministic T0 Physical Instantiation Specification v1.0

**Date:** 2026-08-13  
**Layer:** L2 tactical simulation  
**Status:** normative Phase-3 construction contract; no battle-execution authority  
**Task:** `TASK-20260812-gumas-deterministic-battle-runtime`  
**PR:** `#1506`

## Purpose

Define the bounded, deterministic bridge from the accepted CanonRec tactical-input manifest and frozen flash-rebellion baseline into a complete per-vessel T0 physical state.

This layer is an **instantiator**, not a combat resolver. It may translate pinned inputs into state, but it may not choose maneuvers, targets, weapon effects, damage, withdrawal, surrender, ceasefire, or battle outcome.

Recovered GUMAS v2.0 remains the historical aggregate tactical authority. The physical state defined here is a separately versioned bounded extension subordinate to that authority; none of these per-vessel mechanics are retroactively attributed to historical GUMAS v2.0.

## Controlling inputs

A valid T0 construction requires all of the following to be pinned before execution:

1. frozen baseline `SIM-L2-FR-P17-EQUAL-001`;
2. accepted restored GUMAS runtime `2.0.1-restored.2`;
3. CanonRec commit `dc629a566b2f42fa1c652140b9eef72a4fb0d58a`;
4. CanonRec resolver `1.0.1` and derivation rules `canonrec-tactical-derivation-v1.1`;
5. accepted control resolved-manifest SHA-256 `cd8a22b8d8721106ab94f5f881685cbd8f58c95beeb8f2d86853e09fd61bdfdc`;
6. physical calibration `GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json`;
7. T0 constructor source digest/version once implemented.

If any required identity differs, the resulting T0 snapshot has a different run identity and may not reuse a previous T0 receipt.

## Provenance boundary

The following classification is mandatory:

- CanonRec entity/class/organization identity: `CANON_DIRECT`;
- applicable scoped doctrine: `CANON_SCOPED_DOCTRINE`;
- dimensionless 0–1000 capability and doctrine vectors: `DERIVED_FROM_CANON`;
- physical calibration constants/equations, formation geometry, initial resource fractions, and P17 rotational reference completion: `SCENARIO_LOCAL`.

No numerical calibration value becomes canon by appearing in the T0 state. CanonRec substitutions alter physical state only through the same global calibration equations; class- or polity-specific physical branches are forbidden.

## Authoritative numeric representation

T0 authority uses integer/fixed-point values wherever practical so serialization and equality do not depend on platform floating behavior.

| Quantity | Representation |
|---|---|
| position | integer metres (`position_m`) |
| velocity | integer millimetres/second (`velocity_mm_s`) |
| acceleration limits | integer millimetres/second² (`max_accel_mm_s2`) |
| ranges | integer metres |
| shield/armor/hull/firepower capacities | integer milliunits |
| readiness/resource/capability fractions | integer `q1000` |
| attitude unit vectors | signed integer `q12` where 1.0 = `1_000_000_000_000` |
| rotational phase at T0 | integer `turn_q12` where one full turn = `1_000_000_000_000` |
| rotation period | integer milliseconds |

Baseline decimal numbers are parsed from their textual decimal representation, converted with exact decimal arithmetic, and quantized using round-half-even only at explicitly defined unit boundaries.

Non-finite numbers are invalid. Process-randomized `hash()` is forbidden.

## Canonical serialization

Normalized T0 state uses `aurora-canonical-json-v1`:

- UTF-8;
- object keys sorted lexicographically;
- separators `,` and `:` with no formatting whitespace;
- `ensure_ascii=false`;
- NaN/Infinity forbidden.

The T0 SHA-256 is computed over those exact bytes with the `t0_sha256` field absent from the hashed payload, then inserted as the final receipt field.

## Vessel identity and ordering

Vessel IDs derive solely from the frozen baseline:

`{SIDE3}-{CLASS_TOKEN}-{NN}`

- loyalist prefix: `LOY`;
- rebel prefix: `REB`;
- class token: `CLASS-{TOKEN}-01 → {TOKEN}`;
- instance index: 1-based, zero-padded width 2 within the baseline composition entry;
- authoritative vessel iteration order: complete `ship_id` lexicographic order.

Baseline class IDs are translated to CanonRec class IDs through the explicit identity map in the calibration artifact. The map is data, not executable class-specific combat logic.

## Formation-instantiation algorithm

### Invariants

Each side contains exactly 19 vessels in Run 0. Formation construction is deterministic and consumes no RNG.

1. The sole `flagship_command` vessel occupies local slot `0` at the exact frozen fleet centroid.
2. The remaining 18 vessels are sorted by complete `ship_id` and assigned slots `1..18` in that order.
3. Slots `1..18` use the fixed zero-sum paired offset template stored in the calibration artifact, expressed in permille of the frozen formation radius.
4. Loyalist local offsets use transform sign `+1`; rebel local offsets use `-1` on all three axes.
5. Because both baseline centroids and centroid velocities are exact sign mirrors, this produces exact material and geometric inversion between the two control forces without trigonometric frame construction.
6. Every non-flagship slot magnitude must be ≤ the formation radius; duplicate positions are forbidden.
7. The arithmetic sum of all 19 local offsets must be exactly `[0,0,0]`, preserving the frozen centroid.

### Position conversion

For each axis:

`offset_m = round_half_even(formation_radius_km × 1000 × slot_permille / 1000)`

`position_m = centroid_position_km × 1000 + transform_sign × offset_m`

The current 850 km radius and integer permille template yield integer-metre offsets exactly, so no rounding ambiguity exists for Run 0.

## Initial velocity

All vessels begin with zero relative formation velocity:

`velocity_mm_s = centroid_velocity_km_s × 1_000_000`

No formation spin, station-keeping perturbation, or random velocity jitter exists at T0. Such behavior, if later required, belongs to a separately versioned movement policy after T0.

## Initial attitude

Every vessel faces the opposing fleet centroid at T0.

The authoritative attitude is represented by:

- `forward_q12`: normalized vector from own vessel position to the opposing frozen fleet centroid;
- `up_q12`: the pinned P17 spin-axis unit vector;
- `attitude_frame`: `P17_SCENARIO_INERTIAL_XYZ`.

Normalization uses exact decimal arithmetic with deterministic square-root precision and round-half-even quantization to q12. If `forward` becomes parallel/anti-parallel to `up`, the deterministic fallback up reference is `+Y`; this fallback is part of the constructor contract.

A quaternion is not authoritative at T0. Later attitude integration may introduce a separately versioned representation if required.

## Planetoid P17 rotational reference completion

The frozen baseline supplies a 7.8-hour rotation period but leaves the reference frame, spin axis, and T0 phase unspecified. Phase 3 completes those missing inputs explicitly as scenario-local state:

- inertial frame: `P17_SCENARIO_INERTIAL_XYZ`;
- +X: baseline inertial x-axis and P17 semi-axis `a` at phase zero;
- +Y: baseline inertial y-axis and semi-axis `b` at phase zero;
- +Z: baseline inertial z-axis and semi-axis `c`/spin axis;
- spin axis q12: `[0,0,1000000000000]`;
- phase at T0: `0 turn_q12`;
- positive rotation sense: right-hand rule about +Z;
- exact period: `28,080,000 ms`.

These are **SCENARIO_LOCAL completion parameters**, not CanonRec facts. They are included in the calibration/configuration digest and therefore in run identity.

## Physical calibration contract

The accepted CanonRec resolver emits dimensionless capability vectors on `[0,1000]`. Phase 3 converts those vectors into physical tactical coefficients using only the global equations in the versioned calibration artifact.

Required calibrated fields per vessel:

- `max_accel_mm_s2` from `mobility`;
- `firepower_milliunits` from `firepower`;
- `shield_capacity_milliunits` from `defense`;
- `armor_integrity_milliunits` from weighted `defense` + `endurance`;
- `hull_integrity_milliunits` from weighted `defense` + `endurance`;
- `effective_weapon_range_m` from `range`;
- `sensor_range_m` from `sensors`;
- `electronic_warfare_q1000` from `electronic_warfare`;
- `stealth_q1000` from `stealth`;
- `carrier_projection_q1000` from `carrier_projection`;
- `support_q1000` from `support`;
- `boarding_q1000` from `boarding`;
- `command_q1000` from `command`;
- `endurance_q1000` from `endurance`.

The calibration is intentionally class-agnostic. Any alternate valid class traverses the same equations.

## T0 vessel state schema

Each vessel state must contain at minimum:

```json
{
  "ship_id": "LOY-AEGIS-01",
  "side_id": "loyalist",
  "fleet_id": "TF-LOYALIST-P17",
  "baseline_class_id": "CLASS-AEGIS-01",
  "canonrec_class_id": "cls_aegis",
  "organization_id": "org_galactic_union",
  "role": "battlecruiser",
  "formation_slot": 1,
  "position_m": [0, 0, 0],
  "velocity_mm_s": [0, 0, 0],
  "attitude": {
    "frame": "P17_SCENARIO_INERTIAL_XYZ",
    "forward_q12": [0, 0, 0],
    "up_q12": [0, 0, 1000000000000]
  },
  "physical": {
    "max_accel_mm_s2": 0,
    "firepower_milliunits": 0,
    "shield_capacity_milliunits": 0,
    "shield_current_milliunits": 0,
    "armor_integrity_milliunits": 0,
    "armor_current_milliunits": 0,
    "hull_integrity_milliunits": 0,
    "hull_current_milliunits": 0,
    "effective_weapon_range_m": 0,
    "sensor_range_m": 0
  },
  "capability_q1000": {},
  "resources_q1000": {
    "fuel": 1000,
    "energy": 1000,
    "ammunition": 1000,
    "supply": 1000
  },
  "readiness_q1000": {
    "overall": 1000,
    "sensors": 1000,
    "ew": 1000,
    "propulsion": 1000,
    "weapons": 1000,
    "damage_control": 1000
  },
  "command": {
    "fleet_commander_id": "...",
    "command_team_ids": []
  },
  "morale_q1000": 1000,
  "cohesion_q1000": 1000,
  "damage_state": "undamaged",
  "disposition": "combat_capable",
  "provenance": {}
}
```

Current capacities start at their calibrated maximum. Damage is zero. All initial resource/readiness fractions are explicit scenario-local T0 conditions and may not be silently randomized.

## Complete T0 snapshot schema

The constructor emits one normalized object containing:

- schema/version;
- complete input identities and hashes;
- numeric/canonicalization policy IDs;
- planetoid physical/rotational reference state;
- both side/fleet identities and command teams;
- all 38 vessel states sorted lexicographically by `ship_id`;
- symmetry assertions;
- T0 SHA-256.

Wall-clock timestamps are excluded from the hashed authoritative snapshot.

## Material-symmetry requirements for Run 0

The control is materially symmetric even though command-team attributes differ by design.

The T0 acceptance test must prove:

1. each side has 19 vessels with identical class multiplicities;
2. corresponding class capability/physical coefficients are identical;
3. initial shield/armor/hull/resource/readiness/morale/cohesion values are identical by class;
4. each loyalist local position offset has an exact sign-inverted rebel counterpart under deterministic vessel pairing;
5. frozen fleet centroids and centroid velocities are sign inverses;
6. no vessel starts outside its 850 km formation radius;
7. no vessel intersects P17 at T0;
8. no duplicate vessel IDs or positions occur;
9. constructor replay produces an identical normalized T0 SHA-256.

Command-person attributes are not required to mirror; they are frozen scenario-local inputs reserved for the later deterministic command-policy phase and do not alter T0 material state.

## Fail-closed conditions

T0 construction fails before emitting an accepted snapshot when any of the following is true:

- baseline ID/version or required frozen fields differ from the supported Phase-3 fixture contract;
- CanonRec commit/resolver/manifest identity does not match the supplied pinned input;
- a baseline class lacks an explicit CanonRec identity mapping;
- a required capability value is absent or outside `[0,1000]`;
- a vessel count is non-positive or total count differs from the fixture expectation;
- formation slots are duplicated, outside radius, or fail zero-sum centroid preservation;
- a generated vessel lies inside the P17 collision ellipsoid;
- authoritative numeric conversion is non-finite or non-deterministic;
- symmetry assertions fail for the frozen Run-0 control.

## Phase boundary

Passing Phase 3 proves only that the complete T0 physical state is deterministic and auditable.

It does **not** authorize movement, command decisions, sensing, EW, targeting, firing, damage, withdrawal, surrender, ceasefire, termination, reporting, or Run-0 execution. Those remain later gated phases.
