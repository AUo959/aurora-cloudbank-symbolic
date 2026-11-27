"""Bridge fabric-invariant findings into the drift response pipeline.

Implements RULING-FABRIC-WIRING (2026-07-21 ruling batch). The enforcement trace in
`reports/analysis/velar_fabric_pass__2026-07-21.md` §2 found that the symbolic layer
enforces **zero fabric invariants semantically** — `ethics_engine` covers operational
conduct, `file_lock` is a write mutex, `sensors/` handles layer provenance, and
`DriftResponder` is a generic runbook executor with no fabric-aware detector feeding
it. The ruling's remedy: route `fabric_invariants_check` findings into `DriftAlert`s
so the existing responder can act on them.

Severity mapping, per the ruling: **VIOLATION → alert/escalate, GAP → log/notify.**

Why fabric findings get their OWN runbooks
------------------------------------------
The stock `critical` runbook suspends the agent and hard-rebaselines from a snapshot.
That is correct for a statistically misbehaving agent and wrong for a fabric finding:
a location record overstating its map placement is a canon data-integrity problem, not
a runaway process. Suspending an agent over it would be both useless and disruptive.
The ruling reflects this — it names alert/escalate and log/notify, never suspend,
throttle or rebaseline. So alerts emitted here carry an explicit runbook key
(`fabric_violation` / `fabric_gap`) and `DriftResponder` honours it over the level
default.

Numeric fields on `DriftAlert` assume a statistical metric. A fabric check is
categorical, so they are populated honestly rather than left meaningless: the baseline
is 0.0 (canon is expected to hold zero findings for an invariant) and the current value
is the observed count, making `deviation` the number of findings.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from src.monitoring.drift_detector import DriftAlert, DriftLevel, DriftMethod

logger = logging.getLogger(__name__)

CONTEXT_TAG = "fabric_invariant_bridge_v1"

#: Runbook keys emitted for each fabric severity. Kept distinct from the statistical
#: levels so a canon finding never triggers suspend/throttle/rebaseline.
RUNBOOK_VIOLATION = "fabric_violation"
RUNBOOK_GAP = "fabric_gap"

#: Fabric severity -> (DriftLevel, runbook key). Per RULING-FABRIC-WIRING.
SEVERITY_MAP: Dict[str, tuple] = {
    "VIOLATION": (DriftLevel.CRITICAL, RUNBOOK_VIOLATION),
    "GAP": (DriftLevel.WARNING, RUNBOOK_GAP),
    "INFO": (DriftLevel.INFO, None),
}

#: The agent id fabric findings are attributed to. Fabric findings are properties of
#: the canon corpus, not of any single agent, so they are attributed to the checker.
FABRIC_AGENT_ID = "fabric_invariants_check"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_findings(path: Path | str) -> List[Dict[str, Any]]:
    """Read a `fabric_invariants_check --json` report and return its findings."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return list(data.get("findings", []))


def finding_to_alert(finding: Dict[str, Any]) -> Optional[DriftAlert]:
    """Convert one fabric finding into a DriftAlert.

    Returns None for severities with no defined response (INFO carries no runbook:
    an INFO finding records an answered question, e.g. an explicitly undetermined
    location binding, and warrants no action).
    """
    severity = str(finding.get("severity", "")).upper()
    mapped = SEVERITY_MAP.get(severity)
    if mapped is None:
        logger.debug("[fabric-bridge] unknown severity %r — skipped", severity)
        return None
    level, runbook = mapped
    if runbook is None:
        return None

    invariant = finding.get("invariant", "?")
    subject = finding.get("subject", "?")
    detail = finding.get("detail", "")

    return DriftAlert(
        timestamp=_now(),
        agent_id=FABRIC_AGENT_ID,
        metric_name=f"fabric.{invariant}",
        level=level,
        method=DriftMethod.THRESHOLD,
        # Categorical check expressed honestly: canon should hold zero findings.
        current_value=1.0,
        baseline_value=0.0,
        deviation=1.0,
        description=f"[{invariant}] {subject}: {detail}",
        context_tag=CONTEXT_TAG,
        metadata={
            "runbook": runbook,
            "invariant": invariant,
            "subject": subject,
            "fabric_severity": severity,
            "source": "tools/fabric_invariants_check.py",
            "ruling": "RULING-FABRIC-WIRING (2026-07-21)",
        },
    )


def findings_to_alerts(findings: Iterable[Dict[str, Any]]) -> List[DriftAlert]:
    """Convert fabric findings into actionable DriftAlerts, dropping non-actionable ones."""
    alerts = []
    for finding in findings:
        alert = finding_to_alert(finding)
        if alert is not None:
            alerts.append(alert)
    return alerts


def dispatch(findings: Iterable[Dict[str, Any]], responder: Any) -> List[Any]:
    """Run every actionable fabric finding through the DriftResponder.

    Returns the response events, so a caller (CI, a scheduled scan) can assert on
    what actually fired rather than trusting that it did.
    """
    events = []
    for alert in findings_to_alerts(findings):
        events.append(responder.handle_alert(alert))
    return events
