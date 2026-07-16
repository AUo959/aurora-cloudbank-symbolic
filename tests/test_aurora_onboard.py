"""Focused tests for the repository-grounded engineer onboarding command."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aurora_onboard", ROOT / "scripts" / "aurora_onboard.py")
assert SPEC and SPEC.loader
aurora_onboard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = aurora_onboard
SPEC.loader.exec_module(aurora_onboard)


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
    assert code == 0
    assert report["status"] == "pass"
    assert report["system"]["continuity_version"] == "2.2.5"
    assert report["system"]["lockpoint"] == "SN1_LOCKPOINT_TEST"
    assert report["architecture"]["l1_relay_agents"] == list(aurora_onboard.RELAY_AGENTS)
    assert report["architecture"]["l1_continuity_system_entity"] == "HALO"
    assert report["ethics"]["binding_verified"] is True


def test_skip_interactive_is_ci_safe_on_healthy_repo(healthy_repo: Path) -> None:
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    assert code == 0
    assert "Onboarding complete" in stream.getvalue()


def test_broken_repo_returns_one_without_traceback(healthy_repo: Path) -> None:
    (healthy_repo / "AURORA_CONTEXT.json").write_text("{broken", encoding="utf-8")
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    assert code == 1
    assert "Invalid JSON in AURORA_CONTEXT.json" in stream.getvalue()
    assert "Traceback" not in stream.getvalue()


def test_agent_failure_is_still_valid_json(healthy_repo: Path) -> None:
    (healthy_repo / ".aurora/SIMULATION_STATE.json").unlink()
    stream = io.StringIO()

    code = aurora_onboard.main(["--agent"], repo_root=healthy_repo, stream=stream)

    report = json.loads(stream.getvalue())
    assert code == 1
    assert report["status"] == "fail"
    assert "Cannot read .aurora/SIMULATION_STATE.json" in report["error"]


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
    assert code == 0
    assert len(generated) == 1
    content = generated[0].read_text(encoding="utf-8")
    assert "seed_status: staged" in content
    assert 'engineer_handle: "Engineer One"' in content
    assert "does not become canon" not in content
    assert "It is staged, not canonical" in content


def test_missing_python_floor_returns_partial_status(healthy_repo: Path) -> None:
    (healthy_repo / "setup.py").write_text("# no floor recorded\n", encoding="utf-8")
    stream = io.StringIO()

    code = aurora_onboard.main(["--skip-interactive"], repo_root=healthy_repo, stream=stream)

    assert code == 2
    assert "WARNING" in stream.getvalue()


def test_onboarding_documents_preserve_layer_semantics() -> None:
    getting_started = (ROOT / "GETTING_STARTED_ENGINEER.md").read_text(encoding="utf-8")
    quickmap = (ROOT / "ARCHITECTURE_QUICKMAP.md").read_text(encoding="utf-8")
    agent_context = json.loads((ROOT / "docs/onboarding/AGENT_ONBOARD.md").read_text(encoding="utf-8"))

    assert len(getting_started.splitlines()) <= 200
    assert "L2 relay agents" not in getting_started
    assert "mediation layer" not in getting_started.lower()
    assert "docs/architecture/LAYER_ARCHITECTURE.md" in quickmap
    assert "docs/architecture/QGIA_SIM_BRIDGE.md" in quickmap
    assert "docs/architecture/SYSTEM_ARCHITECTURE_DIAGRAM.md" in quickmap
    assert len(agent_context["identity"]["l1_relay_agents"]) == 5
    assert agent_context["identity"]["l1_continuity_system_entity"] == "HALO"


def test_current_checkout_agent_mode_is_parseable() -> None:
    stream = io.StringIO()

    code = aurora_onboard.main(["--agent"], repo_root=ROOT, stream=stream)

    report = json.loads(stream.getvalue())
    assert code == 0
    assert report["status"] == "pass"
