"""L1 terminal registry reconciliation checks."""

from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.runtime import MeshRuntime  # noqa: E402


def copy_mesh_project(tmp_path: Path) -> Path:
    source = PROJECT_ROOT / "config" / "mesh"
    target = tmp_path / "config" / "mesh"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    return tmp_path


def test_l1_terminal_registry_human_terminals_are_routable(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))
    terminals = runtime.list_terminals()

    human_terminals = [terminal for terminal in terminals if terminal["owner_class"] == "human_l1"]
    checks.assertEqual(len(human_terminals), 41)
    checks.assertTrue(all(terminal["routable"] for terminal in human_terminals))
    checks.assertTrue(all(terminal["mesh_route"]["channel_id"] for terminal in human_terminals))


def test_l1_terminal_registry_ai_core_terminal(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))

    aurora = runtime.get_terminal("aurora.core.term")
    checks.assertEqual(aurora["owner_agent_id"], "aurora")
    checks.assertEqual(aurora["owner_class"], "ai_core")
    checks.assertEqual(aurora["terminal_type"], "aurora")


def test_l1_terminal_registry_l2_relay_terminals(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))
    terminals = runtime.list_terminals()

    l2_relays = [terminal for terminal in terminals if terminal["owner_class"] == "l2_relay"]
    checks.assertGreaterEqual(
        {terminal["owner_display_name"] for terminal in l2_relays},
        {
            "ARCHY",
            "HALO",
            "LIORA",
            "OPPY",
            "RIVERTHREAD_808",
            "STARLING_AU",
        },
    )
    checks.assertTrue(
        any(terminal["owner_display_name"] == "HALO" and not terminal["routable"] for terminal in l2_relays)
    )


def test_l1_terminal_registry_l3_frameworks_are_not_routable(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))
    terminals = runtime.list_terminals()

    l3_frameworks = [terminal for terminal in terminals if terminal["owner_class"] == "l3_framework"]
    checks.assertEqual(len(l3_frameworks), 6)
    checks.assertFalse(any(terminal["routable"] for terminal in l3_frameworks))


def test_l1_terminal_registry_unresolved_terminal(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))

    unresolved = runtime.get_terminal("l1.unresolved.term")
    checks.assertEqual(unresolved["owner_class"], "unresolved")
    checks.assertIsNone(unresolved["owner_agent_id"])
    checks.assertFalse(unresolved["routable"])
