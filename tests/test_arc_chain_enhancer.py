import json
from datetime import datetime, timezone

import pytest

from src.core.arc_chain_enhancer import ArcChainEnhancer, enhance_arc_export


@pytest.fixture
def sample_arc_export():
    return {
        "schema": "ARC_CHAIN_EXPORT_SCHEMA_v1.0",
        "exported_at": "2025-09-22T20:35:00Z",
        "thread_id": "aurora.thread.gumas.v2.4.1",
        "linked_threads": ["halo.thread.v1", "liora.thread.v2"],
        "arc_chain": [
            {
                "type": "INIT_ARC",
                "timestamp": "2025-09-21T00:00:00Z",
                "by": "system",
                "summary": "Thread initiated for GUMAS continuity enhancements.",
                "anchor_pair": ["0xINIT", "0x001"],
                "propagate_to": ["sibling"],
                "driftlog_delta": None,
            },
            {
                "type": "UPLOAD_ARC",
                "timestamp": "2025-09-21T15:42:10Z",
                "by": "Emily Roberts",
                "summary": "Aurora_PATCH_GPT-Editor_T2_v1.0.zip uploaded. Preload snapshot captured.",
                "anchor_pair": ["0x001", "0x002"],
                "propagate_to": ["sibling", "parent"],
                "driftlog_delta": "-0.3%",
            },
            {
                "type": "ETHICS_ARC",
                "timestamp": "2025-09-21T16:03:44Z",
                "by": "Prof. Elena Sorensen",
                "summary": "Symbolic ethics alignment verified (no override).",
                "anchor_pair": ["0x002", "0x003"],
                "propagate_to": ["parent"],
                "driftlog_delta": "Δ0.000",
            },
        ],
        "closure": {
            "type": "CLOSURE_ARC",
            "sealed_by": "system",
            "timestamp": "2025-09-22T18:00:00Z",
            "summary": "Thread finalized for export.",
            "archive_ready": True,
        },
        "signature": "aurora.system.symbolic.v2.4",
        "validation": {
            "checksums": {
                "arc_chain": "SHA256:f97b4cfa...",
                "linked_manifest": "SHA256:ae32b1fa...",
            },
            "validation_passed": True,
        },
    }


def test_enhanced_payload_includes_metadata(sample_arc_export):
    enhancer = ArcChainEnhancer(sample_arc_export)
    payload = enhancer.enhanced_payload()

    assert payload["metadata"]["total_arcs"] == 3
    assert payload["metadata"]["arc_types"] == {
        "INIT_ARC": 1,
        "UPLOAD_ARC": 1,
        "ETHICS_ARC": 1,
    }
    assert payload["metadata"]["participants"]["system_initiated"] is True

    anchors = payload["metadata"]["symbolic_anchors"]
    assert anchors["t1_marker"] == "T1_ARC_CHAIN_CONTINUITY"
    assert anchors["anchor_pairs"][0] == ["0xINIT", "0x001"]


def test_drift_metrics_are_parsed(sample_arc_export):
    payload = enhance_arc_export(sample_arc_export)
    drift = payload["metadata"]["drift"]
    assert pytest.approx(drift["net_drift"], abs=1e-6) == -0.3

    # Ensure parsed drift values are attached to individual events
    parsed_values = [event["parsed_value"] for event in drift["drift_events"]]
    assert parsed_values == [-0.3, 0.0]


def test_timeline_spans_full_thread(sample_arc_export):
    payload = enhance_arc_export(sample_arc_export)
    timeline = payload["metadata"]["timeline"]
    assert timeline["first_event"] == "2025-09-21T00:00:00Z"
    assert timeline["last_event"] == "2025-09-22T18:00:00Z"

    duration = timeline["duration_seconds"]
    expected_duration = (
        datetime(2025, 9, 22, 18, 0, tzinfo=timezone.utc) - datetime(2025, 9, 21, 0, 0, tzinfo=timezone.utc)
    ).total_seconds()
    assert duration == expected_duration


def test_serialisation_round_trip(sample_arc_export):
    enhancer = ArcChainEnhancer(sample_arc_export)
    payload = json.loads(enhancer.to_json())

    assert payload["thread_id"] == "aurora.thread.gumas.v2.4.1"
    assert payload["metadata"]["participants"]["actors"] == [
        "Emily Roberts",
        "Prof. Elena Sorensen",
        "system",
    ]

    closure = payload["closure"]
    assert closure["archive_ready"] is True
