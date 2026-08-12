from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


EXPECTED_REPLAY_SHA256 = "de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea"


def test_restored_v2_combat_contract_smoke() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "simulation/runtime/gumas_v2_restored/restoration_smoke.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=script.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    receipt = json.loads(completed.stdout.strip().splitlines()[-1])
    assert receipt["status"] == "ok"
    assert receipt["restoration_version"] == "2.0.1-restored.1"
    assert receipt["normalized_replay_sha256"] == EXPECTED_REPLAY_SHA256
    assert receipt["combat_turns"] == 1
    assert receipt["automatic_condition"] == "open_space"
    assert receipt["explicit_condition"] == "chokepoint"
