"""Smoke tests for the canonical dependency updater."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_dependency_scan_reports_fastapi_presence(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_path = tmp_path / "dependency_status.json"

    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "gitwiz_dependency_updater.py"),
            "--scan",
            "--output",
            str(output_path),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["python"]["status"] == "ready"
    assert report["python"]["required_packages"]["fastapi"]["declared"] is True
    assert report["python"]["required_packages"]["fastapi"]["installed"] is True
