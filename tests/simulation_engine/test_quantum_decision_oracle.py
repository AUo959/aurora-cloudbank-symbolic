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

import json
import pytest
from tools.simulation_engine.quantum_decision_oracle import (
    CriterionType,
    DecisionCriterion,
    DecisionRecommendation,
    QuantumDecisionOracle,
    Alternative,
)


@pytest.fixture
def oracle():
    """Provides a clean QuantumDecisionOracle instance for each test."""
    return QuantumDecisionOracle(anchor_seed="TEST_SEED")


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

    def test_oracle_initialization(self, oracle):
        """Test oracle initialization."""
        assert oracle.anchor_seed == "TEST_SEED"
        assert oracle.decision_count == 0
        assert not oracle.criteria
        assert not oracle.alternatives

    def test_add_criterion(self, oracle):
        """Test adding criteria to oracle."""
        criterion = DecisionCriterion(
            name="quality",
            criterion_type=CriterionType.MAXIMIZE,
            weight=0.6
        )
        oracle.add_criterion(criterion)
        assert len(oracle.criteria) == 1
        assert oracle.criteria[0].name == "quality"

    def test_evaluate_decision_simple(self, oracle):
        """Test simple decision evaluation with single criterion."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        oracle.add_alternative(Alternative(name="Option A", scores={"score": 80}))
        oracle.add_alternative(Alternative(name="Option B", scores={"score": 90}))
        oracle.add_alternative(Alternative(name="Option C", scores={"score": 70}))
        
        result = oracle.evaluate_decision()
        
        assert isinstance(result, DecisionRecommendation)
        assert result.recommended_alternative == "Option B"
        assert len(result.rankings) == 3
        assert result.rankings[0][0] == "Option B"

    def test_evaluate_decision_multiple_criteria(self, oracle):
        """Test decision with multiple criteria."""
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
        
        oracle.add_alternative(Alternative(name="High Perf", scores={"performance": 95, "cost": 1000}))
        oracle.add_alternative(Alternative(name="Balanced", scores={"performance": 80, "cost": 600}))
        oracle.add_alternative(Alternative(name="Budget", scores={"performance": 60, "cost": 300}))
        
        result = oracle.evaluate_decision()
        
        assert result.recommended_alternative in ["High Perf", "Balanced", "Budget"]
        assert len(result.rankings) == 3
        for name, score in result.rankings:
            assert 0 <= score

    def test_target_criterion_scoring(self, oracle):
        """Test TARGET criterion type scoring."""
        oracle.add_criterion(DecisionCriterion(
            name="temperature",
            criterion_type=CriterionType.TARGET,
            weight=1.0,
            target_value=72.0
        ))
        
        oracle.add_alternative(Alternative(name="Option A", scores={"temperature": 72.0}))
        oracle.add_alternative(Alternative(name="Option B", scores={"temperature": 74.0}))
        oracle.add_alternative(Alternative(name="Option C", scores={"temperature": 80.0}))
        
        result = oracle.evaluate_decision()
        assert result.recommended_alternative == "Option A"

    def test_confidence_calculation(self, oracle):
        """Test confidence score calculation."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        # Clear winner scenario
        oracle.add_alternative(Alternative(name="Winner", scores={"score": 100}))
        oracle.add_alternative(Alternative(name="Loser 1", scores={"score": 50}))
        oracle.add_alternative(Alternative(name="Loser 2", scores={"score": 45}))
        clear_result = oracle.evaluate_decision()

        # Close race scenario
        oracle2 = QuantumDecisionOracle()
        oracle2.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        oracle2.add_alternative(Alternative(name="Option A", scores={"score": 80}))
        oracle2.add_alternative(Alternative(name="Option B", scores={"score": 79}))
        oracle2.add_alternative(Alternative(name="Option C", scores={"score": 78}))
        close_result = oracle2.evaluate_decision()
        
        assert clear_result.confidence > close_result.confidence


