"""
Salvage Sensor — derelict survey and cargo recovery detection.

Recovers the control plane's founding problem into the sensor array: the
local workspace began as a file archive before GitHub workflows existed, so
mature, valuable work exists locally that is absent from the official system
of record. This sensor detects that salvage. It extends the External /
Deep Space scan family (spec §External Sensors).

L1 Station abstraction <-> Platform reality:

|Station Metric          |Platform Metric                                |Alert        |
|------------------------|-----------------------------------------------|-------------|
|Salvage contacts        |Artifacts adrift: mature work on no official   |informational|
|(derelict survey scope) |repo manifest (untracked by any registered git)|             |
|High-value cargo        |Maturity >= 0.6 AND value_score >= threshold,  |> 0          |
|(cargo manifest)        |unregistered — recovery candidates             |             |
|Distress beacons        |Identity-bearing artifacts: anchor refs, DLP   |> 0          |
|(beacon registry)       |tags, version markers — work that *declares*   |             |
|                        |intent to be canonical                         |             |
|Fleet registry match    |Fraction of surveyed artifacts accounted for   |< 0.5        |
|(registry cross-check)  |on official manifests                          |             |
|Cargo aboard, off       |Uncommitted/untracked files INSIDE registered  |informational|
|manifest                |repos (work aboard a vessel, not logged)       |             |
|Loaded, awaiting        |Local commits ahead of origin (unpushed)       |informational|
|departure clearance     |                                               |             |

Function and intent, in physical terms: a derelict is not debris. Debris is
noise; a derelict hull with intact cargo and a transmitting beacon is a
vessel that was *built to fly* and never registered with the fleet. The
survey's job is to tell them apart — by maturity (is the hull sound: tests,
structure, documentation), by cargo value (recovery-index value score), and
by beacon (does it carry anchors, DLP tags, version identity — a declared
intent to be part of canon).

One-way observation: this sensor identifies salvage; it never promotes.
Promotion stays behind the root control plane's explicit gate
(AGENTS.md §Recovery Indexing: candidates remain pending_review /
not_promoted). Evidence arrives via the root runner's report
(tools/aurora_salvage_scan.py at the control plane), keeping repo
boundaries intact — the report file is the interface.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.sensors.core.reading_types import Layer, MetricUnit, SensorReading
from src.sensors.core.sensor_base import Sensor

logger = logging.getLogger(__name__)

# Maturity component weights (ASSUMPTION — tune via RQ-3 harness).
MATURITY_WEIGHTS = {
    "tests": 0.25,         # test_or_fixture signal: the hull was stress-tested
    "structure": 0.20,     # contract_or_schema / code_logic: load-bearing frame
    "version_marker": 0.20,  # vX_Y in name: declared lineage
    "documentation": 0.15,  # substantial prose/docs: operating manual aboard
    "substance": 0.20,     # adequate size/line_count: not a fragment
}
HIGH_VALUE_SCORE = 15          # recovery-index value_score threshold
MATURITY_THRESHOLD = 0.6
REGISTRY_MATCH_ALERT = 0.5

_VERSION_RE = re.compile(r"v\d+[._]\d+|__v\d|_v\d", re.IGNORECASE)
_BEACON_SIGNALS = {"governance_or_control_plane", "narrative_or_agent_logic"}
_BEACON_MARKERS = ("EOS_SEED_ORION", "Picard_Delta_3", "DLP", "ANCHOR",
                   "THREADCORE", "ZIPWIZ", "CANON")


@dataclass
class SalvageCandidate:
    """One surveyed artifact, in both vocabularies."""
    path: str
    value_score: float = 0.0
    signals: List[str] = field(default_factory=list)
    line_count: int = 0
    size_bytes: int = 0
    sha256: str = ""
    on_official_manifest: bool = False     # tracked+committed in a registered repo
    promotion_status: str = "pending_review"
    extension: str = ""
    # Derived:
    maturity: float = 0.0
    is_beacon: bool = False
    classification: str = "debris"         # cargo | beacon | derelict | debris

    @classmethod
    def from_record(cls, rec: Dict[str, Any]) -> "SalvageCandidate":
        c = cls(
            path=rec.get("path", ""),
            value_score=float(rec.get("value_score", 0)),
            signals=list(rec.get("signals", [])),
            line_count=int(rec.get("line_count", 0) or 0),
            size_bytes=int(rec.get("size_bytes", 0) or 0),
            sha256=rec.get("sha256", ""),
            on_official_manifest=bool(rec.get("on_official_manifest", False)),
            promotion_status=rec.get("promotion_status", "pending_review"),
            extension=rec.get("extension", ""),
        )
        # Trust precomputed survey fields when the control-plane report
        # provides them (the report is authoritative evidence); recompute
        # from raw fields only when absent.
        c.maturity = (float(rec["maturity"]) if "maturity" in rec
                      else score_maturity(c))
        c.is_beacon = (bool(rec["is_beacon"]) if "is_beacon" in rec
                       else detect_beacon(c))
        c.classification = (rec["classification"] if "classification" in rec
                            else classify(c))
        # Registered classification implies manifest membership.
        if c.classification == "registered":
            c.on_official_manifest = True
        return c


def score_maturity(c: SalvageCandidate) -> float:
    """Hull soundness, 0-1. Stdlib heuristics over recovery-index records."""
    w = MATURITY_WEIGHTS
    score = 0.0
    sig = set(c.signals)
    if "test_or_fixture" in sig:
        score += w["tests"]
    if {"contract_or_schema", "code_logic"} & sig:
        score += w["structure"]
    if _VERSION_RE.search(c.path):
        score += w["version_marker"]
    if c.extension in (".md", ".txt") and c.line_count >= 100:
        score += w["documentation"]
    elif "cloudbank_runtime" in sig or "qgia_or_forecast" in sig:
        score += w["documentation"] * 0.5
    if c.line_count >= 50 or c.size_bytes >= 4096:
        score += w["substance"]
    return min(score, 1.0)


def detect_beacon(c: SalvageCandidate) -> bool:
    """A beacon declares intent to be canonical: anchors, DLP tags,
    governance signals, version identity in the artifact's name."""
    upper = c.path.upper()
    if any(m in upper for m in _BEACON_MARKERS):
        return True
    return bool(_BEACON_SIGNALS & set(c.signals)) and bool(
        _VERSION_RE.search(c.path))


