"""
Subroutine System Tests
=======================
Anchor: SUBROUTINE-TEST-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Comprehensive tests for Aurora's subroutine system including:
- Reality Sim Monitor validation
- Subroutine Registry operations
- API endpoint functionality
"""

import pytest
from datetime import datetime, timedelta
from src.subroutines.reality_sim_monitor import RealitySimMonitor, RealityCheckResult
from src.subroutines.aurora_vision_alignment import (
    VisionAlignmentManager,
    AlignmentRecord,
    AlignmentReviewResult
)
from src.subroutines.registry import (
    SubroutineRegistry,
    Subroutine,
    SubroutineAuthor,
    SubroutineStatus,
    SubroutineCategory,
    get_subroutine_registry
)


@pytest.mark.unit
class TestRealitySimMonitor:
    """Test RealitySimMonitor subroutine"""

    def test_initialization(self):
        """Test monitor initialization with defaults"""
        monitor = RealitySimMonitor()
        
        assert monitor.registry is not None
        assert monitor.telemetry is not None
        assert monitor.audit_log is not None
        assert monitor.config is not None
        assert monitor._execution_count == 0
        assert monitor._success_count == 0
        assert monitor._failure_count == 0

    def test_enforce_principles_success(self):
        """Test successful reality check"""
        monitor = RealitySimMonitor()
        
        sim_id = "test_sim_001"
        input_data = {"scenario": "test", "params": {"x": 1}}
        results = {
            "status": "verified",
            "output": {"value": 42},
            "verification": {"confidence": 0.95}
        }
        
        result = monitor.enforce_principles(sim_id, input_data, results)
        
        assert isinstance(result, RealityCheckResult)
        assert result.success is True
        assert result.sim_id == sim_id
        assert "provenance" in result.checks_passed
        assert "metrics" in result.checks_passed
        assert "reality_alignment" in result.checks_passed
        assert len(result.checks_failed) == 0
        assert monitor._success_count == 1

    def test_enforce_principles_failure_speculative(self):
        """Test reality check failure for speculative results"""
        monitor = RealitySimMonitor()
        
        sim_id = "test_sim_002"
        input_data = {"scenario": "test"}
        results = {
            "status": "speculative",  # Should fail
            "output": {"value": 42}
        }
        
        result = monitor.enforce_principles(sim_id, input_data, results)
        
        assert result.success is False
        assert "reality_alignment" in result.checks_failed
        assert monitor._failure_count == 1

    def test_enforce_principles_failure_uncorroborated(self):
        """Test reality check failure for uncorroborated results"""
        monitor = RealitySimMonitor()
        
        sim_id = "test_sim_003"
        input_data = {"scenario": "test"}
        results = {
            "status": "uncorroborated",  # Should fail
            "output": {"value": 42}
        }
        
        result = monitor.enforce_principles(sim_id, input_data, results)
        
        assert result.success is False
        assert "reality_alignment" in result.checks_failed

    def test_get_stats(self):
        """Test statistics tracking"""
        monitor = RealitySimMonitor()
        
        # Run multiple checks
        for i in range(5):
            sim_id = f"test_sim_{i}"
            input_data = {"scenario": f"test_{i}"}
            results = {
                "status": "verified" if i < 3 else "speculative",
                "output": {"value": i}
            }
            monitor.enforce_principles(sim_id, input_data, results)
        
        stats = monitor.get_stats()
        
        assert stats['total_executions'] == 5
        assert stats['successful'] == 3
        assert stats['failed'] == 2
        assert stats['success_rate'] == 0.6