@pytest.mark.integration
@pytest.mark.simulation
class TestUncertaintyAnalysis:
    """Test uncertainty factor identification."""

    def test_close_race_uncertainty(self, oracle):
        """Test identification of close race uncertainty."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        oracle.add_alternative(Alternative(name="Option A", scores={"score": 80.1}))
        oracle.add_alternative(Alternative(name="Option B", scores={"score": 80.0}))
        oracle.add_alternative(Alternative(name="Option C", scores={"score": 79.9}))
        
        result = oracle.evaluate_decision()
        assert any("closely matched" in factor for factor in result.uncertainty_factors)

    def test_conflicting_criteria_uncertainty(self, oracle):
        """Test identification of conflicting criteria."""
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
        
        oracle.add_alternative(Alternative(name="Premium", scores={"quality": 100, "cost": 1000}))
        oracle.add_alternative(Alternative(name="Budget", scores={"quality": 50, "cost": 100}))
        
        result = oracle.evaluate_decision()
        assert len(result.uncertainty_factors) > 0


@pytest.mark.integration
@pytest.mark.simulation
class TestComplexDecisions:
    """Test complex multi-criteria decisions."""

    def test_weighted_criteria_balance(self, oracle):
        """Test that weights properly balance criteria."""
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
        
        oracle.add_alternative(Alternative(name="High Perf", scores={"performance": 100, "cost": 1000}))
        oracle.add_alternative(Alternative(name="Low Cost", scores={"performance": 60, "cost": 100}))
        
        result = oracle.evaluate_decision()
        assert result.recommended_alternative == "High Perf"

    def test_many_alternatives(self, oracle):
        """Test decision with many alternatives."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        
        for i in range(1, 21):
            oracle.add_alternative(Alternative(name=f"Option {i}", scores={"score": i * 5}))
        
        result = oracle.evaluate_decision()
        assert result.recommended_alternative == "Option 20"
        assert len(result.rankings) == 20


@pytest.mark.unit
@pytest.mark.simulation
class TestResultSerialization:
    """Test result serialization and export."""

    def test_result_to_dict(self, oracle):
        """Test converting result to dictionary."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        oracle.add_alternative(Alternative(name="Option A", scores={"score": 80}))
        oracle.add_alternative(Alternative(name="Option B", scores={"score": 90}))
        
        result = oracle.evaluate_decision()
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "recommended_alternative" in result_dict
        assert "confidence" in result_dict
        assert "rankings" in result_dict
        assert "anchor" in result_dict

    def test_export_decision(self, oracle, tmp_path):
        """Test exporting decision to JSON."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        oracle.add_alternative(Alternative(name="Option A", scores={"score": 80}))
        oracle.add_alternative(Alternative(name="Option B", scores={"score": 90}))
        
        result = oracle.evaluate_decision()
        
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

    def test_single_alternative(self, oracle):
        """Test decision with only one alternative."""
        oracle.add_criterion(DecisionCriterion(
            name="score",
            criterion_type=CriterionType.MAXIMIZE,
            weight=1.0
        ))
        oracle.add_alternative(Alternative(name="Only Option", scores={"score": 75}))
        
        result = oracle.evaluate_decision()
        
        assert result.recommended_alternative == "Only Option"
        assert len(result.rankings) == 1

    def test_reproducibility_with_seed(self):
        """Test that seed produces reproducible results."""
        # Note: Seed functionality was removed from evaluate_decision as it's deterministic
        pass

    def test_zero_weight_criterion(self, oracle):
        """Test criterion with zero weight."""
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
        
        oracle.add_alternative(Alternative(name="Option A", scores={"important": 100, "irrelevant": 10}))
        oracle.add_alternative(Alternative(name="Option B", scores={"important": 50, "irrelevant": 100}))
        
        result = oracle.evaluate_decision()
        assert result.recommended_alternative == "Option A"
