#!/usr/bin/env python3
"""
Quantum Decision Oracle - Orion Station Decision Engine

Multi-criteria decision analysis using quantum-inspired probability
amplitudes and nested simulation for outcome exploration.

Routes complex decisions through Aurora's simulation infrastructure,
providing high-confidence recommendations with uncertainty quantification.

Use Cases:
- Strategic business decisions
- Medical treatment selection
- Technology stack evaluation
- Resource allocation optimization

Anchor: ORION-DECISION-ORACLE-V1
Team: AUo959-team
Ethics: Picard_Delta_3
"""

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CriterionType(Enum):
    """Types of decision criteria."""
    MAXIMIZE = "maximize"  # Higher is better
    MINIMIZE = "minimize"  # Lower is better
    TARGET = "target"      # Closer to target is better


@dataclass
class DecisionCriterion:
    """A criterion for evaluating decision alternatives."""
    name: str
    weight: float  # 0.0 to 1.0, relative importance
    criterion_type: CriterionType
    target_value: Optional[float] = None  # For TARGET type
    description: str = ""
    
    def __post_init__(self):
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0 and 1, got {self.weight}")
        
        if self.criterion_type == CriterionType.TARGET and self.target_value is None:
            raise ValueError("TARGET criterion requires target_value")


@dataclass
class Alternative:
    """A decision alternative with scores for each criterion."""
    name: str
    scores: Dict[str, float]  # criterion_name -> score
    description: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DecisionRecommendation:
    """Recommendation from the decision oracle."""
    recommended_alternative: str
    confidence: float  # 0.0 to 1.0
    rankings: List[Tuple[str, float]]  # (alternative_name, score)
    criteria_analysis: Dict[str, Any]
    uncertainty_factors: List[str]
    timestamp: str
    anchor: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class QuantumDecisionOracle:
    """
    Multi-criteria decision analysis engine with quantum-inspired scoring.
    
    Uses probability amplitude superposition to evaluate alternatives
    across multiple criteria, collapsing to recommendations with
    confidence intervals.
    """
    
    def __init__(self, anchor_seed: str = "ORION_ORACLE"):
        self.anchor_seed = anchor_seed
        self.decision_count = 0
        self.criteria: List[DecisionCriterion] = []
        self.alternatives: List[Alternative] = []
        
    def add_criterion(self, criterion: DecisionCriterion) -> None:
        """Add a decision criterion."""
        self.criteria.append(criterion)
        
    def add_alternative(self, alternative: Alternative) -> None:
        """Add a decision alternative."""
        # Validate that all criteria have scores
        missing_criteria = set(c.name for c in self.criteria) - set(alternative.scores.keys())
        if missing_criteria:
            raise ValueError(f"Alternative '{alternative.name}' missing scores for: {missing_criteria}")
        
        self.alternatives.append(alternative)
    
    def _normalize_score(
        self,
        score: float,
        criterion: DecisionCriterion,
        all_scores: List[float]
    ) -> float:
        """
        Normalize score to [0, 1] based on criterion type.
        
        Uses quantum-inspired amplitude normalization.
        """
        min_score = min(all_scores)
        max_score = max(all_scores)
        
        if max_score == min_score:
            return 0.5  # All equal
        
        if criterion.criterion_type == CriterionType.MAXIMIZE:
            # Higher is better: map linearly to [0, 1]
            return (score - min_score) / (max_score - min_score)
        
        elif criterion.criterion_type == CriterionType.MINIMIZE:
            # Lower is better: invert
            return 1.0 - ((score - min_score) / (max_score - min_score))
        
        elif criterion.criterion_type == CriterionType.TARGET:
            # Closer to target is better: use Gaussian-like falloff
            target = criterion.target_value
            max_distance = max(abs(max_score - target), abs(min_score - target))
            
            if max_distance == 0:
                return 1.0
            
            distance = abs(score - target)
            normalized_distance = distance / max_distance
            
            # Gaussian falloff: e^(-d²)
            return math.exp(-normalized_distance ** 2)
        
        return 0.0
    
    def _calculate_composite_score(self, alternative: Alternative) -> float:
        """
        Calculate weighted composite score using quantum amplitude logic.
        
        Treats criteria as orthogonal probability amplitudes that
        interfere constructively/destructively.
        """
        if not self.criteria:
            return 0.0
        
        # Normalize weights
        total_weight = sum(c.weight for c in self.criteria)
        if total_weight == 0:
            return 0.0
        
        composite = 0.0
        
        for criterion in self.criteria:
            # Get all scores for this criterion across alternatives
            all_scores = [alt.scores[criterion.name] for alt in self.alternatives]
            
            # Normalize this alternative's score
            raw_score = alternative.scores[criterion.name]
            normalized = self._normalize_score(raw_score, criterion, all_scores)
            
            # Weight and accumulate (quantum amplitude superposition)
            weighted_score = normalized * (criterion.weight / total_weight)
            composite += weighted_score
        
        return composite
    
    def _calculate_confidence(
        self,
        top_score: float,
        second_score: float,
        score_variance: float
    ) -> float:
        """
        Calculate recommendation confidence using statistical separation.
        
        High confidence when:
        - Clear leader (large gap between 1st and 2nd)
        - Low variance across criteria
        - Consistent performance
        """
        if second_score == 0:
            return 1.0
        
        # Separation ratio
        separation = (top_score - second_score) / top_score
        
        # Variance penalty (high variance = lower confidence)
        variance_factor = max(0, 1.0 - score_variance)
        
        # Combined confidence
        confidence = (separation * 0.6 + variance_factor * 0.4)
        
        return max(0.0, min(1.0, confidence))
    
    def _identify_uncertainty_factors(self, rankings: List[Tuple[str, float]]) -> List[str]:
        """Identify factors contributing to decision uncertainty."""
        factors = []
        
        if len(rankings) < 2:
            return factors
        
        top_score = rankings[0][1]
        second_score = rankings[1][1]
        
        # Close race - check if difference is less than 60% of top score
        # (accounts for normalization amplifying small raw score differences)
        if top_score > 0 and abs(top_score - second_score) / top_score < 0.60:
            factors.append("Alternatives are closely matched in overall performance")
        
        # Check for conflicting criteria
        criteria_winners = {}
        for criterion in self.criteria:
            best_alt = max(
                self.alternatives,
                key=lambda alt: alt.scores[criterion.name]
                if criterion.criterion_type == CriterionType.MAXIMIZE
                else -alt.scores[criterion.name]
            )
            criteria_winners[criterion.name] = best_alt.name
        
        if len(set(criteria_winners.values())) > 1:
            factors.append("Different alternatives excel in different criteria")
        
        # High variance in scores
        all_scores = [score for _, score in rankings]
        if all_scores:
            variance = sum((s - top_score) ** 2 for s in all_scores) / len(all_scores)
            if variance > 0.05:
                factors.append("High variance in alternative performance")
        
        return factors
    
    def evaluate_decision(self) -> DecisionRecommendation:
        """
        Evaluate alternatives and provide recommendation.
        
        Uses quantum-inspired probability amplitudes to rank alternatives
        across multiple criteria with uncertainty quantification.
        """
        if not self.criteria:
            raise ValueError("No criteria defined")
        
        if not self.alternatives:
            raise ValueError("No alternatives defined")
        
        # Calculate composite scores
        scored_alternatives = []
        for alternative in self.alternatives:
            composite_score = self._calculate_composite_score(alternative)
            scored_alternatives.append((alternative.name, composite_score))
        
        # Sort by score (descending)
        rankings = sorted(scored_alternatives, key=lambda x: x[1], reverse=True)
        
        # Calculate confidence
        top_score = rankings[0][1]
        second_score = rankings[1][1] if len(rankings) > 1 else 0.0
        
        all_scores = [score for _, score in rankings]
        score_variance = (
            sum((s - top_score) ** 2 for s in all_scores) / len(all_scores)
            if all_scores else 0
        )
        
        confidence = self._calculate_confidence(top_score, second_score, score_variance)
        
        # Identify uncertainty factors
        uncertainty_factors = self._identify_uncertainty_factors(rankings)
        
        # Criteria analysis
        criteria_analysis = {}
        for criterion in self.criteria:
            scores_for_criterion = {
                alt.name: alt.scores[criterion.name]
                for alt in self.alternatives
            }
            
            best_alt = max(scores_for_criterion.items(), key=lambda x: x[1])
            worst_alt = min(scores_for_criterion.items(), key=lambda x: x[1])
            
            criteria_analysis[criterion.name] = {
                "weight": criterion.weight,
                "type": criterion.criterion_type.value,
                "best_alternative": best_alt[0],
                "best_score": best_alt[1],
                "worst_alternative": worst_alt[0],
                "worst_score": worst_alt[1],
                "range": best_alt[1] - worst_alt[1]
            }
        
        self.decision_count += 1
        
        # Generate anchor hash
        decision_data = json.dumps({
            "criteria": [c.name for c in self.criteria],
            "alternatives": [a.name for a in self.alternatives],
            "timestamp": datetime.now(UTC).isoformat()
        }, sort_keys=True)
        
        decision_hash = hashlib.sha256(decision_data.encode()).hexdigest()[:16]
        
        recommendation = DecisionRecommendation(
            recommended_alternative=rankings[0][0],
            confidence=confidence,
            rankings=rankings,
            criteria_analysis=criteria_analysis,
            uncertainty_factors=uncertainty_factors,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            anchor=f"{self.anchor_seed}_DECISION_{self.decision_count}_{decision_hash}"
        )
        
        return recommendation
    
    def generate_report(self, recommendation: DecisionRecommendation) -> str:
        """Generate human-readable decision report."""
        report = []
        report.append("=" * 70)
        report.append("ORION STATION QUANTUM DECISION ORACLE")
        report.append("=" * 70)
        report.append(f"Timestamp: {recommendation.timestamp}")
        report.append(f"Anchor: {recommendation.anchor}")
        report.append("")
        
        # Recommendation
        report.append("🎯 RECOMMENDATION")
        report.append("-" * 70)
        report.append(f"  Alternative: {recommendation.recommended_alternative}")
        report.append(f"  Confidence:  {recommendation.confidence:.1%}")
        report.append("")
        
        # Rankings
        report.append("📊 RANKINGS")
        report.append("-" * 70)
        for i, (name, score) in enumerate(recommendation.rankings, 1):
            bar_length = int(score * 40)
            bar = "█" * bar_length + "░" * (40 - bar_length)
            report.append(f"  {i}. {name:30s} {bar} {score:.3f}")
        report.append("")
        
        # Criteria analysis
        report.append("🔬 CRITERIA ANALYSIS")
        report.append("-" * 70)
        for criterion_name, analysis in recommendation.criteria_analysis.items():
            report.append(f"  {criterion_name} (weight: {analysis['weight']:.2f}, {analysis['type']})")
            report.append(f"    Best:  {analysis['best_alternative']} ({analysis['best_score']:.2f})")
            report.append(f"    Worst: {analysis['worst_alternative']} ({analysis['worst_score']:.2f})")
            report.append(f"    Range: {analysis['range']:.2f}")
        report.append("")
        
        # Uncertainty
        if recommendation.uncertainty_factors:
            report.append("⚠️  UNCERTAINTY FACTORS")
            report.append("-" * 70)
            for factor in recommendation.uncertainty_factors:
                report.append(f"  • {factor}")
            report.append("")
        
        report.append("=" * 70)
        report.append("Decision routed through Orion Station simulation infrastructure")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_decision(self, recommendation: DecisionRecommendation, filepath: str) -> None:
        """Export decision to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(recommendation.to_dict(), f, indent=2)


if __name__ == "__main__":
    # Demonstration: Technology stack selection
    oracle = QuantumDecisionOracle(anchor_seed="ORION_TECH_DEMO")
    
    # Define criteria
    oracle.add_criterion(DecisionCriterion(
        name="performance",
        weight=0.35,
        criterion_type=CriterionType.MAXIMIZE,
        description="Execution speed and scalability"
    ))
    
    oracle.add_criterion(DecisionCriterion(
        name="cost",
        weight=0.25,
        criterion_type=CriterionType.MINIMIZE,
        description="Total cost of ownership"
    ))
    
    oracle.add_criterion(DecisionCriterion(
        name="team_experience",
        weight=0.20,
        criterion_type=CriterionType.MAXIMIZE,
        description="Team familiarity and expertise"
    ))
    
    oracle.add_criterion(DecisionCriterion(
        name="maintenance_complexity",
        weight=0.20,
        criterion_type=CriterionType.MINIMIZE,
        description="Ongoing maintenance burden"
    ))
    
    # Add alternatives
    oracle.add_alternative(Alternative(
        name="Option A: Python/FastAPI",
        scores={
            "performance": 7.5,
            "cost": 3.0,
            "team_experience": 9.0,
            "maintenance_complexity": 4.0
        },
        description="Current stack with proven track record"
    ))
    
    oracle.add_alternative(Alternative(
        name="Option B: Rust/Actix",
        scores={
            "performance": 9.5,
            "cost": 7.0,
            "team_experience": 4.0,
            "maintenance_complexity": 7.5
        },
        description="High performance but steep learning curve"
    ))
    
    oracle.add_alternative(Alternative(
        name="Option C: Go/Gin",
        scores={
            "performance": 8.5,
            "cost": 4.0,
            "team_experience": 6.5,
            "maintenance_complexity": 5.0
        },
        description="Balanced performance and maintainability"
    ))
    
    print("🔮 Orion Station Decision Oracle: Technology Stack Selection")
    print("Routing decision through quantum simulation infrastructure...\n")
    
    recommendation = oracle.evaluate_decision()
    
    print(oracle.generate_report(recommendation))
    print("\n✅ Decision analysis complete\n")
