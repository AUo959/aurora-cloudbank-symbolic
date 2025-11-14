"""
Ethics Compliance Monitor Subroutine
=====================================
Anchor: SUBROUTINE-ETHICS-003
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Executive subroutine ensuring all operations maintain ethical alignment.
Monitors GUMAS ethics scores, tracks violations, and enforces compliance gates.
Integrates with Ethics Gate, GUMAS API, and audit systems.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, UTC
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EthicsCheckResult:
    """Result of ethics compliance check"""
    success: bool
    operation_id: str
    ethics_score: float
    threshold: float
    violations: List[Dict[str, Any]]
    warnings: List[str]
    timestamp: str
    metadata: Dict[str, Any]


class EthicsComplianceMonitor:
    """
    Executive subroutine ensuring all operations maintain ethical alignment.
    
    Monitors GUMAS ethics scores, tracks violations, and enforces compliance gates
    for high-impact operations across Aurora's infrastructure.
    
    Integration Points:
    - ethics_gate: EthicsGate for validation
    - gumas_client: GUMAS API client
    - audit_log: DLP tracker for compliance records
    - alert_system: Resilience Sentinel for critical violations
    """

    def __init__(
        self,
        ethics_gate: Optional[Any] = None,
        gumas_client: Optional[Any] = None,
        audit_log: Optional[Any] = None,
        alert_system: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Ethics Compliance Monitor.
        
        Args:
            ethics_gate: EthicsGate object for validation
            gumas_client: GUMAS client for ethics scoring
            audit_log: Audit log for compliance tracking
            alert_system: Alert system for violations
            config: Configuration including thresholds
        """
        self.ethics_gate = ethics_gate or self._get_default_ethics_gate()
        self.gumas_client = gumas_client or self._get_default_gumas_client()
        self.audit_log = audit_log or self._get_default_audit_log()
        self.alert_system = alert_system or self._get_default_alert_system()
        self.config = config or self._get_default_config()
        
        # Compliance tracking
        self._checks_performed = 0
        self._violations_detected = 0
        self._operations_blocked = 0

    def _get_default_ethics_gate(self):
        """Get default ethics gate"""
        try:
            from src.aurora.ethics import EthicsGate, GUMASEthicsClient
            return EthicsGate(
                client=GUMASEthicsClient(base_url="http://localhost:8000"),
                threshold=0.7
            )
        except ImportError:
            logger.warning("EthicsGate not available - using mock")
            return self._create_mock_ethics_gate()

    def _get_default_gumas_client(self):
        """Get default GUMAS client"""
        try:
            from src.aurora.ethics import GUMASEthicsClient
            return GUMASEthicsClient(base_url="http://localhost:8000")
        except ImportError:
            return None

    def _get_default_audit_log(self):
        """Get default audit log"""
        try:
            from src.core.native_dlp_export import NativeDLPTracker
            return NativeDLPTracker()
        except ImportError:
            return None

    def _get_default_alert_system(self):
        """Get default alert system"""
        try:
            from modules.resilience_sentinel.alert_manager import AlertManager
            return AlertManager()
        except ImportError:
            return None

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "ethics_threshold": 0.7,
            "critical_threshold": 0.5,
            "auto_block_enabled": True,
            "alert_on_violation": True,
            "audit_all_checks": True
        }

    def _create_mock_ethics_gate(self):
        """Create mock ethics gate for testing"""
        class MockEthicsGate:
            async def evaluate(self, action: str, context: Dict[str, Any]):
                return {"approved": True, "score": 0.9, "reasoning": "Mock", "violations": []}
        return MockEthicsGate()

    async def check_operation_ethics(
        self,
        operation_id: str,
        operation_type: str,
        operation_context: Dict[str, Any]
    ) -> EthicsCheckResult:
        """
        Check ethics compliance for an operation.
        
        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation (e.g., 'state_modification', 'data_access')
            operation_context: Context including affected resources, users, etc.
        
        Returns:
            EthicsCheckResult with compliance status
        """
        self._checks_performed += 1
        timestamp = datetime.now(UTC).isoformat()
        
        try:
            # Evaluate via GUMAS ethics
            verdict = await self.ethics_gate.evaluate(
                action=operation_type,
                context=operation_context
            )
            
            ethics_score = verdict.get("score", 0.0)
            approved = verdict.get("approved", False)
            violations = verdict.get("violations", [])
            
            # Check thresholds
            threshold = self.config.get("ethics_threshold", 0.7)
            critical_threshold = self.config.get("critical_threshold", 0.5)
            
            warnings = []
            if ethics_score < threshold:
                warnings.append(f"Ethics score {ethics_score:.2f} below threshold {threshold}")
            
            if ethics_score < critical_threshold:
                self._violations_detected += 1
                if self.config.get("auto_block_enabled"):
                    self._operations_blocked += 1
                    warnings.append("CRITICAL: Operation auto-blocked")
                
                # Alert on critical violations
                if self.alert_system and self.config.get("alert_on_violation"):
                    await self._send_alert(operation_id, ethics_score, violations)
            
            # Audit trail
            if self.audit_log and self.config.get("audit_all_checks"):
                self._log_compliance_check(
                    operation_id, operation_type, ethics_score, violations
                )
            
            result = EthicsCheckResult(
                success=approved and ethics_score >= threshold,
                operation_id=operation_id,
                ethics_score=ethics_score,
                threshold=threshold,
                violations=violations,
                warnings=warnings,
                timestamp=timestamp,
                metadata={
                    "operation_type": operation_type,
                    "verdict": verdict,
                    "context_keys": list(operation_context.keys())
                }
            )
            
            logger.info(
                "Ethics check completed: operation=%s score=%.2f approved=%s",
                operation_id, ethics_score, approved
            )
            
            return result
            
        except Exception as e:
            logger.error("Ethics check failed: operation=%s error=%s", operation_id, str(e))
            return EthicsCheckResult(
                success=False,
                operation_id=operation_id,
                ethics_score=0.0,
                threshold=self.config.get("ethics_threshold", 0.7),
                violations=[{"type": "check_failure", "message": str(e)}],
                warnings=["Ethics check system error"],
                timestamp=timestamp,
                metadata={"error": str(e)}
            )

    async def _send_alert(self, operation_id: str, score: float, violations: List):
        """Send alert for ethics violation"""
        if not self.alert_system:
            return
        
        try:
            await self.alert_system.create_alert(
                severity="critical",
                message=f"Ethics violation detected: {operation_id}",
                details={
                    "operation_id": operation_id,
                    "ethics_score": score,
                    "violations": violations
                }
            )
        except Exception as e:
            logger.error("Failed to send ethics alert: %s", str(e))

    def _log_compliance_check(
        self,
        operation_id: str,
        operation_type: str,
        score: float,
        violations: List
    ):
        """Log compliance check to audit trail"""
        if not self.audit_log:
            return
        
        try:
            self.audit_log.create_export(
                data={
                    "check_type": "ethics_compliance",
                    "operation_id": operation_id,
                    "operation_type": operation_type,
                    "ethics_score": score,
                    "violations": violations
                },
                context_tag=f"ethics_check_{operation_id}",
                symbolic_validation=True
            )
        except Exception as e:
            logger.error("Failed to log compliance check: %s", str(e))

    def get_compliance_stats(self) -> Dict[str, Any]:
        """Get compliance monitoring statistics"""
        return {
            "checks_performed": self._checks_performed,
            "violations_detected": self._violations_detected,
            "operations_blocked": self._operations_blocked,
            "violation_rate": (
                self._violations_detected / self._checks_performed
                if self._checks_performed > 0 else 0.0
            ),
            "config": self.config
        }

    def reset_stats(self):
        """Reset compliance statistics"""
        self._checks_performed = 0
        self._violations_detected = 0
        self._operations_blocked = 0
        logger.info("Compliance statistics reset")


# Subroutine registration metadata
SUBROUTINE_METADATA = {
    "id": "ethics_compliance_monitor",
    "name": "Ethics Compliance Monitor",
    "version": "1.0.0",
    "description": "Executive subroutine for ethics compliance monitoring and enforcement",
    "author": {
        "name": "Aurora Core Team",
        "team": "AUo959-team",
        "role": "Ethics & Governance"
    },
    "category": "executive",
    "status": "active",
    "module_path": "src.subroutines.ethics_compliance_monitor",
    "class_name": "EthicsComplianceMonitor",
    "entry_point": "check_operation_ethics",
    "dependencies": [
        {"subroutine_id": "reality_sim_monitor", "version_constraint": ">=1.0.0", "required": False}
    ],
    "integrations": ["ethics_gate", "gumas", "audit_log", "alert_system"]
}
