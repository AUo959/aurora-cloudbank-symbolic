"""Regression checks for the current mesh runtime surface."""

from __future__ import annotations

import shutil
import sys
import asyncio
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.runtime import MeshRuntime  # noqa: E402


CHECKS = unittest.TestCase()


def test_mesh_runtime_initializes_from_agent_manifests(tmp_path: Path) -> None:
    """The current mesh runtime should initialize from the checked-in agent manifests."""

    mesh_src = PROJECT_ROOT / "config" / "mesh"
    mesh_dst = tmp_path / "config" / "mesh"
    mesh_dst.parent.mkdir(parents=True)
    shutil.copytree(mesh_src, mesh_dst, dirs_exist_ok=True)

    manifest_paths = sorted((mesh_src / "agents").glob("*.json"))
    CHECKS.assertTrue(manifest_paths, "expected checked-in mesh agent manifests")

    runtime = MeshRuntime(tmp_path)
    status = runtime.get_status()

    checks = unittest.TestCase()
    checks.assertEqual(status["mesh_status"], "operational")
    checks.assertEqual(status["total_agents"], len(manifest_paths))
    checks.assertGreater(status["total_terminals"], status["total_agents"])
    checks.assertEqual(runtime.get_agent("captain alex line")["agent_id"], "Alex Thorne")
    checks.assertEqual(runtime.get_terminal("core_development.carmen.term")["owner_agent_id"], "carmen_rivas")
    checks.assertTrue((tmp_path / "config" / "mesh" / "memory" / "alex_thorne.md").exists())


def test_pilot_is_default_sender_and_captain_stays_legacy_alias(tmp_path):
    """Canon ORION.ROLE.PILOT: defaults are Pilot; captain routes as legacy alias."""
    from src.mesh.models import MeshMessageRequest

    default = MeshMessageRequest.from_dict({"to": "alex_thorne", "content": "hi"})
    CHECKS.assertEqual(default.sender_id, "pilot")
    CHECKS.assertEqual(default.sender_name, "Pilot")

    legacy = MeshMessageRequest.from_dict(
        {"to": "alex_thorne", "content": "hi", "sender_id": "captain", "sender_name": "Captain"}
    )
    CHECKS.assertEqual(legacy.sender_name, "Captain")  # historical senders remain representable


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

    checks = unittest.TestCase()
    checks.assertEqual(result["status"], "accepted")
    checks.assertEqual(result["targets"], ["carmen_rivas"])
    checks.assertEqual(result["target_terminals"], ["l1_carmen_rivas_terminal"])
    checks.assertEqual(result["channel_id"], "private:crew:carmen_rivas")
