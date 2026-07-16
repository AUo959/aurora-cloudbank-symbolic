"""Focused tests for the repository-grounded engineer onboarding command."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aurora_onboard", ROOT / "scripts" / "aurora_onboard.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load scripts/aurora_onboard.py")
aurora_onboard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = aurora_onboard
SPEC.loader.exec_module(aurora_onboard)
CHECK = unittest.TestCase()


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _json(root: Path, relative: str, value: object) -> None:
    _write(root, relative, json.dumps(value))


@pytest.fixture()
def healthy_repo(tmp_path: Path) -> Path:
    _write(tmp_path, "setup.py", 'python_requires=">=3.11"\n')
    _json(
        tmp_path,
        ".aurora/SIMULATION_STATE.json",
        {"last_updated": "2026-07-13T00:00:00Z", "simulation": {"status": "ACTIVE"}},
    )
    _json(
        tmp_path,
        "AURORA_CONTEXT.json",
        {
            "document_generated": "2026-07-13",
            "system_identity": {"name": "Aurora"},
            "architecture_layers": {"L1": "station", "L2": "simulation", "L3": "frameworks"},
            "active_state": {
                "lockpoint": "SN1_LOCKPOINT_TEST",
                "_staleness_warning": "snapshot",
            },
            "active_modules": {"ethics": {"status": "active"}},
        },
    )
    terms = (*aurora_onboard.RELAY_AGENTS, aurora_onboard.SYSTEM_ENTITY, *aurora_onboard.L3_FRAMEWORKS)
    _write(
        tmp_path,
        "docs/architecture/LAYER_ARCHITECTURE.md",
        "Triplex Handshake\n" + "\n".join(terms),
    )
    _write(
        tmp_path,
        "src/api/l1_relay_api.manifest.yaml",
        "continuity_seal: Aurora_Continuity_Seal_v2.2.5\n",
    )
    _json(
        tmp_path,
        "QGIA_integration/QUANTUM_FORGE_Axiom_Manifest.json",
        {"ethics_binding": "GUMAS_Thermax"},
    )
    _write(
        tmp_path,
        "QGIA_Integration/04_GUMAS_AuditSchema.md",
        "### GAE-001 | TEST_RULE\n- **Trigger condition:** A deterministic test trigger\n",
    )
    _write(tmp_path, "scripts/activate_l3_ethics.sh", "Picard_Delta_3\n")
    _write(tmp_path, "CANON_INDEX.md", "`seeds/onboarding/README.md`\n")
    _write(tmp_path, "seeds/onboarding/README.md", "staged, non-canonical\n")
    return tmp_path


def test_agent_mode_emits_parseable_json(healthy_repo: Path) -> None:
    stream = io.StringIO()

    code = aurora_onboard.main(["--agent"], repo_root=healthy_repo, stream=stream)

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report["status"], "pass")
    CHECK.assertEqual(report["system"]["continuity_version"], "2.2.5")
    CHECK.assertEqual(report["system"]["lockpoint"], "SN1_LOCKPOINT_TEST")
    CHECK.assertEqual(report["architecture"]["l1_relay_agents"], list(aurora_onboard.RELAY_AGENTS))
    CHECK.assertEqual(report["architecture"]["l1_continuity_system_entity"], "HALO")
    CHECK.assertTrue(report["ethics"]["binding_verified"])
    identity_check = next(check for check in report["checks"] if check["name"] == "system_identity")
    CHECK.assertEqual(
        identity_check["source"],
        "AURORA_CONTEXT.json + src/api/l1_relay_api.manifest.yaml",
    )


def test_skip_interactive_is_ci_safe_on_healthy_repo(healthy_repo: Path) -> None:
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    CHECK.assertEqual(code, 0)
    CHECK.assertIn("Onboarding complete", stream.getvalue())


def test_broken_repo_returns_one_without_traceback(healthy_repo: Path) -> None:
    (healthy_repo / "AURORA_CONTEXT.json").write_text("{broken", encoding="utf-8")
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    CHECK.assertEqual(code, 1)
    CHECK.assertIn("Invalid JSON in AURORA_CONTEXT.json", stream.getvalue())
    CHECK.assertNotIn("Traceback", stream.getvalue())


def test_agent_failure_is_still_valid_json(healthy_repo: Path) -> None:
    (healthy_repo / ".aurora/SIMULATION_STATE.json").unlink()
    stream = io.StringIO()

    code = aurora_onboard.main(["--agent"], repo_root=healthy_repo, stream=stream)

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(report["status"], "fail")
    CHECK.assertIn("Cannot read .aurora/SIMULATION_STATE.json", report["error"])


def test_full_flow_writes_a_staged_seed(healthy_repo: Path) -> None:
    answers = iter(["", "y", "Engineer One"])
    stream = io.StringIO()

    code = aurora_onboard.main(
        [],
        repo_root=healthy_repo,
        stream=stream,
        input_fn=lambda _prompt: next(answers),
    )

    generated = list((healthy_repo / "seeds/onboarding").glob("engineer-engineer-one-*.md"))
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(len(generated), 1)
    content = generated[0].read_text(encoding="utf-8")
    CHECK.assertIn("seed_status: staged", content)
    CHECK.assertIn('engineer_handle: "Engineer One"', content)
    CHECK.assertNotIn("does not become canon", content)
    CHECK.assertIn("It is staged, not canonical", content)


def test_same_second_seed_writes_have_unique_paths(healthy_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    moments = iter(
        [
            aurora_onboard.datetime(2026, 7, 16, 7, 0, 0, 1, tzinfo=aurora_onboard.timezone.utc),
            aurora_onboard.datetime(2026, 7, 16, 7, 0, 0, 2, tzinfo=aurora_onboard.timezone.utc),
        ]
    )

    class Clock:
        @staticmethod
        def now(_timezone: object) -> object:
            return next(moments)

    monkeypatch.setattr(aurora_onboard, "datetime", Clock)
    app = aurora_onboard.AuroraOnboarding(healthy_repo, io.StringIO(), lambda _prompt: "")

    first = app.write_seed("Engineer One")
    second = app.write_seed("Engineer One")

    CHECK.assertNotEqual(first["path"], second["path"])
    CHECK.assertTrue((healthy_repo / first["path"]).is_file())
    CHECK.assertTrue((healthy_repo / second["path"]).is_file())


def test_failed_validation_does_not_offer_or_write_completion_seed(healthy_repo: Path) -> None:
    _write(healthy_repo, "docs/architecture/LAYER_ARCHITECTURE.md", "Triplex Handshake\n")
    stream = io.StringIO()

    code = aurora_onboard.main(
        [],
        repo_root=healthy_repo,
        stream=stream,
        input_fn=lambda _prompt: "SKIP",
    )

    CHECK.assertEqual(code, 1)
    CHECK.assertEqual(list((healthy_repo / "seeds/onboarding").glob("engineer-*.md")), [])
    CHECK.assertIn("Skipped because environment validation failed", stream.getvalue())


def test_missing_python_floor_returns_partial_status(healthy_repo: Path) -> None:
    (healthy_repo / "setup.py").write_text("# no floor recorded\n", encoding="utf-8")
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    CHECK.assertEqual(code, 2)
    CHECK.assertIn("WARNING", stream.getvalue())
    CHECK.assertIn("fallback >=3.11", stream.getvalue())


def test_environment_note_is_truthful_without_freshness_warning(healthy_repo: Path) -> None:
    context_path = healthy_repo / "AURORA_CONTEXT.json"
    context = json.loads(context_path.read_text(encoding="utf-8"))
    context["active_state"].pop("_staleness_warning")
    context_path.write_text(json.dumps(context), encoding="utf-8")
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    CHECK.assertEqual(code, 0)
    CHECK.assertIn("no freshness warning is recorded", stream.getvalue())


def test_onboarding_documents_preserve_layer_semantics() -> None:
    getting_started = (ROOT / "GETTING_STARTED_ENGINEER.md").read_text(encoding="utf-8")
    quickmap = (ROOT / "ARCHITECTURE_QUICKMAP.md").read_text(encoding="utf-8")
    agent_context = json.loads((ROOT / "docs/onboarding/AGENT_ONBOARD.md").read_text(encoding="utf-8"))

    CHECK.assertLessEqual(len(getting_started.splitlines()), 200)
    CHECK.assertNotIn("L2 relay agents", getting_started)
    CHECK.assertNotIn("mediation layer", getting_started.lower())
    CHECK.assertIn("docs/architecture/LAYER_ARCHITECTURE.md", quickmap)
    CHECK.assertIn("docs/architecture/QGIA_SIM_BRIDGE.md", quickmap)
    CHECK.assertIn("docs/architecture/SYSTEM_ARCHITECTURE_DIAGRAM.md", quickmap)
    CHECK.assertEqual(len(agent_context["identity"]["l1_relay_agents"]), 5)
    CHECK.assertEqual(agent_context["identity"]["l1_continuity_system_entity"], "HALO")


def test_current_checkout_agent_mode_is_parseable() -> None:
    stream = io.StringIO()

    code = aurora_onboard.main(["--agent"], repo_root=ROOT, stream=stream)

    report = json.loads(stream.getvalue())
    CHECK.assertEqual(code, 0)
    CHECK.assertEqual(report["status"], "pass")
