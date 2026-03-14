"""CLI for the Aurora mesh router runtime."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


DEFAULT_BASE_URL = os.getenv("MESH_ROUTER_URL", "http://127.0.0.1:8000")
DEFAULT_CONTROL_TOKEN = os.getenv("AURORA_MESH_CONTROL_TOKEN", "")


def request_json(method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Perform a JSON HTTP request against the mesh runtime."""

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if DEFAULT_CONTROL_TOKEN:
        headers["Authorization"] = f"Bearer {DEFAULT_CONTROL_TOKEN}"
    request = urllib.request.Request(
        urllib.parse.urljoin(DEFAULT_BASE_URL, path),
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"detail": body}
        message = parsed.get("detail") or parsed.get("error") or body or str(exc)
        raise SystemExit(f"mesh runtime error: {message}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"mesh runtime unavailable at {DEFAULT_BASE_URL}: {exc.reason}") from exc


def dump_json(payload: Dict[str, Any]) -> None:
    """Print pretty JSON to stdout."""

    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def command_status(args: argparse.Namespace) -> int:
    dump_json(request_json("GET", "/api/mesh/status"))
    return 0


def command_send(args: argparse.Namespace) -> int:
    payload = {
        "to": args.to,
        "channel": args.channel,
        "content": args.message,
        "sender_id": args.sender_id,
        "sender_name": args.sender_name,
        "type": "direct",
    }
    dump_json(request_json("POST", "/api/mesh/messages", payload))
    return 0


def command_broadcast(args: argparse.Namespace) -> int:
    payload = {
        "channel": args.channel,
        "content": args.message,
        "sender_id": args.sender_id,
        "sender_name": args.sender_name,
        "type": "broadcast",
    }
    dump_json(request_json("POST", "/api/mesh/messages", payload))
    return 0


def command_history(args: argparse.Namespace) -> int:
    path = f"/api/mesh/channels/{urllib.parse.quote(args.channel, safe='')}/history?limit={args.limit}"
    dump_json(request_json("GET", path))
    return 0


def command_activate(args: argparse.Namespace) -> int:
    path = f"/api/mesh/agents/{urllib.parse.quote(args.agent, safe='')}/activate"
    dump_json(request_json("POST", path))
    return 0


def command_tail(args: argparse.Namespace) -> int:
    cursor = args.after
    while True:
        payload = request_json("GET", f"/api/mesh/events?after={cursor}&limit={args.limit}")
        events = payload.get("events", [])
        for event in events:
            dump_json(event)
        cursor = payload.get("next_cursor", cursor)
        if not args.follow:
            break
        time.sleep(args.interval)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the mesh CLI argument parser."""

    parser = argparse.ArgumentParser(description="Aurora mesh router CLI")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Mesh runtime base URL")
    parser.add_argument("--token", default=DEFAULT_CONTROL_TOKEN, help="Optional mesh control token for remote runtimes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show mesh runtime status")
    status_parser.set_defaults(func=command_status)

    send_parser = subparsers.add_parser("send", help="Send a direct message to an agent")
    send_parser.add_argument("--to", required=True, help="Target agent id or alias")
    send_parser.add_argument("--channel", help="Explicit channel id")
    send_parser.add_argument("--message", required=True, help="Message text")
    send_parser.add_argument("--sender-id", default="captain", help="Sender id")
    send_parser.add_argument("--sender-name", default="Captain", help="Sender display name")
    send_parser.set_defaults(func=command_send)

    broadcast_parser = subparsers.add_parser("broadcast", help="Broadcast a message into a channel")
    broadcast_parser.add_argument("--channel", required=True, help="Broadcast channel, for example #crew_lounge")
    broadcast_parser.add_argument("--message", required=True, help="Message text")
    broadcast_parser.add_argument("--sender-id", default="captain", help="Sender id")
    broadcast_parser.add_argument("--sender-name", default="Captain", help="Sender display name")
    broadcast_parser.set_defaults(func=command_broadcast)

    history_parser = subparsers.add_parser("history", help="Replay channel history")
    history_parser.add_argument("channel", help="Channel id")
    history_parser.add_argument("--limit", type=int, default=100, help="Maximum events to fetch")
    history_parser.set_defaults(func=command_history)

    activate_parser = subparsers.add_parser("activate", help="Activate an agent")
    activate_parser.add_argument("agent", help="Agent id or alias")
    activate_parser.set_defaults(func=command_activate)

    tail_parser = subparsers.add_parser("tail", help="Print mesh events")
    tail_parser.add_argument("--after", type=int, default=0, help="Start after this event cursor")
    tail_parser.add_argument("--limit", type=int, default=100, help="Events per poll")
    tail_parser.add_argument("--follow", action="store_true", help="Poll continuously")
    tail_parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    tail_parser.set_defaults(func=command_tail)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""

    global DEFAULT_BASE_URL, DEFAULT_CONTROL_TOKEN
    parser = build_parser()
    args = parser.parse_args(argv)
    DEFAULT_BASE_URL = args.base_url
    DEFAULT_CONTROL_TOKEN = args.token
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
