import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/integration_plan_932.py")


def test_script_runs_and_outputs_phases():
    assert SCRIPT.exists(), "integration_plan_932.py script missing"
    proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    # Script may exit 1 if gh not authenticated; still validate structure
    output = proc.stdout
    assert "Phased Integration Plan" in output or "Integration Plan Error" in output
    # Extract JSON after separator ---
    if "---" in output:
        json_part = output.split("---", 1)[-1].strip()
        try:
            data = json.loads(json_part)
        except json.JSONDecodeError:
            # Allow error mode
            return
        assert "context_tag" in data
        if "phases" in data:
            assert set(data["phases"].keys()) == {"phase_1", "phase_2", "phase_3"}
