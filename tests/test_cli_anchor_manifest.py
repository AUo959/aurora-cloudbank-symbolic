import json
import tempfile
from pathlib import Path
import subprocess
import sys
import pytest

CLI = str(Path("tools/cli/aurora_dev_cli.py").resolve())
PY = sys.executable


@pytest.mark.unit
@pytest.mark.cli
def test_cli_manifest_json_and_dlp_export():
    # Use repo root to exercise integrated behavior
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_out = Path(tmpdir) / "cli_manifest.json"
        dlp_out = Path(tmpdir) / "cli_dlp.json"
        proc = subprocess.run(
            [PY, CLI, "manifest", "--json", "--output", str(manifest_out), "--dlp-manifest-out", str(dlp_out)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert proc.returncode == 0, proc.stderr
        data = json.loads(proc.stdout.splitlines()[-1])
        assert data["manifest_path"] == str(manifest_out)
        # DLP may or may not be exported depending on availability but path should be provided
        assert "dlp_manifest_path" in data

        # Files should exist
        assert manifest_out.exists()
        if data.get("dlp_manifest_path"):
            assert dlp_out.exists()


@pytest.mark.unit
@pytest.mark.cli
def test_cli_anchor_track_ext_json():
    proc = subprocess.run(
        [PY, CLI, "anchor", "track", "--ext", ".md", "--json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    assert proc.returncode == 0, proc.stderr
    # Ensure it prints JSON
    out = proc.stdout.strip().splitlines()[-1]
    parsed = json.loads(out)
    assert "total_files" in parsed and "total_anchors" in parsed
