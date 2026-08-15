from __future__ import annotations

import json
from pathlib import Path

import pytest

from simulation.runtime.gumas_physical_t0.constructor import (
    _calibrate_physical,
    _inside_triaxial_ellipsoid,
    _normalize_q12,
    _round_half_even_fraction,
    _slot_offset_m,
)
from simulation.runtime.gumas_physical_t0.t0_smoke import _resolve_snapshot_output

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = (
    ROOT
    / "simulation/calibration/gumas/"
    "GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json"
)


def _calibration():
    return json.loads(CALIBRATION.read_text(encoding="utf-8"))


def test_integer_half_even_rounding_is_exact() -> None:
    assert _round_half_even_fraction(1, 2) == 0
    assert _round_half_even_fraction(3, 2) == 2
    assert _round_half_even_fraction(5, 2) == 2
    assert _round_half_even_fraction(7, 2) == 4
    assert _round_half_even_fraction(-3, 2) == -2


def test_zero_sum_formation_slots_are_exact_and_mirrored() -> None:
    calibration = _calibration()
    loyalist = [
        _slot_offset_m(slot, 850, "loyalist", calibration)
        for slot in range(1, 19)
    ]
    rebel = [
        _slot_offset_m(slot, 850, "rebel", calibration)
        for slot in range(1, 19)
    ]
    assert [sum(vector[axis] for vector in loyalist) for axis in range(3)] == [
        0,
        0,
        0,
    ]
    assert rebel == [[-axis for axis in vector] for vector in loyalist]
    assert len({tuple(vector) for vector in loyalist}) == 18


def test_global_calibration_responds_to_capability_without_class_branch() -> None:
    calibration = _calibration()
    base = {
        "firepower": 500,
        "defense": 500,
        "mobility": 500,
        "sensors": 500,
        "stealth": 500,
        "electronic_warfare": 500,
        "carrier_projection": 500,
        "support": 500,
        "boarding": 500,
        "command": 500,
        "range": 500,
        "endurance": 500,
    }
    faster = dict(base)
    faster["mobility"] = 600
    physical_base, direct_base = _calibrate_physical(base, calibration)
    physical_faster, direct_faster = _calibrate_physical(faster, calibration)
    assert physical_faster["max_accel_mm_s2"] > physical_base["max_accel_mm_s2"]
    for key in physical_base:
        if key != "max_accel_mm_s2":
            assert physical_faster[key] == physical_base[key]
    assert direct_faster == direct_base


def test_ellipsoid_membership_uses_exact_integer_geometry() -> None:
    axes = [190_000, 135_000, 90_000]
    assert _inside_triaxial_ellipsoid([0, 0, 0], axes)
    assert _inside_triaxial_ellipsoid([190_000, 0, 0], axes)
    assert not _inside_triaxial_ellipsoid([190_001, 0, 0], axes)
    assert not _inside_triaxial_ellipsoid(
        [6_500_000, 1_600_000, -500_000], axes
    )


def test_q12_attitude_normalization_is_repeatable() -> None:
    first = _normalize_q12([13_000_000, 3_200_000, -1_000_000])
    second = _normalize_q12([13_000_000, 3_200_000, -1_000_000])
    assert first == second
    assert any(first)


def test_snapshot_output_resolves_beneath_allowed_root(tmp_path: Path) -> None:
    allowed_root = tmp_path / "repo"
    allowed_root.mkdir()

    assert _resolve_snapshot_output(
        Path("evidence/t0.json"),
        root=allowed_root,
    ) == allowed_root / "evidence/t0.json"
    assert _resolve_snapshot_output(
        allowed_root / "direct.json",
        root=allowed_root,
    ) == allowed_root / "direct.json"


def test_snapshot_output_rejects_parent_and_symlink_escapes(tmp_path: Path) -> None:
    allowed_root = tmp_path / "repo"
    allowed_root.mkdir()

    with pytest.raises(ValueError, match="outside allowed root"):
        _resolve_snapshot_output(Path("../outside.json"), root=allowed_root)

    outside = tmp_path / "outside"
    outside.mkdir()
    (allowed_root / "escape").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="outside allowed root"):
        _resolve_snapshot_output(Path("escape/t0.json"), root=allowed_root)
