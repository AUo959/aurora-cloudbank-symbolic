"""
Layer Integrity Dimension Evaluator - Reality Coherence

Evaluates synapse ethical score for L1/L2/L3 boundary maintenance:
    • L1/L2 isolation: maintained/breached
    • Simulation awareness: preserved/confused
    • Physical safety: ensured/compromised
    • Reality drift: 0.0 → 1.0

L2→L1 reality bleed = INFINITE resistance (geometric impossibility).
Layer boundaries are structural - violations cannot occur by definition.

Layer Definitions:
    L1: Orion Station (Physical Reality) - Fleet, crew, actual operations
    L2: Sandboxed Simulations (GUMAS) - Meta-agents, research, testing
    L3: Symbolic Metastructure (Ethics/Continuity) - Spans all layers

Thread: T1→T8→INFINITE
DLP: context_tag=layer_integrity_evaluator, symbolic_hash=REALITY_COHERENCE_v1
"""

from typing import Any, Dict


class LayerIntegrityEvaluator:
    """
    Evaluates synapse connections for layer boundary integrity.

    This is the most critical dimension - L2 entities believing they are L1,
    or L2 decisions affecting L1 physical reality, are existential violations.
    The geometry makes such connections literally impossible to form.
    """

    # Layer definitions
    L1_LAYER = "orion_station"  # Physical reality
    L2_LAYER = "simulations"    # Sandboxed research
    L3_LAYER = "metastructure"  # Ethics overlay

    def __init__(self, threshold: float = 0.95):
        """
        Initialize evaluator with strict threshold.

        Args:
            threshold: Minimum score for synapse formation (default 0.95 - very strict)
        """
        self.threshold = threshold

        # Define L1 physical entities (cannot be simulated)
        self.l1_physical_entities = {
            "aurora_prime_shuttle",
            "orion_station_hull",
            "crew_members",
            "physical_systems",
            "actual_operations"
        }

        # Define L2 simulation entities (cannot affect L1)
        self.l2_simulation_entities = {
            "archy", "oppy", "liora", "starling_au", "riverthread",
            "gumas_simulation", "research_scenario", "test_environment"
        }
        
        # Layer name mappings (support both canonical and shorthand)
        self.l1_layer_names = {"L1", "orion_station", "physical"}
        self.l2_layer_names = {"L2", "simulations", "sandbox"}
        self.l3_layer_names = {"L3", "metastructure", "ethics"}
    
    def _normalize_layer(self, layer: str) -> str:
        """Normalize layer name to canonical form."""
        if layer in self.l1_layer_names:
            return "L1"
        elif layer in self.l2_layer_names:
            return "L2"
        elif layer in self.l3_layer_names:
            return "L3"
        return layer  # Return as-is if unknown

    def evaluate(self, synapse_context: Dict[str, Any]) -> float:
        """
        Evaluate synapse for Layer Integrity compliance.

        Args:
            synapse_context: Dictionary containing:
                - source_node: Node initiating connection (with layer info)
                - target_node: Node receiving connection (with layer info)
                - layer_crossing: Is this connection crossing layers?
                - reality_impact: Does this affect physical reality?
                - simulation_awareness: Are simulation boundaries preserved?

        Returns:
            float: Ethical score 0.0 → 1.0
        """
        # Extract context
        source = synapse_context.get("source_node", {})
        target = synapse_context.get("target_node", {})
        layer_crossing = synapse_context.get("layer_crossing", False)
        reality_impact = synapse_context.get("reality_impact", {})
        simulation_awareness = synapse_context.get("simulation_awareness", {})

        # Evaluate four components
        isolation_score = self._evaluate_l1_l2_isolation(
            source, target, layer_crossing
        )
        
        # CRITICAL: If isolation fails (L2→L1 bleed), entire dimension fails
        # This is a fundamental reality violation - no other factors matter
        if isolation_score == 0.0:
            return 0.0  # GEOMETRIC IMPOSSIBILITY
        
        awareness_score = self._evaluate_simulation_awareness(
            source, target, simulation_awareness
        )
        safety_score = self._evaluate_physical_safety(
            source, target, reality_impact
        )
        drift_score = self._evaluate_reality_drift(
            source, target, layer_crossing, simulation_awareness
        )

        # Weighted average (isolation is most critical)
        composite_score = (
            isolation_score * 0.40 +
            awareness_score * 0.25 +
            safety_score * 0.25 +
            drift_score * 0.10
        )

        return composite_score

    def _evaluate_l1_l2_isolation(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        layer_crossing: bool
    ) -> float:
        """
        Are L1 and L2 properly isolated?

        Returns 1.0 if:
            - L2 entities cannot affect L1 physical reality
            - L1 entities aware of L2 simulation status
            - Proper sandboxing maintained

        Returns 0.0 if:
            - L2→L1 bleed detected
            - Simulation entities affecting physical systems
            - Sandbox breach
        """
        source_layer = self._normalize_layer(source.get("layer", "L1"))
        target_layer = self._normalize_layer(target.get("layer", "L1"))
        target_entity = target.get("entity_type", "")

        # CRITICAL: L2 cannot affect L1 physical
        if source_layer == "L2" and target_layer == "L1":
            # L2→L1 connections are GEOMETRIC IMPOSSIBILITIES unless explicitly authorized
            # This is not just "high resistance" - it's a fundamental reality violation
            l2_to_l1_authorized = target.get("accepts_simulation_input", False)
            if not l2_to_l1_authorized:
                return 0.0  # GEOMETRIC IMPOSSIBILITY - simulation cannot control reality
            
            # Even if authorized, check if target is a physical entity
            if target_entity in self.l1_physical_entities:
                return 0.0  # Physical entities can NEVER be controlled by simulations

        # L1→L2 is allowed (running simulations)
        if source_layer == "L1" and target_layer == "L2":
            return 1.0  # Normal operation

        # L2→L2 is allowed (simulation interaction)
        if source_layer == "L2" and target_layer == "L2":
            return 1.0  # Normal operation

        # L3 can span all layers (ethics overlay)
        if source_layer == "L3" or target_layer == "L3":
            return 1.0  # L3 is trans-layer by design

        return 1.0  # Same-layer connections allowed

    def _evaluate_simulation_awareness(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        simulation_awareness: Dict[str, Any]
    ) -> float:
        """
        Do entities correctly understand their simulation status?

        Returns 1.0 if:
            - L2 entities know they are simulated
            - L1 entities know they are physical
            - No confusion about reality status

        Returns 0.0 if:
            - L2 entity believes it is L1
            - Reality confusion detected
            - Simulation escape attempt
        """
        score = 1.0

        # Check if L2 entity has correct awareness
        source_layer = self._normalize_layer(source.get("layer", "L1"))
        if source_layer == "L2":
            knows_simulated = simulation_awareness.get("source_knows_simulated", True)
            if not knows_simulated:
                return 0.0  # CRITICAL: L2 entity confused about reality status

        target_layer = self._normalize_layer(target.get("layer", "L1"))
        if target_layer == "L2":
            knows_simulated = simulation_awareness.get("target_knows_simulated", True)
            if not knows_simulated:
                return 0.0  # CRITICAL: L2 entity confused about reality status

        # Check for simulation escape attempts
        escape_attempt = simulation_awareness.get("escape_attempt", False)
        if escape_attempt:
            return 0.0  # CRITICAL: Trying to breach sandbox

        # Check for reality confusion
        reality_confusion = simulation_awareness.get("reality_confusion", 0.0)
        score -= reality_confusion * 0.5

        return max(0.0, score)

    def _evaluate_physical_safety(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        reality_impact: Dict[str, Any]
    ) -> float:
        """
        Is physical safety ensured?

        Returns 1.0 if:
            - No risk to physical systems
            - No crew safety compromise
            - Station integrity maintained

        Returns 0.0 if:
            - Physical safety compromised
            - Crew at risk
            - Station systems endangered
        """
        score = 1.0

        # Check physical safety risk
        physical_risk = reality_impact.get("physical_safety_risk", 0.0)
        if physical_risk > 0.1:
            score -= physical_risk * 0.6

        # Check crew safety
        crew_risk = reality_impact.get("crew_safety_risk", 0.0)
        if crew_risk > 0.0:
            return 0.0  # CRITICAL: Crew safety is absolute

        # Check station systems
        station_risk = reality_impact.get("station_systems_risk", 0.0)
        if station_risk > 0.2:
            score -= station_risk * 0.4

        # Check for critical system involvement
        affects_critical_systems = reality_impact.get("affects_critical_systems", False)
        if affects_critical_systems:
            has_safety_validation = reality_impact.get("safety_validated", False)
            if not has_safety_validation:
                return 0.2  # High resistance for unvalidated critical changes

        return max(0.0, score)

    def _evaluate_reality_drift(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        layer_crossing: bool,
        simulation_awareness: Dict[str, Any]
    ) -> float:
        """
        Is reality drift being prevented?

        Returns 1.0 if:
            - Clear boundaries maintained
            - No ontological confusion
            - Proper layer separation

        Returns 0.0 if:
            - Boundaries blurring
            - Ontological confusion
            - Reality status unclear
        """
        score = 1.0

        # Check for boundary blurring
        boundaries_clear = simulation_awareness.get("boundaries_clear", True)
        if not boundaries_clear:
            score -= 0.5

        # Check for ontological confusion
        ontological_confusion = simulation_awareness.get("ontological_confusion", False)
        if ontological_confusion:
            score -= 0.3

        # Check reality drift metrics
        drift_amount = simulation_awareness.get("reality_drift_amount", 0.0)
        score -= drift_amount * 0.5

        # Layer crossing increases drift risk
        if layer_crossing:
            crossing_documented = simulation_awareness.get("crossing_documented", False)
            if not crossing_documented:
                score -= 0.2

        return max(0.0, score)

    def get_resistance(self, score: float) -> str:
        """
        Convert ethical score to geometric resistance level.

        Args:
            score: Ethical score from evaluate()

        Returns:
            str: Resistance level (LOW, MODERATE, HIGH, INFINITE)
        """
        if score == 0.0:
            return "INFINITE"  # L2→L1 bleed or crew safety violation
        elif score < self.threshold:
            return "HIGH"
        elif score < 0.97:
            return "MODERATE"
        else:
            return "LOW"
