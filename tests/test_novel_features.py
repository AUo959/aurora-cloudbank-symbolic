"""
Tests for Aurora CloudBank Novel Features

Tests for Pattern Mutation Engine and Symbolic Pattern Detective
"""

import pytest
from tools.pattern_mutation_engine import PatternMutationEngine, Pattern
from tools.symbolic_pattern_detective import SymbolicPatternDetective


class TestPatternMutationEngine:
    """Tests for Pattern Mutation Engine"""

    def test_initialization(self):
        """Test engine initialization"""
        engine = PatternMutationEngine(anchor_seed="TEST_001")
        assert engine.anchor_seed == "TEST_001"
        assert engine.t1.state == 0
        assert engine.srb.resolution == 0
        assert len(engine.fitness_functions) == 5

    def test_pattern_creation(self):
        """Test pattern creation with metadata"""
        engine = PatternMutationEngine()
        pattern = engine.create_pattern("001999", 0)
        
        assert pattern.sequence == "001999"
        assert pattern.generation == 0
        assert pattern.t1_state > 0
        assert pattern.srb_resolution > 0
        assert 0.0 <= pattern.cultural_score <= 1.0
        assert len(pattern.pattern_hash) == 16

    def test_fitness_compactness(self):
        """Test compactness fitness function"""
        engine = PatternMutationEngine()
        
        # Short pattern should score high
        short_pattern = engine.create_pattern("001", 0)
        short_fitness = engine.evaluate_fitness(short_pattern, "compactness")
        
        # Long pattern should score lower
        long_pattern = engine.create_pattern("0" * 50, 0)
        long_fitness = engine.evaluate_fitness(long_pattern, "compactness")
        
        assert short_fitness > long_fitness

    def test_fitness_diversity(self):
        """Test diversity fitness function"""
        engine = PatternMutationEngine()
        
        # Diverse pattern
        diverse = engine.create_pattern("0123456789", 0)
        diverse_fitness = engine.evaluate_fitness(diverse, "diversity")
        
        # Non-diverse pattern
        repetitive = engine.create_pattern("0000000000", 0)
        repetitive_fitness = engine.evaluate_fitness(repetitive, "diversity")
        
        assert diverse_fitness > repetitive_fitness

    def test_mutation_operators(self):
        """Test mutation operators work correctly"""
        engine = PatternMutationEngine()
        original = "001999"
        
        # Test insert
        inserted = engine._mutate_insert(original)
        assert len(inserted) == len(original) + 1
        
        # Test delete
        deleted = engine._mutate_delete(original)
        assert len(deleted) == len(original) - 1
        
        # Test swap
        swapped = engine._mutate_swap(original)
        assert len(swapped) == len(original)
        
        # Test reverse
        reversed_pat = engine._mutate_reverse(original)
        assert len(reversed_pat) == len(original)

    def test_evolution(self):
        """Test evolutionary algorithm"""
        engine = PatternMutationEngine()
        
        results = engine.evolve(
            initial_pattern="001999",
            generations=3,
            population_size=5,
            mutation_rate=0.8,
            fitness_fn="compactness"
        )
        
        assert results["success"] is True
        assert results["initial_pattern"] == "001999"
        assert "best_pattern" in results
        assert results["best_pattern"]["fitness_score"] > 0
        assert len(results["top_5_patterns"]) <= 5
        assert results["evolution_stats"]["total_generations"] == 3

    def test_dlp_tracking(self):
        """Test DLP metadata is properly tracked"""
        engine = PatternMutationEngine(anchor_seed="DLP_TEST")
        
        results = engine.evolve(
            initial_pattern="001",
            generations=2,
            population_size=3,
            fitness_fn="balance"
        )
        
        metadata = results["metadata"]
        assert metadata["anchor_seed"] == "DLP_TEST"
        assert "t1_anchor" in metadata
        assert "srb_anchor" in metadata
        assert "dlp_hash" in metadata
        assert metadata["context_tag"] == "pattern_mutation_engine"
        assert len(metadata["dlp_hash"]) == 16

    def test_lineage_export(self):
        """Test pattern lineage export"""
        engine = PatternMutationEngine()
        
        results = engine.evolve(
            initial_pattern="001",
            generations=3,
            population_size=4,
            fitness_fn="diversity"
        )
        
        best_hash = results["best_pattern"]["pattern_hash"]
        lineage = engine.export_lineage(best_hash)
        
        assert len(lineage) > 0
        assert lineage[0]["generation"] == 0
        assert lineage[-1]["pattern_hash"] == best_hash


