from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AURORA_DIR = PROJECT_ROOT / ".aurora"


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_retired_builder_refuses_to_construct_live_state():
    builder = _load_module(AURORA_DIR / "build_canonical_state.py", "retired_state_builder")

    with pytest.raises(RuntimeError, match="builder is retired"):
        builder.build_canonical_state()


@pytest.mark.unit
def test_retired_builder_status_is_read_only_and_preserves_old_claims_as_history():
    result = subprocess.run(
        [sys.executable, str(AURORA_DIR / "build_canonical_state.py"), "--status"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "retired_builder"
    assert payload["legacy_state_genesis_authority"] is False
    assert (
        payload["orbital_locus_status"]
        == "resolved_siting_class_exact_point_unresolved"
    )
    assert payload["historical_current_crew_81"].startswith("quarantined")


@pytest.mark.unit
def test_retired_builder_default_execution_fails_without_rewriting_state():
    state_path = AURORA_DIR / "SIMULATION_STATE.json"
    before = state_path.read_bytes()

    result = subprocess.run(
        [sys.executable, str(AURORA_DIR / "build_canonical_state.py")],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "will not rewrite" in result.stderr
    assert state_path.read_bytes() == before


@pytest.mark.unit
def test_legacy_loader_cannot_persist_or_embody_pilot():
    loader = _load_module(AURORA_DIR / "load_simulation.py", "retired_simulation_loader")

    assert loader.save_simulation_state({"simulation": {"status": "ACTIVE"}}) is False
    routed = loader.route_to_location("bridge")
    assert routed["success"] is False
    assert routed["pilot_embodied"] is False
    assert routed["replacement"] == "OrionL1Runtime.observe(focus)"


@pytest.mark.unit
def test_current_init_protocol_contains_no_legacy_genesis_claims():
    protocol = (AURORA_DIR / "SIMULATION_INIT_PROTOCOL.md").read_text(encoding="utf-8")

    assert "**Pilot:** User — Directs simulation" not in protocol
    assert "**Station:** Orion Station (L4 Lagrange Point)" not in protocol
    assert "36 human + 6 L2 + 6 L3" not in protocol
    assert "python .aurora/init_l1.py preflight" in protocol
    assert "python .aurora/init_l1.py init --seed 1337" in protocol
