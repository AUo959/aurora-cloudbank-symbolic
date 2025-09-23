import json
from pathlib import Path

import pytest

from tools.symbolic.arc_chain_processor import ArcChainProcessor


def load_sample() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "arc_chain_sample.json"


def test_arc_chain_summary_metrics():
    processor = ArcChainProcessor.from_file(load_sample())
    summary = processor.build_summary()

    assert summary["schema"] == "ARC_CHAIN_EXPORT_SCHEMA_v1.0"
    assert summary["thread_id"] == "aurora.thread.gumas.v2.4.1"
    assert summary["total_events"] == 3
    assert summary["event_types"]["INIT_ARC"] == 1
    assert summary["event_types"]["UPLOAD_ARC"] == 1
    assert summary["event_types"]["ETHICS_ARC"] == 1
    assert summary["drift_metrics"]["max_delta"] == pytest.approx(0.0)
    assert summary["drift_metrics"]["max_abs_delta"] == pytest.approx(0.3)
    assert summary["closure"]["sealed"] is True
    assert summary["validation_passed"] is True
    assert "anomalies" not in summary or not summary["anomalies"]


def test_arc_chain_enhanced_payload_contains_summary(tmp_path):
    processor = ArcChainProcessor.from_file(load_sample())
    enhanced = processor.export_enhanced_payload()

    assert "enhancements" in enhanced
    assert "summary" in enhanced["enhancements"]
    summary = enhanced["enhancements"]["summary"]
    assert summary["total_events"] == 3
    assert enhanced["enhancements"]["anomalies"] == summary.get("anomalies", [])

    output_path = tmp_path / "enhanced.json"
    output_path.write_text(json.dumps(enhanced), encoding="utf-8")
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["enhancements"]["summary"]["thread_id"] == "aurora.thread.gumas.v2.4.1"
