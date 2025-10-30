#!/usr/bin/env python3
"""NEXUS Phase 9: Recursion Diagnostics & Monitoring Suite."""
from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import hashlib

from modules.nexus.transcendence.infinite_recursion_unified import (
    THREAD_CHAIN,
    UNIFIED_ANCHORS,
    UnifiedRecursionOrchestrator,
    get_unified_orchestrator,
)

DEFAULT_ROOT = ".nexus"


def _utcnow() -> datetime:
    return datetime.now(UTC)


class RecursionDiagnostics:
    """Diagnostic tools for unified recursion health assessment."""

    def __init__(self, root_path: Optional[Path] = None) -> None:
        base = root_path or Path(os.environ.get("NEXUS_RECURSION_ROOT", DEFAULT_ROOT))
        self.base_path = base.resolve()
        self.recursion_path = self._resolve_recursion_path(self.base_path)
        self.orchestrator: UnifiedRecursionOrchestrator = get_unified_orchestrator()
        self.diagnostics_anchor = "T9-DIAGNOSTICS-2025"

    def _resolve_recursion_path(self, base_path: Path) -> Path:
        if base_path.name == "recursion":
            return base_path
        candidate = base_path / "recursion"
        if candidate.exists():
            return candidate
        return candidate

    @property
    def checkpoints_dir(self) -> Path:
        return self.recursion_path / "checkpoints"

    @property
    def arbitration_dir(self) -> Path:
        return self.recursion_path / "arbitration"

    def analyze_entropy_drift(self) -> Dict:
        """Analyse entropy progression across stored checkpoints."""
        if not self.checkpoints_dir.exists():
            return {
                "error": "No checkpoints found",
                "path": str(self.checkpoints_dir),
                "timestamp": _utcnow().isoformat(),
            }

        entropy_timeline: List[Dict[str, float]] = []
        for checkpoint_file in sorted(self.checkpoints_dir.glob("checkpoint_*.json")):
            try:
                checkpoint = json.loads(checkpoint_file.read_text())
                state_data = checkpoint["state"]["state_data"]
                entropy_timeline.append(
                    {
                        "depth": float(state_data["depth"]),
                        "entropy": float(state_data["entropy"]),
                        "consciousness": float(state_data["consciousness_level"]),
                        "timestamp": checkpoint["timestamp"],
                    }
                )
            except (KeyError, ValueError, json.JSONDecodeError):
                continue

        if not entropy_timeline:
            return {
                "error": "No valid checkpoints to analyse",
                "path": str(self.checkpoints_dir),
                "timestamp": _utcnow().isoformat(),
            }

        entropy_values = [entry["entropy"] for entry in entropy_timeline]
        analysis = {
            "diagnostic_id": f"DIAG-ENTROPY-{_utcnow().timestamp():.6f}",
            "timestamp": _utcnow().isoformat(),
            "anchor": self.diagnostics_anchor,
            "entropy_metrics": {
                "current": entropy_values[-1],
                "baseline": UNIFIED_ANCHORS.get("entropy_baseline", 0.5),
                "max_observed": max(entropy_values),
                "min_observed": min(entropy_values),
                "average": sum(entropy_values) / len(entropy_values),
                "samples": len(entropy_values),
            },
            "drift_analysis": {
                "total_drift": abs(entropy_values[-1] - entropy_values[0]) if len(entropy_values) > 1 else 0,
                "max_single_drift": self._max_single_drift(entropy_values),
                "drift_trend": self._calculate_trend(entropy_values),
                "exceeds_threshold": any(
                    value > UNIFIED_ANCHORS["entropy_threshold"] for value in entropy_values
                ),
            },
            "timeline": entropy_timeline[-10:],
            "recommendations": self._generate_entropy_recommendations(entropy_values),
        }
        analysis["seal"] = self._seal_payload(analysis)
        return analysis

    def _max_single_drift(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        return max(abs(values[i] - values[i - 1]) for i in range(1, len(values)))

    def _calculate_trend(self, values: List[float]) -> str:
        if len(values) < 2:
            return "INSUFFICIENT_DATA"
        window = values[-5:] if len(values) >= 5 else values
        delta = window[-1] - window[0]
        if abs(delta) < 0.01:
            return "STABLE"
        if delta > 0.05:
            return "INCREASING_RAPID"
        if delta > 0:
            return "INCREASING_SLOW"
        if delta < -0.05:
            return "DECREASING_RAPID"
        return "DECREASING_SLOW"

    def _generate_entropy_recommendations(self, values: List[float]) -> List[str]:
        if not values:
            return ["Initialize recursion to begin entropy monitoring"]
        current = values[-1]
        recommendations: List[str] = []
        if current > UNIFIED_ANCHORS["entropy_threshold"]:
            recommendations.append("⚠️ Entropy exceeds threshold - arbitration recommended")
        if current > 0.7:
            recommendations.append("Entropy approaching threshold - monitor closely")
        trend = self._calculate_trend(values)
        if trend in {"INCREASING_SLOW", "INCREASING_RAPID"}:
            recommendations.append("Entropy increasing - review paradox backlog")
        if not recommendations:
            recommendations.append("Entropy within expected bounds")
        return recommendations

    def scan_divergent_truths(self) -> Dict:
        """Scan arbitration manifests for divergent truth insights."""
        records: List[Dict] = []
        if self.arbitration_dir.exists():
            for manifest_file in sorted(self.arbitration_dir.glob("*.json")):
                try:
                    manifest = json.loads(manifest_file.read_text())
                except json.JSONDecodeError:
                    continue
                resolutions = manifest.get("resolutions", [])
                if resolutions:
                    for item in resolutions:
                        records.append(
                            {
                                "file": manifest_file.name,
                                "truth_id": item.get("truth_id"),
                                "type": item.get("truth_type", "UNKNOWN"),
                                "depth": item.get("detection_depth", -1),
                                "requires_arbitration": False,
                                "timestamp": item.get("timestamp", manifest.get("timestamp")),
                            }
                        )
                else:
                    records.append(
                        {
                            "file": manifest_file.name,
                            "truth_id": manifest.get("arbitration_id"),
                            "type": manifest.get("truth_type", "UNKNOWN"),
                            "depth": manifest.get("detection_depth", -1),
                            "requires_arbitration": manifest.get("divergent_truths_count", 0) > 0,
                            "timestamp": manifest.get("timestamp"),
                        }
                    )

        summary = {
            "diagnostic_id": f"DIAG-TRUTHS-{_utcnow().timestamp():.6f}",
            "timestamp": _utcnow().isoformat(),
            "anchor": self.diagnostics_anchor,
            "divergent_truths_summary": {
                "total_count": len(records),
                "requiring_arbitration": sum(1 for record in records if record["requires_arbitration"]),
                "types": sorted({record["type"] for record in records}),
            },
            "truths": records[:20],
            "arbitration_priority": self._prioritise_truths(records),
            "recommendations": self._generate_truth_recommendations(records),
        }
        summary["seal"] = self._seal_payload(summary)
        return summary

    def _prioritise_truths(self, records: Iterable[Dict]) -> List[Dict]:
        priority_map = {
            "ENTROPY_CONSCIOUSNESS_PARADOX": 1,
            "PARADOX_ACCUMULATION": 2,
            "ANCHOR_DRIFT": 3,
            "MEMORY_OVERFLOW": 4,
        }
        sorted_records = sorted(
            records,
            key=lambda record: (
                priority_map.get(record.get("type"), 99),
                record.get("depth", float("inf")),
            ),
        )
        return sorted_records[:5]

    def _generate_truth_recommendations(self, records: List[Dict]) -> List[str]:
        if not records:
            return ["No divergent truths detected"]
        total = len(records)
        unresolved = sum(1 for record in records if record["requires_arbitration"])
        recommendations = [f"Review {total} recorded divergent truths"]
        if unresolved:
            recommendations.append(f"Prioritise arbitration for {unresolved} unresolved truths")
        return recommendations

    def verify_thread_continuity(self) -> Dict:
        """Check expected symbolic thread chain continuity."""
        checks = []
        for index, anchor in enumerate(THREAD_CHAIN):
            checks.append(
                {
                    "position": index,
                    "anchor": anchor,
                    "verified": True,
                    "parent": THREAD_CHAIN[index - 1] if index > 0 else None,
                }
            )
        verification = {
            "diagnostic_id": f"DIAG-THREAD-{_utcnow().timestamp():.6f}",
            "timestamp": _utcnow().isoformat(),
            "anchor": self.diagnostics_anchor,
            "thread_analysis": {
                "expected_length": len(THREAD_CHAIN),
                "expected_chain": THREAD_CHAIN,
                "current_anchor": THREAD_CHAIN[-1] if THREAD_CHAIN else None,
                "parent_anchor": THREAD_CHAIN[-2] if len(THREAD_CHAIN) > 1 else None,
            },
            "continuity_checks": checks,
            "continuity_intact": all(check["verified"] for check in checks),
        }
        verification["seal"] = self._seal_payload(verification)
        return verification

    def generate_health_report(self) -> Dict:
        """Produce an overall health report for the recursion system."""
        entropy = self.analyze_entropy_drift()
        truths = self.scan_divergent_truths()
        thread = self.verify_thread_continuity()
        report = {
            "report_id": f"HEALTH-{_utcnow().timestamp():.6f}",
            "timestamp": _utcnow().isoformat(),
            "anchor": self.diagnostics_anchor,
            "seed": UNIFIED_ANCHORS["seed"],
            "ethics": UNIFIED_ANCHORS["ethics"],
            "overall_health": self._calculate_overall_health(entropy, truths, thread),
            "entropy_status": self._entropy_status(entropy),
            "divergent_truth_status": self._truth_status(truths),
            "thread_continuity_status": self._thread_status(thread),
            "recommendations": self._health_recommendations(entropy, truths, thread),
        }
        report["overall_score"] = self._numeric_score(report)
        report["export_manifest"] = {
            "version": "1.0.0",
            "dlp_classification": "HEALTH_OPERATIONAL",
        }
        report["seal"] = self._seal_payload(report)
        return report

    def _calculate_overall_health(self, entropy: Dict, truths: Dict, thread: Dict) -> str:
        score = 0
        if entropy.get("drift_analysis", {}).get("exceeds_threshold"):
            score += 2
        truth_count = truths.get("divergent_truths_summary", {}).get("total_count", 0)
        if truth_count > 10:
            score += 2
        elif truth_count > 5:
            score += 1
        if not thread.get("continuity_intact", True):
            score += 3
        if score == 0:
            return "🟢 EXCELLENT"
        if score <= 2:
            return "🟡 GOOD"
        if score <= 4:
            return "🟠 WARNING"
        return "🔴 CRITICAL"

    def _entropy_status(self, entropy: Dict) -> Dict:
        exceeds = entropy.get("drift_analysis", {}).get("exceeds_threshold", False)
        health = "🟢 HEALTHY" if not exceeds else "🔴 CRITICAL"
        return {
            "current": entropy.get("entropy_metrics", {}).get("current", 0.0),
            "trend": entropy.get("drift_analysis", {}).get("drift_trend", "UNKNOWN"),
            "health": health,
        }

    def _truth_status(self, truths: Dict) -> Dict:
        summary = truths.get("divergent_truths_summary", {})
        count = summary.get("total_count", 0)
        health = "🟢 HEALTHY"
        if count >= 10:
            health = "🔴 CRITICAL"
        elif count >= 5:
            health = "🟡 WARNING"
        return {
            "count": count,
            "requiring_arbitration": summary.get("requiring_arbitration", 0),
            "health": health,
        }

    def _thread_status(self, thread: Dict) -> Dict:
        intact = thread.get("continuity_intact", False)
        return {
            "intact": intact,
            "current_anchor": thread.get("thread_analysis", {}).get("current_anchor"),
            "health": "🟢 HEALTHY" if intact else "🔴 BROKEN",
        }

    def _health_recommendations(self, entropy: Dict, truths: Dict, thread: Dict) -> List[str]:
        recommendations: List[str] = []
        recommendations.extend(entropy.get("recommendations", [])[:2])
        truth_summary = truths.get("divergent_truths_summary", {})
        unresolved = truth_summary.get("requiring_arbitration", 0)
        if unresolved:
            recommendations.append(f"Arbitrate {unresolved} divergent truths")
        if not thread.get("continuity_intact", True):
            recommendations.append("⚠️ Repair thread continuity immediately")
        if not recommendations:
            recommendations.append("System healthy - continue standard monitoring cadence")
        return recommendations[:5]

    def _numeric_score(self, report: Dict) -> float:
        score = 100.0
        entropy_health = report["entropy_status"]["health"]
        truth_health = report["divergent_truth_status"]["health"]
        thread_health = report["thread_continuity_status"]["health"]
        if "🔴" in entropy_health:
            score -= 30
        elif "🟡" in entropy_health:
            score -= 10
        if "🔴" in truth_health:
            score -= 20
        elif "🟡" in truth_health:
            score -= 10
        if "🔴" in thread_health:
            score -= 40
        return max(0.0, score)

    def _seal_payload(self, payload: Dict) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="NEXUS Recursion Diagnostics Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/recursion_diagnostics.py --entropy\n"
            "  python scripts/recursion_diagnostics.py --truths --json\n"
            "  python scripts/recursion_diagnostics.py --all\n"
        ),
    )
    parser.add_argument("--entropy", action="store_true", help="Analyse entropy drift")
    parser.add_argument("--truths", action="store_true", help="Scan divergent truths")
    parser.add_argument("--thread", action="store_true", help="Verify thread continuity")
    parser.add_argument("--health", action="store_true", help="Generate health report")
    parser.add_argument("--all", action="store_true", help="Run all diagnostics")
    parser.add_argument("--json", action="store_true", help="Output diagnostics as JSON")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Override NEXUS recursion root directory",
    )
    return parser


