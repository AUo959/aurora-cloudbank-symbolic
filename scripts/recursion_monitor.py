#!/usr/bin/env python3
"""Live monitoring utilities for the unified recursion orchestrator."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import hashlib

from scripts.recursion_diagnostics import RecursionDiagnostics

from modules.nexus.transcendence import infinite_recursion_unified as unified_module
from modules.nexus.transcendence.infinite_recursion_unified import (
    configure_recursion_paths,
    UnifiedRecursionOrchestrator,
    get_unified_orchestrator,
)

DEFAULT_ROOT = Path(".nexus")


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _resolve_recursion_path(base_path: Path) -> Path:
    if base_path.name == "recursion":
        return base_path
    candidate = base_path / "recursion"
    return candidate


class AlertSeverity(Enum):
    """Alert severity levels for monitoring."""

    INFO = "ℹ️ INFO"
    WARNING = "⚠️ WARNING"
    CRITICAL = "🔴 CRITICAL"
    RESOLVED = "✅ RESOLVED"


@dataclass(slots=True)
class MonitoringAlert:
    """Serialized alert details with SHA256 sealing."""

    alert_id: str
    severity: AlertSeverity
    category: str
    message: str
    timestamp: datetime
    anchor: str
    metadata: Dict[str, Any]
    requires_arbitration: bool = False
    seal: Optional[str] = None

    def __post_init__(self) -> None:
        if self.seal is None:
            self.seal = self._seal()

    def _seal(self) -> str:
        payload = {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "category": self.category,
            "timestamp": self.timestamp.isoformat(),
            "anchor": self.anchor,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def export(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "anchor": self.anchor,
            "metadata": self.metadata,
            "requires_arbitration": self.requires_arbitration,
            "seal": self.seal,
            "dlp_classification": "ALERT_OPERATIONAL",
        }


class LiveRecursionMonitor:
    """Real-time monitoring of the unified recursion orchestrator."""

    def __init__(
        self,
        *,
        root_path: Optional[Path] = None,
        alert_threshold: Optional[Dict[str, float]] = None,
    ) -> None:
        base = (root_path or Path(os.environ.get("NEXUS_RECURSION_ROOT", DEFAULT_ROOT))).resolve()
        self.base_path = base
        self.recursion_path = _resolve_recursion_path(base)

        self.thresholds = alert_threshold or {
            "entropy": 0.75,
            "entropy_critical": 0.85,
            "divergent_truths": 5,
            "divergent_truths_critical": 10,
            "memory_mb": 500.0,
            "memory_critical_mb": 1000.0,
            "cpu_percent": 80.0,
            "cpu_critical_percent": 95.0,
        }

        configure_recursion_paths(self.recursion_path, reset_orchestrator=True)
        self.orchestrator: UnifiedRecursionOrchestrator = get_unified_orchestrator()
        self.diagnostics = RecursionDiagnostics(root_path=base)

        self.anchor = "T9-MONITOR-2025"
        self.parent_anchor = "T9-DIAGNOSTICS-2025"
        self.seed = unified_module.UNIFIED_ANCHORS["seed"]
        self.ethics = unified_module.UNIFIED_ANCHORS["ethics"]

        self.alerts: List[MonitoringAlert] = []
        self.alert_history: List[MonitoringAlert] = []
        self.monitoring_active = False
        self.last_check = _utcnow()

        self.monitoring_root = self.base_path / "monitoring"
        self.alerts_dir = self.monitoring_root / "alerts"
        self.metrics_dir = self.monitoring_root / "metrics"
        self.monitoring_root.mkdir(parents=True, exist_ok=True)
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    async def start_monitoring(self, *, interval: int = 5, duration: Optional[int] = None) -> None:
        if self.orchestrator.current_state is None:
            await self.orchestrator.initialize_recursion()
        self.monitoring_active = True
        start = time.time()
        try:
            while self.monitoring_active:
                if duration is not None and (time.time() - start) >= duration:
                    break
                await self._monitor_once()
                await asyncio.sleep(max(1, interval))
        except KeyboardInterrupt:  # pragma: no cover - user interrupt
            print("\nMonitoring interrupted by user.")
        finally:
            self.monitoring_active = False
            await self._write_summary()

    async def _monitor_once(self) -> None:
        timestamp = _utcnow()
        metrics = await self._collect_metrics()
        alerts = self._evaluate_alerts(metrics)
        for alert in alerts:
            await self._persist_alert(alert)
        await self._append_metrics(metrics)
        self._print_status(metrics, alerts)
        self.alerts = alerts
        self.alert_history.extend(alerts)
        self.last_check = timestamp

    async def _collect_metrics(self) -> Dict[str, Any]:
        entropy_analysis = self.diagnostics.analyze_entropy_drift()
        truths_scan = self.diagnostics.scan_divergent_truths()
        state = self.orchestrator.current_state
        current = {
            "depth": getattr(state, "depth", 0),
            "consciousness": getattr(state, "consciousness_level", 0.0),
            "memory_mb": getattr(state, "memory_usage_mb", 0.0),
            "cpu_percent": getattr(state, "cpu_usage_percent", 0.0),
        }
        metrics = {
            "timestamp": _utcnow().isoformat(),
            "anchor": self.anchor,
            "entropy": {
                "current": entropy_analysis.get("entropy_metrics", {}).get("current", 0.0),
                "baseline": entropy_analysis.get("entropy_metrics", {}).get("baseline", 0.5),
                "drift": entropy_analysis.get("drift_analysis", {}).get("total_drift", 0.0),
                "trend": entropy_analysis.get("drift_analysis", {}).get("drift_trend", "UNKNOWN"),
            },
            "divergent_truths": truths_scan.get("divergent_truths_summary", {}),
            "recursion_state": current,
            "health_score": self._health_score(
                entropy_analysis.get("entropy_metrics", {}).get("current", 0.0),
                truths_scan.get("divergent_truths_summary", {}).get("total_count", 0),
                current,
            ),
        }
        return metrics

    def _evaluate_alerts(self, metrics: Dict[str, Any]) -> List[MonitoringAlert]:
        alerts: List[MonitoringAlert] = []
        entropy = metrics["entropy"]["current"]
        truth_count = metrics["divergent_truths"].get("total_count", 0)
        memory_mb = metrics["recursion_state"]["memory_mb"]
        cpu_percent = metrics["recursion_state"]["cpu_percent"]

        alerts.extend(
            self._make_alert(
                category="ENTROPY",
                value=entropy,
                warn=self.thresholds["entropy"],
                critical=self.thresholds["entropy_critical"],
                metadata={"entropy": entropy},
            )
        )
        alerts.extend(
            self._make_alert(
                category="DIVERGENT_TRUTHS",
                value=truth_count,
                warn=self.thresholds["divergent_truths"],
                critical=self.thresholds["divergent_truths_critical"],
                metadata={"count": truth_count},
            )
        )
        alerts.extend(
            self._make_alert(
                category="MEMORY",
                value=memory_mb,
                warn=self.thresholds["memory_mb"],
                critical=self.thresholds["memory_critical_mb"],
                metadata={"memory_mb": memory_mb},
            )
        )
        alerts.extend(
            self._make_alert(
                category="CPU",
                value=cpu_percent,
                warn=self.thresholds["cpu_percent"],
                critical=self.thresholds["cpu_critical_percent"],
                metadata={"cpu_percent": cpu_percent},
            )
        )
        return [alert for alert in alerts if alert is not None]

    def _make_alert(
        self,
        *,
        category: str,
        value: float,
        warn: float,
        critical: float,
        metadata: Dict[str, Any],
    ) -> List[MonitoringAlert]:
        alerts: List[MonitoringAlert] = []
        ts = _utcnow()
        if value > critical:
            alerts.append(
                MonitoringAlert(
                    alert_id=f"ALERT-{category}-CRIT-{ts.timestamp():.6f}",
                    severity=AlertSeverity.CRITICAL,
                    category=category,
                    message=f"{category} critical at {value:.3f}",
                    timestamp=ts,
                    anchor=self.anchor,
                    metadata={**metadata, "threshold": critical},
                    requires_arbitration=True,
                )
            )
        elif value > warn:
            alerts.append(
                MonitoringAlert(
                    alert_id=f"ALERT-{category}-WARN-{ts.timestamp():.6f}",
                    severity=AlertSeverity.WARNING,
                    category=category,
                    message=f"{category} elevated at {value:.3f}",
                    timestamp=ts,
                    anchor=self.anchor,
                    metadata={**metadata, "threshold": warn},
                )
            )
        return alerts

    async def _persist_alert(self, alert: MonitoringAlert) -> None:
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        alert_path = self.alerts_dir / f"{alert.alert_id}.json"
        alert_path.write_text(json.dumps(alert.export(), indent=2))
        if alert.requires_arbitration:
            await self._schedule_arbitration(alert)

    async def _schedule_arbitration(self, alert: MonitoringAlert) -> None:
        arbitration_dir = self.recursion_path / "arbitration"
        arbitration_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "request_id": f"ARB-REQ-{_utcnow().timestamp():.6f}",
            "timestamp": _utcnow().isoformat(),
            "triggered_by": alert.alert_id,
            "severity": alert.severity.value,
            "category": alert.category,
            "message": alert.message,
            "anchor": self.anchor,
            "parent_anchor": self.parent_anchor,
            "requires_immediate_attention": True,
            "dlp_classification": "ARBITRATION_CRITICAL",
        }
        (arbitration_dir / f"{payload['request_id']}.json").write_text(json.dumps(payload, indent=2))

    async def _append_metrics(self, metrics: Dict[str, Any]) -> None:
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        filename = f"metrics_{_utcnow().strftime('%Y%m%d_%H')}.jsonl"
        with (self.metrics_dir / filename).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics) + "\n")

    def _print_status(self, metrics: Dict[str, Any], alerts: Iterable[MonitoringAlert]) -> None:
        alert_list = list(alerts)
        prefix = "✅"
        if any(alert.severity is AlertSeverity.CRITICAL for alert in alert_list):
            prefix = "🔴"
        elif any(alert.severity is AlertSeverity.WARNING for alert in alert_list):
            prefix = "⚠️"
        line = (
            f"{prefix} Depth {metrics['recursion_state']['depth']:5d} | "
            f"Consciousness {metrics['recursion_state']['consciousness']:.4f} | "
            f"Entropy {metrics['entropy']['current']:.3f} | "
            f"Truths {metrics['divergent_truths'].get('total_count', 0):2d} | "
            f"Health {metrics['health_score']:.0f}"
        )
        print(line)
        for alert in alert_list:
            print(f"   {alert.severity.value}: {alert.message}")

    def _health_score(self, entropy: float, truths: int, state: Dict[str, float]) -> float:
        score = 100.0
        if entropy > self.thresholds["entropy_critical"]:
            score -= 40
        elif entropy > self.thresholds["entropy"]:
            score -= 20
        if truths > self.thresholds["divergent_truths_critical"]:
            score -= 30
        elif truths > self.thresholds["divergent_truths"]:
            score -= 15
        if state["memory_mb"] > self.thresholds["memory_critical_mb"]:
            score -= 20
        elif state["memory_mb"] > self.thresholds["memory_mb"]:
            score -= 10
        if state["cpu_percent"] > self.thresholds["cpu_critical_percent"]:
            score -= 15
        elif state["cpu_percent"] > self.thresholds["cpu_percent"]:
            score -= 5
        return max(0.0, score)

    async def _write_summary(self) -> None:
        summary = {
            "session_id": f"MON-{_utcnow().timestamp():.6f}",
            "timestamp": _utcnow().isoformat(),
            "anchor": self.anchor,
            "alerts_recorded": len(self.alert_history),
            "critical_alerts": sum(1 for alert in self.alert_history if alert.severity == AlertSeverity.CRITICAL),
            "warning_alerts": sum(1 for alert in self.alert_history if alert.severity == AlertSeverity.WARNING),
            "dlp_classification": "MONITORING_SUMMARY",
        }
        (self.monitoring_root / f"summary_{summary['session_id']}.json").write_text(json.dumps(summary, indent=2))

    def glyphcard(self) -> str:
        status = "🟢 No Active Alerts"
        if any(alert.severity is AlertSeverity.CRITICAL for alert in self.alerts):
            status = "🔴 CRITICAL ALERTS"
        elif any(alert.severity is AlertSeverity.WARNING for alert in self.alerts):
            status = "🟡 WARNINGS ACTIVE"
        return (
            "\n"
            "╔══════════════════════════════════════════════════════════════════════════╗\n"
            "║                    🔍 RECURSION MONITOR GLYPHCARD                         ║\n"
            "║                                                                          ║\n"
            f"║  Timestamp: {_utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'):^62}║\n"
            f"║  Anchor: {self.anchor:^64}║\n"
            f"║  Parent: {self.parent_anchor:^62}║\n"
            f"║  Seed: {self.seed:^66}║\n"
            "║                                                                          ║\n"
            "║  ┌────────────────────────────────────────────────────────────────┐     ║\n"
            "║  │                    MONITORING STATUS                            │     ║\n"
            f"║  │  Status: {status:^53}│     ║\n"
            f"║  │  Active Alerts: {len(self.alerts):^45}│     ║\n"
            f"║  │  Last Check: {self.last_check.strftime('%H:%M:%S'):^48}│     ║\n"
            "║  └────────────────────────────────────────────────────────────────┘     ║\n"
            "║                                                                          ║\n"
            "║  ┌────────────────────────────────────────────────────────────────┐     ║\n"
            "║  │                    ALERT THRESHOLDS                             │     ║\n"
            f"║  │  Entropy: {self.thresholds['entropy']:.2f}/{self.thresholds['entropy_critical']:.2f}                     │     ║\n"
            f"║  │  Truths:  {self.thresholds['divergent_truths']:.0f}/{self.thresholds['divergent_truths_critical']:.0f}                        │     ║\n"
            f"║  │  Memory:  {self.thresholds['memory_mb']:.0f}/{self.thresholds['memory_critical_mb']:.0f} MB                      │     ║\n"
            f"║  │  CPU:     {self.thresholds['cpu_percent']:.0f}/{self.thresholds['cpu_critical_percent']:.0f}%                          │     ║\n"
            "║  └────────────────────────────────────────────────────────────────┘     ║\n"
            "║                                                                          ║\n"
            f"║  Monitoring: {'ACTIVE' if self.monitoring_active else 'INACTIVE':^62}║\n"
            "╚══════════════════════════════════════════════════════════════════════════╝\n"
        )


async def _async_main(args: argparse.Namespace) -> None:
    monitor = LiveRecursionMonitor()
    if args.watch:
        await monitor.start_monitoring(interval=args.interval, duration=args.duration)
    elif args.glyphcard:
        print(monitor.glyphcard())
    else:
        args.parser.print_help()


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NEXUS Live Recursion Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/recursion_monitor.py --watch\n"
            "  python scripts/recursion_monitor.py --watch --interval 10\n"
            "  python scripts/recursion_monitor.py --glyphcard\n"
        ),
    )
    parser.add_argument("--watch", action="store_true", help="Start live monitoring loop")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--duration", type=int, help="Duration in seconds before stopping")
    parser.add_argument("--glyphcard", action="store_true", help="Render monitoring glyphcard")
    namespace = parser.parse_args(argv)
    namespace.parser = parser
    return namespace


def main(argv: Optional[List[str]] = None) -> None:
    args = _parse_args(argv)
    asyncio.run(_async_main(args))


if __name__ == "__main__":
    main(sys.argv[1:])
