import json
import subprocess
import sys
from pathlib import Path


CLI = str(Path("tools/cli/aurora_dev_cli.py").resolve())
PY = sys.executable


def test_cli_status_json_basic():
    proc = subprocess.run(
        [PY, CLI, "status", "--json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    assert proc.returncode == 0, proc.stderr
    # Ensure it prints JSON
    out = proc.stdout.strip().splitlines()[-1]
    data = json.loads(out)
    assert "total_files" in data
    assert "total_anchors" in data
    assert "lineages_mapped" in data
    assert "drift" in data and isinstance(data["drift"], dict)
    assert "repo" in data and "version" in data
