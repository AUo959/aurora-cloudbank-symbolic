"""Integer-only geometry primitives for GUMAS movement/geometry v1.0."""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from .constants import (
    CORDIC_ANGLE_Q,
    CORDIC_ATAN_TURN_Q62,
    CORDIC_K_INV_Q60,
    CORDIC_XY_Q,
    P17_MU_UM3_S2,
    P17_ROTATION_PERIOD_MS,
    Q12,
)

Vector3 = tuple[int, int, int]


class GeometryError(RuntimeError):
    """Raised when authoritative geometry cannot be evaluated safely."""


def vec3(values: Sequence[int]) -> Vector3:
    if len(values) != 3:
        raise GeometryError("3-vector required")
    return int(values[0]), int(values[1]), int(values[2])


def round_half_even_fraction(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise GeometryError("rounding denominator must be positive")
    sign = -1 if numerator < 0 else 1
    quotient, remainder = divmod(abs(int(numerator)), int(denominator))
    doubled = remainder * 2
    if doubled > denominator or (doubled == denominator and quotient % 2):
        quotient += 1
    return sign * quotient


def ceil_fraction(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise GeometryError("ceiling denominator must be positive")
    return -((-int(numerator)) // int(denominator))


def nearest_isqrt(value: int) -> int:
    if value < 0:
        raise GeometryError("square root of negative integer")
    lower = math.isqrt(value)
    upper = lower + 1
    lower_error = value - lower * lower
    upper_error = upper * upper - value
    if lower_error < upper_error:
        return lower
    if upper_error < lower_error:
        return upper
    return lower if lower % 2 == 0 else upper


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    a = vec3(left)
    b = vec3(right)
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def add(left: Sequence[int], right: Sequence[int]) -> Vector3:
    a = vec3(left)
    b = vec3(right)
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def subtract(left: Sequence[int], right: Sequence[int]) -> Vector3:
    a = vec3(left)
    b = vec3(right)
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def negate(vector: Sequence[int]) -> Vector3:
    a = vec3(vector)
    return -a[0], -a[1], -a[2]


def cross(left: Sequence[int], right: Sequence[int]) -> Vector3:
    a = vec3(left)
    b = vec3(right)
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def norm_nearest(vector: Sequence[int]) -> int:
    a = vec3(vector)
    return nearest_isqrt(dot(a, a))


def normalize_q12(vector: Sequence[int]) -> Vector3:
    a = vec3(vector)
    norm = norm_nearest(a)
    if norm == 0:
        raise GeometryError("cannot normalize zero vector")
    return (
        round_half_even_fraction(a[0] * Q12, norm),
        round_half_even_fraction(a[1] * Q12, norm),
        round_half_even_fraction(a[2] * Q12, norm),
    )


def scale_q12(vector_q12: Sequence[int], magnitude: int) -> Vector3:
    a = vec3(vector_q12)
    return (
        round_half_even_fraction(a[0] * magnitude, Q12),
        round_half_even_fraction(a[1] * magnitude, Q12),
        round_half_even_fraction(a[2] * magnitude, Q12),
    )


def clamp_vector_magnitude(vector: Sequence[int], maximum: int) -> Vector3:
    if maximum < 0:
        raise GeometryError("negative vector cap")
    a = vec3(vector)
    magnitude = norm_nearest(a)
    if magnitude <= maximum:
        return a
    if maximum == 0:
        return (0, 0, 0)
    return scale_q12(normalize_q12(a), maximum)


def cordic_sin_cos_q12(phase_turn_q12: int) -> tuple[int, int]:
    """Return (sin, cos) in q12 using committed integer CORDIC constants."""
    phase = int(phase_turn_q12) % Q12
    quarter = Q12 // 4
    quadrant = phase // quarter
    remainder = phase - quadrant * quarter
    cardinal = (
        (0, Q12),
        (Q12, 0),
        (0, -Q12),
        (-Q12, 0),
    )
    if remainder == 0:
        return cardinal[quadrant]

    z = round_half_even_fraction(remainder * CORDIC_ANGLE_Q, Q12)
    x = CORDIC_K_INV_Q60
    y = 0
    for index, angle in enumerate(CORDIC_ATAN_TURN_Q62):
        if z >= 0:
            next_x = x - (y >> index)
            next_y = y + (x >> index)
            z -= angle
        else:
            next_x = x + (y >> index)
            next_y = y - (x >> index)
            z += angle
        x, y = next_x, next_y

    cos_base = round_half_even_fraction(x * Q12, CORDIC_XY_Q)
    sin_base = round_half_even_fraction(y * Q12, CORDIC_XY_Q)
    if quadrant == 0:
        sin_value, cos_value = sin_base, cos_base
    elif quadrant == 1:
        sin_value, cos_value = cos_base, -sin_base
    elif quadrant == 2:
        sin_value, cos_value = -sin_base, -cos_base
    else:
        sin_value, cos_value = -cos_base, sin_base
    return sin_value, cos_value


def phase_at_elapsed_ms(elapsed_ms: int, *, phase_t0_q12: int = 0) -> int:
    if elapsed_ms < 0:
        raise GeometryError("elapsed time cannot be negative")
    delta = round_half_even_fraction(elapsed_ms * Q12, P17_ROTATION_PERIOD_MS)
    return (int(phase_t0_q12) + delta) % Q12


def inertial_to_body(
    position_um: Sequence[int], phase_turn_q12: int
) -> Vector3:
    x, y, z = vec3(position_um)
    sin_q12, cos_q12 = cordic_sin_cos_q12(phase_turn_q12)
    body_x = round_half_even_fraction(cos_q12 * x + sin_q12 * y, Q12)
    body_y = round_half_even_fraction(-sin_q12 * x + cos_q12 * y, Q12)
    return body_x, body_y, z


def body_to_inertial(
    position_um: Sequence[int], phase_turn_q12: int
) -> Vector3:
    x, y, z = vec3(position_um)
    sin_q12, cos_q12 = cordic_sin_cos_q12(phase_turn_q12)
    inertial_x = round_half_even_fraction(cos_q12 * x - sin_q12 * y, Q12)
    inertial_y = round_half_even_fraction(sin_q12 * x + cos_q12 * y, Q12)
    return inertial_x, inertial_y, z


def ellipsoid_implicit_scaled(
    body_position_um: Sequence[int], axes_um: Sequence[int]
) -> int:
    x, y, z = vec3(body_position_um)
    a, b, c = vec3(axes_um)
    if min(a, b, c) <= 0:
        raise GeometryError("ellipsoid axes must be positive")
    a2, b2, c2 = a * a, b * b, c * c
    return (
        x * x * b2 * c2
        + y * y * a2 * c2
        + z * z * a2 * b2
        - a2 * b2 * c2
    )


def _ellipsoid_segment_coefficients(
    p0: Sequence[int], p1: Sequence[int], axes_um: Sequence[int]
) -> tuple[int, int, int]:
    x0, y0, z0 = vec3(p0)
    x1, y1, z1 = vec3(p1)
    a, b, c = vec3(axes_um)
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    a2, b2, c2 = a * a, b * b, c * c
    wx, wy, wz = b2 * c2, a2 * c2, a2 * b2
    qa = dx * dx * wx + dy * dy * wy + dz * dz * wz
    qb = 2 * (x0 * dx * wx + y0 * dy * wy + z0 * dz * wz)
    qc = x0 * x0 * wx + y0 * y0 * wy + z0 * z0 * wz - a2 * b2 * c2
    return qa, qb, qc


def _quadratic_scaled_value(a: int, b: int, c: int, t_q12: int) -> int:
    return a * t_q12 * t_q12 + b * t_q12 * Q12 + c * Q12 * Q12


def segment_ellipsoid_first_contact_t_q12(
    p0_body_um: Sequence[int],
    p1_body_um: Sequence[int],
    axes_um: Sequence[int],
) -> int | None:
    """Earliest quantized contact fraction on [0,1], or None."""
    qa, qb, qc = _ellipsoid_segment_coefficients(
        p0_body_um, p1_body_um, axes_um
    )
    if qc <= 0:
        return 0
    if qa == 0:
        return None
    end_value = qa + qb + qc
    discriminant = qb * qb - 4 * qa * qc
    vertex_inside_interval = qb < 0 and -qb < 2 * qa
    if discriminant < 0:
        return None
    if end_value > 0 and not vertex_inside_interval:
        return None
    if discriminant == 0:
        candidate = round_half_even_fraction(-qb * Q12, 2 * qa)
        if 0 <= candidate <= Q12:
            return candidate
        return None

    sqrt_scaled = math.isqrt(discriminant * Q12 * Q12)
    candidate = ceil_fraction(-qb * Q12 - sqrt_scaled, 2 * qa)
    lower = max(0, candidate - 4)
    upper = min(Q12, candidate + 4)
    for t_q12 in range(lower, upper + 1):
        if _quadratic_scaled_value(qa, qb, qc, t_q12) <= 0:
            return t_q12
    if end_value <= 0:
        return Q12
    return None


def segment_ellipsoid_occulted(
    p0_body_um: Sequence[int],
    p1_body_um: Sequence[int],
    axes_um: Sequence[int],
) -> bool:
    """Whether the open segment intersects/touches the ellipsoid."""
    qa, qb, qc = _ellipsoid_segment_coefficients(
        p0_body_um, p1_body_um, axes_um
    )
    if qa == 0:
        return False
    discriminant = qb * qb - 4 * qa * qc
    if discriminant < 0:
        return False
    if discriminant == 0:
        root_q12 = round_half_even_fraction(-qb * Q12, 2 * qa)
        return 0 < root_q12 < Q12
    sqrt_scaled = math.isqrt(discriminant * Q12 * Q12)
    root1 = round_half_even_fraction(-qb * Q12 - sqrt_scaled, 2 * qa)
    root2 = round_half_even_fraction(-qb * Q12 + sqrt_scaled, 2 * qa)
    if root1 > root2:
        root1, root2 = root2, root1
    return max(root1, 0) < min(root2, Q12)


def interpolate_q12(
    start: Sequence[int], end: Sequence[int], fraction_q12: int
) -> Vector3:
    if not 0 <= fraction_q12 <= Q12:
        raise GeometryError("interpolation fraction outside q12 bounds")
    a = vec3(start)
    b = vec3(end)
    return (
        a[0] + round_half_even_fraction((b[0] - a[0]) * fraction_q12, Q12),
        a[1] + round_half_even_fraction((b[1] - a[1]) * fraction_q12, Q12),
        a[2] + round_half_even_fraction((b[2] - a[2]) * fraction_q12, Q12),
    )


def gravity_acceleration_um_s2(position_um: Sequence[int]) -> Vector3:
    r = vec3(position_um)
    radius = norm_nearest(r)
    if radius <= 0:
        raise GeometryError("gravity undefined at P17 center")
    denominator = radius * radius * radius
    return (
        round_half_even_fraction(-P17_MU_UM3_S2 * r[0], denominator),
        round_half_even_fraction(-P17_MU_UM3_S2 * r[1], denominator),
        round_half_even_fraction(-P17_MU_UM3_S2 * r[2], denominator),
    )


def separation_um(left: Sequence[int], right: Sequence[int]) -> int:
    return norm_nearest(subtract(right, left))


def closing_rate_um_s(
    left_position: Sequence[int],
    left_velocity: Sequence[int],
    right_position: Sequence[int],
    right_velocity: Sequence[int],
) -> int:
    delta_position = subtract(right_position, left_position)
    distance = norm_nearest(delta_position)
    if distance == 0:
        raise GeometryError("closing rate undefined for coincident distinct points")
    delta_velocity = subtract(right_velocity, left_velocity)
    return round_half_even_fraction(-dot(delta_position, delta_velocity), distance)


def mean_vector_round_half_even(vectors: Iterable[Sequence[int]]) -> Vector3:
    items = [vec3(item) for item in vectors]
    if not items:
        raise GeometryError("cannot average empty vector set")
    count = len(items)
    return (
        round_half_even_fraction(sum(item[0] for item in items), count),
        round_half_even_fraction(sum(item[1] for item in items), count),
        round_half_even_fraction(sum(item[2] for item in items), count),
    )


def segment_sphere_exit_t_q12(
    p0: Sequence[int], p1: Sequence[int], radius: int
) -> int | None:
    """First inside->outside crossing fraction for a sphere, if present."""
    start = vec3(p0)
    end = vec3(p1)
    r2 = radius * radius
    start_inside = dot(start, start) <= r2
    end_outside = dot(end, end) > r2
    if not (start_inside and end_outside):
        return None
    delta = subtract(end, start)
    qa = dot(delta, delta)
    qb = 2 * dot(start, delta)
    qc = dot(start, start) - r2
    discriminant = qb * qb - 4 * qa * qc
    if qa == 0 or discriminant < 0:
        return None
    sqrt_scaled = math.isqrt(discriminant * Q12 * Q12)
    candidate = round_half_even_fraction(-qb * Q12 + sqrt_scaled, 2 * qa)
    return max(0, min(Q12, candidate))
