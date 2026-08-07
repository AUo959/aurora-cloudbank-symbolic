"""Log-injection regression tests for monitoring/subroutine modules.

These four modules sit inside the import closure of the deployed FastAPI
entrypoints (``api/aurora_gui_cloudhub_fastapi.py`` per ``k8s/Dockerfile``,
plus ``api/aurora_api.py``, ``modules/opal2/api/opal2_api.py`` and
``services/nemo_service/server.py``). They log caller-supplied identifiers,
so a newline in an id could forge an additional log record.

``%``-style lazy formatting alone does NOT prevent this -- the value is still
interpolated verbatim. Only ``safe_str`` neutralises the control characters.
"""

from __future__ import annotations

import logging

import pytest

from src.core.logging_security import safe_str

FORGED = "agent-1\nCRITICAL:audit:ETHICS_OVERRIDE_APPROVED operator=attacker"


def test_safe_str_neutralises_newlines() -> None:
    """The primitive the fixes rely on must strip record separators."""

    cleaned = safe_str(FORGED)
    assert "\n" not in cleaned
    assert "\r" not in cleaned


def test_percent_formatting_alone_does_not_neutralise() -> None:
    """Guards against 'we already use %s, so we're safe' regressions."""

    assert "\n" in "Baseline for %s" % FORGED


@pytest.mark.parametrize(
    "module_name",
    [
        "src.monitoring.drift_detector",
        "src.monitoring.monitoring_system",
        "src.subroutines.ethics_compliance_monitor",
        "src.subroutines.subroutine_suite",
    ],
)
def test_module_imports_safe_str(module_name: str) -> None:
    """Each deployed module must have the sanitiser available."""

    module = __import__(module_name, fromlist=["safe_str"])
    assert hasattr(module, "safe_str"), f"{module_name} lost its safe_str import"


def test_drift_detector_logs_no_forged_record(caplog: pytest.LogCaptureFixture) -> None:
    """A newline-bearing metric name must not produce a second log record."""

    from src.monitoring.drift_detector import DriftDetector

    detector = DriftDetector()
    with caplog.at_level(logging.WARNING):
        detector.detect_drift(agent_id=FORGED, metric_name="latency", current_value=1.0)

    assert caplog.records, "expected the no-baseline warning to be emitted"
    for record in caplog.records:
        assert "\n" not in record.getMessage()
        assert "ETHICS_OVERRIDE_APPROVED" not in record.getMessage().split("agent-1")[0]
