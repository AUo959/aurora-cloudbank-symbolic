from __future__ import annotations

import ast
from pathlib import Path

import pytest

from simulation.runtime.gumas_factual_reporter import (
    PHASE10_CONTRACT_ID,
    PHASE10_VERSION,
    source_identity,
)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "simulation/runtime/gumas_factual_reporter"
SPEC = ROOT / (
    "simulation/specs/"
    "GUMAS__SPEC__DETERMINISTIC_FACTUAL_REPORTER_EVIDENCE_EXPORT__v1.0__2026-08-15.md"
)


def _authoritative_runtime_files():
    return [path for path in sorted(RUNTIME.glob("*.py")) if not path.name.endswith("_smoke.py")]


def test_phase10_contract_and_source_identity_are_versioned():
    assert PHASE10_CONTRACT_ID == "GUMAS_DETERMINISTIC_FACTUAL_REPORTER_EVIDENCE_EXPORT_v1_0"
    assert PHASE10_VERSION == "1.0.0"
    assert SPEC.is_file()
    identity = source_identity()
    assert set(identity["module_sha256"]) == {
        "__init__.py",
        "constants.py",
        "identity.py",
        "validation.py",
        "projection.py",
        "rendering.py",
        "exporter.py",
    }
    assert len(identity["bundle_sha256"]) == 64


def test_authoritative_reporter_has_no_transition_or_nondeterministic_imports():
    forbidden_prefixes = {
        "datetime",
        "os",
        "random",
        "requests",
        "socket",
        "subprocess",
        "time",
        "urllib",
        "simulation.runtime.gumas_acceptance_fixture",
        "simulation.runtime.gumas_battle_orchestrator",
        "simulation.runtime.gumas_command_policy",
        "simulation.runtime.gumas_movement_geometry",
        "simulation.runtime.gumas_sensing_weapons",
        "simulation.runtime.gumas_damage_disposition",
        "simulation.runtime.gumas_morale_resolution",
    }
    authoritative_text = []
    for path in _authoritative_runtime_files():
        text = path.read_text(encoding="utf-8")
        authoritative_text.append(text)
        tree = ast.parse(text)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        assert not {
            name
            for name in imported
            if any(name == prefix or name.startswith(f"{prefix}.") for prefix in forbidden_prefixes)
        }, path
    assert "execute_macrostep" not in "\n".join(authoritative_text)


def test_contract_names_training_pair_provenance_and_execution_boundaries():
    text = SPEC.read_text(encoding="utf-8")
    assert "command_observation" in text
    assert "statement-to-artifact evidence index" in text
    assert "simulation_truth_v1" in text
    assert "public_summary_v1" in text
    assert "no second `execute_macrostep` call" in text
    assert "Run 0 remains blocked" in text
