from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "ops" / "work_queue" / "queue.json"
SCHEMA_PATH = ROOT / "ops" / "work_queue" / "queue_schema.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validator() -> Draft7Validator:
    schema = load_json(SCHEMA_PATH)
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def test_current_queue_json_matches_compatibility_schema():
    data = load_json(QUEUE_PATH)
    errors = sorted(validator().iter_errors(data), key=lambda error: list(error.path))
    assert errors == []


def test_schema_accepts_future_state_and_bridge_metadata():
    data = {
        "_meta": {
            "version": "test",
            "description": "test queue",
            "last_aurora_review": "2026-06-24T00:00:00Z",
            "schema": "ops/work_queue/queue_schema.json",
        },
        "active": [
            {
                "id": "#1161",
                "github_issue": 1161,
                "linked_prs": [1166, 1167, 1168, 1169],
                "title": "Coordinate queue with control-plane handoff",
                "state": "active",
                "priority": "HIGH",
                "priority_score": 68,
                "area": "operations",
                "labels": ["ops", "coordination"],
                "depends_on": [],
                "blocks": [],
                "consumer_fit": ["aurora", "agent", "human"],
                "context_pack": [
                    "ops/work_queue/CROSS_PLATFORM_COORDINATION.md",
                    "ops/work_queue/BRIDGE_FIELDS.md",
                ],
                "next_action": "Run claim preflight before mutation.",
                "done_when": "Bridge metadata is represented without breaking legacy views.",
                "opened": "2026-06-24",
                "last_updated": "2026-06-24",
                "preferred_platform": "either",
                "claim_required": True,
                "claim_paths": ["ops/work_queue/queue.json"],
                "session_state_ref": None,
                "review_class": "coordination-layer",
                "handoff_surface": "catalog/session_state.json",
                "coordination_notes": "Use control-plane claims before mutation.",
                "metrics_tags": ["ops", "queue"],
            }
        ],
        "completed": [
            {
                "id": "#1160",
                "title": "Queue state sync",
                "status": "done",
                "closed": "2026-06-24",
            }
        ],
    }

    errors = sorted(validator().iter_errors(data), key=lambda error: list(error.path))
    assert errors == []


def test_schema_rejects_item_without_status_or_state():
    data = {
        "_meta": {
            "version": "test",
            "description": "test queue",
            "last_aurora_review": "2026-06-24T00:00:00Z",
            "schema": "ops/work_queue/queue_schema.json",
        },
        "active": [
            {
                "id": "#9999",
                "title": "Missing lifecycle field",
            }
        ],
        "completed": [],
    }

    errors = sorted(validator().iter_errors(data), key=lambda error: list(error.path))
    assert errors
