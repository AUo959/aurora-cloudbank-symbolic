"""
Tests for Quantum Decision Oracle.

Test Coverage:
- Criterion creation and validation
- Alternative evaluation with different criteria types
- Quantum-inspired probability amplitude scoring
- Confidence calculation
- Uncertainty identification
- Multi-criteria decision analysis
- Edge cases and error handling

Anchor: TEST-QUANTUM-DECISION-V1
"""

import pytest
import json
from tools.simulation_engine.quantum_decision_oracle import (
    QuantumDecisionOracle,
    DecisionCriterion,
    CriterionType,
    DecisionRecommendation
)


@pytest.mark.unit
@pytest.mark.simulation
class TestDecisionCriterion:
    """Test DecisionCriterion creation and validation."""
    
    def test_maximize_criterion(self):
        """Test MAXIMIZE criterion type."""
        criterion = DecisionCriterion(
            name="performance",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.7
        )
        assert criterion.name == "performance"
        assert criterion.criterion_type == CriterionType.MAXIMIZE
        assert criterion.weight == 0.7
    
    def test_minimize_criterion(self):
        """Test MINIMIZE criterion type."""
        criterion = DecisionCriterion(
            name="cost",
            criterion_type=CriterionType.MINIMIZE,
            weight=0.3
        )
        assert criterion.criterion_type == CriterionType.MINIMIZE
        assert criterion.weight == 0.3
    
    def test_target_criterion(self):
        """Test TARGET criterion type."""
        criterion = DecisionCriterion(
            name="temperature",
            criterion_type=CriterionType.TARGET,
            weight=1.0,
            target_value=72.0
        )
        assert criterion.criterion_type == CriterionType.TARGET
        assert criterion.target_value == 72.0


