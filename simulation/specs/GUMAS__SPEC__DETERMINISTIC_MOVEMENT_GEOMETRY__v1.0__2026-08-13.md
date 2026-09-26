# GUMAS Deterministic Movement & Geometry Specification v1.0

**Contract ID:** `GUMAS_MOVEMENT_GEOMETRY_v1_0`  
**Layer:** L2 tactical simulation  
**Phase:** 5  
**Status:** normative pre-implementation specification  
**DTER:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.4__2026-08-13.md`

## 1. Purpose

Advance the accepted 38-vessel physical state through deterministic, physically bounded translational movement around Planetoid P17.

Phase 5 consumes already-committed physical state plus deterministic command-policy orders. It may move vessels and derive geometry. It may not decide sensor truth, EW outcomes, target eligibility, weapon fire, damage, morale, surrender, ceasefire effectiveness, battle termination, or narrative.

The authoritative order is:

`committed state → committed command orders → physically constrained movement → committed next physical state → geometry products`

A later reporter may describe those committed facts. It may not alter them.

## 2. Controlling inputs

A valid Phase-5 step pins:

1. accepted T0 or previous movement-state SHA-256;
2. command-decision receipt SHA-256 for each participating fleet;
3. command policy bundle SHA-256 `8c9ba9d413945404e7648c8f427b660576b0e85887c7639a0944f56b38585b3f` for the current control lineage;
4. P17 physical and rotational state from accepted Phase 3;
5. movement/geometry kernel version and complete source identity;
6. any `MotionReferenceV1` object required by a navigation intent;
7. macrostep index and simulation elapsed time.

No wall-clock value participates in authoritative state.

## 3. Physical model boundary

Phase 5 models:

- Newtonian translation;
- vessel thrust bounded by each vessel's Phase-3 `max_accel_mm_s2`;
- P17 point-mass gravity;
- P17 rotating triaxial collision geometry;
- P17 line-of-sight occultation geometry;
- exact deterministic range/separation/closing calculations under the discrete numeric model;
- spherical battle-volume/withdrawal-boundary geometry.

Phase 5 does **not** model:

- ship-ship gravity;
- relativistic corrections;
- FTL;
- weapon recoil;
- ship-ship collision, because no authoritative per-class hull dimensions are presently resolved;
- rotational inertia or bounded attitude slew;
- propulsion fuel consumption.

Inter-vessel motion therefore treats vessels as translational point masses. P17 remains a hard extended body.

The control's acceleration envelope and six-hour maximum duration remain far below the numerical validity ceiling established below. If that ceiling is exceeded, execution fails closed rather than silently switching models.

## 4. Authoritative numeric representation

Movement authority upgrades T0 translational state to integer micrometre units:

| Quantity | Authoritative representation |
|---|---|
| position | integer micrometres `position_um` |
| velocity | integer micrometres/second `velocity_um_s` |
| acceleration | integer micrometres/second² `acceleration_um_s2` |
| time | integer milliseconds |
| normalized direction | signed `q12`, where 1.0 = `1_000_000_000_000` |
| body phase | `turn_q12` |
| distance/range | integer micrometres |
| closing rate | integer micrometres/second |

Exact T0 conversion:

- `position_um = position_m × 1_000_000`;
- `velocity_um_s = velocity_mm_s × 1_000`;
- `max_accel_um_s2 = max_accel_mm_s2 × 1_000`.

All arithmetic affecting authoritative branches uses integers. Division uses explicit round-half-even unless a condition below requires floor/ceiling. Non-finite floating values are forbidden. Python process `hash()` is forbidden.

## 5. P17 constants in Phase-5 units

The baseline P17 values remain scenario-local control inputs:

- semi-axis A: `190 km = 190_000_000_000 um`;
- semi-axis B: `135 km = 135_000_000_000 um`;
- semi-axis C: `90 km = 90_000_000_000 um`;
- gravitational parameter: baseline decimal `2000718121.0585666 m^3/s^2`;
- authoritative converted `mu_um3_s2 = 2_000_718_121_058_566_600_000_000_000`;
- rotation period: `28_080_000 ms`;
- phase at T0: `0 turn_q12`;
- spin axis: `+Z` in `P17_SCENARIO_INERTIAL_XYZ`;
- withdrawal/combat-volume radius: `20_000 km = 20_000_000_000_000 um`;
- macro integration step: `10_000 ms`;
- maximum run duration: `21_600_000 ms`.

P17 gravity is always centered at inertial origin.

## 6. Dynamics subdivision and integrator

Each 10-second macrostep contains exactly **100 authoritative 100-ms dynamics substeps**.

This subdivision is part of v1.0 semantics, not an implementation optimization. Changing it changes the model version.

Every substep uses deterministic velocity-Verlet translation.

For substep duration `dt_ms = 100`:

1. derive requested thrust acceleration from current position, command orders, and any required motion reference;
2. clamp thrust magnitude to the vessel's current physical acceleration cap;
3. calculate P17 gravity acceleration `g0` at `position0`;
4. `a0 = thrust0 + g0`;
5. predict `position1` using `position0`, `velocity0`, `a0`, and exact integer round-half-even arithmetic;
6. perform swept P17 collision testing for the substep under Section 11;
7. if no collision, recompute guidance/thrust and gravity at `position1`, producing `a1`;
8. update velocity using the average of `a0` and `a1`;
9. commit the substep state;
10. continue until exactly 100 substeps have completed.

Equivalent continuous formulas are:

`p1 = p0 + v0*dt + 0.5*a0*dt^2`

`v1 = v0 + 0.5*(a0+a1)*dt`

Implementation must evaluate them with integer numerators/denominators, not binary floating point.

## 7. P17 point-mass gravity

Let vessel position from P17 center be integer vector `r_um`.

1. `r2 = x^2 + y^2 + z^2`;
2. radius `r` is the deterministic nearest integer square root of `r2`, ties to even;
3. before gravity is evaluated, collision/inside-body guards ensure `r > 0` and the vessel is not within the hard ellipsoid;
4. each acceleration component is:

`g_i = round_half_even(-mu_um3_s2 * r_i / r^3)`

in `um/s^2`.

The gravity routine consumes no RNG and contains no class or side branch.

## 8. Motion-reference contract

Some navigation intents require a committed external positional reference. Phase 5 therefore accepts an optional immutable `MotionReferenceV1`:

```json
{
  "schema": "aurora://simulation/gumas/motion_reference/v1.0",
  "reference_kind": "observed_enemy_centroid",
  "position_um": [0, 0, 0],
  "source_state_sha256": "...",
  "source_receipt_sha256": "...",
  "confidence_q1000": 0
}
```

Actual Run 0 may use an enemy/threat reference only when a later sensing phase has committed it. Phase 5 may not substitute hidden ground-truth hostile coordinates.

Synthetic references are permitted in Phase-5 unit/acceptance tests and must be labeled `test_fixture`.

If an action requires a reference and none is supplied, execution fails closed for that order rather than inventing a vector.

## 9. Command-order to thrust translation

Phase 4 emits fleet strategic posture, navigation intent, and engineering intent. Phase 5 converts those existing orders to a translational thrust request through versioned global coefficients. No ship-class name or side label participates.

### Strategic throttle caps `q1000`

- `HOLD`: 400
- `PRESS`: 1000
- `POSITIONAL_MANEUVER`: 800
- `DISENGAGE`: 900
- `CEASEFIRE_PROBE`: 300

### Navigation throttle demands `q1000`

- `HOLD_VECTOR`: 0
- `POSITION_FOR_ADVANTAGE`: 800
- `EVASIVE_VECTOR`: 850
- `WITHDRAW_VECTOR`: 900

### Engineering propulsion caps `q1000`

- `BALANCED_POWER`: 800
- `REINFORCE_DEFENSE`: 650
- `PRIORITIZE_PROPULSION`: 1000
- `DAMAGE_CONTROL_SURGE`: 500

Applied throttle is:

`min(strategic_cap, navigation_demand, engineering_cap)`.

Requested thrust magnitude is:

`round_half_even(max_accel_um_s2 × applied_throttle_q1000 / 1000)`.

This magnitude is then clamped again to `[0, max_accel_um_s2]` as a physical invariant.

The tables above are `SCENARIO_LOCAL` movement-policy coefficients. They are not CanonRec facts. Their bytes must be included in the movement-kernel source identity.

## 10. Navigation guidance vectors

Guidance recomputes at each 100-ms substep from committed state.

### `HOLD_VECTOR`

Requested thrust vector is zero. Existing inertial velocity continues; P17 gravity still acts.

### `POSITION_FOR_ADVANTAGE`

Let `r` be the vessel's current body-centered position and `spin` the pinned +Z spin axis.

Direction is the normalized positive body tangent:

`cross(spin, r)`.

If degenerate, deterministic fallback is `+X`.

Because the two control forces begin as exact position inverses, this rule naturally produces mirrored tangential directions without a side branch.

### `WITHDRAW_VECTOR`

Direction is normalized radial-outward vector `r`.

### `EVASIVE_VECTOR`

Requires `MotionReferenceV1`.

Let `threat = reference_position - vessel_position`.

Direction is normalized `cross(spin, threat)`, producing a deterministic lateral vector relative to the threat line. If degenerate, fallback is the `POSITION_FOR_ADVANTAGE` tangent; if that too is degenerate, fallback is `+X`.

All vector normalization uses integer square-root and q12 round-half-even arithmetic.

## 11. Rotating triaxial body transform

P17's ellipsoid rotates about +Z. Authoritative body/inertial transforms use an **integer-only CORDIC** trigonometric kernel.

Requirements:

- phase input: `turn_q12`;
- internal CORDIC angle constants: immutable integer table expressed in turns, committed with the kernel;
- fixed CORDIC gain constant: committed integer;
- minimum iterations: 40;
- output sine/cosine: signed q12;
- quadrant reduction: deterministic integer logic;
- no runtime use of `math.sin`, `math.cos`, NumPy, platform libm, or binary floating point.

Phase at elapsed `t_ms` is:

`(phase_t0 + round_half_even(t_ms × 1_000_000_000_000 / 28_080_000)) mod 1_000_000_000_000`.

For collision during each 100-ms dynamics substep, the ellipsoid orientation is **discretely authoritative at that substep's midpoint phase**. The body is held at that orientation for the swept-segment collision test. This is the explicit v1.0 discrete rotating-body approximation.

For a point-in-time occultation query, the body transform uses the exact queried simulation timestamp phase.

## 12. Triaxial point and swept-segment collision

Transform inertial points into P17 body coordinates for the applicable authoritative phase.

For body-frame point `(x,y,z)` and semi-axes `(a,b,c)`, use the denominator-free implicit form:

`F = x^2*b^2*c^2 + y^2*a^2*c^2 + z^2*a^2*b^2 - a^2*b^2*c^2`.

- `F < 0`: inside hard body;
- `F = 0`: surface contact;
- `F > 0`: outside.

For swept segment `p(t)=p0+t*(p1-p0)`, construct exact integer quadratic `A*t^2+B*t+C` from the same scaled implicit form.

Intersection existence on `[0,1]` is decided using integer endpoint/vertex/discriminant logic only.

If a vessel starts outside and the swept segment first reaches the body:

1. earliest entry fraction is solved deterministically from the integer quadratic and quantized to `t_q12`;
2. vessel state is advanced only to that contact fraction;
3. movement status becomes `collision_contact`;
4. remaining substep thrust/motion for that vessel is suppressed;
5. a geometry event records body ID, contact position, substep index, fraction, and pre-contact velocity;
6. later damage/disposition phases must consume that contact before the vessel can resume normal movement.

Phase 5 detects and locates contact but does not decide damage.

## 13. Line-of-sight occultation

Occultation is a pure geometry query over two committed inertial positions at one committed simulation timestamp.

1. transform observer and target positions into P17 body coordinates at that timestamp;
2. apply the same exact segment/ellipsoid intersection test;
3. `occulted=true` only when the open segment between endpoints intersects the hard ellipsoid;
4. endpoints on the surface are handled explicitly and may not produce ambiguous platform-dependent behavior.

The occultation function does not decide whether either side actually detects the other. Phase 6 will consume this geometry result.

## 14. Separation, closing rate, and fleet centroid

For vessel pair positions `r_a`, `r_b`:

- separation is nearest integer square root of squared relative distance;
- relative radial closing rate is `round_half_even(-dot(delta_position, delta_velocity) / separation)`;
- positive closing rate means separation is decreasing;
- zero separation is invalid for distinct vessel point states and fails closed.

Fleet centroid is the round-half-even integer mean of all combat-present vessel positions sorted by `ship_id`. Phase 5 may calculate the centroid but may not infer fleet defeat/disengagement from it.

## 15. Battle-volume and withdrawal geometry

P17-centered boundary radius is exactly `20_000_000_000_000 um`.

For each vessel and each fleet centroid, Phase 5 emits:

- `radius_from_p17_um`;
- `inside_combat_volume = radius <= boundary`;
- `outside_withdrawal_boundary = radius > boundary`;
- whether the boundary was crossed during the macrostep and, if so, deterministic first crossing fraction.

Being outside the boundary does **not** itself terminate combat. Interception viability and withdrawal termination remain Phase 8.

## 16. Numerical validity envelope

Phase 5 remains Newtonian. A state fails closed if any vessel speed reaches or exceeds `0.02 c`.

Using exact SI `c = 299_792_458 m/s`, the ceiling is:

`5_995_849_160_000 um/s`.

The frozen six-hour Run-0 acceleration envelope is expected to remain below this guard. The guard is a model-validity stop condition, not a propulsion capability claim.

## 17. Movement state and receipt

A committed `MovementStepReceiptV1` contains at minimum:

- movement contract ID/version and complete source identity;
- prior state SHA-256;
- command-decision SHA-256 per fleet;
- motion-reference SHA-256 values where used;
- macrostep index;
- start/end elapsed simulation milliseconds;
- numeric policy ID;
- per-vessel start/end `position_um` and `velocity_um_s`;
- per-vessel max acceleration, applied throttle, requested/applied thrust vectors;
- substep collision/contact record if any;
- P17 phase at macrostep start/end;
- derived fleet centroids;
- boundary crossing records;
- deterministic geometry summary;
- `rng_used:false`;
- `floating_authority_used:false`;
- canonical next-state SHA-256;
- canonical movement-receipt SHA-256.

Vessels are always serialized in lexicographic `ship_id` order. Maps are canonical-key sorted. Wall-clock timestamps are excluded from authoritative hashes.

## 18. Acceptance tests

Phase 5 cannot pass without all of the following.

1. **One-step replay:** identical state/orders/references produce byte-identical next state and receipt.
2. **Multi-step replay:** at least 100 macrosteps replay identically.
3. **Insertion-order independence:** vessel/map construction order cannot affect output.
4. **Inertial sanity:** a zero-thrust synthetic case follows the specified integrator under gravity only.
5. **Gravity direction:** +X point receives -X P17 gravity; mirrored points receive mirrored acceleration.
6. **Acceleration cap:** no applied thrust vector magnitude exceeds a vessel's Phase-3 cap.
7. **Class causal sensitivity:** under identical nonzero throttle/direction, vessels with different Phase-3 `max_accel_mm_s2` receive correspondingly different bounded thrust without class-name branching.
8. **Control-order causal sensitivity:** the accepted Phase-4 loyalist and rebel order sets map to their defined different throttle/direction requests when supplied valid references.
9. **Mirror symmetry:** mirrored synthetic state + mirrored references + identical orders remains sign-mirrored under P17 gravity and guidance where the guidance law is symmetry-preserving.
10. **CORDIC cardinal phases:** 0, quarter, half, and three-quarter turns resolve to exact signed-axis expectations; intermediate-phase tests remain within the pinned q12 error contract.
11. **Collision detection:** an outside-to-inside swept path produces deterministic earliest contact; a non-intersecting path does not.
12. **Rotated ellipsoid:** a case whose result changes between A/B-axis orientation proves P17 rotation materially affects geometry.
13. **Occultation:** line through P17 is occulted; line missing P17 is not; rotated-body case is deterministic.
14. **Withdrawal boundary:** equality is still inside; strictly greater radius is outside; crossing fraction is deterministic.
15. **No hidden enemy truth:** `EVASIVE_VECTOR` fails closed without a motion reference.
16. **No RNG / no binary-float authority:** static/runtime checks and receipts confirm both.
17. **Full-suite regression:** repository-wide tests pass on the accepted implementation head.

## 19. Phase boundary

Passing Phase 5 proves only deterministic physical movement and geometry.

It does **not** authorize sensing truth, EW, weapons, damage, morale, surrender, ceasefire, termination, reporting, or Run-0 execution.

Phase 6 may consume committed Phase-5 geometry and movement state. It may not retroactively alter Phase-5 motion.

**Run 0 remains blocked.**
