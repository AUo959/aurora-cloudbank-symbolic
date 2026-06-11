"""Regression checks for the current mesh runtime surface."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.runtime import MeshRuntime


def test_mesh_runtime_initializes_from_agent_manifests(tmp_path: Path) -> None:
    """The current mesh runtime should initialize from the checked-in agent manifests."""

    manifest_src = PROJECT_ROOT / "config" / "mesh" / "agents"
    manifest_dst = tmp_path / "config" / "mesh" / "agents"
    manifest_dst.mkdir(parents=True)

    manifest_paths = sorted(manifest_src.glob("*.json"))
    assert manifest_paths, "expected checked-in mesh agent manifests"

    for path in manifest_paths:
        shutil.copy2(path, manifest_dst / path.name)

    runtime = MeshRuntime(tmp_path)
    status = runtime.get_status()

    assert status["mesh_status"] == "operational"
    assert status["total_agents"] == len(manifest_paths)
    assert runtime.get_agent("captain alex line")["agent_id"] == "alex_thorne"
    assert (tmp_path / "config" / "mesh" / "memory" / "alex_thorne.md").exists()


def test_pilot_is_default_sender_and_captain_stays_legacy_alias(tmp_path):
    """Canon ORION.ROLE.PILOT: defaults are Pilot; captain routes as legacy alias."""
    from src.mesh.models import MeshMessageRequest

    default = MeshMessageRequest.from_dict({"to": "alex_thorne", "content": "hi"})
    assert default.sender_id == "pilot"
    assert default.sender_name == "Pilot"

    legacy = MeshMessageRequest.from_dict(
        {"to": "alex_thorne", "content": "hi", "sender_id": "captain", "sender_name": "Captain"}
    )
    assert legacy.sender_name == "Captain"  # historical senders remain representable