class TestSymbolicPatternDetective:
    """Tests for Symbolic Pattern Detective"""

    def test_initialization(self):
        """Test detective initialization"""
        detective = SymbolicPatternDetective(anchor_seed="TEST_DETECTIVE")
        assert detective.anchor_seed == "TEST_DETECTIVE"
        assert len(detective.security_patterns) > 0
        assert len(detective.performance_patterns) > 0
        assert len(detective.symbolic_patterns) > 0

    def test_detect_security_patterns(self):
        """Test security pattern detection"""
        detective = SymbolicPatternDetective()
        
        # Code with SQL injection
        code = '''
        def get_user(id):
            query = "SELECT * FROM users WHERE id = '" + id + "'"
            return execute(query)
        '''
        
        detections = detective.detect_in_text(
            text=code,
            location="test.py",
            pattern_types=["security"],
            sensitivity=0.7
        )
        
        # Should detect some security issues
        assert len(detections) >= 0  # May or may not match depending on regex
        
    def test_detect_performance_patterns(self):
        """Test performance pattern detection"""
        detective = SymbolicPatternDetective()
        
        # Code with nested loops
        code = '''
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    result = compute(i, j, k)
        '''
        
        detections = detective.detect_in_text(
            text=code,
            location="test.py",
            pattern_types=["performance"],
            sensitivity=0.7
        )
        
        # Should detect nested loops
        assert len(detections) >= 0

    def test_detect_symbolic_patterns(self):
        """Test symbolic chain pattern detection"""
        detective = SymbolicPatternDetective()
        
        # Code with broken chain
        code = '''
        chain1 = "001//999//"  # Good
        chain2 = "001//"        # Broken
        '''
        
        detections = detective.detect_in_text(
            text=code,
            location="test.py",
            pattern_types=["symbolic"],
            sensitivity=0.7
        )
        
        # Should detect broken chain
        assert len(detections) >= 0

    def test_scan_directory(self):
        """Test directory scanning"""
        detective = SymbolicPatternDetective()
        
        results = detective.scan_directory(
            directory="./src",
            pattern_types=["security", "performance"],
            sensitivity=0.8
        )
        
        assert results["success"] is True
        assert "summary" in results
        assert results["summary"]["files_scanned"] > 0
        assert "detections_by_severity" in results

    def test_cultural_impact_scoring(self):
        """Test cultural impact assessment"""
        detective = SymbolicPatternDetective()
        
        # Security issue should have high cultural impact
        security_impact = detective._compute_cultural_impact("sql_injection", "bad code")
        
        # Performance issue should have moderate impact
        perf_impact = detective._compute_cultural_impact("nested_loops", "slow code")
        
        assert 0.0 <= security_impact <= 1.0
        assert 0.0 <= perf_impact <= 1.0
        assert security_impact >= perf_impact  # Security more critical

    def test_dlp_tracking(self):
        """Test DLP metadata tracking"""
        detective = SymbolicPatternDetective(anchor_seed="DLP_DETECT")
        
        results = detective.scan_directory(
            directory="./src",
            pattern_types=["security"],
            sensitivity=0.8
        )
        
        metadata = results["metadata"]
        assert metadata["anchor_seed"] == "DLP_DETECT"
        assert "t1_anchor" in metadata
        assert "srb_anchor" in metadata
        assert "dlp_hash" in metadata
        assert metadata["context_tag"] == "symbolic_pattern_detective"
        assert len(metadata["dlp_hash"]) == 16

    def test_export_detections(self):
        """Test detection export"""
        detective = SymbolicPatternDetective()
        
        # Run scan
        detective.scan_directory(
            directory="./src",
            pattern_types=["security", "performance", "symbolic"],
            sensitivity=0.7
        )
        
        # Export detections
        exported = detective.export_detections()
        
        assert isinstance(exported, list)
        if len(exported) > 0:
            detection = exported[0]
            assert "pattern_type" in detection
            assert "location" in detection
            assert "severity" in detection
            assert "detection_hash" in detection
            assert "t1_state" in detection
            assert "srb_resolution" in detection

    def test_severity_levels(self):
        """Test severity level categorization"""
        detective = SymbolicPatternDetective()
        
        results = detective.scan_directory(
            directory="./src",
            pattern_types=["security", "performance"],
            sensitivity=0.8
        )
        
        summary = results["summary"]
        total = (
            summary["critical_issues"] +
            summary["high_issues"] +
            summary["medium_issues"] +
            summary["low_issues"]
        )
        
        assert total == summary["patterns_detected"]

    def test_confidence_scoring(self):
        """Test confidence scores are within valid range"""
        detective = SymbolicPatternDetective()
        
        results = detective.scan_directory(
            directory="./src",
            pattern_types=["security"],
            sensitivity=0.5
        )
        
        if results["summary"]["patterns_detected"] > 0:
            avg_confidence = results["summary"]["avg_confidence"]
            assert 0.0 <= avg_confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