def classify(c: SalvageCandidate) -> str:
    """Physical-terms classification.

    cargo    — sound hull, valuable, unregistered: recover it.
    beacon   — transmitting identity, unregistered: investigate first.
    derelict — built to fly (some maturity) but low immediate value.
    debris   — peripheral noise; advisory only (mirrors SII periphery damping).
    """
    if c.on_official_manifest:
        return "registered"
    if c.is_beacon:
        return "beacon"
    if c.maturity >= MATURITY_THRESHOLD and c.value_score >= HIGH_VALUE_SCORE:
        return "cargo"
    if c.maturity >= 0.3:
        return "derelict"
    return "debris"


class SalvageSensor(Sensor):
    """Derelict survey over candidate records (push-fed, read-only).

    Feed it recovery-index/salvage-report records via ``ingest_records``;
    ``read()`` reports the survey in station-metric terms.
    """

    budget_key = "external_sensor"

    def __init__(self):
        super().__init__("external.salvage", Layer.L1, "salvage")
        self.candidates: List[SalvageCandidate] = []
        self.repo_divergence: Dict[str, Dict[str, int]] = {}

    def ingest_records(self, records: List[Dict[str, Any]]) -> None:
        self.candidates = [SalvageCandidate.from_record(r) for r in records]

    def ingest_repo_divergence(self, divergence: Dict[str, Dict[str, int]]) -> None:
        """Per-registered-repo: {'uncommitted': n, 'unpushed_commits': n}."""
        self.repo_divergence = dict(divergence)

    def ingest(self, source: str, payload: Dict[str, Any]) -> None:
        if "candidates" in payload:
            self.ingest_records(payload["candidates"])
        if "repo_divergence" in payload:
            self.ingest_repo_divergence(payload["repo_divergence"])

    # -- survey ------------------------------------------------------------------

    def manifest(self, classification: Optional[str] = None) -> List[SalvageCandidate]:
        """The cargo manifest, optionally filtered by classification."""
        out = sorted(self.candidates,
                     key=lambda c: (c.maturity * c.value_score), reverse=True)
        if classification:
            out = [c for c in out if c.classification == classification]
        return out

    def read(self) -> SensorReading:
        surveyed = self.candidates
        adrift = [c for c in surveyed if not c.on_official_manifest]
        cargo = [c for c in adrift if c.classification == "cargo"]
        beacons = [c for c in adrift if c.classification == "beacon"]
        registered = len(surveyed) - len(adrift)
        match_rate = registered / len(surveyed) if surveyed else 1.0
        uncommitted = sum(d.get("uncommitted", 0)
                          for d in self.repo_divergence.values())
        unpushed = sum(d.get("unpushed_commits", 0)
                       for d in self.repo_divergence.values())
        mean_maturity = (sum(c.maturity for c in adrift) / len(adrift)
                         if adrift else 0.0)

        alerts: List[str] = []
        if cargo:
            alerts.append(
                f"{len(cargo)} high-value cargo contact(s) off-manifest — "
                "recovery candidates await routing")
        if beacons:
            alerts.append(
                f"{len(beacons)} distress beacon(s): identity-bearing "
                "artifacts unregistered")
        if surveyed and match_rate < REGISTRY_MATCH_ALERT:
            alerts.append(
                f"fleet registry match {match_rate:.2f} < "
                f"{REGISTRY_MATCH_ALERT}: majority of surveyed field is adrift")

        return self._reading(
            values={
                "salvage_contacts": float(len(adrift)),
                "high_value_cargo": float(len(cargo)),
                "beacon_signals": float(len(beacons)),
                "registry_match_rate": match_rate,
                "mean_cargo_maturity": mean_maturity,
                "uncommitted_in_repos": float(uncommitted),
                "unpushed_commits": float(unpushed),
            },
            units={
                "salvage_contacts": MetricUnit.COUNT,
                "high_value_cargo": MetricUnit.COUNT,
                "beacon_signals": MetricUnit.COUNT,
                "registry_match_rate": MetricUnit.RATIO,
                "mean_cargo_maturity": MetricUnit.RATIO,
                "uncommitted_in_repos": MetricUnit.COUNT,
                "unpushed_commits": MetricUnit.COUNT,
            },
            alerts=alerts,
            metadata={
                "top_cargo": [
                    {"path": c.path, "maturity": round(c.maturity, 2),
                     "value_score": c.value_score,
                     "classification": c.classification,
                     "promotion_status": c.promotion_status}
                    for c in self.manifest()[:10]
                    if not c.on_official_manifest
                ],
                "repo_divergence": self.repo_divergence,
            },
        )
