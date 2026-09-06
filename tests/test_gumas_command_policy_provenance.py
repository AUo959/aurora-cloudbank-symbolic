from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from simulation.runtime.gumas_command_policy.policy import _source_identity

pytestmark = pytest.mark.unit


def test_policy_source_identity_binds_policy_and_coefficients() -> None:
    identity = _source_identity()
    policy_path = Path(
        "simulation/runtime/gumas_command_policy/policy.py"
    ).resolve()
    coefficients_path = policy_path.with_name("coefficients.py")
    policy_bytes = policy_path.read_bytes()
    coefficients_bytes = coefficients_path.read_bytes()

    assert identity["policy_module_sha256"] == hashlib.sha256(
        policy_bytes
    ).hexdigest()
    assert identity["coefficient_table_sha256"] == hashlib.sha256(
        coefficients_bytes
    ).hexdigest()

    expected = hashlib.sha256()
    expected.update(b"policy.py\0")
    expected.update(policy_bytes)
    expected.update(b"\0coefficients.py\0")
    expected.update(coefficients_bytes)
    assert identity["bundle_sha256"] == expected.hexdigest()


def test_coefficient_change_would_change_bundle_identity() -> None:
    policy_path = Path(
        "simulation/runtime/gumas_command_policy/policy.py"
    ).resolve()
    coefficients_path = policy_path.with_name("coefficients.py")
    policy_bytes = policy_path.read_bytes()
    coefficients_bytes = coefficients_path.read_bytes()

    baseline = hashlib.sha256()
    baseline.update(b"policy.py\0")
    baseline.update(policy_bytes)
    baseline.update(b"\0coefficients.py\0")
    baseline.update(coefficients_bytes)

    changed = hashlib.sha256()
    changed.update(b"policy.py\0")
    changed.update(policy_bytes)
    changed.update(b"\0coefficients.py\0")
    changed.update(coefficients_bytes + b"\n# simulated coefficient mutation\n")

    assert changed.hexdigest() != baseline.hexdigest()
