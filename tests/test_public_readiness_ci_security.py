from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_cross_platform_ci_uses_exact_wheel_only_locks():
    workflow = (WORKFLOWS / "cross-platform-paths.yml").read_text(encoding="utf-8")
    assert "--only-binary=:all:" in workflow
    assert "requirements-runtime-lock.txt" in workflow
    assert "requirements-test-lock.txt" in workflow
    assert "pip install --upgrade pip" not in workflow

    for lock_name in ("requirements-runtime-lock.txt", "requirements-test-lock.txt"):
        lock = (ROOT / lock_name).read_text(encoding="utf-8")
        requirements = [
            line for line in lock.splitlines() if line and not line.startswith(("#", " "))
        ]
        assert requirements
        assert all("==" in line for line in requirements)


def test_queue_workflows_pin_actions_and_python_packages():
    for workflow_name in ("queue-issue-ingestion.yml", "queue-validation.yml"):
        workflow = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
        action_refs = re.findall(r"uses: [^@\s]+@([^\s]+)", workflow)
        assert action_refs
        assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)
        assert "--only-binary=:all:" in workflow
        assert "pip install --upgrade pip" not in workflow


def test_constellation_ci_executes_only_installed_node_tools():
    workflow = (WORKFLOWS / "constellation-ci.yml").read_text(encoding="utf-8")
    assert "npx " not in workflow
    assert workflow.count("npm ci --ignore-scripts") == 3
    assert "./node_modules/.bin/tsc" in workflow


def test_cloudhub_image_uses_hash_locked_wheels():
    dockerfile = (ROOT / "Dockerfile_aurora_gui_cloudhub").read_text(encoding="utf-8")
    dockerignore = (ROOT / "Dockerfile_aurora_gui_cloudhub.dockerignore").read_text(
        encoding="utf-8"
    )
    assert "requirements-hashed.txt" in dockerfile
    assert "--only-binary=:all:" in dockerfile
    assert "--require-hashes" in dockerfile
    assert "!requirements-hashed.txt" in dockerignore
    assert "!requirements.txt\n" not in dockerignore
