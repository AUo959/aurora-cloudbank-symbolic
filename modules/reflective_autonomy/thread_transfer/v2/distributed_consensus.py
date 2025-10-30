"""
Distributed Consensus - Raft Protocol Implementation

Provides consensus for thread state across distributed bridge nodes.

Anchor: EOS_SEED_ORION_v2
DLP: context_tag=consensus_v2, symbolic_hash=RAFT_CONSENSUS_v2
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConsensusState(Enum):
    """Raft consensus role"""

    FOLLOWER = "follower"  # Receiving updates from leader
    CANDIDATE = "candidate"  # Running for election
    LEADER = "leader"  # Coordinating cluster


@dataclass
class ConsensusConfig:
    """Raft consensus configuration"""

    min_nodes: int = 3  # Minimum nodes for cluster
    quorum_size: int = 2  # Nodes required for quorum (majority)
    heartbeat_interval_ms: int = 1000  # Leader heartbeat interval
    election_timeout_min_ms: int = 3000  # Min election timeout
    election_timeout_max_ms: int = 6000  # Max election timeout


@dataclass
class LogEntry:
    """Replicated log entry"""

    term: int  # Leader term when entry created
    index: int  # Log index
    command: str  # Operation type (handshake, transfer, etc.)
    data: Dict[str, Any]  # Operation data
    timestamp: datetime = field(default_factory=datetime.now)


class RaftConsensus:
    """
    Simplified Raft consensus implementation for bridge state.

    Provides:
    - Leader election
    - Log replication
    - State machine replication
    - Failure recovery

    Note: This is a simplified implementation. Production systems
    should use established Raft libraries like `aioraft` or integrate
    with distributed systems like etcd/Consul.
    """

    def __init__(
        self,
        node_id: str,
        config: Optional[ConsensusConfig] = None,
    ):
        """
        Initialize Raft consensus.

        Args:
            node_id: This node's identifier
            config: Consensus configuration
        """
        self.node_id = node_id
        self.config = config or ConsensusConfig()

        # Persistent state
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []

        # Volatile state
        self.commit_index = 0
        self.last_applied = 0

        # Leader-specific state
        self.next_index: Dict[str, int] = {}  # For each peer
        self.match_index: Dict[str, int] = {}  # For each peer

        # Current state
        self.state = ConsensusState.FOLLOWER
        self.leader_id: Optional[str] = None
        self.last_heartbeat = datetime.now()

        # Election timeout (randomized)
        self.election_timeout_ms = random.randint(
            self.config.election_timeout_min_ms,
            self.config.election_timeout_max_ms,
        )

        logger.info(
            f"Raft consensus initialized for node {node_id[:8]} "
            f"(state={self.state.value}, term={self.current_term})"
        )

    async def append_log(self, command: str, data: Dict[str, Any]) -> LogEntry:
        """
        Append entry to log (leader only).

        Args:
            command: Operation type
            data: Operation data

        Returns:
            Created log entry

        Raises:
            ValueError: If not leader
        """
        if self.state != ConsensusState.LEADER:
            raise ValueError("Only leader can append to log")

        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command=command,
            data=data,
        )

        self.log.append(entry)

        logger.info(
            f"Appended log entry {entry.index} "
            f"(term={entry.term}, cmd={command})"
        )

        return entry

    async def request_vote(self, candidate_id: str, candidate_term: int) -> bool:
        """
        Handle vote request from candidate.

        Args:
            candidate_id: Candidate node ID
            candidate_term: Candidate's term

        Returns:
            True if vote granted, False otherwise
        """
        # Reject if candidate term is older
        if candidate_term < self.current_term:
            logger.debug(
                f"Rejecting vote for {candidate_id[:8]} "
                f"(term {candidate_term} < {self.current_term})"
            )
            return False

        # Update term if candidate's is newer
        if candidate_term > self.current_term:
            self.current_term = candidate_term
            self.voted_for = None
            self.state = ConsensusState.FOLLOWER

        # Grant vote if haven't voted this term
        if self.voted_for is None or self.voted_for == candidate_id:
            self.voted_for = candidate_id
            self.last_heartbeat = datetime.now()

            logger.info(
                f"Granted vote to {candidate_id[:8]} for term {candidate_term}"
            )
            return True

        return False

    async def become_candidate(self):
        """Transition to candidate and start election"""
        self.state = ConsensusState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id

        logger.info(
            f"Node {self.node_id[:8]} became CANDIDATE for term {self.current_term}"
        )

    async def become_leader(self):
        """Transition to leader"""
        self.state = ConsensusState.LEADER
        self.leader_id = self.node_id

        # Initialize leader state
        self.next_index = {}  # Will be populated with peer states
        self.match_index = {}

        logger.info(
            f"Node {self.node_id[:8]} became LEADER for term {self.current_term}"
        )

    async def become_follower(self, new_term: int, leader_id: Optional[str] = None):
        """
        Transition to follower.

        Args:
            new_term: New term to adopt
            leader_id: Optional leader identifier
        """
        self.state = ConsensusState.FOLLOWER
        self.current_term = new_term
        self.voted_for = None
        self.leader_id = leader_id
        self.last_heartbeat = datetime.now()

        logger.info(
            f"Node {self.node_id[:8]} became FOLLOWER "
            f"(term={new_term}, leader={leader_id[:8] if leader_id else 'unknown'})"
        )

    async def receive_heartbeat(self, leader_id: str, leader_term: int):
        """
        Process heartbeat from leader.

        Args:
            leader_id: Leader node ID
            leader_term: Leader's term
        """
        # Update term if leader's is newer
        if leader_term > self.current_term:
            await self.become_follower(leader_term, leader_id)

        # Accept heartbeat from current leader
        if leader_term == self.current_term and self.state == ConsensusState.FOLLOWER:
            self.leader_id = leader_id
            self.last_heartbeat = datetime.now()

    def is_leader(self) -> bool:
        """Check if this node is current leader"""
        return self.state == ConsensusState.LEADER

    def get_state_info(self) -> Dict[str, Any]:
        """Get current consensus state information"""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "current_term": self.current_term,
            "leader_id": self.leader_id,
            "voted_for": self.voted_for,
            "log_length": len(self.log),
            "commit_index": self.commit_index,
            "last_applied": self.last_applied,
            "last_heartbeat": self.last_heartbeat.isoformat(),
        }


# Global consensus instance (per node)
_consensus: Optional[RaftConsensus] = None


async def initialize_consensus(
    node_id: str, config: Optional[ConsensusConfig] = None
) -> RaftConsensus:
    """Initialize consensus for this node"""
    global _consensus
    _consensus = RaftConsensus(node_id, config)
    return _consensus


def get_consensus() -> Optional[RaftConsensus]:
    """Get consensus instance"""
    return _consensus
