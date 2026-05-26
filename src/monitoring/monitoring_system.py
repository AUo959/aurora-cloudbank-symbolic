"""
Integrated Monitoring and Alerting System

Coordinates drift detection, ethics compliance, behavioral monitoring,
and alerting for comprehensive agent oversight.
"""

import logging
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from src.core.time_utils import utc_now, utc_iso
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from .drift_detector import DriftDetector, DriftAlert, DriftLevel
from .ethics_engine import EthicsEngine, EthicsViolation, ActionContext, ViolationSeverity
from .behavioral_monitor import BehaviorMonitor
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of automated interventions"""
    BLOCK_ACTION = "block_action"
    REQUEST_REVIEW = "request_review"
    NOTIFY_OPERATOR = "notify_operator"
    THROTTLE_AGENT = "throttle_agent"
    SUSPEND_AGENT = "suspend_agent"
    RESET_BASELINE = "reset_baseline"


@dataclass
class AlertConfig:
    """Configuration for alerting system"""
    info_notify_delay_seconds: int = 300  # 5 minutes
    warning_notify_delay_seconds: int = 60  # 1 minute
    critical_notify_immediate: bool = True
    enable_auto_intervention: bool = True
    intervention_cooldown_seconds: int = 300  # 5 minutes
    max_violations_per_hour: int = 10


@dataclass
class Intervention:
    """Record of automated intervention"""
    timestamp: str
    agent_id: str
    type: InterventionType
    reason: str
    context: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Intervention":
        """Restore an intervention from persisted data."""
        return cls(
            timestamp=data['timestamp'],
            agent_id=data['agent_id'],
            type=InterventionType(data['type']),
            reason=data['reason'],
            context=data.get('context', {}),
            success=data['success'],
            error=data.get('error')
        )


class MonitoringSystem:
    """
    Integrated Monitoring and Alerting System
    
    Provides comprehensive agent oversight through:
    - Real-time behavioral monitoring
    - Drift detection and alerting
    - Ethics compliance enforcement
    - Automated intervention
    - Immutable audit logging
    - Dashboard integration
    
    This is the main entry point for R-2 agent monitoring.
    """
    
    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        ethics_rules_path: Optional[Path] = None,
        config: Optional[AlertConfig] = None
    ):
        """
        Initialize monitoring system
        
        Args:
            storage_dir: Directory for persistent storage
            ethics_rules_path: Path to ethics rules configuration
            config: Alert configuration
        """
        self.storage_dir = Path(storage_dir or "./monitoring_data")
        self._state_path = self.storage_dir / "monitoring_state.json"
        self.config = config or AlertConfig()
        
        # Initialize subsystems
        self.behavior_monitor = BehaviorMonitor(retention_hours=168)
        self.drift_detector = DriftDetector(
            alerts_path=self.storage_dir / "drift_alerts.jsonl"
        )
        self.ethics_engine = EthicsEngine(
            rules_path=ethics_rules_path,
            violations_path=self.storage_dir / "ethics_violations.jsonl"
        )
        
        audit_storage = self.storage_dir / "audit_log.jsonl"
        self.audit_logger = AuditLogger(storage_path=audit_storage)
        
        # Intervention tracking
        self.interventions: List[Intervention] = []
        self.last_intervention_time: Dict[str, datetime] = {}
        self._enforcement_handlers: Dict[InterventionType, Callable] = {}
        
        # Alert handlers
        self.alert_handlers: Dict[AlertLevel, List[Callable]] = {
            AlertLevel.INFO: [],
            AlertLevel.WARNING: [],
            AlertLevel.CRITICAL: []
        }

        self.import_state()
        
        logger.info("Monitoring system initialized (storage=%s)", storage_dir)

    def register_enforcement_handler(
        self,
        intervention_type: InterventionType,
        handler: Callable
    ):
        """
        Register a concrete handler for an automated intervention type.

        Handlers receive agent_id and should return True only after the
        enforcement action is complete.
        """
        self._enforcement_handlers[intervention_type] = handler
        logger.info("Registered enforcement handler for %s", intervention_type.value)
    
    def register_alert_handler(self, level: AlertLevel, handler: Callable):
        """
        Register handler for alert notifications
        
        Args:
            level: Alert level to handle
            handler: Callable that takes alert data
        """
        self.alert_handlers[level].append(handler)
        logger.info("Registered alert handler for %s level", level.value)
    
    def establish_agent_baseline(
        self,
        agent_id: str,
        historical_data: Dict[str, List[float]]
    ):
        """
        Establish baseline behavior for an agent
        
        Args:
            agent_id: Agent identifier
            historical_data: Dictionary of metric_name -> values
        """
        for metric_name, values in historical_data.items():
            if values:
                self.drift_detector.establish_baseline(
                    agent_id=agent_id,
                    metric_name=metric_name,
                    values=values
                )
        
        logger.info(
            "Established baseline for %s with %d metrics",
            agent_id, len(historical_data)
        )
    
    def record_agent_behavior(
        self,
        agent_id: str,
        metrics: Dict[str, float],
        context_tag: Optional[str] = None
    ):
        """
        Record behavioral metrics for an agent
        
        Args:
            agent_id: Agent identifier
            metrics: Dictionary of metric values
            context_tag: DLP context tag
        """
        for metric_name, value in metrics.items():
            self.behavior_monitor.record_metric(
                agent_id=agent_id,
                metric_name=metric_name,
                value=value,
                context_tag=context_tag
            )
    
    def check_agent_behavior(
        self,
        agent_id: str,
        context_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check agent behavior for drift
        
        Args:
            agent_id: Agent identifier
            context_tag: DLP context tag
        
        Returns:
            Dictionary with drift alerts and recommended actions
        """
        # Snapshot current metrics
        current_metrics = self.behavior_monitor.snapshot_metrics(agent_id)
        
        if not current_metrics:
            return {'drift_detected': False, 'alerts': []}
        
        # Check each metric for drift
        drift_alerts = []
        
        metrics_dict = current_metrics.to_dict()
        for metric_name, value in metrics_dict.items():
            if metric_name in ['agent_id', 'timestamp', 'custom_metrics']:
                continue
            
            if isinstance(value, (int, float)):
                alert = self.drift_detector.detect_drift(
                    agent_id=agent_id,
                    metric_name=metric_name,
                    current_value=float(value),
                    context_tag=context_tag
                )
                
                if alert:
                    drift_alerts.append(alert)
                    
                    # Log to audit
                    self.audit_logger.log_drift_alert(
                        agent_id=agent_id,
                        severity=alert.level.value,
                        metric_name=metric_name,
                        current_value=alert.current_value,
                        baseline_value=alert.baseline_value,
                        context_tag=context_tag
                    )
                    
                    # Notify handlers
                    alert_level = self._map_drift_to_alert_level(alert.level)
                    self._notify_handlers(alert_level, alert.to_dict())
                    
                    # Check for intervention
                    if alert.level == DriftLevel.CRITICAL:
                        self._evaluate_intervention(agent_id, alert)
        
        return {
            'drift_detected': len(drift_alerts) > 0,
            'alerts': [a.to_dict() for a in drift_alerts],
            'agent_id': agent_id,
            'timestamp': utc_iso()
        }
    
    def evaluate_action(
        self,
        agent_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        context_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate action against ethics rules
        
        Args:
            agent_id: Agent identifier
            action_type: Type of action
            parameters: Action parameters
            context_tag: DLP context tag
        
        Returns:
            Dictionary with violations and whether action is blocked
        """
        context = ActionContext(
            agent_id=agent_id,
            action_type=action_type,
            parameters=parameters,
            context_tag=context_tag
        )
        
        violations = self.ethics_engine.evaluate_action(context)
        should_block = self.ethics_engine.check_should_block(violations)
        
        # Log violations
        for violation in violations:
            self.audit_logger.log_ethics_violation(
                agent_id=agent_id,
                severity=violation.severity.value,
                rule_id=violation.rule_id,
                rule_name=violation.rule_name,
                blocked=violation.blocked,
                context=parameters,
                context_tag=context_tag
            )
            
            # Notify handlers
            alert_level = self._map_severity_to_alert_level(violation.severity)
            self._notify_handlers(alert_level, violation.to_dict())
            
            # Intervention for critical violations
            if violation.severity == ViolationSeverity.CRITICAL:
                self._intervene_ethics_violation(agent_id, violation)
        
        return {
            'violations': [v.to_dict() for v in violations],
            'blocked': should_block,
            'violation_count': len(violations),
            'agent_id': agent_id,
            'timestamp': utc_iso()
        }
    
    def _evaluate_intervention(self, agent_id: str, drift_alert: DriftAlert):
        """Evaluate and execute intervention for drift"""
        if not self.config.enable_auto_intervention:
            return
        
        # Check cooldown
        if agent_id in self.last_intervention_time:
            elapsed = (utc_now() - self.last_intervention_time[agent_id]).total_seconds()
            if elapsed < self.config.intervention_cooldown_seconds:
                logger.debug("Intervention cooldown active for %s", agent_id)
                return
        
        # Determine intervention type
        if drift_alert.deviation > 1.0:  # > 100% deviation
            intervention_type = InterventionType.SUSPEND_AGENT
        elif drift_alert.deviation > 0.5:  # > 50% deviation
            intervention_type = InterventionType.THROTTLE_AGENT
        else:
            intervention_type = InterventionType.REQUEST_REVIEW
        
        self._execute_intervention(
            agent_id=agent_id,
            intervention_type=intervention_type,
            reason=f"Drift detected: {drift_alert.description}"
        )
    
    def _intervene_ethics_violation(self, agent_id: str, violation: EthicsViolation):
        """Execute intervention for ethics violation"""
        if not self.config.enable_auto_intervention:
            return
        
        if violation.blocked:
            intervention_type = InterventionType.BLOCK_ACTION
        else:
            intervention_type = InterventionType.NOTIFY_OPERATOR
        
        self._execute_intervention(
            agent_id=agent_id,
            intervention_type=intervention_type,
            reason=f"Ethics violation: {violation.description}"
        )
    
    def _execute_intervention(
        self,
        agent_id: str,
        intervention_type: InterventionType,
        reason: str
    ):
        """Execute an automated intervention"""
        success = False
        error = None
        handler = self._enforcement_handlers.get(intervention_type)

        if handler:
            try:
                success = self._run_enforcement_handler(
                    handler,
                    agent_id=agent_id
                )
            except Exception as exc:
                error = str(exc)
                logger.error(
                    "Intervention handler failed for %s on %s: %s",
                    intervention_type.value, agent_id, error
                )
        else:
            error = f"No enforcement handler registered for {intervention_type.value}"

        intervention = Intervention(
            timestamp=utc_iso(),
            agent_id=agent_id,
            type=intervention_type,
            reason=reason,
            context={},
            success=success,
            error=error
        )
        
        self.interventions.append(intervention)
        if success:
            self.last_intervention_time[agent_id] = utc_now()
        self._persist_state()
        
        # Log to audit
        self.audit_logger.log_intervention(
            agent_id=agent_id,
            severity="critical",
            intervention_type=intervention_type.value,
            action_taken=intervention_type.value if success else "not_executed",
            reason=reason,
            success=success,
            error=error
        )
        
        logger.warning(
            "Intervention recorded for %s: %s success=%s - %s",
            agent_id, intervention_type.value, success, reason
        )
        
        # Notify critical handlers
        self._notify_handlers(AlertLevel.CRITICAL, intervention.to_dict())

    def _run_enforcement_handler(
        self,
        handler: Callable,
        agent_id: str
    ) -> bool:
        """Run a registered enforcement handler and normalize its result."""
        result = handler(agent_id)

        if isinstance(result, dict):
            if not result.get("success", False) and result.get("error"):
                raise RuntimeError(str(result["error"]))
            return bool(result.get("success", False))

        return bool(result)
    
    def _map_drift_to_alert_level(self, drift_level: DriftLevel) -> AlertLevel:
        """Map drift level to alert level"""
        mapping = {
            DriftLevel.INFO: AlertLevel.INFO,
            DriftLevel.WARNING: AlertLevel.WARNING,
            DriftLevel.CRITICAL: AlertLevel.CRITICAL
        }
        return mapping[drift_level]
    
    def _map_severity_to_alert_level(self, severity: ViolationSeverity) -> AlertLevel:
        """Map violation severity to alert level"""
        if severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]:
            return AlertLevel.CRITICAL
        elif severity == ViolationSeverity.MEDIUM:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def _notify_handlers(self, level: AlertLevel, data: Dict[str, Any]):
        """Notify registered alert handlers"""
        for handler in self.alert_handlers[level]:
            try:
                handler(data)
            except Exception as e:
                logger.error("Alert handler failed: %s", e)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get comprehensive status for an agent
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Dictionary with agent status and metrics
        """
        # Get recent violations
        since = utc_now() - timedelta(hours=24)
        violations = self.ethics_engine.get_violations(agent_id=agent_id, since=since)
        drift_alerts = self.drift_detector.get_alerts(agent_id=agent_id, since=since)
        
        # Get behavioral aggregates
        aggregates = self.behavior_monitor.calculate_aggregates(agent_id, since=since)
        
        # Get interventions
        agent_interventions = [
            i for i in self.interventions
            if i.agent_id == agent_id and datetime.fromisoformat(i.timestamp) >= since
        ]
        
        return {
            'agent_id': agent_id,
            'status': 'healthy' if not violations and not drift_alerts else 'alert',
            'violations_24h': len(violations),
            'drift_alerts_24h': len(drift_alerts),
            'interventions_24h': len(agent_interventions),
            'behavioral_metrics': aggregates,
            'last_check': utc_iso()
        }
    
    def generate_compliance_report(
        self,
        since: Optional[datetime] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report
        
        Args:
            since: Start time for report
            agent_id: Specific agent (default: all agents)
        
        Returns:
            Comprehensive compliance report
        """
        since = since or datetime.now(timezone.utc) - timedelta(days=7)
        
        # Get violations
        violations = self.ethics_engine.get_violations(
            agent_id=agent_id,
            since=since
        )
        
        # Get drift alerts
        drift_alerts = self.drift_detector.get_alerts(
            agent_id=agent_id,
            since=since
        )
        
        # Get interventions
        interventions = [
            i for i in self.interventions
            if (not agent_id or i.agent_id == agent_id) and
            datetime.fromisoformat(i.timestamp).replace(tzinfo=timezone.utc) >= since
        ]
        
        # Get audit entries
        audit_entries = self.audit_logger.get_entries(
            agent_id=agent_id,
            since=since
        )
        
        # Calculate statistics
        violation_by_severity = {}
        for v in violations:
            severity = v.severity.value
            violation_by_severity[severity] = violation_by_severity.get(severity, 0) + 1
        
        alert_by_level = {}
        for a in drift_alerts:
            level = a.level.value
            alert_by_level[level] = alert_by_level.get(level, 0) + 1
        
        return {
            'report_period': {
                'start': since.isoformat(),
                'end': utc_iso()
            },
            'agent_id': agent_id or 'all',
            'summary': {
                'total_violations': len(violations),
                'violations_by_severity': violation_by_severity,
                'total_drift_alerts': len(drift_alerts),
                'alerts_by_level': alert_by_level,
                'total_interventions': len(interventions),
                'audit_entries': len(audit_entries)
            },
            'violations': [v.to_dict() for v in violations],
            'drift_alerts': [a.to_dict() for a in drift_alerts],
            'interventions': [i.to_dict() for i in interventions],
            'audit_verified': self.audit_logger.verify_chain()
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export full monitoring system state"""
        return {
            'baselines': self.drift_detector.export_baselines(),
            'drift_alerts': self.drift_detector.export_alerts(),
            'rules': self.ethics_engine.export_rules(),
            'violations': self.ethics_engine.export_violations(),
            'behavior_history': self.behavior_monitor.export_history(),
            'interventions': [i.to_dict() for i in self.interventions],
            'last_intervention_time': {
                agent_id: timestamp.isoformat()
                for agent_id, timestamp in self.last_intervention_time.items()
            }
        }

    def import_state(self, state: Optional[Dict[str, Any]] = None) -> bool:
        """
        Import persisted monitoring system state.

        When state is omitted, the method attempts to load monitoring_state.json
        from storage_dir. Missing state is a normal first-start condition.
        """
        if state is None:
            if not self._state_path.exists():
                return False

            try:
                with open(self._state_path, 'r') as f:
                    state = json.load(f)
            except Exception as e:
                logger.error("Failed to load monitoring state: %s", e)
                return False

        if 'baselines' in state:
            self.drift_detector.import_baselines(state['baselines'])
        if 'drift_alerts' in state:
            self.drift_detector.import_alerts(state['drift_alerts'])
        if 'violations' in state:
            self.ethics_engine.import_violations(state['violations'])

        self.interventions = [
            Intervention.from_dict(intervention_data)
            for intervention_data in state.get('interventions', [])
        ]
        self.last_intervention_time = {
            agent_id: datetime.fromisoformat(timestamp)
            for agent_id, timestamp in state.get('last_intervention_time', {}).items()
        }

        logger.info(
            "Imported monitoring state: interventions=%d cooldowns=%d",
            len(self.interventions), len(self.last_intervention_time)
        )
        return True

    def _persist_state(self):
        """Persist intervention state needed for restart-safe cooldowns."""
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._state_path, 'w') as f:
                json.dump(
                    {
                        'interventions': [
                            intervention.to_dict()
                            for intervention in self.interventions
                        ],
                        'last_intervention_time': {
                            agent_id: timestamp.isoformat()
                            for agent_id, timestamp in self.last_intervention_time.items()
                        }
                    },
                    f,
                    indent=2,
                    sort_keys=True
                )
        except Exception as e:
            logger.error("Failed to persist monitoring state: %s", e)
