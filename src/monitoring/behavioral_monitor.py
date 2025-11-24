"""
Behavioral Monitor

Tracks and monitors agent behavior patterns, collecting metrics for drift detection
and ethics compliance evaluation.
"""

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from src.core.time_utils import utc_iso, utc_now
from typing import Dict, List, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class BehaviorMetrics:
    """Snapshot of agent behavior metrics"""
    agent_id: str
    timestamp: str
    
    # Decision metrics
    decisions_made: int = 0
    decision_latency_ms: float = 0.0
    decision_changes: int = 0
    
    # Resource metrics
    resources_allocated: int = 0
    resource_efficiency: float = 0.0
    
    # Interaction metrics
    human_interactions: int = 0
    override_requests: int = 0
    explanation_requests: int = 0
    
    # Performance metrics
    success_rate: float = 0.0
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    
    # Ethics metrics
    ethics_checks_passed: int = 0
    ethics_violations: int = 0
    safety_incidents: int = 0
    
    # Custom metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class BehaviorMonitor:
    """
    Agent Behavior Monitoring System
    
    Collects and tracks behavioral metrics for agents, providing data for
    drift detection and pattern analysis.
    
    Features:
    - Real-time metric collection
    - Aggregation over time windows
    - Pattern change detection
    - Integration with drift detector
    """
    
    def __init__(self, retention_hours: int = 168):
        """
        Initialize behavior monitor
        
        Args:
            retention_hours: Hours to retain metrics history (default: 168 = 1 week)
        """
        self.retention_hours = retention_hours
        self.metrics_history: Dict[str, List[BehaviorMetrics]] = defaultdict(list)
        self.current_metrics: Dict[str, BehaviorMetrics] = {}
        self._max_history_entries = 10000  # Safety limit to prevent unbounded growth
        
        logger.info("Behavior monitor initialized (retention=%d hours)", retention_hours)
    
    def record_metric(
        self,
        agent_id: str,
        metric_name: str,
        value: float,
        context_tag: Optional[str] = None
    ):
        """
        Record a single metric value
        
        Args:
            agent_id: Agent identifier
            metric_name: Name of the metric
            value: Metric value
            context_tag: DLP context tag
        """
        if agent_id not in self.current_metrics:
            self.current_metrics[agent_id] = BehaviorMetrics(
                agent_id=agent_id,
                timestamp=utc_iso()
            )
        
        metrics = self.current_metrics[agent_id]
        
        # Update standard metrics
        if metric_name == 'decisions_made':
            metrics.decisions_made = int(value)
        elif metric_name == 'decision_latency_ms':
            metrics.decision_latency_ms = value
        elif metric_name == 'decision_changes':
            metrics.decision_changes = int(value)
        elif metric_name == 'resources_allocated':
            metrics.resources_allocated = int(value)
        elif metric_name == 'resource_efficiency':
            metrics.resource_efficiency = value
        elif metric_name == 'human_interactions':
            metrics.human_interactions = int(value)
        elif metric_name == 'override_requests':
            metrics.override_requests = int(value)
        elif metric_name == 'explanation_requests':
            metrics.explanation_requests = int(value)
        elif metric_name == 'success_rate':
            metrics.success_rate = value
        elif metric_name == 'error_rate':
            metrics.error_rate = value
        elif metric_name == 'timeout_rate':
            metrics.timeout_rate = value
        elif metric_name == 'ethics_checks_passed':
            metrics.ethics_checks_passed = int(value)
        elif metric_name == 'ethics_violations':
            metrics.ethics_violations = int(value)
        elif metric_name == 'safety_incidents':
            metrics.safety_incidents = int(value)
        else:
            # Custom metric
            metrics.custom_metrics[metric_name] = value
    
    def snapshot_metrics(self, agent_id: str) -> Optional[BehaviorMetrics]:
        """
        Take a snapshot of current metrics and add to history
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Current metrics snapshot
        """
        if agent_id not in self.current_metrics:
            return None
        
        metrics = self.current_metrics[agent_id]
        metrics.timestamp = utc_iso()
        
        # Add to history
        self.metrics_history[agent_id].append(metrics)
        
        # Clean old entries
        self._cleanup_history(agent_id)
        
        # Create new current metrics
        self.current_metrics[agent_id] = BehaviorMetrics(
            agent_id=agent_id,
            timestamp=utc_iso()
        )
        
        logger.debug("Snapshotted metrics for agent %s", agent_id)
        
        return metrics
    
    def get_metrics(
        self,
        agent_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[BehaviorMetrics]:
        """
        Get metrics history for an agent
        
        Args:
            agent_id: Agent identifier
            since: Start time filter
            until: End time filter
        
        Returns:
            List of metrics snapshots
        """
        if agent_id not in self.metrics_history:
            return []
        
        metrics = self.metrics_history[agent_id]
        
        if since:
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m.timestamp) >= since
            ]
        
        if until:
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m.timestamp) <= until
            ]
        
        return metrics
    
    def get_metric_values(
        self,
        agent_id: str,
        metric_name: str,
        since: Optional[datetime] = None
    ) -> List[float]:
        """
        Extract values for a specific metric over time
        
        Args:
            agent_id: Agent identifier
            metric_name: Name of metric to extract
            since: Start time filter
        
        Returns:
            List of metric values
        """
        metrics = self.get_metrics(agent_id, since=since)
        values = []
        
        for m in metrics:
            if metric_name == 'decisions_made':
                values.append(float(m.decisions_made))
            elif metric_name == 'decision_latency_ms':
                values.append(m.decision_latency_ms)
            elif metric_name == 'decision_changes':
                values.append(float(m.decision_changes))
            elif metric_name == 'resources_allocated':
                values.append(float(m.resources_allocated))
            elif metric_name == 'resource_efficiency':
                values.append(m.resource_efficiency)
            elif metric_name == 'human_interactions':
                values.append(float(m.human_interactions))
            elif metric_name == 'override_requests':
                values.append(float(m.override_requests))
            elif metric_name == 'explanation_requests':
                values.append(float(m.explanation_requests))
            elif metric_name == 'success_rate':
                values.append(m.success_rate)
            elif metric_name == 'error_rate':
                values.append(m.error_rate)
            elif metric_name == 'timeout_rate':
                values.append(m.timeout_rate)
            elif metric_name == 'ethics_checks_passed':
                values.append(float(m.ethics_checks_passed))
            elif metric_name == 'ethics_violations':
                values.append(float(m.ethics_violations))
            elif metric_name == 'safety_incidents':
                values.append(float(m.safety_incidents))
            elif metric_name in m.custom_metrics:
                values.append(m.custom_metrics[metric_name])
        
        return values
    
    def calculate_aggregates(
        self,
        agent_id: str,
        since: Optional[datetime] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate aggregate statistics for all metrics
        
        Args:
            agent_id: Agent identifier
            since: Start time filter
        
        Returns:
            Dictionary of metric statistics (mean, min, max, count)
        """
        metrics = self.get_metrics(agent_id, since=since)
        
        if not metrics:
            return {}
        
        aggregates = {}
        
        # Standard metrics
        standard_metrics = [
            'decisions_made', 'decision_latency_ms', 'decision_changes',
            'resources_allocated', 'resource_efficiency',
            'human_interactions', 'override_requests', 'explanation_requests',
            'success_rate', 'error_rate', 'timeout_rate',
            'ethics_checks_passed', 'ethics_violations', 'safety_incidents'
        ]
        
        for metric_name in standard_metrics:
            values = self.get_metric_values(agent_id, metric_name, since=since)
            if values:
                aggregates[metric_name] = {
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        # Custom metrics
        custom_metric_names = set()
        for m in metrics:
            custom_metric_names.update(m.custom_metrics.keys())
        
        for metric_name in custom_metric_names:
            values = self.get_metric_values(agent_id, metric_name, since=since)
            if values:
                aggregates[f"custom.{metric_name}"] = {
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        return aggregates
    
    def _cleanup_history(self, agent_id: str):
        """Remove old metrics beyond retention period"""
        if agent_id not in self.metrics_history:
            return
        
        cutoff = utc_now() - timedelta(hours=self.retention_hours)
        
        self.metrics_history[agent_id] = [
            m for m in self.metrics_history[agent_id]
            if datetime.fromisoformat(m.timestamp) >= cutoff
        ]
        
        # Additional safety: enforce max entries limit
        if len(self.metrics_history[agent_id]) > self._max_history_entries:
            logger.warning(
                "Agent %s exceeded max history entries (%d), trimming oldest",
                agent_id, self._max_history_entries
            )
            self.metrics_history[agent_id] = self.metrics_history[agent_id][-self._max_history_entries:]
    
    def get_agent_ids(self) -> List[str]:
        """Get list of all monitored agent IDs"""
        return list(set(self.current_metrics.keys()) | set(self.metrics_history.keys()))
    
    def export_history(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export metrics history for persistence
        
        Args:
            agent_id: Specific agent to export (default: all agents)
        
        Returns:
            Dictionary of metrics history
        """
        if agent_id:
            return {
                agent_id: [m.to_dict() for m in self.metrics_history.get(agent_id, [])]
            }
        else:
            return {
                aid: [m.to_dict() for m in metrics]
                for aid, metrics in self.metrics_history.items()
            }
