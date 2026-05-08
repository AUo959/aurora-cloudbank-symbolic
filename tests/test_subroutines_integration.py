"""
Subroutine Integration Tests
=============================
Anchor: SUBROUTINE-TESTS-001
Team: AUo959-team
Ethics: Picard_Delta_3

Tests for new subroutine functionality.
"""

import pytest
import asyncio
import unittest


class TestEthicsComplianceMonitor:
    """Tests for Ethics Compliance Monitor subroutine"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_ethics_check_high_score(self):
        """Test ethics check with high compliance score"""
        from src.subroutines import EthicsComplianceMonitor
        
        monitor = EthicsComplianceMonitor()
        result = await monitor.check_operation_ethics(
            operation_id="test_op_001",
            operation_type="read_operation",
            operation_context={"user": "test_user", "resource": "public_data"}
        )
        
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'ethics_score')
        assert hasattr(result, 'violations')
    
    @pytest.mark.unit
    def test_ethics_stats(self):
        """Test ethics compliance statistics"""
        from src.subroutines import EthicsComplianceMonitor
        
        monitor = EthicsComplianceMonitor()
        stats = monitor.get_compliance_stats()
        
        assert isinstance(stats, dict)
        assert 'checks_performed' in stats
        assert 'violations_detected' in stats
        assert 'operations_blocked' in stats


class TestResourceOptimizationManager:
    """Tests for Resource Optimization Manager subroutine"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_collect_metrics(self):
        """Test resource metrics collection"""
        from src.subroutines import ResourceOptimizationManager
        
        optimizer = ResourceOptimizationManager()
        metrics = await optimizer.collect_resource_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, 'cpu_percent')
        assert hasattr(metrics, 'memory_percent')
        assert hasattr(metrics, 'disk_percent')
        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.memory_percent <= 100
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_optimization_analysis(self):
        """Test optimization analysis"""
        from src.subroutines import ResourceOptimizationManager
        
        optimizer = ResourceOptimizationManager()
        actions = await optimizer.analyze_and_optimize()
        
        assert isinstance(actions, list)
        # Actions may be empty if no optimization needed

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_resource_analysis_endpoint_serializes_network_io(self, monkeypatch):
        """Test resource endpoint serializes nested network I/O fields without crashing."""
        import src.subroutines as subroutines
        from src.subroutines.api_enhanced import ResourceMetricsRequest, analyze_resources
        from src.subroutines.resource_optimization import OptimizationAction, ResourceMetrics

        class StubResourceOptimizationManager:
            async def collect_resource_metrics(self):
                return ResourceMetrics(
                    timestamp="2026-05-08T00:00:00+00:00",
                    cpu_percent=12.5,
                    memory_percent=34.0,
                    disk_percent=56.0,
                    network_io={"bytes_sent": 1234, "bytes_recv": 5678},
                    quantum_circuit_queue=2,
                    api_rate_limit_remaining={},
                    active_processes=9
                )

            async def analyze_and_optimize(self):
                return [
                    OptimizationAction(
                        action_type="rebalance",
                        resource_target="cpu",
                        reason="test",
                        priority="low",
                        estimated_impact="test impact"
                    )
                ]

        monkeypatch.setattr(subroutines, "ResourceOptimizationManager", StubResourceOptimizationManager)

        result = await analyze_resources(
            ResourceMetricsRequest(
                include_network=True,
                include_quantum=True
            )
        )

        checks = unittest.TestCase()
        checks.assertIs(result["success"], True)

        metrics = result["metrics"]
        checks.assertEqual(metrics["network_io_sent"], 1234)
        checks.assertEqual(metrics["network_io_recv"], 5678)
        checks.assertEqual(metrics["quantum_circuit_queue"], 2)
        checks.assertEqual(metrics["active_processes"], 9)


