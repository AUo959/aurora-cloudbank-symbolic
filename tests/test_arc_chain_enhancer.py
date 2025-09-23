"""Tests for the ARC Chain Enhancer utility."""

from datetime import datetime

import pytest

from tools.symbolic.arc_chain_enhancer import ARCChainEnhancer, ARCValidationError


@pytest.fixture
def sample_arc_payload() -> dict:
    return {
        "schema": "ARC_CHAIN_EXPORT_SCHEMA_v1.0",
        "exported_at": "2025-09-22T20:35:00Z",
        "thread_id": "aurora.thread.gumas.v2.4.1",
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
    }


def test_enhancement_summary(sample_arc_payload):
    enhancer = ARCChainEnhancer(sample_arc_payload)
    summary = enhancer.enhancement_summary()

    assert summary["schema"] == "ARC_CHAIN_EXPORT_SCHEMA_v1.0"
    assert summary["thread_id"] == "aurora.thread.gumas.v2.4.1"
    assert summary["chain_length"] == 3
    assert summary["arc_types"]["UPLOAD_ARC"] == 1
    assert summary["propagation"]["targets"]["parent"] == 2
    assert summary["anchor_integrity"]["initial_pair"] == ("0xINIT", "0x001")
    assert summary["driftlog"]["entries_with_drift"] == 2
    assert summary["closure"]["sealed"] is True

    exported_at = datetime.fromisoformat(summary["exported_at"])
    assert exported_at.year == 2025


def test_enhanced_payload_contains_anchor_metadata(sample_arc_payload):
    enhancer = ARCChainEnhancer(sample_arc_payload)
    payload = enhancer.enhanced_payload()

    assert "arc_enhancement" in payload
    enhancement_block = payload["arc_enhancement"]

    assert enhancement_block["t1_anchor_seed"] == ARCChainEnhancer.T1_ANCHOR_SEED
    assert enhancement_block["srb_bridge"] == ARCChainEnhancer.SRB_BRIDGE_ANCHOR
    assert enhancement_block["summary"]["chain_length"] == 3


def test_validation_error_on_missing_root_key(sample_arc_payload):
    invalid_payload = {**sample_arc_payload}
    invalid_payload.pop("arc_chain")

    with pytest.raises(ARCValidationError):
        ARCChainEnhancer(invalid_payload)
