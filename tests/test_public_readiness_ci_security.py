from __future__ import annotations

import re
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CHECK = TestCase()


def test_cross_platform_ci_uses_exact_wheel_only_locks():
    workflow = (WORKFLOWS / "cross-platform-paths.yml").read_text(encoding="utf-8")
    CHECK.assertIn("--only-binary=:all:", workflow)
    CHECK.assertIn("--require-hashes", workflow)
    CHECK.assertIn("requirements-ci-hashed.txt", workflow)
    CHECK.assertNotIn("pip install --upgrade pip", workflow)

    lock = (ROOT / "requirements-ci-hashed.txt").read_text(encoding="utf-8")
    requirements = [
        line for line in lock.splitlines() if line and not line.startswith(("#", " "))
    ]
    CHECK.assertTrue(requirements)
    CHECK.assertTrue(all("==" in line for line in requirements))
    CHECK.assertIn("--hash=sha256:", lock)


def test_queue_workflows_pin_actions_and_python_packages():
    for workflow_name in ("queue-issue-ingestion.yml", "queue-validation.yml"):
        workflow = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
        action_refs = re.findall(r"uses: [^@\s]+@([^\s]+)", workflow)
        CHECK.assertTrue(action_refs)
        CHECK.assertTrue(
            all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)
        )
        CHECK.assertIn("--only-binary=:all:", workflow)
        CHECK.assertNotIn("pip install --upgrade pip", workflow)


def test_constellation_ci_executes_only_installed_node_tools():
    workflow = (WORKFLOWS / "constellation-ci.yml").read_text(encoding="utf-8")
    CHECK.assertNotIn("npx ", workflow)
    CHECK.assertEqual(workflow.count("npm ci --ignore-scripts"), 3)
    CHECK.assertIn("./node_modules/.bin/tsc", workflow)


def test_cloudhub_image_uses_hash_locked_wheels():
    dockerfile = (ROOT / "Dockerfile_aurora_gui_cloudhub").read_text(encoding="utf-8")
    dockerignore = (ROOT / "Dockerfile_aurora_gui_cloudhub.dockerignore").read_text(
        encoding="utf-8"
    )
    CHECK.assertIn("requirements-hashed.txt", dockerfile)
    CHECK.assertIn("--only-binary=:all:", dockerfile)
    CHECK.assertIn("--require-hashes", dockerfile)
    CHECK.assertIn("!requirements-hashed.txt", dockerignore)
    CHECK.assertNotIn("!requirements.txt\n", dockerignore)
