#!/usr/bin/env python3
"""Continue and observe a persisted governed Orion L1 run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
for import_path in (PROJECT_ROOT, SIMULATION_DIR):
    value = str(import_path)
    if value not in sys.path:
        sys.path.insert(0, value)

from l1_instrumentation import (  # noqa: E402
    build_logical_schematic,
    build_sensor_snapshot,
)
from l1_runtime import OrionL1Runtime, PreflightError  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed Orion L1 continuation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("status", "Read persisted run status without advancing"),
        ("sensors", "Read ledger-bound sensors and the causal-safe schematic"),
        ("advance", "Advance one bounded autonomous simulation window"),
        ("await-response", "Advance until a specific station response reaches Earth"),
        ("explain-response", "Show the character action that caused a response"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        _add_run_arguments(command)
        if name == "advance":
            command.add_argument("--minutes", type=int, default=1)
        if name == "await-response":
            command.add_argument("--message-id", required=True)
            command.add_argument("--minutes", type=int, default=1)
            command.add_argument("--max-windows", type=int, default=4)
        if name == "explain-response":
            command.add_argument("--message-id", required=True)
    return parser


def _add_run_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="External persistence root (default: ~/.aurora/l1-runs)",
    )


def main() -> int:
    args = build_parser().parse_args()
    runtime = OrionL1Runtime()
    try:
        runtime.load_run(args.run_id, run_root=args.run_root)
        result = _execute(runtime, args)
    except (PreflightError, ValueError, RuntimeError) as exc:
        print(f"CONTINUATION BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.command == "await-response" and result["response"] is None:
        return 3
    return 0


def _execute(runtime: OrionL1Runtime, args: argparse.Namespace) -> Dict[str, Any]:
    if args.command == "status":
        return _status(runtime)
    if args.command == "sensors":
        return _instrumentation(runtime)
    if args.command == "advance":
        event = runtime.advance(elapsed_minutes=args.minutes)
        return {**_status(runtime), "event": event}
    if args.command == "await-response":
        return _await_response(
            runtime,
            message_id=args.message_id,
            elapsed_minutes=args.minutes,
            max_windows=args.max_windows,
        )
    return _explain_response(runtime, args.message_id)


def _status(runtime: OrionL1Runtime) -> Dict[str, Any]:
    state = runtime.state
    if state is None:
        raise RuntimeError("persisted run failed to load")
    return {
        "run_id": state.manifest.run_id,
        "runtime_contract_version": state.manifest.runtime_contract_version,
        "status": state.manifest.status,
        "tick": state.manifest.tick,
        "station_cycle_minute": state.manifest.station_cycle_minute,
        "event_count": len(state.events),
        "communication_count": len(state.communications),
        "character_action_count": len(state.character_actions),
    }


def _instrumentation(runtime: OrionL1Runtime) -> Dict[str, Any]:
    state = runtime.state
    if state is None:
        raise RuntimeError("persisted run failed to load")
    return {
        **_status(runtime),
        "sensors": build_sensor_snapshot(state),
        "schematic": build_logical_schematic(state, runtime.baseline),
    }


def _await_response(
    runtime: OrionL1Runtime,
    *,
    message_id: str,
    elapsed_minutes: int,
    max_windows: int,
) -> Dict[str, Any]:
    if max_windows < 0:
        raise ValueError("max_windows cannot be negative")
    events = []
    response = _delivered_response(runtime, message_id)
    while response is None and len(events) < max_windows:
        events.append(runtime.advance(elapsed_minutes=elapsed_minutes))
        response = _delivered_response(runtime, message_id)
    return {
        **_instrumentation(runtime),
        "response_to_message_id": message_id,
        "advancement_windows": len(events),
        "events": events,
        "response": response,
    }


def _delivered_response(
    runtime: OrionL1Runtime,
    message_id: str,
) -> Optional[Dict[str, Any]]:
    state = runtime.state
    if state is None:
        return None
    for communication in state.communications:
        if (
            communication.get("direction") == "station_to_earth"
            and communication.get("reply_to_message_id") == message_id
            and communication.get("status") == "delivered_to_earth"
        ):
            return communication
    return None


def _explain_response(
    runtime: OrionL1Runtime,
    message_id: str,
) -> Dict[str, Any]:
    state = runtime.state
    if state is None:
        raise RuntimeError("persisted run failed to load")
    for action in state.character_actions:
        if message_id in {
            action.get("trigger_message_id"),
            action.get("response_message_id"),
        }:
            return {**_status(runtime), "character_action": action}
    raise RuntimeError("no character action is recorded for that communication")


if __name__ == "__main__":
    raise SystemExit(main())
