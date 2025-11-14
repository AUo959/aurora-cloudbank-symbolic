"""
Quick Subroutine Test - Fast Validation
========================================
Anchor: SUBROUTINE-QUICKTEST-001
"""

import pytest


@pytest.mark.unit
def test_subroutine_imports():
    """Test that all subroutines can be imported"""
    from src.subroutines import (
        RealitySimMonitor,
        VisionAlignmentManager,
        EthicsComplianceMonitor,
        ResourceOptimizationManager,
        AnomalyDetectionEngine,
        IntegrationValidator,
        KnowledgeBaseSyncManager,
        QuantumCircuitOptimizer,
        SecurityThreatDetector,
        DependencyHealthMonitor,
        PerformanceProfiler
    )
    
    assert RealitySimMonitor is not None
    assert VisionAlignmentManager is not None
    assert EthicsComplianceMonitor is not None
    assert ResourceOptimizationManager is not None
    assert AnomalyDetectionEngine is not None
    assert IntegrationValidator is not None
    assert KnowledgeBaseSyncManager is not None
    assert QuantumCircuitOptimizer is not None
    assert SecurityThreatDetector is not None
    assert DependencyHealthMonitor is not None
    assert PerformanceProfiler is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ethics_monitor_instantiation():
    """Test EthicsComplianceMonitor can be instantiated"""
    from src.subroutines import EthicsComplianceMonitor
    
    monitor = EthicsComplianceMonitor()
    assert monitor is not None
    stats = monitor.get_compliance_stats()
    assert isinstance(stats, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resource_optimizer_instantiation():
    """Test ResourceOptimizationManager can be instantiated"""
    from src.subroutines import ResourceOptimizationManager
    
    optimizer = ResourceOptimizationManager()
    assert optimizer is not None
    metrics = await optimizer.collect_resource_metrics()
    assert metrics is not None


@pytest.mark.unit
def test_registry_has_builtin_subroutines():
    """Test registry has at least the built-in subroutines"""
    from src.subroutines.registry import get_subroutine_registry
    
    registry = get_subroutine_registry()
    all_subs = registry.list_all()
    
    # Should have at least 2 built-in subroutines
    assert len(all_subs) >= 2
    
    sub_ids = [s.id for s in all_subs]
    assert 'reality_sim_monitor' in sub_ids
    assert 'vision_alignment_manager' in sub_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
