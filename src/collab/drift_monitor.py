"""
Drift Monitoring and Analytics Module

Real-time drift monitoring, statistics tracking, and dashboard endpoints
for cross-repository collaboration.

Thread: T1→COLLAB→DRIFT_MONITOR
DLP: context_tag=collab_drift_monitoring
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import json
import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class DriftLevel(Enum):
    """Drift alert levels based on thresholds."""
    GREEN = "green"  # < 0.1% drift
    YELLOW = "yellow"  # 0.1-0.2% drift
    RED = "red"  # > 0.2% drift


class DriftEventType(Enum):
    """Types of drift events."""
    CAPSULE_IMPORT = "capsule_import"
    CAPSULE_EXPORT = "capsule_export"
    ANCHOR_VERIFICATION = "anchor_verification"
    AGENT_SYNC = "agent_sync"
    MANUAL_CHECK = "manual_check"


@dataclass
class DriftEvent:
    """Individual drift measurement event."""
    event_id: str
    timestamp: str
    event_type: DriftEventType
    drift_value: float
    drift_level: DriftLevel
    source_repo: Optional[str] = None
    target_repo: Optional[str] = None
    capsule_id: Optional[str] = None
    agent_roster: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "drift_value": self.drift_value,
            "drift_level": self.drift_level.value,
            "source_repo": self.source_repo,
            "target_repo": self.target_repo,
            "capsule_id": self.capsule_id,
            "agent_roster": self.agent_roster,
            "metadata": self.metadata
        }


@dataclass
class DriftStatistics:
    """Statistical summary of drift measurements."""
    total_events: int
    current_drift: float
    average_drift: float
    max_drift: float
    min_drift: float
    drift_trend: str  # "increasing", "decreasing", "stable"
    green_count: int
    yellow_count: int
    red_count: int
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_events": self.total_events,
            "current_drift": self.current_drift,
            "average_drift": self.average_drift,
            "max_drift": self.max_drift,
            "min_drift": self.min_drift,
            "drift_trend": self.drift_trend,
            "green_count": self.green_count,
            "yellow_count": self.yellow_count,
            "red_count": self.red_count,
            "last_updated": self.last_updated
        }


class DriftMonitor:
    """
    Drift monitoring and analytics system.
    
    Tracks drift events, computes statistics, and provides alerts
    for cross-repository collaboration.
    """
    
    # Drift thresholds
    THRESHOLD_YELLOW = 0.001  # 0.1%
    THRESHOLD_RED = 0.002  # 0.2%
    
    # History size for rolling statistics
    MAX_HISTORY_SIZE = 1000
    
    def __init__(self):
        """Initialize drift monitor."""
        self.events: deque = deque(maxlen=self.MAX_HISTORY_SIZE)
        self.current_drift = 0.0
        self._event_counter = 0
    
    def classify_drift(self, drift_value: float) -> DriftLevel:
        """Classify drift value into alert level."""
        if drift_value < self.THRESHOLD_YELLOW:
            return DriftLevel.GREEN
        elif drift_value < self.THRESHOLD_RED:
            return DriftLevel.YELLOW
        else:
            return DriftLevel.RED
    
    def record_drift(
        self,
        drift_value: float,
        event_type: DriftEventType,
        source_repo: Optional[str] = None,
        target_repo: Optional[str] = None,
        capsule_id: Optional[str] = None,
        agent_roster: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DriftEvent:
        """
        Record a drift measurement event.
        
        Args:
            drift_value: Measured drift value
            event_type: Type of event that triggered drift measurement
            source_repo: Source repository (if applicable)
            target_repo: Target repository (if applicable)
            capsule_id: Associated capsule ID (if applicable)
            agent_roster: Agents involved (if applicable)
            metadata: Additional metadata
            
        Returns:
            Created DriftEvent
        """
        self._event_counter += 1
        event_id = f"drift_event_{self._event_counter:06d}"
        
        drift_level = self.classify_drift(drift_value)
        
        event = DriftEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            drift_value=drift_value,
            drift_level=drift_level,
            source_repo=source_repo,
            target_repo=target_repo,
            capsule_id=capsule_id,
            agent_roster=agent_roster or [],
            metadata=metadata or {}
        )
        
        self.events.append(event)
        self.current_drift = drift_value
        
        logger.info(
            "Drift recorded: %.4f%% [%s] - %s",
            drift_value * 100,
            drift_level.value.upper(),
            event_type.value
        )
        
        return event
    
    def get_statistics(self) -> DriftStatistics:
        """
        Compute drift statistics from recorded events.
        
        Returns:
            DriftStatistics summary
        """
        if not self.events:
            return DriftStatistics(
                total_events=0,
                current_drift=0.0,
                average_drift=0.0,
                max_drift=0.0,
                min_drift=0.0,
                drift_trend="stable",
                green_count=0,
                yellow_count=0,
                red_count=0,
                last_updated=datetime.now().isoformat()
            )
        
        drift_values = [e.drift_value for e in self.events]
        
        # Count by level
        green_count = sum(1 for e in self.events if e.drift_level == DriftLevel.GREEN)
        yellow_count = sum(1 for e in self.events if e.drift_level == DriftLevel.YELLOW)
        red_count = sum(1 for e in self.events if e.drift_level == DriftLevel.RED)
        
        # Compute trend (last 10 events)
        recent_events = list(self.events)[-10:]
        if len(recent_events) >= 2:
            first_half_avg = sum(e.drift_value for e in recent_events[:len(recent_events)//2]) / (len(recent_events)//2)
            second_half_avg = sum(e.drift_value for e in recent_events[len(recent_events)//2:]) / \
                              (len(recent_events) - len(recent_events)//2)
            
            if second_half_avg > first_half_avg * 1.1:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return DriftStatistics(
            total_events=len(self.events),
            current_drift=self.current_drift,
            average_drift=sum(drift_values) / len(drift_values),
            max_drift=max(drift_values),
            min_drift=min(drift_values),
            drift_trend=trend,
            green_count=green_count,
            yellow_count=yellow_count,
            red_count=red_count,
            last_updated=datetime.now().isoformat()
        )
    
    def get_recent_events(self, count: int = 10) -> List[DriftEvent]:
        """Get most recent drift events."""
        return list(self.events)[-count:]
    
    def get_events_by_level(self, level: DriftLevel) -> List[DriftEvent]:
        """Get all events matching specific drift level."""
        return [e for e in self.events if e.drift_level == level]
    
    def get_events_by_type(self, event_type: DriftEventType) -> List[DriftEvent]:
        """Get all events matching specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_repo(self, repo_id: str) -> List[DriftEvent]:
        """Get all events involving specific repository."""
        return [
            e for e in self.events
            if e.source_repo == repo_id or e.target_repo == repo_id
        ]
    
    def get_events_since(self, since: datetime) -> List[DriftEvent]:
        """Get all events since specified timestamp."""
        since_iso = since.isoformat()
        return [e for e in self.events if e.timestamp >= since_iso]
    
    def compute_capsule_diff(
        self,
        before_capsule: Dict[str, Any],
        after_capsule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute difference between capsule states before/after event.
        
        Args:
            before_capsule: Capsule state before operation
            after_capsule: Capsule state after operation
            
        Returns:
            Diff summary dictionary
        """
        diff = {
            "timestamp": datetime.now().isoformat(),
            "changes": []
        }
        
        # Compare drift values
        drift_before = before_capsule.get("symbolic_drift", 0.0)
        drift_after = after_capsule.get("symbolic_drift", 0.0)
        if drift_before != drift_after:
            diff["changes"].append({
                "field": "symbolic_drift",
                "before": drift_before,
                "after": drift_after,
                "delta": drift_after - drift_before
            })
        
        # Compare agent rosters
        agents_before = set(before_capsule.get("agent_roster", []))
        agents_after = set(after_capsule.get("agent_roster", []))
        if agents_before != agents_after:
            diff["changes"].append({
                "field": "agent_roster",
                "added": list(agents_after - agents_before),
                "removed": list(agents_before - agents_after)
            })
        
        # Compare linked repos
        repos_before = len(before_capsule.get("linked_repos", []))
        repos_after = len(after_capsule.get("linked_repos", []))
        if repos_before != repos_after:
            diff["changes"].append({
                "field": "linked_repos_count",
                "before": repos_before,
                "after": repos_after,
                "delta": repos_after - repos_before
            })
        
        # Compare anchors
        anchors_before = len(before_capsule.get("shared_anchors", []))
        anchors_after = len(after_capsule.get("shared_anchors", []))
        if anchors_before != anchors_after:
            diff["changes"].append({
                "field": "shared_anchors_count",
                "before": anchors_before,
                "after": anchors_after,
                "delta": anchors_after - anchors_before
            })
        
        diff["has_changes"] = len(diff["changes"]) > 0
        return diff
    
    def export_metrics(self, file_path: str):
        """Export drift metrics to JSON file."""
        stats = self.get_statistics()
        recent_events = self.get_recent_events(50)
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "statistics": stats.to_dict(),
            "recent_events": [e.to_dict() for e in recent_events],
            "thresholds": {
                "yellow": self.THRESHOLD_YELLOW,
                "red": self.THRESHOLD_RED
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info("Drift metrics exported to: %s", file_path)


# Global drift monitor instance
_drift_monitor = None
_drift_monitor_lock = threading.Lock()


def get_drift_monitor() -> DriftMonitor:
    """Get or create global drift monitor instance (thread-safe)."""
    global _drift_monitor
    if _drift_monitor is None:
        with _drift_monitor_lock:
            # Double-check pattern for thread safety
            if _drift_monitor is None:
                _drift_monitor = DriftMonitor()
    return _drift_monitor
