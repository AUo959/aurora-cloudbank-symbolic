"""
Aurora Subroutine System
========================
Anchor: SUBROUTINE-SYS-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Official subroutine authoring and tracking system for Aurora's neural net.
Provides versioning, provenance, and execution monitoring for all subroutines.

Available Subroutines (10):
1. RealitySimMonitor - Reality sim alignment validation
2. VisionAlignmentManager - Strategic vision alignment
3. EthicsComplianceMonitor - Ethics validation & enforcement
4. ResourceOptimizationManager - Resource allocation & optimization
5. AnomalyDetectionEngine - Anomaly detection & response
6. IntegrationValidator - Cross-module integration validation
7. KnowledgeBaseSyncManager - Knowledge base synchronization
8. QuantumCircuitOptimizer - Quantum circuit optimization
9. SecurityThreatDetector - Security threat detection
10. DependencyHealthMonitor - Dependency health monitoring
"""

from src.subroutines.reality_sim_monitor import RealitySimMonitor
from src.subroutines.aurora_vision_alignment import VisionAlignmentManager
from src.subroutines.ethics_compliance_monitor import EthicsComplianceMonitor
from src.subroutines.resource_optimization import ResourceOptimizationManager
from src.subroutines.subroutine_suite import (
    AnomalyDetectionEngine,
    IntegrationValidator,
    KnowledgeBaseSyncManager,
    QuantumCircuitOptimizer,
    SecurityThreatDetector,
    DependencyHealthMonitor,
    PerformanceProfiler
)
from src.subroutines.registry import SubroutineRegistry, Subroutine

__version__ = "2.0.0"
__all__ = [
    "RealitySimMonitor",
    "VisionAlignmentManager",
    "EthicsComplianceMonitor",
    "ResourceOptimizationManager",
    "AnomalyDetectionEngine",
    "IntegrationValidator",
    "KnowledgeBaseSyncManager",
    "QuantumCircuitOptimizer",
    "SecurityThreatDetector",
    "DependencyHealthMonitor",
    "PerformanceProfiler",
    "SubroutineRegistry",
    "Subroutine"
]
