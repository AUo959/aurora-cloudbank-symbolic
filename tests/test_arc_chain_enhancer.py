from copy import deepcopy
from decimal import Decimal

import pytest

from src.coordination.arc_chain_enhancer import ArcChainEnhancer, ArcChainValidationError, ARC_CHAIN_SCHEMA


@pytest.fixture()
def arc_export_payload():
    return {
        "schema": ARC_CHAIN_SCHEMA,
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


def test_arc_chain_enhancer_generates_summary(arc_export_payload):
    enhancer = ArcChainEnhancer(arc_export_payload)

    summary = enhancer.generate_summary()

    assert summary["schema"] == ARC_CHAIN_SCHEMA
    assert summary["thread_id"] == "aurora.thread.gumas.v2.4.1"
    assert summary["total_entries"] == 3
    assert summary["anchor_chain_integrity"] is True
    assert summary["anchor_sequence"] == ["0xINIT", "0x001", "0x002", "0x003"]

    drift = summary["drift"]
    assert drift["entries_with_percent"] == 1
    assert drift["cumulative_percent"] == Decimal("-0.3")
    assert drift["entries_with_absolute"] == 1
    assert drift["cumulative_absolute"] == Decimal("0.000")

    diagnostics = summary["diagnostics"]
    assert diagnostics["schema_valid"] is True
    assert diagnostics["anchor_continuity"] is True
    assert diagnostics["propagation_targets_valid"] is True
    assert diagnostics["closure_present"] is True

    closure = summary["closure"]
    assert closure["sealed_by"] == "system"
    assert closure["archive_ready"] is True


def test_arc_chain_enhancer_detects_anchor_break(arc_export_payload):
    invalid_payload = deepcopy(arc_export_payload)
    invalid_payload["arc_chain"][1]["anchor_pair"] = ["0xABC", "0x999"]

    enhancer = ArcChainEnhancer(invalid_payload)

    assert enhancer.validate_anchor_sequence() is False


def test_arc_chain_enhancer_rejects_invalid_schema(arc_export_payload):
    invalid_payload = deepcopy(arc_export_payload)
    invalid_payload["schema"] = "ARC_CHAIN_EXPORT_SCHEMA_v0.9"

    with pytest.raises(ArcChainValidationError):
        ArcChainEnhancer(invalid_payload)
