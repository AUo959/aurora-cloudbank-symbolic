"""
Multi-Repository Capsule Schema

Extends the existing capsule structure to support cross-repo collaboration
with linked repositories, shared anchors, and agent roster tracking.

Thread: T1→COLLAB→CAPSULE_SCHEMA
DLP: context_tag=collab_capsule_schema
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class CapsuleVersion(Enum):
    """Capsule schema versions for backward compatibility."""
    V1_0 = "1.0"  # Original single-repo capsule
    V2_0 = "2.0"  # Multi-repo with linked_repos
    CURRENT = "2.0"


class AgentRole(Enum):
    """Agent roles in cross-repo collaboration."""
    R2 = "R-2"  # Functionality and integration agent
    COPILOT = "Copilot"  # Code generation and assistance
    AURORA = "Aurora"  # Core orchestration
    CUSTOM = "Custom"  # User-defined agents


@dataclass
class LinkedRepository:
    """Information about a linked repository."""
    repo_url: str
    owner: str
    repo_name: str
    access_token_name: Optional[str] = None  # Name/reference, not actual token
    narrative_timestamp: Optional[str] = None
    accepted_agents: List[str] = field(default_factory=list)
    trust_level: str = "pending"  # pending, trusted, verified
    last_sync: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repo_url": self.repo_url,
            "owner": self.owner,
            "repo_name": self.repo_name,
            "access_token_name": self.access_token_name,
            "narrative_timestamp": self.narrative_timestamp,
            "accepted_agents": self.accepted_agents,
            "trust_level": self.trust_level,
            "last_sync": self.last_sync,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinkedRepository":
        """Create from dictionary."""
        return cls(
            repo_url=data["repo_url"],
            owner=data["owner"],
            repo_name=data["repo_name"],
            access_token_name=data.get("access_token_name"),
            narrative_timestamp=data.get("narrative_timestamp"),
            accepted_agents=data.get("accepted_agents", []),
            trust_level=data.get("trust_level", "pending"),
            last_sync=data.get("last_sync"),
            metadata=data.get("metadata", {})
        )


@dataclass
class SharedAnchor:
    """Shared symbolic anchor for cross-repo trust chains."""
    anchor_id: str
    anchor_name: str
    anchor_seed: str
    provenance_hash: str
    created_at: str
    verified_repos: List[str] = field(default_factory=list)
    signatures: Dict[str, str] = field(default_factory=dict)  # repo_id -> signature
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anchor_id": self.anchor_id,
            "anchor_name": self.anchor_name,
            "anchor_seed": self.anchor_seed,
            "provenance_hash": self.provenance_hash,
            "created_at": self.created_at,
            "verified_repos": self.verified_repos,
            "signatures": self.signatures,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharedAnchor":
        """Create from dictionary."""
        return cls(
            anchor_id=data["anchor_id"],
            anchor_name=data["anchor_name"],
            anchor_seed=data["anchor_seed"],
            provenance_hash=data["provenance_hash"],
            created_at=data["created_at"],
            verified_repos=data.get("verified_repos", []),
            signatures=data.get("signatures", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class MultiRepoCapsule:
    """
    Multi-repository capsule for cross-repo collaboration.
    
    Extends the original capsule with linked_repos and shared_anchors.
    """
    # Core identification
    capsule_id: str
    capsule_version: str = CapsuleVersion.CURRENT.value
    title: str = ""
    
    # Original capsule fields
    anchor_seed: str = "EOS_SEED_ORION"
    ethics_protocol: str = "Picard_Delta_3"
    threadcore_status: str = "active"
    symbolic_drift: float = 0.0
    
    # Multi-repo extensions
    linked_repos: List[LinkedRepository] = field(default_factory=list)
    shared_anchors: List[SharedAnchor] = field(default_factory=list)
    
    # Agent roster
    agent_roster: List[str] = field(default_factory=list)
    active_agents: Set[str] = field(default_factory=set)
    
    # Timestamps and status
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Metadata
    glyph_chain: List[Dict[str, str]] = field(default_factory=list)
    augmentations: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_linked_repo(self, linked_repo: LinkedRepository):
        """Add a linked repository."""
        self.linked_repos.append(linked_repo)
        self.last_modified = datetime.now().isoformat()
    
    def add_shared_anchor(self, anchor: SharedAnchor):
        """Add a shared anchor."""
        self.shared_anchors.append(anchor)
        self.last_modified = datetime.now().isoformat()
    
    def add_agent(self, agent_name: str):
        """Add an agent to the roster."""
        if agent_name not in self.agent_roster:
            self.agent_roster.append(agent_name)
            self.active_agents.add(agent_name)
            self.last_modified = datetime.now().isoformat()
    
    def verify_anchor_integrity(self) -> bool:
        """Verify integrity of all shared anchors."""
        for anchor in self.shared_anchors:
            # Recompute hash
            anchor_data = f"{anchor.anchor_name}:{anchor.anchor_seed}:{anchor.created_at}"
            computed_hash = hashlib.sha256(anchor_data.encode()).hexdigest()
            
            if anchor.provenance_hash != computed_hash:
                return False
        
        return True
    
    def verify_ethics_compliance(self) -> bool:
        """Verify ethics protocol compliance."""
        # Check ethics protocol is set
        if not self.ethics_protocol:
            return False
        
        # Verify all linked repos have accepted agents with ethics compliance
        for repo in self.linked_repos:
            if repo.trust_level == "pending":
                return False
        
        return True
    
    def compute_signature(self) -> str:
        """Compute capsule signature for verification."""
        capsule_core = {
            "capsule_id": self.capsule_id,
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "created_at": self.created_at
        }
        signature_data = json.dumps(capsule_core, sort_keys=True)
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert capsule to dictionary."""
        return {
            "capsule_id": self.capsule_id,
            "capsule_version": self.capsule_version,
            "title": self.title,
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "threadcore_status": self.threadcore_status,
            "symbolic_drift": self.symbolic_drift,
            "linked_repos": [repo.to_dict() for repo in self.linked_repos],
            "shared_anchors": [anchor.to_dict() for anchor in self.shared_anchors],
            "agent_roster": self.agent_roster,
            "active_agents": list(self.active_agents),
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "glyph_chain": self.glyph_chain,
            "augmentations": self.augmentations,
            "metadata": self.metadata,
            "signature": self.compute_signature()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiRepoCapsule":
        """Create capsule from dictionary."""
        capsule = cls(
            capsule_id=data["capsule_id"],
            capsule_version=data.get("capsule_version", CapsuleVersion.V1_0.value),
            title=data.get("title", ""),
            anchor_seed=data.get("anchor_seed", "EOS_SEED_ORION"),
            ethics_protocol=data.get("ethics_protocol", "Picard_Delta_3"),
            threadcore_status=data.get("threadcore_status", "active"),
            symbolic_drift=data.get("symbolic_drift", 0.0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_modified=data.get("last_modified", datetime.now().isoformat()),
            glyph_chain=data.get("glyph_chain", []),
            augmentations=data.get("augmentations", {}),
            metadata=data.get("metadata", {})
        )
        
        # Parse linked repos
        for repo_data in data.get("linked_repos", []):
            capsule.linked_repos.append(LinkedRepository.from_dict(repo_data))
        
        # Parse shared anchors
        for anchor_data in data.get("shared_anchors", []):
            capsule.shared_anchors.append(SharedAnchor.from_dict(anchor_data))
        
        # Parse agent roster
        capsule.agent_roster = data.get("agent_roster", [])
        capsule.active_agents = set(data.get("active_agents", []))
        
        return capsule
    
    def to_json(self, indent: int = 2) -> str:
        """Convert capsule to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> "MultiRepoCapsule":
        """Create capsule from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


def create_shared_anchor(
    anchor_name: str,
    anchor_seed: str,
    metadata: Optional[Dict[str, Any]] = None
) -> SharedAnchor:
    """
    Create a new shared anchor for cross-repo trust chains.
    
    Args:
        anchor_name: Name of the anchor
        anchor_seed: Seed value for the anchor
        metadata: Optional metadata
        
    Returns:
        SharedAnchor instance
    """
    created_at = datetime.now().isoformat()
    anchor_id = f"anchor_{int(time.time() * 1000)}"
    
    # Compute provenance hash
    anchor_data = f"{anchor_name}:{anchor_seed}:{created_at}"
    provenance_hash = hashlib.sha256(anchor_data.encode()).hexdigest()
    
    return SharedAnchor(
        anchor_id=anchor_id,
        anchor_name=anchor_name,
        anchor_seed=anchor_seed,
        provenance_hash=provenance_hash,
        created_at=created_at,
        metadata=metadata or {}
    )


def validate_capsule_compatibility(
    capsule1: MultiRepoCapsule,
    capsule2: MultiRepoCapsule
) -> Dict[str, Any]:
    """
    Validate compatibility between two capsules for cross-repo exchange.
    
    Args:
        capsule1: First capsule
        capsule2: Second capsule
        
    Returns:
        Validation result dict
    """
    result = {
        "compatible": True,
        "checks": [],
        "warnings": [],
        "errors": []
    }
    
    # Check version compatibility
    if capsule1.capsule_version != capsule2.capsule_version:
        result["warnings"].append(
            f"Version mismatch: {capsule1.capsule_version} vs {capsule2.capsule_version}"
        )
    
    # Check anchor seed compatibility
    if capsule1.anchor_seed != capsule2.anchor_seed:
        result["errors"].append(
            f"Anchor seed mismatch: {capsule1.anchor_seed} vs {capsule2.anchor_seed}"
        )
        result["compatible"] = False
    
    # Check ethics protocol
    if capsule1.ethics_protocol != capsule2.ethics_protocol:
        result["warnings"].append(
            f"Ethics protocol differs: {capsule1.ethics_protocol} vs {capsule2.ethics_protocol}"
        )
    
    # Check symbolic drift
    combined_drift = capsule1.symbolic_drift + capsule2.symbolic_drift
    if combined_drift > 0.002:  # 0.2% threshold
        result["errors"].append(
            f"Combined drift too high: {combined_drift:.4f} (>0.002)"
        )
        result["compatible"] = False
    
    result["checks"].extend([
        {"check": "version_compatibility", "passed": len(result["errors"]) == 0},
        {"check": "anchor_seed_match", "passed": capsule1.anchor_seed == capsule2.anchor_seed},
        {"check": "ethics_alignment", "passed": capsule1.ethics_protocol == capsule2.ethics_protocol},
        {"check": "drift_acceptable", "passed": combined_drift <= 0.002}
    ])
    
    return result
