"""Canon consistency gate.

Asserts that the three surfaces carrying Orion Station identity agree:

1. the canon contract (``config/canonical_validation.yaml`` — staff registry
   and ORION core identity invariants),
2. the mesh agent manifests (``config/mesh/agents/*.json``), and
3. the mesh runtime's embedded ``ORION_CORE`` constants.

This is the enforcement point that makes the narrative layer load-bearing:
canon drift on any of these surfaces turns CI red. See the control-plane
ADR ``ORION__ADR_LITE__NARRATIVE_LAYER_PROMOTION__v1.0__2026-06-10``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CANON_PATH = PROJECT_ROOT / "config" / "canonical_validation.yaml"
AGENTS_DIR = PROJECT_ROOT / "config" / "mesh" / "agents"
MEMORY_DIR = PROJECT_ROOT / "config" / "mesh" / "memory"


def load_canon() -> dict:
    return yaml.safe_load(CANON_PATH.read_text())["canonical_spec"]


def load_manifests() -> dict:
    manifests = {}
    for path in sorted(AGENTS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        manifests[data["id"]] = data
    return manifests


@pytest.mark.critical
def test_canon_contract_exists_with_identity_invariants() -> None:
    canon = load_canon()
    core = canon["core_parameters"]
    assert core["anchor_seed"] == "EOS_SEED_ORION"
    assert core["ethics_protocol"] == "Picard_Delta_3"
    assert core["continuity_seal"].startswith("Aurora_Continuity_Seal")
    assert float(core["drift_lock"]) == 0.0


@pytest.mark.critical
def test_runtime_core_matches_canon_contract() -> None:
    from src.mesh.runtime import ORION_CORE

    core = load_canon()["core_parameters"]
    for key, value in ORION_CORE.items():
        if key in core:
            assert core[key] == value, (
                f"runtime ORION_CORE[{key!r}]={value!r} disagrees with canonical_validation.yaml"
            )


@pytest.mark.critical
def test_canon_staff_registry_seats_are_filled_in_mesh() -> None:
    """Every named canon command seat must have a mesh agent with that display name."""
    staff = load_canon()["staff_registry"]
    mesh_names = {m["display_name"].lower() for m in load_manifests().values()}
    missing = []
    for seat, name in staff.items():
        if "/" in name or name.lower().startswith(("assigned", "rotating")):
            continue  # rotating seats are institutional, not characters
        bare = name.replace("Dr. ", "").replace("Lt. ", "").strip().lower()
        if bare not in mesh_names and name.strip().lower() not in mesh_names:
            missing.append(f"{seat}: {name}")
    assert not missing, f"canon command seats without mesh agents: {missing}"


@pytest.mark.critical
def test_aurora_seat_is_canonical() -> None:
    manifests = load_manifests()
    assert "aurora" in manifests, "Aurora (aurora_core, always-on arbitration) must hold a mesh seat"
    aurora = manifests["aurora"]
    assert "station control plane" in [a.lower() for a in aurora["aliases"]]
    for memory_file in aurora.get("memory_files", []):
        assert (PROJECT_ROOT / memory_file).exists(), f"missing Aurora memory: {memory_file}"


@pytest.mark.critical
def test_every_mesh_agent_has_memory_grounding() -> None:
    """Each boarded agent's declared memory files must exist and be non-empty."""
    problems = []
    for agent_id, manifest in load_manifests().items():
        for relative in manifest.get("memory_files", []):
            target = PROJECT_ROOT / relative
            if not target.exists() or not target.read_text().strip():
                problems.append(f"{agent_id}: {relative}")
    assert not problems, f"agents with missing/empty memory files: {problems}"