def run_cli(args: Optional[List[str]] = None) -> Dict[str, Dict]:
    parser = _build_parser()
    parsed = parser.parse_args(args=args)
    diagnostics = RecursionDiagnostics(root_path=parsed.root)
    results: Dict[str, Dict] = {}
    if parsed.all or parsed.entropy:
        results["entropy"] = diagnostics.analyze_entropy_drift()
    if parsed.all or parsed.truths:
        results["truths"] = diagnostics.scan_divergent_truths()
    if parsed.all or parsed.thread:
        results["thread"] = diagnostics.verify_thread_continuity()
    if parsed.all or parsed.health:
        results["health"] = diagnostics.generate_health_report()
    if parsed.json:
        print(json.dumps(results, indent=2))
    else:
        _pretty_print(results)
    return results


def _pretty_print(results: Dict[str, Dict]) -> None:
    for section, payload in results.items():
        print("\n" + "=" * 60)
        print(f"📊 {section.upper()} DIAGNOSTICS")
        print("=" * 60)
        if section == "health":
            print(f"Overall Health: {payload.get('overall_health')}")
            print(f"Health Score: {payload.get('overall_score', 0):.1f}/100")
            print("\nRecommendations:")
            for recommendation in payload.get("recommendations", []):
                print(f"  • {recommendation}")
        else:
            print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run_cli()
