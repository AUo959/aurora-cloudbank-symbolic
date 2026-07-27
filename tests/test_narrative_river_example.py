"""Executable example coverage for the Narrative River CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from modules.narrative_river.cli import main


def test_committed_example_runs_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    example = Path(__file__).parents[1] / "modules" / "narrative_river" / "examples" / "dark_star"
    exit_code = main(
        [
            "run-scene",
            "--workspace",
            str(tmp_path / "dark-star"),
            "--scene-request",
            str(example / "scene_request.yaml"),
            "--canon-snapshot",
            str(example / "canon_snapshot.yaml"),
            "--axioms",
            str(example / "axioms.md"),
            "--draft",
            str(example / "draft.md"),
            "--delta",
            str(example / "scene_delta.yaml"),
        ]
    )
    assert exit_code == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["scene_closed"] is True
    assert Path(receipt["prompt_path"]).exists()
