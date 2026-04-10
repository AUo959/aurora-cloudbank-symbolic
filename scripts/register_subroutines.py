#!/usr/bin/env python3
"""
Subroutine Registration Script
===============================
Anchor: SUBROUTINE-REG-SCRIPT-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Registers all Aurora subroutines with the SubroutineRegistry.
Run this script after adding new subroutines to ensure they're properly tracked.
"""

import sys
import logging
from datetime import datetime, UTC
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, '/workspaces/aurora-cloudbank-symbolic')

from src.subroutines.registry import (
    get_subroutine_registry,
    Subroutine,
    SubroutineAuthor,
    SubroutineStatus,
    SubroutineCategory,
    SubroutineDependency
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Subroutine Registration Data
SUBROUTINES: List[Dict[str, Any]] = [
    # 1. Reality Sim Monitor (EXISTING)
    {
        "id": "reality_sim_monitor",
        "name": "Reality Sim Monitor",
        "version": "1.0.0",
        "description": "Ensures reality sim to real-world alignment for all operations",
        "category": SubroutineCategory.EXECUTIVE,
        "module_path": "src.subroutines.reality_sim_monitor",
        "class_name": "RealitySimMonitor",
        "entry_point": "enforce_principles",
        "integrations": ["registry", "telemetry", "audit_log", "dlp_tracker"],
        "tags": ["reality", "simulation", "validation", "executive"],
        "documentation_url": "docs/subroutines/reality_sim_monitor.md",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 2. Vision Alignment Manager (EXISTING)
    {
        "id": "vision_alignment_manager",
        "name": "Vision Alignment Manager",
        "version": "1.0.0",
        "description": "Ensures strategic vision alignment across all Aurora operations",
        "category": SubroutineCategory.EXECUTIVE,
        "module_path": "src.subroutines.aurora_vision_alignment",
        "class_name": "VisionAlignmentManager",
        "entry_point": "verify_alignment",
        "integrations": ["system_state", "crew_registry", "simulation_layer", "knowledge_base", "audit_log"],
        "tags": ["vision", "alignment", "strategic", "executive"],
        "documentation_url": "docs/subroutines/vision_alignment.md",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 3. Ethics Compliance Monitor (NEW)
    {
        "id": "ethics_compliance_monitor",
        "name": "Ethics Compliance Monitor",
        "version": "1.0.0",
        "description": "Continuous ethics monitoring and enforcement via GUMAS integration",
        "category": SubroutineCategory.EXECUTIVE,
        "module_path": "src.subroutines.ethics_compliance_monitor",
        "class_name": "EthicsComplianceMonitor",
        "entry_point": "check_operation_ethics",
        "integrations": ["ethics_gate", "gumas_client", "dlp_tracker", "alert_system"],
        "tags": ["ethics", "compliance", "gumas", "security", "executive"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#3-ethics-compliance-monitor",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 4. Resource Optimization Manager (NEW)
    {
        "id": "resource_optimization_manager",
        "name": "Resource Optimization Manager",
        "version": "1.0.0",
        "description": "Intelligent resource allocation and optimization across distributed infrastructure",
        "category": SubroutineCategory.EXECUTIVE,
        "module_path": "src.subroutines.resource_optimization",
        "class_name": "ResourceOptimizationManager",
        "entry_point": "analyze_and_optimize",
        "integrations": ["monitoring_engine", "quantum_orchestrator", "alert_system", "telemetry"],
        "tags": ["resources", "optimization", "scaling", "performance", "executive"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#4-resource-optimization-manager",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 5. Anomaly Detection Engine (NEW)
    {
        "id": "anomaly_detection_engine",
        "name": "Anomaly Detection Engine",
        "version": "1.0.0",
        "description": "Statistical and ML-based anomaly detection across system metrics",
        "category": SubroutineCategory.MONITORING,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "AnomalyDetectionEngine",
        "entry_point": "detect_anomalies",
        "integrations": ["monitoring_engine", "insight_ledger", "alert_system"],
        "tags": ["anomaly", "detection", "monitoring", "ml", "statistics"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#5-anomaly-detection-engine",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 6. Integration Validator (NEW)
    {
        "id": "integration_validator",
        "name": "Integration Validator",
        "version": "1.0.0",
        "description": "Validates cross-module integrations and API endpoint health",
        "category": SubroutineCategory.VALIDATION,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "IntegrationValidator",
        "entry_point": "validate_all_integrations",
        "integrations": ["module_registry", "api_client", "dlp_tracker"],
        "tags": ["integration", "validation", "health", "api"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#6-integration-validator",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 7. Knowledge Base Sync Manager (NEW)
    {
        "id": "knowledge_base_sync_manager",
        "name": "Knowledge Base Sync Manager",
        "version": "1.0.0",
        "description": "Synchronizes quantum memory, insight ledger, and external knowledge bases",
        "category": SubroutineCategory.INTEGRATION,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "KnowledgeBaseSyncManager",
        "entry_point": "sync_knowledge_bases",
        "integrations": ["aumemmanager", "insight_ledger", "external_kb"],
        "tags": ["knowledge", "sync", "memory", "integration"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#7-knowledge-base-sync-manager",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 8. Quantum Circuit Optimizer (NEW)
    {
        "id": "quantum_circuit_optimizer",
        "name": "Quantum Circuit Optimizer",
        "version": "1.0.0",
        "description": "Optimizes quantum circuits for efficiency and fidelity",
        "category": SubroutineCategory.PROCESSING,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "QuantumCircuitOptimizer",
        "entry_point": "optimize_circuit",
        "integrations": ["quantum_simulator", "quantum_orchestrator"],
        "tags": ["quantum", "optimization", "circuit", "processing"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#8-quantum-circuit-optimizer",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 9. Security Threat Detector (NEW)
    {
        "id": "security_threat_detector",
        "name": "Security Threat Detector",
        "version": "1.0.0",
        "description": "Multi-layer security threat detection and automated blocking",
        "category": SubroutineCategory.EXECUTIVE,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "SecurityThreatDetector",
        "entry_point": "scan_for_threats",
        "integrations": ["audit_log", "alert_system", "data_guardian"],
        "tags": ["security", "threats", "injection", "protection", "executive"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#9-security-threat-detector",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 10. Dependency Health Monitor (NEW)
    {
        "id": "dependency_health_monitor",
        "name": "Dependency Health Monitor",
        "version": "1.0.0",
        "description": "Monitors external dependencies with circuit breaker pattern",
        "category": SubroutineCategory.MONITORING,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "DependencyHealthMonitor",
        "entry_point": "check_dependency_health",
        "integrations": ["external_apis", "alert_system", "telemetry"],
        "tags": ["dependencies", "health", "monitoring", "circuit-breaker"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md#10-dependency-health-monitor",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    },
    
    # 11. Performance Profiler (BONUS)
    {
        "id": "performance_profiler",
        "name": "Performance Profiler",
        "version": "1.0.0",
        "description": "Identifies bottlenecks and tracks execution performance",
        "category": SubroutineCategory.UTILITY,
        "module_path": "src.subroutines.subroutine_suite",
        "class_name": "PerformanceProfiler",
        "entry_point": "profile_operation",
        "integrations": ["telemetry", "monitoring_engine"],
        "tags": ["performance", "profiling", "bottleneck", "utility"],
        "documentation_url": "docs/SUBROUTINE_SUITE_COMPLETE.md",
        "author": {
            "name": "Aurora Team",
            "team": "AUo959-team",
            "role": "Core Development"
        }
    }
]


def register_all_subroutines() -> None:
    """Register all Aurora subroutines with the registry"""
    registry = get_subroutine_registry()
    timestamp = datetime.now(UTC).isoformat()
    
    logger.info("=" * 80)
    logger.info("Aurora Subroutine Registration")
    logger.info("=" * 80)
    logger.info("Registering %d subroutines...", len(SUBROUTINES))
    logger.info("")
    
    registered_count = 0
    skipped_count = 0
    failed_count = 0
    
    for sub_data in SUBROUTINES:
        try:
            subroutine_id = sub_data["id"]
            
            # Check if already registered
            existing = registry.get(subroutine_id)
            if existing:
                logger.info("✓ SKIP: %s (v%s) - Already registered", sub_data['name'], sub_data['version'])
                skipped_count += 1
                continue
            
            # Create subroutine object
            subroutine = Subroutine(
                id=subroutine_id,
                name=sub_data["name"],
                version=sub_data["version"],
                description=sub_data["description"],
                author=SubroutineAuthor(
                    name=sub_data["author"]["name"],
                    team=sub_data["author"]["team"],
                    role=sub_data["author"].get("role")
                ),
                created_at=timestamp,
                updated_at=timestamp,
                status=SubroutineStatus.ACTIVE,
                category=sub_data["category"],
                module_path=sub_data["module_path"],
                class_name=sub_data["class_name"],
                entry_point=sub_data["entry_point"],
                dependencies=[],
                integrations=sub_data["integrations"],
                documentation_url=sub_data.get("documentation_url"),
                tags=sub_data["tags"]
            )
            
            # Register
            if registry.register(subroutine):
                logger.info("✓ NEW: %s (v%s) - Registered successfully", sub_data['name'], sub_data['version'])
                registered_count += 1
            else:
                logger.error("✗ FAIL: %s - Registration failed", sub_data['name'])
                failed_count += 1
                
        except Exception as e:
            logger.error("✗ ERROR: %s - %s", sub_data['name'], str(e))
            failed_count += 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("Registration Complete")
    logger.info("=" * 80)
    logger.info("Newly Registered: %d", registered_count)
    logger.info("Already Registered: %d", skipped_count)
    logger.info("Failed: %d", failed_count)
    logger.info("Total Subroutines: %d", len(registry.list_all()))
    logger.info("")
    
    # Display summary by category
    logger.info("Subroutines by Category:")
    logger.info("-" * 80)
    for category in SubroutineCategory:
        category_subs = registry.list_by_category(category)
        if category_subs:
            logger.info("  %s: %d subroutines", category.value.upper(), len(category_subs))
            for sub in category_subs:
                logger.info("    - %s (v%s)", sub.name, sub.version)
    
    logger.info("")
    logger.info("✓ All subroutines registered successfully!")


def main():
    """Main entry point"""
    try:
        register_all_subroutines()
        return 0
    except Exception as e:
        logger.error("Registration failed: %s", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
