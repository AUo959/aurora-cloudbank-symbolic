"""Executable example coverage for the Narrative River CLI."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from modules.narrative_river.cli import main


def test_committed_example_runs_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    example = Path(__file__).parents[1] / "modules" / "narrative_river" / "examples" / "dark_star"
    inputs = tmp_path / "inputs"
    shutil.copytree(example, inputs)
    exit_code = main(
        [
            "run-scene",
            "--workspace",
            str(tmp_path / "dark-star"),
            "--allowed-root",
            str(tmp_path),
            "--scene-request",
            str(inputs / "scene_request.yaml"),
            "--canon-snapshot",
            str(inputs / "canon_snapshot.yaml"),
            "--axioms",
            str(inputs / "axioms.md"),
            "--draft",
            str(inputs / "draft.md"),
            "--delta",
            str(inputs / "scene_delta.yaml"),
        ]
    )
    assert exit_code == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["scene_closed"] is True
    assert Path(receipt["prompt_path"]).exists()
