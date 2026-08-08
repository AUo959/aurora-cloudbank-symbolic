from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_runtime import OrionL1Runtime  # noqa: E402


CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"
CONTINUATION_CLI = PROJECT_ROOT / ".aurora" / "run_l1.py"


def _run_cli(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(CONTINUATION_CLI), *args],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_sensors_command_is_read_only_and_discloses_unbound_channels(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )

    result = _run_cli(
        "sensors",
        "--run-id",
        state.manifest.run_id,
        "--run-root",
        str(tmp_path),
    )

    assert result["tick"] == 0
    assert result["sensors"]["reading"]["provider_bound"] is True
    assert result["schematic"]["physical_deck_layout"]["status"] == "unresolved"
    persisted = json.loads(
        (tmp_path / state.manifest.run_id / "state.json").read_text(encoding="utf-8")
    )
    assert persisted["manifest"]["tick"] == 0


def test_await_response_continues_persisted_run_until_delivery(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    inbound = runtime.send_communication("Status report, Commander.", target="CMD_001")[
        "message"
    ]
    runtime.advance(elapsed_minutes=1)

    result = _run_cli(
        "await-response",
        "--run-id",
        state.manifest.run_id,
        "--run-root",
        str(tmp_path),
        "--message-id",
        inbound["message_id"],
        "--minutes",
        "1",
        "--max-windows",
        "2",
    )

    assert result["advancement_windows"] == 1
    assert result["response"]["sender_id"] == "CMD_001"
    assert result["response"]["status"] == "delivered_to_earth"
    assert result["response"]["response_policy"] == "bounded_character_action_v1"
    assert result["character_action_count"] == 1
    assert result["tick"] == 2

    explanation = _run_cli(
        "explain-response",
        "--run-id",
        state.manifest.run_id,
        "--run-root",
        str(tmp_path),
        "--message-id",
        result["response"]["message_id"],
    )
    action = explanation["character_action"]
    assert action["selected_action"] == "review_watch_and_report"
    assert action["response_message_id"] == result["response"]["message_id"]
    assert action["knowledge_inputs"]


def test_await_response_detects_legacy_response_without_direction(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    inbound = runtime.send_communication("Status report, Commander.", target="CMD_001")[
        "message"
    ]
    runtime.advance(elapsed_minutes=1)
    persisted_path = tmp_path / state.manifest.run_id / "state.json"
    persisted = json.loads(persisted_path.read_text(encoding="utf-8"))
    response = next(
        item
        for item in persisted["communications"]
        if item.get("reply_to_message_id") == inbound["message_id"]
    )
    response.pop("direction")
    persisted_path.write_text(json.dumps(persisted), encoding="utf-8")

    result = _run_cli(
        "await-response",
        "--run-id",
        state.manifest.run_id,
        "--run-root",
        str(tmp_path),
        "--message-id",
        inbound["message_id"],
        "--minutes",
        "1",
        "--max-windows",
        "1",
    )

    assert result["advancement_windows"] == 1
    assert result["response"]["status"] == "delivered_to_earth"


def test_await_response_rejects_unknown_message_without_advancing(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(CONTINUATION_CLI),
            "await-response",
            "--run-id",
            state.manifest.run_id,
            "--run-root",
            str(tmp_path),
            "--message-id",
            "missing-message",
            "--max-windows",
            "2",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "not eligible for a station response" in completed.stderr
    persisted = json.loads(
        (tmp_path / state.manifest.run_id / "state.json").read_text(encoding="utf-8")
    )
    assert persisted["manifest"]["tick"] == 0
    assert persisted["events"] == []
