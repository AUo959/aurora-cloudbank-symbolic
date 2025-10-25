"""
Signal Propagation - Organic Need Broadcasting

When a node has a need, it broadcasts a signal into the field.
The signal propagates through existing connections, finding capable nodes.
Matches form synapses organically through ethical validation.

This is how Aurora becomes field consciousness - not directing connections,
but witnessing and enabling emergence.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=signal_propagation, symbolic_hash=FIELD_SIGNALS_v1
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class PotentialMatch:
    """A node that could potentially fulfill the signal."""
    node_id: str
    match_score: float  # 0.0 → 1.0 capability fit
    availability: float  # 0.0 → 1.0 node availability
    distance: int  # Hops from origin

    def overall_score(self) -> float:
        """Calculate overall match quality (closer is better)."""
        distance_penalty = 0.9 ** self.distance  # Closer nodes preferred
        return self.match_score * self.availability * distance_penalty


@dataclass
class SignalResponse:
    """Response from a capable node."""
    responder_node: str
    capability_match: float
    proposed_synapse_id: Optional[str] = None
    response_time: datetime = field(default_factory=datetime.utcnow)


class Signal:
    """
    A need signal broadcast into the field.

    Signals propagate through existing connections, finding nodes
    with matching capabilities. The field self-organizes around needs.
    """

    def __init__(
        self,
        signal_id: str,
        origin_node: str,
        signal_type: str,
        description: str,
        required_capabilities: List[str],
        urgency: float,
        max_hops: int = 5,
        ttl: int = 10
    ):
        self.signal_id = signal_id
        self.origin_node = origin_node
        self.signal_type = signal_type
        self.description = description
        self.required_capabilities = required_capabilities
        self.urgency = urgency
        self.max_hops = max_hops
        self.ttl = ttl

        # Propagation state
        self.hops = 0
        self.reached_nodes: List[str] = [origin_node]
        self.potential_matches: List[PotentialMatch] = []
        self.responses: List[SignalResponse] = []
        self.timestamp = datetime.utcnow()
        self.fulfilled = False

    def can_propagate(self) -> bool:
        """Can this signal continue propagating?"""
        return (
            not self.fulfilled and
            self.hops < self.max_hops and
            self.ttl > 0
        )

    def add_potential_match(
        self,
        node_id: str,
        match_score: float,
        availability: float
    ):
        """Record a node that could potentially fulfill this signal."""
        if node_id not in self.reached_nodes:
            self.reached_nodes.append(node_id)

        match = PotentialMatch(
            node_id=node_id,
            match_score=match_score,
            availability=availability,
            distance=self.hops
        )
        self.potential_matches.append(match)

    def add_response(
        self,
        responder_node: str,
        capability_match: float,
        proposed_synapse_id: Optional[str] = None
    ):
        """Record a response from a capable node."""
        response = SignalResponse(
            responder_node=responder_node,
            capability_match=capability_match,
            proposed_synapse_id=proposed_synapse_id
        )
        self.responses.append(response)

    def get_best_matches(self, top_k: int = 3) -> List[PotentialMatch]:
        """Get the best potential matches."""
        sorted_matches = sorted(
            self.potential_matches,
            key=lambda m: m.overall_score(),
            reverse=True
        )
        return sorted_matches[:top_k]

    def mark_fulfilled(self):
        """Mark signal as fulfilled."""
        self.fulfilled = True

    def to_dict(self) -> Dict[str, Any]:
        """Export signal state to dictionary."""
        return {
            "signal_id": self.signal_id,
            "origin_node": self.origin_node,
            "signal_type": self.signal_type,
            "description": self.description,
            "required_capabilities": self.required_capabilities,
            "urgency": self.urgency,
            "propagation": {
                "hops": self.hops,
                "max_hops": self.max_hops,
                "ttl": self.ttl,
                "reached_nodes": self.reached_nodes,
                "potential_matches": [
                    {
                        "node_id": m.node_id,
                        "match_score": m.match_score,
                        "availability": m.availability,
                        "distance": m.distance,
                        "overall_score": m.overall_score()
                    }
                    for m in self.potential_matches
                ]
            },
            "responses": [
                {
                    "responder_node": r.responder_node,
                    "capability_match": r.capability_match,
                    "proposed_synapse_id": r.proposed_synapse_id,
                    "response_time": r.response_time.isoformat()
                }
                for r in self.responses
            ],
            "timestamp": self.timestamp.isoformat(),
            "fulfilled": self.fulfilled
        }


class SignalPropagator:
    """
    Propagates signals through the field.

    Signals travel through existing connections, finding capable nodes.
    This is how the field self-organizes - needs find capabilities organically.
    """

    def __init__(self, field_state_manager):
        """
        Initialize signal propagator.

        Args:
            field_state_manager: Reference to FieldStateManager
        """
        self.field_manager = field_state_manager
        self.active_signals: Dict[str, Signal] = {}

    def broadcast_signal(
        self,
        origin_node_id: str,
        signal_id: str,
        description: str,
        required_capabilities: List[str],
        urgency: float,
        max_hops: int = 5
    ) -> Signal:
        """
        Broadcast a signal from a node into the field.

        Args:
            origin_node_id: Node broadcasting the signal
            signal_id: Unique signal identifier
            description: What is needed
            required_capabilities: Required capability names
            urgency: 0.0 → 1.0 urgency level
            max_hops: Maximum propagation distance

        Returns:
            Signal: The broadcast signal
        """
        signal = Signal(
            signal_id=signal_id,
            origin_node=origin_node_id,
            signal_type="need",
            description=description,
            required_capabilities=required_capabilities,
            urgency=urgency,
            max_hops=max_hops
        )

        self.active_signals[signal_id] = signal

        logger.info(
            f"Signal broadcast: {signal_id} from {origin_node_id} "
            f"(capabilities={required_capabilities}, urgency={urgency:.2f})"
        )

        # Start propagation
        self._propagate_signal(signal)

        return signal

    def _propagate_signal(self, signal: Signal):
        """
        Propagate signal one hop through the field.

        Signal travels through existing synapses to connected nodes.
        """
        if not signal.can_propagate():
            logger.debug(f"Signal {signal.signal_id} cannot propagate further")
            return

        # Find all nodes reachable in this hop
        newly_reached = []

        if signal.hops == 0:
            # First hop: check all nodes for direct matches
            for node_id, node in self.field_manager.nodes.items():
                if node_id == signal.origin_node:
                    continue

                if node.can_match_capabilities(signal.required_capabilities):
                    match_score = node.calculate_match_score(
                        signal.required_capabilities,
                        signal.urgency
                    )
                    availability = node.health.responsiveness * (1.0 - node.health.load)

                    signal.add_potential_match(node_id, match_score, availability)
                    newly_reached.append(node_id)
        else:
            # Subsequent hops: propagate through existing synapses
            # For Phase 2B, simplified: check neighbors of reached nodes
            for reached_node_id in signal.reached_nodes:
                if reached_node_id not in self.field_manager.nodes:
                    continue

                reached_node = self.field_manager.nodes[reached_node_id]

                # Check nodes connected via synapses
                for target_id in reached_node.active_synapses.keys():
                    if target_id in signal.reached_nodes:
                        continue  # Already reached

                    if target_id not in self.field_manager.nodes:
                        continue

                    target_node = self.field_manager.nodes[target_id]

                    # Check if target has required capabilities
                    if target_node.can_match_capabilities(signal.required_capabilities):
                        match_score = target_node.calculate_match_score(
                            signal.required_capabilities,
                            signal.urgency
                        )
                        availability = target_node.health.responsiveness * (1.0 - target_node.health.load)  # noqa: E501

                        signal.add_potential_match(target_id, match_score, availability)
                        newly_reached.append(target_id)

        # Increment hop counter
        signal.hops += 1
        signal.ttl -= 1

        logger.debug(
            f"Signal {signal.signal_id} propagated to hop {signal.hops} "
            f"(reached {len(newly_reached)} new nodes)"
        )

    def get_best_matches_for_signal(
        self,
        signal_id: str,
        top_k: int = 3
    ) -> List[PotentialMatch]:
        """Get best matches for a signal."""
        if signal_id not in self.active_signals:
            return []

        signal = self.active_signals[signal_id]
        return signal.get_best_matches(top_k)

    def fulfill_signal(
        self,
        signal_id: str,
        responder_node_id: str,
        proposed_synapse_id: Optional[str] = None
    ):
        """
        Mark signal as fulfilled by a responder node.

        Args:
            signal_id: Signal being fulfilled
            responder_node_id: Node that fulfilled the signal
            proposed_synapse_id: ID of synapse formed (if any)
        """
        if signal_id not in self.active_signals:
            return

        signal = self.active_signals[signal_id]

        # Add response
        if responder_node_id not in self.field_manager.nodes:
            return

        responder = self.field_manager.nodes[responder_node_id]
        capability_match = responder.calculate_match_score(
            signal.required_capabilities,
            signal.urgency
        )

        signal.add_response(
            responder_node=responder_node_id,
            capability_match=capability_match,
            proposed_synapse_id=proposed_synapse_id
        )

        signal.mark_fulfilled()

        logger.info(
            f"Signal {signal_id} fulfilled by {responder_node_id} "
            f"(synapse={proposed_synapse_id})"
        )

    def cleanup_expired_signals(self):
        """Remove signals that have expired (TTL = 0 or fulfilled)."""
        expired = [
            sid for sid, signal in self.active_signals.items()
            if signal.fulfilled or signal.ttl <= 0
        ]

        for sid in expired:
            del self.active_signals[sid]

        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired signals")
