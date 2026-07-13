"""Regression checks for Personal Access Terminal mesh compatibility."""

from __future__ import annotations

import shutil
import sys
import asyncio
import unittest
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.runtime import MeshRuntime  # noqa: E402
from src.mesh.models import MeshMessageRequest  # noqa: E402
from src.mesh.terminals import MeshTerminalRoute, is_personnel_attention_tag  # noqa: E402


def copy_mesh_project(tmp_path: Path) -> Path:
    source = PROJECT_ROOT / "config" / "mesh"
    target = tmp_path / "config" / "mesh"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    return tmp_path


def test_pat_live_subset_is_overlay_not_full_terminal_universe(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))
    terminals = runtime.list_terminals()

    pat_terminals = [terminal for terminal in terminals if terminal["pat_overlay"]]
    checks.assertEqual(len(pat_terminals), 9)
    checks.assertGreater(len(terminals), len(pat_terminals))

    dev_group = runtime.get_terminal("aurora.dev.code.query")
    checks.assertIs(dev_group["terminal_group"], True)
    checks.assertEqual(dev_group["terminal_id"], "aurora.dev.code.query")
    checks.assertEqual(dev_group["terminal_namespace"], "aurora.dev.code.query")
    checks.assertEqual(
        {member["owner_agent_id"] for member in dev_group["members"]},
        {"carmen_rivas", "ira_menon", "tobias_qin"},
    )

    alternate_spelling = runtime.get_terminal("  AURORA-dev-code-query  ")
    checks.assertEqual(alternate_spelling["terminal_id"], dev_group["terminal_id"])
    checks.assertEqual(alternate_spelling["terminal_namespace"], dev_group["terminal_namespace"])

    carmen = runtime.get_terminal("core_development.carmen.term")
    checks.assertEqual(carmen["owner_agent_id"], "carmen_rivas")
    checks.assertEqual(carmen["pat_overlay"]["anchor_node"], "aurora.dev.code.query")
    checks.assertEqual(carmen["mesh_route"]["channel_id"], "private:crew:carmen_rivas")

    routed = asyncio.run(
        runtime.send_message(
            MeshMessageRequest.from_dict({"to": "aurora.dev.code.query", "content": "PAT anchor check."})
        )
    )
    checks.assertEqual(sorted(routed["targets"]), ["carmen_rivas", "ira_menon", "tobias_qin"])
    checks.assertEqual(
        sorted(routed["target_terminals"]),
        ["l1_carmen_rivas_terminal", "l1_ira_menon_terminal", "l1_tobias_qin_terminal"],
    )
    checks.assertEqual(routed["channel_id"], "aurora.dev.code.query")


def test_personnel_attention_tags_do_not_resolve_as_terminal_routes(tmp_path: Path) -> None:
    checks = unittest.TestCase()
    runtime = MeshRuntime(copy_mesh_project(tmp_path))
    tag = "{{@Carmen-Rivas:::Adhesive flow rate nominal}}"

    checks.assertTrue(is_personnel_attention_tag(tag))
    with pytest.raises(ValueError, match="Personnel Attention Tags"):
        runtime.get_terminal(tag)


def test_terminal_route_null_strings_use_valid_defaults() -> None:
    checks = unittest.TestCase()
    route = MeshTerminalRoute.from_dict({"channel_id": None, "route_kind": None})

    checks.assertEqual(route.channel_id, "")
    checks.assertEqual(route.route_kind, "mesh_agent")