class TestAnomalyDetectionEngine:
    """Tests for Anomaly Detection Engine subroutine"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_anomaly(self):
        """Test normal metric (no anomaly)"""
        from src.subroutines import AnomalyDetectionEngine
        
        detector = AnomalyDetectionEngine()
        result = await detector.detect_anomalies(
            metric_name="test_metric",
            current_value=50.0,
            context={"baseline": 50.0, "std_dev": 5.0}
        )
        
        # Result may be None if no anomaly detected
        assert result is None or hasattr(result, 'severity')
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_clear_anomaly(self):
        """Test clear anomaly detection"""
        from src.subroutines import AnomalyDetectionEngine
        
        detector = AnomalyDetectionEngine()
        result = await detector.detect_anomalies(
            metric_name="test_metric",
            current_value=1000.0,  # Clearly anomalous
            context={"baseline": 50.0, "std_dev": 5.0}
        )
        
        # Should detect anomaly with high value
        assert result is not None
        assert hasattr(result, 'severity')
        assert hasattr(result, 'confidence_score')

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_anomaly_endpoint_serializes_dataclass_schema(self):
        """Test anomaly endpoint returns the current dataclass schema without crashing."""
        from src.subroutines.api_enhanced import AnomalyCheckRequest, detect_anomaly

        result = await detect_anomaly(
            AnomalyCheckRequest(
                metric_name="test_metric",
                current_value=1000.0,
                context={}
            )
        )

        checks = unittest.TestCase()
        checks.assertIs(result["success"], True)
        checks.assertIs(result["anomaly_detected"], True)

        anomaly = result["anomaly"]
        checks.assertIn("anomaly_id", anomaly)
        checks.assertEqual(anomaly["anomaly_type"], "statistical_deviation")
        checks.assertEqual(anomaly["severity"], "high")
        checks.assertEqual(anomaly["metric_name"], "test_metric")
        checks.assertEqual(anomaly["current_value"], 1000.0)
        checks.assertEqual(anomaly["baseline_mean"], 50.0)
        checks.assertEqual(anomaly["baseline_std"], 10.0)
        checks.assertAlmostEqual(anomaly["deviation_score"], 95.0)
        checks.assertIn("test_metric", anomaly["affected_components"])
        checks.assertTrue(anomaly["recommended_actions"])


class TestIntegrationValidator:
    """Tests for Integration Validator subroutine"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_validate_integrations(self):
        """Test integration validation"""
        from src.subroutines import IntegrationValidator
        
        validator = IntegrationValidator()
        results = await validator.validate_all_integrations()
        
        assert isinstance(results, dict)
        assert 'modules_validated' in results
        assert 'modules_healthy' in results
        assert 'modules_failed' in results


class TestKnowledgeBaseSyncManager:
    """Tests for Knowledge Base Sync Manager subroutine"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_knowledge_sync(self):
        """Test knowledge base synchronization"""
        from src.subroutines import KnowledgeBaseSyncManager
        
        sync_manager = KnowledgeBaseSyncManager()
        results = await sync_manager.sync_knowledge_bases()
        
        assert isinstance(results, dict)
        assert 'sources_synced' in results
        assert 'sync_status' in results


class TestQuantumCircuitOptimizer:
    """Tests for Quantum Circuit Optimizer subroutine"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_circuit_optimization(self):
        """Test quantum circuit optimization"""
        from src.subroutines import QuantumCircuitOptimizer
        
        optimizer = QuantumCircuitOptimizer()
        
        # Simple test circuit
        circuit = {
            "gates": ["H", "CNOT", "RZ", "CNOT"],
            "gate_count": 4
        }
        
        result = await optimizer.optimize_circuit(circuit=circuit)
        
        assert isinstance(result, dict)
        assert 'gate_count_before' in result
        assert 'gate_count_after' in result
        assert 'reduction_percent' in result


class TestSecurityThreatDetector:
    """Tests for Security Threat Detector subroutine"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="SecurityThreatDetector not yet implemented - work in progress")
    async def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        from src.subroutines import SecurityThreatDetector
        
        detector = SecurityThreatDetector()
        
        # Clear SQL injection attempt
        request_data = {
            "query": "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        }
        
        report = await detector.scan_for_threats(request_data=request_data)
        
        assert isinstance(report, dict)
        assert 'threats' in report
        # Should detect SQL injection
        if report['threats']:
            assert any('sql' in t['type'].lower() for t in report['threats'])
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="SecurityThreatDetector not yet implemented")
    async def test_clean_request(self):
        """Test clean request (no threats)"""
        from src.subroutines import SecurityThreatDetector
        
        detector = SecurityThreatDetector()
        
        request_data = {
            "query": "normal search query",
            "user": "test_user"
        }
        
        report = await detector.scan_for_threats(request_data=request_data)
        
        assert isinstance(report, dict)
        # Clean request should have no threats


class TestDependencyHealthMonitor:
    """Tests for Dependency Health Monitor subroutine"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dependency_health_check(self):
        """Test dependency health check"""
        from src.subroutines import DependencyHealthMonitor
        
        monitor = DependencyHealthMonitor()
        
        # Mock health check function
        async def mock_health_check():
            return {"healthy": True}
        
        result = await monitor.check_dependency_health(
            dependency_name="test_dependency",
            health_check_func=mock_health_check
        )

        checks = unittest.TestCase()
        checks.assertIsInstance(result, dict)
        checks.assertEqual(result["dependency"], "test_dependency")
        checks.assertEqual(result["status"], "healthy")
        checks.assertEqual(result["details"], {"healthy": True})

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dependency_health_check_default_probe(self):
        """Test default dependency health probe when no callback is provided."""
        from src.subroutines import DependencyHealthMonitor

        monitor = DependencyHealthMonitor()

        result = await monitor.check_dependency_health(
            dependency_name="json",
            health_check_func=None
        )

        checks = unittest.TestCase()
        checks.assertIsInstance(result, dict)
        checks.assertEqual(result["dependency"], "json")
        checks.assertEqual(result["status"], "healthy")
        checks.assertEqual(result["details"]["module"], "json")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dependency_health_endpoint_uses_default_probe(self):
        """Test dependency health endpoint no longer crashes without a custom callback."""
        from src.subroutines.api_enhanced import check_dependencies

        result = await check_dependencies()

        checks = unittest.TestCase()
        checks.assertIs(result["success"], True)
        checks.assertIsInstance(result["dependency_health"], dict)
        checks.assertTrue(result["dependency_health"])
        for dependency_name, dependency_result in result["dependency_health"].items():
            checks.assertEqual(dependency_result["dependency"], dependency_name)
            checks.assertIn(dependency_result["status"], {"healthy", "unhealthy", "error"})


