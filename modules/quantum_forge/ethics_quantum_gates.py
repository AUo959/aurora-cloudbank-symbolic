"""
Ethics-Aware Quantum Gates v1.0

GUMAS_Thermax integration at quantum circuit level for safe quantum operations.
Validates quantum gates before execution with graduated intervention.

Features:
- Pre-execution ethics validation
- Quantum circuit safety checks
- Graduated intervention (WARN/THROTTLE/BLOCK)
- Audit trail for all quantum decisions
- Emergency shutdown capability

T1: ETHICS_QUANTUM_GATES_v1.0
SRB: QUANTUM_SAFETY_ENFORCEMENT
DLP: context_tag=ethics_quantum_gates, symbolic_hash=EQG_v1

Author: Aurora CloudBank Team
Version: 1.0.0
Date: 2025-11-13
Ethics: GUMAS_Thermax, Quantum_Critical_Safety
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from modules.quantum_forge.quantum_forge_v2 import GUMAS_Thermax, EthicsLevel, InterventionType

logger = logging.getLogger(__name__)


class GateRiskLevel(Enum):
    """Risk levels for quantum gate operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EthicsAwareQuantumGate:
    """
    Ethics validation wrapper for quantum circuit operations
    
    Ensures all quantum operations comply with GUMAS_Thermax protocol.
    """
    
    def __init__(self, ethics_level: EthicsLevel = EthicsLevel.BALANCED):
        self.gumas = GUMAS_Thermax(level=ethics_level)
        self.audit_log: List[Dict[str, Any]] = []
        self.blocked_operations = 0
        self.throttled_operations = 0
        self.total_operations = 0
        
        logger.info(f"🛡️  Ethics-Aware Quantum Gates initialized (level: {ethics_level.value})")
        
    def validate_gate_operation(
        self,
        gate_type: str,
        qubits: List[int],
        intent_score: float
    ) -> Dict[str, Any]:
        """
        Validate quantum gate operation before execution
        
        Args:
            gate_type: Type of quantum gate (H, CNOT, X, Y, Z, etc.)
            qubits: Qubits involved in operation
            intent_score: Alignment score for operation intent
            
        Returns:
            Dict with validation result and intervention
        """
        self.total_operations += 1
        
        # Assess risk level
        risk = self._assess_gate_risk(gate_type, qubits)
        
        # Ethics enforcement
        is_acceptable, intervention = self.gumas.enforce_alignment(intent_score)
        
        result = {
            "gate_type": gate_type,
            "qubits": qubits,
            "intent_score": intent_score,
            "risk_level": risk.value,
            "acceptable": is_acceptable,
            "intervention": intervention.value if intervention else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Apply intervention
        if intervention == InterventionType.BLOCK:
            self.blocked_operations += 1
            result["allowed"] = False
            result["message"] = f"⛔ Gate {gate_type} BLOCKED: Risky operation (intent: {intent_score:.3f})"
            logger.warning(result["message"])
            
        elif intervention == InterventionType.THROTTLE:
            self.throttled_operations += 1
            result["allowed"] = True
            result["throttle_factor"] = 0.5
            result["message"] = f"⚠️  Gate {gate_type} THROTTLED: Reduced fidelity for safety"
            logger.info(result["message"])
            
        elif intervention == InterventionType.WARN:
            result["allowed"] = True
            result["message"] = f"⚠️  Gate {gate_type} WARNING: Low intent alignment"
            logger.info(result["message"])
            
        else:
            result["allowed"] = True
            result["message"] = f"✅ Gate {gate_type} approved"
            
        # Audit log
        self.audit_log.append(result)
        
        # Track violation if blocked or throttled
        if intervention in [InterventionType.BLOCK, InterventionType.THROTTLE]:
            self.gumas.violation_log.append({
                "type": "quantum_gate",
                "gate": gate_type,
                "intervention": intervention.value,
                "intent_score": intent_score,
                "timestamp": result["timestamp"]
            })
        
        return result
        
    def _assess_gate_risk(self, gate_type: str, qubits: List[int]) -> GateRiskLevel:
        """Assess risk level of quantum gate operation"""
        # Multi-qubit gates are riskier
        if len(qubits) > 2:
            return GateRiskLevel.HIGH
        elif len(qubits) == 2:
            return GateRiskLevel.MEDIUM
        
        # Certain gate types are higher risk
        high_risk_gates = ["SWAP", "TOFFOLI", "FREDKIN"]
        if gate_type.upper() in high_risk_gates:
            return GateRiskLevel.HIGH
            
        return GateRiskLevel.LOW
        
    def get_ethics_metrics(self) -> Dict[str, Any]:
        """Get ethics enforcement metrics"""
        return {
            "total_operations": self.total_operations,
            "blocked": self.blocked_operations,
            "throttled": self.throttled_operations,
            "allowed": self.total_operations - self.blocked_operations,
            "block_rate": self.blocked_operations / self.total_operations if self.total_operations > 0 else 0.0,
            "audit_log_size": len(self.audit_log)
        }
        
    def export_ethics_manifest(self) -> Dict[str, Any]:
        """Export sealed manifest for audit trail"""
        manifest = {
            "component": "ethics_quantum_gates",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "ethics_level": self.gumas.level.value,
            "metrics": self.get_ethics_metrics(),
            "recent_audit_log": self.audit_log[-10:],  # Last 10 entries
            "integrity_hash": self._compute_manifest_hash()
        }
        return manifest
        
    def _compute_manifest_hash(self) -> str:
        """Compute integrity hash for manifest"""
        data = json.dumps({
            "total_ops": self.total_operations,
            "blocked": self.blocked_operations,
            "audit_size": len(self.audit_log)
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# Convenience singleton
_ethics_gate_instance: Optional[EthicsAwareQuantumGate] = None


def get_ethics_quantum_gate(ethics_level: EthicsLevel = EthicsLevel.BALANCED) -> EthicsAwareQuantumGate:
    """Get singleton ethics gate validator"""
    global _ethics_gate_instance
    if _ethics_gate_instance is None:
        _ethics_gate_instance = EthicsAwareQuantumGate(ethics_level)
    return _ethics_gate_instance
