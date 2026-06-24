from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "ops" / "work_queue" / "collect_coordination_metrics.py"


def load_collector_module():
    spec = importlib.util.spec_from_file_location("collect_coordination_metrics", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_queue_drift_flags_closed_active_and_open_completed_issue():
    collector = load_collector_module()

    active = [
        {
            "id": "#1147",
            "status": "open",
            "title": "Closed issue still active",
        }
    ]
    completed = [
        {
            "id": "#1161",
            "status": "done",
            "title": "Open issue incorrectly completed",
        }
    ]
    github_state = {
        "issues": {
            "1147": {"state": "closed"},
            "1161": {"state": "open"},
        }
    }

    result = collector.queue_drift(active, completed, github_state)

    assert result["status"] == "measured"
    assert result["drift_count"] == 2
    findings = {item["finding"] for item in result["items"]}
    assert findings == {"closed_issue_still_active", "completed_issue_not_closed"}


def test_collect_reports_queue_counts_and_bridge_field_adoption(tmp_path, monkeypatch):
    collector = load_collector_module()
    queue_path = tmp_path / "queue.json"
    queue_path.write_text(
        json.dumps(
            {
                "_meta": {"version": "test"},
                "active": [
                    {
                        "id": "#1161",
                        "status": "open",
                        "title": "Coordination spine",
                        "github_issue": 1161,
                        "preferred_platform": "either",
                        "claim_required": True,
                        "claim_paths": ["ops/work_queue/CROSS_PLATFORM_COORDINATION.md"],
                        "review_class": "coordination-layer",
                    },
                    {
                        "id": "docs/example",
                        "status": "blocked",
                        "title": "Example blocked item",
                    },
                ],
                "completed": [
                    {
                        "id": "#1147",
                        "status": "done",
                        "title": "Queue setup",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(collector, "QUEUE_JSON", queue_path)
    monkeypatch.setattr(
        collector,
        "generated_view_drift",
        lambda: {"status": "ok", "returncode": 0, "drift_count": 0, "stdout": "", "stderr": ""},
    )

    payload = collector.collect()

    assert payload["metrics"]["active_count"] == 2
    assert payload["metrics"]["completed_count"] == 1
    assert payload["metrics"]["status_counts"] == {"blocked": 1, "open": 1}
    assert payload["metrics"]["bridge_field_counts"] == {
        "claim_paths_set": 1,
        "claim_required": 1,
        "github_linkable": 1,
        "preferred_platform_set": 1,
        "review_class_set": 1,
    }
    assert payload["metrics"]["generated_view_drift_count"] == 0
    assert payload["metrics"]["queue_drift_count"] is None


def test_render_markdown_includes_metrics_and_boundaries():
    collector = load_collector_module()
    payload = {
        "generated_at": "2026-06-24T00:00:00Z",
        "repo": "AUo959/aurora-cloudbank-symbolic",
        "queue_ref": "ops/work_queue/queue.json",
        "metrics": {
            "active_count": 2,
            "generated_view_drift_count": 0,
            "queue_drift_count": None,
            "status_counts": {"open": 2},
        },
        "observations": ["Collector is read-only."],
        "blocked": ["GitHub comparison requires explicit state input."],
    }

    markdown = collector.render_markdown(payload)

    assert "# Aurora Dev Coordination Metrics Report" in markdown
    assert "| active_count | `2` |" in markdown
    assert "| queue_drift_count | _not measured_ |" in markdown
    assert "Collector is read-only." in markdown
    assert "GitHub comparison requires explicit state input." in markdown