class TestPerformanceProfiler:
    """Tests for Performance Profiler subroutine"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_performance_profile_endpoint_uses_report_method(self):
        """Test performance profile endpoint returns the implemented report schema."""
        from src.subroutines.api_enhanced import get_performance_profile

        result = await get_performance_profile()

        checks = unittest.TestCase()
        checks.assertIs(result["success"], True)

        profile = result["performance_profile"]
        checks.assertIn("timestamp", profile)
        checks.assertEqual(profile["operations_profiled"], 0)
        checks.assertEqual(profile["slow_operations_detected"], 0)
        checks.assertEqual(profile["profiles"], {})
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="PerformanceProfiler not yet implemented")
    async def test_profile_operation(self):
        """Test operation profiling"""
        from src.subroutines import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        
        # Profile a simple operation
        async def test_operation():
            await asyncio.sleep(0.1)
            return "done"
        
        result = await profiler.profile_operation(
            operation_name="test_op"
        )
        # Call the test operation separately
        await test_operation()
        
        assert isinstance(result, dict)
        assert 'execution_time_ms' in result
        assert result['execution_time_ms'] >= 100  # Should be at least 100ms
    
    @pytest.mark.unit
    @pytest.mark.xfail(reason="PerformanceProfiler not yet implemented")
    def test_profiler_stats(self):
        """Test profiler statistics"""
        from src.subroutines import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        stats = profiler.get_profiler_stats()
        
        assert isinstance(stats, dict)
        assert 'operations_profiled' in stats
        assert 'bottlenecks_identified' in stats


class TestSubroutineRegistry:
    """Tests for Subroutine Registry"""
    
    @pytest.mark.unit
    @pytest.mark.xfail(reason="Subroutine registry incomplete - work in progress")
    def test_registry_contains_all_subroutines(self):
        """Test that registry contains all 11 subroutines"""
        from src.subroutines.registry import get_subroutine_registry
        
        registry = get_subroutine_registry()
        all_subroutines = registry.list_all()
        
        # Should have at least 11 subroutines registered
        assert len(all_subroutines) >= 11
        
        # Check for key subroutines
        subroutine_ids = [s.id for s in all_subroutines]
        assert 'reality_sim_monitor' in subroutine_ids
        assert 'vision_alignment_manager' in subroutine_ids
        assert 'ethics_compliance_monitor' in subroutine_ids
        assert 'resource_optimization_manager' in subroutine_ids
    
    @pytest.mark.unit
    @pytest.mark.xfail(reason="Subroutine registry incomplete")
    def test_registry_categories(self):
        """Test subroutine categorization"""
        from src.subroutines.registry import (
            get_subroutine_registry,
            SubroutineCategory
        )
        
        registry = get_subroutine_registry()
        
        # Test each category
        executive = registry.list_by_category(SubroutineCategory.EXECUTIVE)
        monitoring = registry.list_by_category(SubroutineCategory.MONITORING)
        validation = registry.list_by_category(SubroutineCategory.VALIDATION)
        
        assert len(executive) >= 5  # At least 5 executive subroutines
        assert len(monitoring) >= 2  # At least 2 monitoring subroutines
        assert len(validation) >= 1  # At least 1 validation subroutine


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