@pytest.mark.unit
class TestSubroutineRegistry:
    """Test SubroutineRegistry"""

    def test_initialization(self):
        """Test registry initialization"""
        registry = SubroutineRegistry()
        
        assert len(registry._subroutines) > 0  # Should have built-in subroutines
        assert "reality_sim_monitor" in registry._subroutines
        
        stats = registry.get_stats()
        assert stats['total_subroutines'] > 0

    def test_register_subroutine(self):
        """Test registering a new subroutine"""
        registry = SubroutineRegistry()
        
        author = SubroutineAuthor(
            name="Test Author",
            team="Test Team",
            email="test@example.com"
        )
        
        subroutine = Subroutine(
            id="test_subroutine",
            name="Test Subroutine",
            version="1.0.0",
            description="Test description",
            author=author,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            status=SubroutineStatus.DRAFT,
            category=SubroutineCategory.UTILITY,
            module_path="test.module",
            class_name="TestClass",
            entry_point="test_method"
        )
        
        success = registry.register(subroutine)
        
        assert success is True
        assert registry.get("test_subroutine") is not None

    def test_register_duplicate(self):
        """Test registering duplicate subroutine fails"""
        registry = SubroutineRegistry()
        
        # Try to register reality_sim_monitor again
        author = SubroutineAuthor(name="Test", team="Test")
        subroutine = Subroutine(
            id="reality_sim_monitor",  # Duplicate ID
            name="Duplicate",
            version="2.0.0",
            description="Duplicate",
            author=author,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            status=SubroutineStatus.DRAFT,
            category=SubroutineCategory.UTILITY,
            module_path="test",
            class_name="Test",
            entry_point="test"
        )
        
        success = registry.register(subroutine)
        assert success is False

    def test_list_by_category(self):
        """Test listing subroutines by category"""
        registry = SubroutineRegistry()
        
        executive_subroutines = registry.list_by_category(SubroutineCategory.EXECUTIVE)
        
        assert len(executive_subroutines) > 0
        assert all(s.category == SubroutineCategory.EXECUTIVE for s in executive_subroutines)

    def test_list_by_status(self):
        """Test listing subroutines by status"""
        registry = SubroutineRegistry()
        
        active_subroutines = registry.list_by_status(SubroutineStatus.ACTIVE)
        
        assert len(active_subroutines) > 0
        assert all(s.status == SubroutineStatus.ACTIVE for s in active_subroutines)

    def test_update_status(self):
        """Test updating subroutine status"""
        registry = SubroutineRegistry()
        
        # Get built-in subroutine
        subroutine = registry.get("reality_sim_monitor")
        original_status = subroutine.status
        
        # Update status
        success = registry.update_status("reality_sim_monitor", SubroutineStatus.DEPRECATED)
        
        assert success is True
        updated = registry.get("reality_sim_monitor")
        assert updated.status == SubroutineStatus.DEPRECATED
        
        # Restore original status
        registry.update_status("reality_sim_monitor", original_status)

    def test_record_execution(self):
        """Test recording subroutine execution"""
        registry = SubroutineRegistry()
        
        inputs = {"sim_id": "test", "data": {"x": 1}}
        outputs = {"success": True, "result": 42}
        
        success = registry.record_execution(
            subroutine_id="reality_sim_monitor",
            inputs=inputs,
            outputs=outputs,
            success=True,
            duration_ms=123.45
        )
        
        assert success is True
        
        subroutine = registry.get("reality_sim_monitor")
        assert subroutine.total_executions > 0
        assert len(subroutine.executions) > 0

    def test_search_by_query(self):
        """Test searching subroutines by query"""
        registry = SubroutineRegistry()
        
        results = registry.search(query="reality")
        
        assert len(results) > 0
        assert any("reality" in s.id.lower() for s in results)

    def test_search_by_tags(self):
        """Test searching subroutines by tags"""
        registry = SubroutineRegistry()
        
        results = registry.search(query="", tags=["reality"])
        
        assert len(results) > 0
        assert all(any("reality" in tag for tag in s.tags) for s in results)

    def test_export_registry(self):
        """Test exporting registry state"""
        registry = SubroutineRegistry()
        
        export = registry.export_registry()
        
        assert "registry_version" in export
        assert "exported_at" in export
        assert "subroutines" in export
        assert "stats" in export
        assert len(export["subroutines"]) > 0

    def test_get_singleton(self):
        """Test global singleton pattern"""
        registry1 = get_subroutine_registry()
        registry2 = get_subroutine_registry()
        
        assert registry1 is registry2  # Same instance


