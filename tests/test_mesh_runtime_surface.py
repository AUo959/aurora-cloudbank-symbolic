"""Regression checks for the current mesh runtime surface."""

from __future__ import annotations

import shutil
import sys
import asyncio
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.runtime import MeshRuntime  # noqa: E402


def test_mesh_runtime_initializes_from_agent_manifests(tmp_path: Path) -> None:
    """The current mesh runtime should initialize from the checked-in agent manifests."""

    mesh_src = PROJECT_ROOT / "config" / "mesh"
    mesh_dst = tmp_path / "config" / "mesh"
    mesh_dst.parent.mkdir(parents=True)
    shutil.copytree(mesh_src, mesh_dst, dirs_exist_ok=True)

    manifest_paths = sorted((mesh_src / "agents").glob("*.json"))
    assert manifest_paths, "expected checked-in mesh agent manifests"

    runtime = MeshRuntime(tmp_path)
    status = runtime.get_status()

    assert status["mesh_status"] == "operational"
    assert status["total_agents"] == len(manifest_paths)
    assert status["total_terminals"] > status["total_agents"]
    assert runtime.get_agent("captain alex line")["agent_id"] == "alex_thorne"
    assert runtime.get_terminal("core_development.carmen.term")["owner_agent_id"] == "carmen_rivas"
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


def test_mesh_runtime_routes_terminal_namespace_to_owner_channel(tmp_path: Path) -> None:
    """Personal Access Terminal aliases should use the owner's mesh channel."""

    mesh_src = PROJECT_ROOT / "config" / "mesh"
    mesh_dst = tmp_path / "config" / "mesh"
    mesh_dst.parent.mkdir(parents=True)
    shutil.copytree(mesh_src, mesh_dst, dirs_exist_ok=True)

    from src.mesh.models import MeshMessageRequest

    runtime = MeshRuntime(tmp_path)
    result = asyncio.run(
        runtime.send_message(
            MeshMessageRequest.from_dict(
                {
                    "to": "core_development.carmen.term",
                    "content": "Terminal route check.",
                }
            )
        )
    )

    assert result["status"] == "accepted"
    assert result["targets"] == ["carmen_rivas"]
    assert result["target_terminals"] == ["l1_carmen_rivas_terminal"]
    assert result["channel_id"] == "private:crew:carmen_rivas"
