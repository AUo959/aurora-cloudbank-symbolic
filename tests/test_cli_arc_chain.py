import json
import subprocess
import sys
from pathlib import Path

CLI = str(Path("tools/cli/aurora_dev_cli.py").resolve())
PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cli_arc_analyze_json_output():
    sample = Path(__file__).resolve().parent / "fixtures" / "arc_chain_sample.json"

    proc = subprocess.run(
        [PYTHON, CLI, "arc", "analyze", str(sample), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["thread_id"] == "aurora.thread.gumas.v2.4.1"
    assert payload["total_events"] == 3
    assert payload["validation_passed"] is True
    assert "drift_metrics" in payload
