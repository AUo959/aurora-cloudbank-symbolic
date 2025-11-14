"""
Hierarchy Validator Module - Thread Transfer Bridge v2
=====================================================

Cascading validation for multi-layer bridge hierarchies.

Features:
- Layer-by-layer validation
- Dependency verification
- Drift tolerance enforcement
- PKI certificate validation
- Ethics protocol propagation

Thread: T1→BRIDGE_V2→HIERARCHY_VAL
DLP: context_tag=bridge_v2_hierarchy_validator
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from .layer_manager import BridgeLayer, LayerBridge, LAYER_CONFIGS

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Validation issue."""
    severity: ValidationSeverity
    layer: BridgeLayer
    bridge_id: str
    code: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity.value,
            "layer": self.layer.value,
            "bridge_id": self.bridge_id,
            "code": self.code,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    thread_id: str
    valid: bool
    timestamp: datetime
    issues: List[ValidationIssue]
    layer_status: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "thread_id": self.thread_id,
            "valid": self.valid,
            "timestamp": self.timestamp.isoformat(),
            "issues": [i.to_dict() for i in self.issues],
            "layer_status": self.layer_status,
            "metadata": self.metadata
        }
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get critical issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]


class HierarchyValidator:
    """
    Hierarchy validator for multi-layer bridges.
    
    Performs comprehensive validation across bridge layers with cascading checks.
    """
    
    def __init__(self):
        """Initialize hierarchy validator."""
        self.validation_history: List[ValidationReport] = []
        self._validator_lock = asyncio.Lock()

    async def validate_hierarchy(
        self,
        bridges: List[LayerBridge],
        thread_id: str,
        strict_mode: bool = True
    ) -> ValidationReport:
        """
        Validate bridge hierarchy.

        Args:
            bridges: List of bridges to validate
            thread_id: Thread identifier
            strict_mode: Enable strict validation rules

        Returns:
            ValidationReport with comprehensive results
        """
        async with self._validator_lock:
            issues: List[ValidationIssue] = []
            layer_status = {}
            
            # Group bridges by layer
            by_layer = {
                BridgeLayer.L1: [],
                BridgeLayer.L2: [],
                BridgeLayer.L3: []
            }
            
            for bridge in bridges:
                by_layer[bridge.layer].append(bridge)
            
            # Validate each layer in order
            for layer in [BridgeLayer.L1, BridgeLayer.L2, BridgeLayer.L3]:
                layer_bridges = by_layer[layer]
                
                if not layer_bridges:
                    layer_status[layer.value] = "not_present"
                    continue
                
                layer_issues = await self._validate_layer(
                    layer,
                    layer_bridges,
                    strict_mode
                )
                issues.extend(layer_issues)
                
                # Determine layer status
                critical_count = sum(
                    1 for i in layer_issues
                    if i.severity == ValidationSeverity.CRITICAL
                )
                error_count = sum(
                    1 for i in layer_issues
                    if i.severity == ValidationSeverity.ERROR
                )
                
                if critical_count > 0:
                    layer_status[layer.value] = "critical"
                elif error_count > 0:
                    layer_status[layer.value] = "invalid"
                elif layer_issues:
                    layer_status[layer.value] = "warning"
                else:
                    layer_status[layer.value] = "valid"
            
            # Check cross-layer dependencies
            dependency_issues = await self._validate_dependencies(
                by_layer,
                strict_mode
            )
            issues.extend(dependency_issues)
            
            # Overall validity
            valid = all(
                status in ["valid", "warning", "not_present"]
                for status in layer_status.values()
            ) and not any(i.severity == ValidationSeverity.CRITICAL for i in issues)
            
            report = ValidationReport(
                thread_id=thread_id,
                valid=valid,
                timestamp=datetime.now(),
                issues=issues,
                layer_status=layer_status,
                metadata={
                    "bridge_count": len(bridges),
                    "strict_mode": strict_mode,
                    "issue_count": len(issues)
                }
            )
            
            self.validation_history.append(report)
            
            # Keep last 100 reports
            if len(self.validation_history) > 100:
                self.validation_history = self.validation_history[-100:]
            
            logger.info(
                f"Hierarchy validation for {thread_id}: "
                f"{'VALID' if valid else 'INVALID'} "
                f"({len(issues)} issues)"
            )
            
            return report

    async def _validate_layer(
        self,
        layer: BridgeLayer,
        bridges: List[LayerBridge],
        strict_mode: bool
    ) -> List[ValidationIssue]:
        """Validate all bridges in a layer."""
        issues = []
        config = LAYER_CONFIGS[layer]
        
        for bridge in bridges:
            # Check bridge status
            if bridge.status != "completed":
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    layer=layer,
                    bridge_id=bridge.bridge_id,
                    code="INCOMPLETE_BRIDGE",
                    message=f"Bridge status is '{bridge.status}', expected 'completed'"
                ))
            
            # Check drift tolerance
            if bridge.drift_percentage > config.max_drift_percentage:
                severity = (
                    ValidationSeverity.CRITICAL if strict_mode
                    else ValidationSeverity.ERROR
                )
                issues.append(ValidationIssue(
                    severity=severity,
                    layer=layer,
                    bridge_id=bridge.bridge_id,
                    code="DRIFT_EXCEEDED",
                    message=(
                        f"Drift {bridge.drift_percentage:.4f}% exceeds "
                        f"layer maximum {config.max_drift_percentage}%"
                    )
                ))
            
            # Check PKI requirement
            if config.requires_pki and not bridge.pki_verified:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    layer=layer,
                    bridge_id=bridge.bridge_id,
                    code="PKI_MISSING",
                    message=f"{layer.value} requires PKI verification"
                ))
            
            # Check handshake stages
            if bridge.current_stage < config.handshake_stages:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    layer=layer,
                    bridge_id=bridge.bridge_id,
                    code="INCOMPLETE_HANDSHAKE",
                    message=(
                        f"Only {bridge.current_stage}/{config.handshake_stages} "
                        "stages completed"
                    )
                ))
            
            # Strict mode: Check for warnings
            if strict_mode:
                if bridge.drift_percentage > config.max_drift_percentage * 0.8:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        layer=layer,
                        bridge_id=bridge.bridge_id,
                        code="DRIFT_HIGH",
                        message=(
                            f"Drift {bridge.drift_percentage:.4f}% approaching "
                            f"limit {config.max_drift_percentage}%"
                        )
                    ))
        
        return issues

    async def _validate_dependencies(
        self,
        by_layer: Dict[BridgeLayer, List[LayerBridge]],
        strict_mode: bool
    ) -> List[ValidationIssue]:
        """Validate cross-layer dependencies."""
        issues = []
        
        # L2 requires L1
        if by_layer[BridgeLayer.L2] and not by_layer[BridgeLayer.L1]:
            for bridge in by_layer[BridgeLayer.L2]:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    layer=BridgeLayer.L2,
                    bridge_id=bridge.bridge_id,
                    code="MISSING_L1_DEPENDENCY",
                    message="L2 bridge requires L1 foundation"
                ))
        
        # L3 requires L1 and L2
        if by_layer[BridgeLayer.L3]:
            if not by_layer[BridgeLayer.L1]:
                for bridge in by_layer[BridgeLayer.L3]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        layer=BridgeLayer.L3,
                        bridge_id=bridge.bridge_id,
                        code="MISSING_L1_DEPENDENCY",
                        message="L3 bridge requires L1 foundation"
                    ))
            
            if not by_layer[BridgeLayer.L2]:
                for bridge in by_layer[BridgeLayer.L3]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        layer=BridgeLayer.L3,
                        bridge_id=bridge.bridge_id,
                        code="MISSING_L2_DEPENDENCY",
                        message="L3 bridge requires L2 intermediate layer"
                    ))
        
        # Strict mode: Check thread ID consistency
        if strict_mode:
            for layer, bridges in by_layer.items():
                thread_ids = {b.thread_id for b in bridges}
                if len(thread_ids) > 1:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        layer=layer,
                        bridge_id="multiple",
                        code="MIXED_THREADS",
                        message=(
                            f"{layer.value} contains bridges from "
                            f"{len(thread_ids)} different threads"
                        )
                    ))
        
        return issues

    async def validate_ethics_propagation(
        self,
        bridges: List[LayerBridge],
        expected_ethics: str = "Picard_Delta_3_Extended"
    ) -> Dict[str, Any]:
        """
        Validate that ethics protocol is consistent across layers.

        Args:
            bridges: Bridges to validate
            expected_ethics: Expected ethics protocol

        Returns:
            Validation result
        """
        violations = []
        
        for bridge in bridges:
            bridge_ethics = bridge.metadata.get("ethics_protocol")
            
            if not bridge_ethics:
                violations.append({
                    "bridge_id": bridge.bridge_id,
                    "layer": bridge.layer.value,
                    "issue": "Missing ethics protocol"
                })
            elif bridge_ethics != expected_ethics:
                violations.append({
                    "bridge_id": bridge.bridge_id,
                    "layer": bridge.layer.value,
                    "issue": f"Ethics mismatch: expected {expected_ethics}, got {bridge_ethics}"
                })
        
        return {
            "valid": len(violations) == 0,
            "expected_ethics": expected_ethics,
            "violations": violations,
            "checked_bridges": len(bridges)
        }

    async def validate_anchor_continuity(
        self,
        bridges: List[LayerBridge]
    ) -> Dict[str, Any]:
        """
        Validate that anchors are continuous across layers.

        Args:
            bridges: Bridges to validate

        Returns:
            Validation result
        """
        # Group by layer
        by_layer = {
            BridgeLayer.L1: [],
            BridgeLayer.L2: [],
            BridgeLayer.L3: []
        }
        
        for bridge in bridges:
            by_layer[bridge.layer].append(bridge)
        
        discontinuities = []
        
        # Check L1 → L2 continuity
        if by_layer[BridgeLayer.L1] and by_layer[BridgeLayer.L2]:
            l1_anchors = {b.metadata.get("anchor_hash") for b in by_layer[BridgeLayer.L1]}
            l2_anchors = {b.metadata.get("anchor_hash") for b in by_layer[BridgeLayer.L2]}
            
            if not l1_anchors.intersection(l2_anchors):
                discontinuities.append({
                    "layers": "L1→L2",
                    "issue": "No common anchors between L1 and L2"
                })
        
        # Check L2 → L3 continuity
        if by_layer[BridgeLayer.L2] and by_layer[BridgeLayer.L3]:
            l2_anchors = {b.metadata.get("anchor_hash") for b in by_layer[BridgeLayer.L2]}
            l3_anchors = {b.metadata.get("anchor_hash") for b in by_layer[BridgeLayer.L3]}
            
            if not l2_anchors.intersection(l3_anchors):
                discontinuities.append({
                    "layers": "L2→L3",
                    "issue": "No common anchors between L2 and L3"
                })
        
        return {
            "valid": len(discontinuities) == 0,
            "discontinuities": discontinuities,
            "checked_layers": len([layer for layer, bridges in by_layer.items() if bridges])
        }

    def get_validation_history(
        self,
        thread_id: Optional[str] = None,
        limit: int = 10
    ) -> List[ValidationReport]:
        """
        Get validation history.

        Args:
            thread_id: Optional thread filter
            limit: Maximum results

        Returns:
            List of validation reports
        """
        history = self.validation_history
        
        if thread_id:
            history = [r for r in history if r.thread_id == thread_id]
        
        return history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "valid_rate": 0.0
            }
        
        total = len(self.validation_history)
        valid_count = sum(1 for r in self.validation_history if r.valid)
        
        issue_counts = {
            "critical": 0,
            "error": 0,
            "warning": 0,
            "info": 0
        }
        
        for report in self.validation_history:
            for issue in report.issues:
                issue_counts[issue.severity.value] += 1
        
        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "valid_rate": valid_count / total if total > 0 else 0,
            "issue_counts": issue_counts,
            "last_validation": (
                self.validation_history[-1].timestamp.isoformat()
                if self.validation_history else None
            )
        }


# Global validator instance
_validator = None


def get_hierarchy_validator() -> HierarchyValidator:
    """Get global hierarchy validator instance."""
    global _validator
    if _validator is None:
        _validator = HierarchyValidator()
    return _validator