@pytest.mark.unit
@pytest.mark.simulation
class TestQuantumDecisionOracle:
    """Test Quantum Decision Oracle core functionality."""
    
    def test_oracle_initialization(self):
        """Test oracle initialization."""
        oracle = QuantumDecisionOracle(
            name="Test Oracle",
            anchor_seed="TEST_SEED"
        )
        assert oracle.name == "Test Oracle"
        assert oracle.anchor_seed == "TEST_SEED"
        assert oracle.decision_count == 0
    
    def test_add_criterion(self):
        """Test adding criteria to oracle."""
        oracle = QuantumDecisionOracle(name="Test")
        
        criterion = DecisionCriterion(
            name="quality",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.6
        )
        
        oracle.add_criterion(criterion)
        assert len(oracle.criteria) == 1
        assert oracle.criteria[0].name == "quality"
    
    def test_evaluate_decision_simple(self):
        """Test simple decision evaluation with single criterion."""
        oracle = QuantumDecisionOracle(name="Simple Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        alternatives = {
            "Option A": {"score": 80},
            "Option B": {"score": 90},
            "Option C": {"score": 70}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        assert isinstance(result, DecisionRecommendation)
        assert result.recommended_alternative == "Option B"  # Highest score
        assert len(result.ranked_alternatives) == 3
        assert result.ranked_alternatives[0][0] == "Option B"
    
    def test_evaluate_decision_multiple_criteria(self):
        """Test decision with multiple criteria."""
        oracle = QuantumDecisionOracle(name="Multi-Criteria Test")
        
        # Maximize performance, minimize cost
        oracle.add_criterion(DecisionCriterion(
            name="performance",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.6
        ))
        
        oracle.add_criterion(DecisionCriterion(
            name="cost",
            criterion_type=CriterionType.MINIMIZE,
            weight=0.4
        ))
        
        alternatives = {
            "High Perf": {"performance": 95, "cost": 1000},
            "Balanced": {"performance": 80, "cost": 600},
            "Budget": {"performance": 60, "cost": 300}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        assert result.recommended_alternative in alternatives
        assert len(result.ranked_alternatives) == 3
        
        # All alternatives should have scores
        for name, score in result.ranked_alternatives:
            assert 0 <= score <= 1
    
    def test_target_criterion_scoring(self):
        """Test TARGET criterion type scoring."""
        oracle = QuantumDecisionOracle(name="Target Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="temperature",
            criterion_type=CriterionType.TARGET,
            weight=1.0,
            target_value=72.0
        ))
        
        alternatives = {
            "Option A": {"temperature": 72.0},  # Exact target
            "Option B": {"temperature": 74.0},  # Close
            "Option C": {"temperature": 80.0}   # Far
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # Option A (exact target) should rank highest
        assert result.recommended_alternative == "Option A"
    
    def test_quantum_probability_amplitudes(self):
        """Test quantum-inspired probability amplitude calculation."""
        oracle = QuantumDecisionOracle(name="Quantum Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="metric",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        alternatives = {
            "Low": {"metric": 30},
            "Medium": {"metric": 60},
            "High": {"metric": 90}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # Verify scores are normalized (sum of squares = 1)
        sum_of_squares = sum(score ** 2 for _, score in result.ranked_alternatives)
        assert 0.99 < sum_of_squares < 1.01  # Allow small floating point error
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        oracle = QuantumDecisionOracle(name="Confidence Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        # Clear winner scenario
        clear_alternatives = {
            "Winner": {"score": 100},
            "Loser 1": {"score": 50},
            "Loser 2": {"score": 45}
        }
        
        clear_result = oracle.evaluate_decision(clear_alternatives, seed=42)
        
        # Close race scenario
        oracle2 = QuantumDecisionOracle(name="Close Race")
        oracle2.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        close_alternatives = {
            "Option A": {"score": 80},
            "Option B": {"score": 79},
            "Option C": {"score": 78}
        }
        
        close_result = oracle2.evaluate_decision(close_alternatives, seed=42)
        
        # Clear winner should have higher confidence
        assert clear_result.confidence_score > close_result.confidence_score


@pytest.mark.integration
@pytest.mark.simulation
class TestUncertaintyAnalysis:
    """Test uncertainty factor identification."""
    
    def test_close_race_uncertainty(self):
        """Test identification of close race uncertainty."""
        oracle = QuantumDecisionOracle(name="Close Race Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        # Very close scores
        alternatives = {
            "Option A": {"score": 80.1},
            "Option B": {"score": 80.0},
            "Option C": {"score": 79.9}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # Should identify close race
        assert any("close race" in factor.lower() for factor in result.uncertainty_factors)
    
    def test_conflicting_criteria_uncertainty(self):
        """Test identification of conflicting criteria."""
        oracle = QuantumDecisionOracle(name="Conflict Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="quality",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.5
        ))
        
        oracle.add_criterion(DecisionCriterion(
            name="cost",
            criterion_type=CriterionType.MINIMIZE,
            weight=0.5
        ))
        
        # One option is high quality but expensive
        alternatives = {
            "Premium": {"quality": 100, "cost": 1000},
            "Budget": {"quality": 50, "cost": 100}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # Should have some uncertainty factors
        assert len(result.uncertainty_factors) > 0


@pytest.mark.integration
@pytest.mark.simulation
class TestComplexDecisions:
    """Test complex multi-criteria decisions."""
    
    def test_weighted_criteria_balance(self):
        """Test that weights properly balance criteria."""
        oracle = QuantumDecisionOracle(name="Weighted Test")
        
        # Heavy weight on performance
        oracle.add_criterion(DecisionCriterion(
            name="performance",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.8
        ))
        
        oracle.add_criterion(DecisionCriterion(
            name="cost",
            criterion_type=CriterionType.MINIMIZE,
            weight=0.2
        ))
        
        alternatives = {
            "High Perf": {"performance": 100, "cost": 1000},
            "Low Cost": {"performance": 60, "cost": 100}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # High performance should win due to higher weight
        assert result.recommended_alternative == "High Perf"
    
    def test_many_alternatives(self):
        """Test decision with many alternatives."""
        oracle = QuantumDecisionOracle(name="Many Options")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        # Generate 20 alternatives
        alternatives = {
            f"Option {i}": {"score": i * 5}
            for i in range(1, 21)
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # Highest score should win
        assert result.recommended_alternative == "Option 20"
        assert len(result.ranked_alternatives) == 20


@pytest.mark.unit
@pytest.mark.simulation
class TestResultSerialization:
    """Test result serialization and export."""
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        oracle = QuantumDecisionOracle(name="Export Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        alternatives = {"Option A": {"score": 80}, "Option B": {"score": 90}}
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "recommended_alternative" in result_dict
        assert "confidence_score" in result_dict
        assert "ranked_alternatives" in result_dict
        assert "anchor" in result_dict
    
    def test_export_decision(self, tmp_path):
        """Test exporting decision to JSON."""
        oracle = QuantumDecisionOracle(name="Export Test")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        alternatives = {"Option A": {"score": 80}, "Option B": {"score": 90}}
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        filepath = tmp_path / "test_decision.json"
        oracle.export_decision(result, str(filepath))
        
        assert filepath.exists()
        
        with open(filepath) as f:
            data = json.load(f)
        
        assert data["recommended_alternative"] == result.recommended_alternative


@pytest.mark.unit
@pytest.mark.simulation
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_alternative(self):
        """Test decision with only one alternative."""
        oracle = QuantumDecisionOracle(name="Single Option")
        
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        alternatives = {"Only Option": {"score": 75}}
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        assert result.recommended_alternative == "Only Option"
        assert len(result.ranked_alternatives) == 1
    
    def test_reproducibility_with_seed(self):
        """Test that seed produces reproducible results."""
        alternatives = {
            "Option A": {"score": 80},
            "Option B": {"score": 90},
            "Option C": {"score": 85}
        }
        
        oracle1 = QuantumDecisionOracle(name="Test 1")
        oracle1.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        oracle2 = QuantumDecisionOracle(name="Test 2")
        oracle2.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        result1 = oracle1.evaluate_decision(alternatives, seed=42)
        result2 = oracle2.evaluate_decision(alternatives, seed=42)
        
        # Results should be identical with same seed
        assert result1.recommended_alternative == result2.recommended_alternative
        assert result1.confidence_score == result2.confidence_score
    
    def test_zero_weight_criterion(self):
        """Test criterion with zero weight."""
        oracle = QuantumDecisionOracle(name="Zero Weight")
        
        oracle.add_criterion(DecisionCriterion(
            name="important",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        oracle.add_criterion(DecisionCriterion(
            name="irrelevant",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.0
        ))
        
        alternatives = {
            "Option A": {"important": 100, "irrelevant": 10},
            "Option B": {"important": 50, "irrelevant": 100}
        }
        
        result = oracle.evaluate_decision(alternatives, seed=42)
        
        # Option A should win based on important criterion
        assert result.recommended_alternative == "Option A"
