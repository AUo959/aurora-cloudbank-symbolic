from __future__ import annotations

import ast
from pathlib import Path

import pytest

from simulation.runtime.gumas_battle_orchestrator import (
    PHASE9_CONTRACT_ID,
    PHASE9_VERSION,
    accepted_source_identities,
    source_identity,
)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "simulation/runtime/gumas_battle_orchestrator"
SPEC = ROOT / (
    "simulation/specs/" "GUMAS__SPEC__DETERMINISTIC_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER__v1.0__2026-08-15.md"
)


def _authoritative_runtime_files():
    return [path for path in sorted(RUNTIME.glob("*.py")) if not path.name.endswith("_smoke.py")]


def test_phase9_contract_and_source_identity_are_versioned():
    assert PHASE9_CONTRACT_ID == "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0"
    assert PHASE9_VERSION == "1.0.0"
    assert SPEC.is_file()
    identity = source_identity()
    assert set(identity["module_sha256"]) == {
        "__init__.py",
        "constants.py",
        "identity.py",
        "live_observation.py",
        "orchestrator.py",
    }
    assert len(identity["bundle_sha256"]) == 64
    assert set(accepted_source_identities()) == {
        "phase4_command_policy",
        "phase5_movement_geometry",
        "phase6_sensing_weapons",
        "phase7_damage_disposition",
        "phase8_morale_resolution",
        "phase9_orchestrator",
    }


def test_authoritative_runtime_does_not_import_acceptance_fixture_or_random():
    forbidden_imports = {"random", "simulation.runtime.gumas_acceptance_fixture"}
    for path in _authoritative_runtime_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        assert not imported.intersection(forbidden_imports), path


def test_runtime_contains_no_synthetic_control_observation_or_reporter_call():
    authoritative = "\n".join(path.read_text(encoding="utf-8") for path in _authoritative_runtime_files())
    assert "CONTROL_OBSERVATION" not in authoritative
    assert "load_acceptance_fixture" not in authoritative
    assert 'reporter_invoked": True' not in authoritative
    assert 'run0_executed": True' not in authoritative


def test_contract_names_information_flow_and_run0_prohibition():
    text = SPEC.read_text(encoding="utf-8")
    assert "LIVE_COMMAND_OBSERVATION_BRIDGE" in text
    assert "No opposing raw vessel field" in text
    assert "immutable hash-linked ledger" in text
    assert "Run 0 remains blocked" in text