@pytest.mark.unit
class TestVisionAlignmentManager:
    """Test Vision Alignment Manager subroutine"""

    def test_initialization(self):
        """Test manager initialization with defaults"""
        manager = VisionAlignmentManager()
        
        assert manager.system_state is not None
        assert manager.crew_registry is not None
        assert manager.simulation_layer is not None
        assert manager.knowledge_base is not None
        assert manager.audit_log is not None
        assert manager.min_fidelity == 0.95
        assert manager._alignment_count == 0

    def test_enforce_alignment_success(self):
        """Test successful vision alignment"""
        manager = VisionAlignmentManager()
        
        comp_id = "test_comp_001"
        input_data = {"computation_type": "quantum_opt", "params": {"x": 1}}
        outcomes = {"result": "success", "metrics": {"fidelity": 0.98}}
        
        record = manager.enforce_alignment(comp_id, input_data, outcomes)
        
        assert isinstance(record, AlignmentRecord)
        assert record.computation_id == comp_id
        assert record.alignment_status == 'aligned'
        assert record.fidelity_score >= manager.min_fidelity
        assert len(record.gaps_detected) == 0
        assert manager._success_count == 1

    def test_enforce_alignment_low_fidelity(self):
        """Test alignment failure due to low fidelity"""
        manager = VisionAlignmentManager(min_fidelity=0.99)  # Set high threshold
        
        comp_id = "test_comp_002"
        input_data = {"computation_type": "test"}
        outcomes = {"result": "test"}
        
        record = manager.enforce_alignment(comp_id, input_data, outcomes)
        
        # Mock sim returns 0.98, should fail 0.99 threshold
        assert record.alignment_status == 'failed'
        assert record.fidelity_score < 0.99
        assert manager._failure_count == 1

    def test_periodic_review_not_due(self):
        """Test periodic review when not yet due"""
        manager = VisionAlignmentManager(review_interval_days=30)
        
        # Set last review to recent
        manager._last_review = datetime.utcnow() - timedelta(days=5)
        
        result = manager.periodic_alignment_review()
        
        assert isinstance(result, AlignmentReviewResult)
        assert result.computations_reviewed == 0
        assert "not yet due" in result.recommendations[0].lower()

    def test_periodic_review_with_gaps(self):
        """Test periodic review detecting alignment gaps"""
        manager = VisionAlignmentManager(review_interval_days=30)
        
        # Run some alignments first
        for i in range(5):
            comp_id = f"test_comp_{i}"
            manager.enforce_alignment(comp_id, {"test": i}, {"result": i})
        
        # Set last review to past
        last_review = datetime.utcnow() - timedelta(days=31)
        
        result = manager.periodic_alignment_review(last_review)
        
        assert isinstance(result, AlignmentReviewResult)
        assert result.computations_reviewed > 0
        assert result.overall_health in ['healthy', 'warning', 'critical']

    def test_get_stats(self):
        """Test statistics tracking"""
        manager = VisionAlignmentManager()
        
        # Run multiple alignments
        for i in range(5):
            comp_id = f"test_comp_{i}"
            manager.enforce_alignment(comp_id, {"test": i}, {"result": i})
        
        stats = manager.get_stats()
        
        assert stats['total_alignments'] == 5
        assert stats['successful'] > 0
        assert 'success_rate' in stats
        assert 'alignment_rate' in stats

    def test_vision_statement(self):
        """Test vision statement is set"""
        manager = VisionAlignmentManager()
        
        assert "ultra-high fidelity reality simulation" in manager.vision_statement.lower()
        assert "orion station" in manager.vision_statement.lower()
        assert "collaborative" in manager.vision_statement.lower()


@pytest.mark.unit
class TestSubroutineRegistryExtended:
    """Test SubroutineRegistry with Vision Alignment Manager"""

    def test_initialization(self):
        """Test registry initialization"""
        registry = SubroutineRegistry()
        
        assert len(registry._subroutines) >= 2  # Should have both built-in subroutines
        assert "reality_sim_monitor" in registry._subroutines
        assert "vision_alignment_manager" in registry._subroutines
        
        stats = registry.get_stats()
        assert stats['total_subroutines'] >= 2

    def test_vision_alignment_registered(self):
        """Test Vision Alignment Manager is properly registered"""
        registry = SubroutineRegistry()
        
        vision_sub = registry.get("vision_alignment_manager")
        
        assert vision_sub is not None
        assert vision_sub.name == "Vision Alignment Manager"
        assert vision_sub.version == "1.0.0"
        assert vision_sub.category == SubroutineCategory.EXECUTIVE
        assert vision_sub.status == SubroutineStatus.ACTIVE
        assert "vision" in vision_sub.tags
        assert "alignment" in vision_sub.tags


@pytest.mark.integration
class TestSubroutineAPI:
    """Test Subroutine API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from src.subroutines.api import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_health_check(self, client):
        """Test health endpoint"""
        response = client.get("/subroutines/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "healthy"

    def test_list_subroutines(self, client):
        """Test listing subroutines"""
        response = client.get("/subroutines/list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "subroutines" in data
        assert len(data["subroutines"]) > 0

    def test_get_subroutine(self, client):
        """Test getting specific subroutine"""
        response = client.get("/subroutines/get/reality_sim_monitor")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subroutine"]["id"] == "reality_sim_monitor"

    def test_get_nonexistent(self, client):
        """Test getting nonexistent subroutine"""
        response = client.get("/subroutines/get/nonexistent")
        
        assert response.status_code == 404

    def test_search_subroutines(self, client):
        """Test searching subroutines"""
        response = client.post(
            "/subroutines/search",
            json={"query": "reality"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["results"]) > 0

    def test_get_stats(self, client):
        """Test getting registry stats"""
        response = client.get("/subroutines/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        assert data["stats"]["total_subroutines"] > 0

    def test_export_registry(self, client):
        """Test exporting registry"""
        response = client.get("/subroutines/export")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "export" in data
        assert "subroutines" in data["export"]


# Add markers for pytest
pytest.main([__file__, "-v", "-m", "unit"])
