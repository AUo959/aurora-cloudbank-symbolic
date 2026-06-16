"""L1 terminal registry reconciliation checks."""

from __future__ import annotations

import shutil
import sys
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


def test_l1_terminal_registry_keeps_owner_classes_separate(tmp_path: Path) -> None:
    runtime = MeshRuntime(copy_mesh_project(tmp_path))
    terminals = runtime.list_terminals()

    human_terminals = [terminal for terminal in terminals if terminal["owner_class"] == "human_l1"]
    assert len(human_terminals) == 41
    assert all(terminal["routable"] for terminal in human_terminals)
    assert all(terminal["mesh_route"]["channel_id"] for terminal in human_terminals)

    aurora = runtime.get_terminal("aurora.core.term")
    assert aurora["owner_agent_id"] == "aurora"
    assert aurora["owner_class"] == "ai_core"
    assert aurora["terminal_type"] == "aurora"

    l2_relays = [terminal for terminal in terminals if terminal["owner_class"] == "l2_relay"]
    assert {terminal["owner_display_name"] for terminal in l2_relays} >= {
        "ARCHY",
        "HALO",
        "LIORA",
        "OPPY",
        "RIVERTHREAD_808",
        "STARLING_AU",
    }
    assert any(terminal["owner_display_name"] == "HALO" and not terminal["routable"] for terminal in l2_relays)

    l3_frameworks = [terminal for terminal in terminals if terminal["owner_class"] == "l3_framework"]
    assert len(l3_frameworks) == 6
    assert not any(terminal["routable"] for terminal in l3_frameworks)

    unresolved = runtime.get_terminal("l1.unresolved.term")
    assert unresolved["owner_class"] == "unresolved"
    assert unresolved["owner_agent_id"] is None
    assert unresolved["routable"] is False
