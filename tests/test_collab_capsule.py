"""
Tests for Cross-Repository Collaboration Module

Thread: T1→COLLAB→TESTS
DLP: context_tag=collab_tests
"""

import json
import pytest
from datetime import datetime

from src.collab.capsule_schema import (
    MultiRepoCapsule,
    LinkedRepository,
    SharedAnchor,
    create_shared_anchor,
    validate_capsule_compatibility,
    CapsuleVersion
)


class TestMultiRepoCapsule:
    """Test multi-repo capsule functionality."""
    
    def test_create_capsule(self):
        """Test creating a basic multi-repo capsule."""
        capsule = MultiRepoCapsule(
            capsule_id="TEST_CAPSULE_001",
            title="Test Capsule",
            anchor_seed="EOS_SEED_ORION",
            ethics_protocol="Picard_Delta_3"
        )
        
        assert capsule.capsule_id == "TEST_CAPSULE_001"
        assert capsule.anchor_seed == "EOS_SEED_ORION"
        assert capsule.ethics_protocol == "Picard_Delta_3"
        assert capsule.capsule_version == CapsuleVersion.CURRENT.value
    
    def test_add_linked_repo(self):
        """Test adding a linked repository."""
        capsule = MultiRepoCapsule(capsule_id="TEST_001")
        
        linked_repo = LinkedRepository(
            repo_url="https://github.com/test/repo",
            owner="test",
            repo_name="repo",
            accepted_agents=["R-2", "Copilot"],
            trust_level="trusted"
        )
        
        capsule.add_linked_repo(linked_repo)
        
        assert len(capsule.linked_repos) == 1
        assert capsule.linked_repos[0].owner == "test"
        assert capsule.linked_repos[0].repo_name == "repo"
    
    def test_add_shared_anchor(self):
        """Test adding a shared anchor."""
        capsule = MultiRepoCapsule(capsule_id="TEST_001")
        
        anchor = create_shared_anchor(
            anchor_name="TEST_ANCHOR",
            anchor_seed="EOS_SEED_ORION"
        )
        
        capsule.add_shared_anchor(anchor)
        
        assert len(capsule.shared_anchors) == 1
        assert capsule.shared_anchors[0].anchor_name == "TEST_ANCHOR"
    
    def test_verify_anchor_integrity(self):
        """Test anchor integrity verification."""
        capsule = MultiRepoCapsule(capsule_id="TEST_001")
        
        anchor = create_shared_anchor(
            anchor_name="TEST_ANCHOR",
            anchor_seed="EOS_SEED_ORION"
        )
        
        capsule.add_shared_anchor(anchor)
        
        # Should pass with valid anchor
        assert capsule.verify_anchor_integrity() is True
        
        # Corrupt the hash
        capsule.shared_anchors[0].provenance_hash = "invalid_hash"
        
        # Should fail with invalid anchor
        assert capsule.verify_anchor_integrity() is False
    
    def test_compute_signature(self):
        """Test capsule signature computation."""
        capsule = MultiRepoCapsule(
            capsule_id="TEST_001",
            anchor_seed="EOS_SEED_ORION",
            ethics_protocol="Picard_Delta_3"
        )
        
        signature1 = capsule.compute_signature()
        assert len(signature1) == 64  # SHA-256 hash length
        
        # Same capsule should produce same signature
        signature2 = capsule.compute_signature()
        assert signature1 == signature2
        
        # Modified capsule should produce different signature
        capsule.capsule_id = "TEST_002"
        signature3 = capsule.compute_signature()
        assert signature1 != signature3
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        capsule = MultiRepoCapsule(
            capsule_id="TEST_001",
            title="Test Capsule",
            anchor_seed="EOS_SEED_ORION",
            agent_roster=["R-2", "Copilot"]
        )
        
        # Add linked repo
        linked_repo = LinkedRepository(
            repo_url="https://github.com/test/repo",
            owner="test",
            repo_name="repo"
        )
        capsule.add_linked_repo(linked_repo)
        
        # Add shared anchor
        anchor = create_shared_anchor("TEST_ANCHOR", "EOS_SEED_ORION")
        capsule.add_shared_anchor(anchor)
        
        # Serialize
        capsule_dict = capsule.to_dict()
        assert isinstance(capsule_dict, dict)
        assert capsule_dict["capsule_id"] == "TEST_001"
        
        # Deserialize
        restored_capsule = MultiRepoCapsule.from_dict(capsule_dict)
        assert restored_capsule.capsule_id == capsule.capsule_id
        assert restored_capsule.title == capsule.title
        assert len(restored_capsule.linked_repos) == 1
        assert len(restored_capsule.shared_anchors) == 1
    
    def test_to_json_and_from_json(self):
        """Test JSON serialization."""
        capsule = MultiRepoCapsule(
            capsule_id="TEST_001",
            title="Test Capsule"
        )
        
        # Serialize to JSON
        json_str = capsule.to_json()
        assert isinstance(json_str, str)
        
        # Parse JSON
        parsed = json.loads(json_str)
        assert parsed["capsule_id"] == "TEST_001"
        
        # Deserialize from JSON
        restored = MultiRepoCapsule.from_json(json_str)
        assert restored.capsule_id == capsule.capsule_id


class TestCapsuleCompatibility:
    """Test capsule compatibility validation."""
    
    def test_compatible_capsules(self):
        """Test validation of compatible capsules."""
        capsule1 = MultiRepoCapsule(
            capsule_id="CAPSULE_1",
            anchor_seed="EOS_SEED_ORION",
            ethics_protocol="Picard_Delta_3",
            symbolic_drift=0.0001
        )
        
        capsule2 = MultiRepoCapsule(
            capsule_id="CAPSULE_2",
            anchor_seed="EOS_SEED_ORION",
            ethics_protocol="Picard_Delta_3",
            symbolic_drift=0.0001
        )
        
        result = validate_capsule_compatibility(capsule1, capsule2)
        
        assert result["compatible"] is True
        assert len(result["errors"]) == 0
    
    def test_incompatible_anchor_seed(self):
        """Test validation with incompatible anchor seeds."""
        capsule1 = MultiRepoCapsule(
            capsule_id="CAPSULE_1",
            anchor_seed="EOS_SEED_ORION"
        )
        
        capsule2 = MultiRepoCapsule(
            capsule_id="CAPSULE_2",
            anchor_seed="DIFFERENT_ANCHOR"
        )
        
        result = validate_capsule_compatibility(capsule1, capsule2)
        
        assert result["compatible"] is False
        assert len(result["errors"]) > 0
        assert any("Anchor seed mismatch" in err for err in result["errors"])
    
    def test_high_drift(self):
        """Test validation with high symbolic drift."""
        capsule1 = MultiRepoCapsule(
            capsule_id="CAPSULE_1",
            symbolic_drift=0.0015
        )
        
        capsule2 = MultiRepoCapsule(
            capsule_id="CAPSULE_2",
            symbolic_drift=0.0015
        )
        
        result = validate_capsule_compatibility(capsule1, capsule2)
        
        # Combined drift = 0.003, which exceeds 0.002 threshold
        assert result["compatible"] is False
        assert any("drift too high" in err for err in result["errors"])


class TestSharedAnchor:
    """Test shared anchor functionality."""
    
    def test_create_shared_anchor(self):
        """Test creating a shared anchor."""
        anchor = create_shared_anchor(
            anchor_name="TEST_ANCHOR",
            anchor_seed="EOS_SEED_ORION",
            metadata={"test": "value"}
        )
        
        assert anchor.anchor_name == "TEST_ANCHOR"
        assert anchor.anchor_seed == "EOS_SEED_ORION"
        assert "anchor_" in anchor.anchor_id
        assert len(anchor.provenance_hash) == 64  # SHA-256
        assert anchor.metadata["test"] == "value"
    
    def test_anchor_serialization(self):
        """Test anchor serialization."""
        anchor = create_shared_anchor(
            anchor_name="TEST_ANCHOR",
            anchor_seed="EOS_SEED_ORION"
        )
        
        # Serialize
        anchor_dict = anchor.to_dict()
        assert isinstance(anchor_dict, dict)
        assert anchor_dict["anchor_name"] == "TEST_ANCHOR"
        
        # Deserialize
        restored = SharedAnchor.from_dict(anchor_dict)
        assert restored.anchor_name == anchor.anchor_name
        assert restored.provenance_hash == anchor.provenance_hash


class TestLinkedRepository:
    """Test linked repository functionality."""
    
    def test_create_linked_repo(self):
        """Test creating a linked repository."""
        repo = LinkedRepository(
            repo_url="https://github.com/test/repo",
            owner="test",
            repo_name="repo",
            accepted_agents=["R-2", "Copilot"],
            trust_level="trusted"
        )
        
        assert repo.owner == "test"
        assert repo.repo_name == "repo"
        assert len(repo.accepted_agents) == 2
        assert repo.trust_level == "trusted"
    
    def test_repo_serialization(self):
        """Test repository serialization."""
        repo = LinkedRepository(
            repo_url="https://github.com/test/repo",
            owner="test",
            repo_name="repo"
        )
        
        # Serialize
        repo_dict = repo.to_dict()
        assert isinstance(repo_dict, dict)
        assert repo_dict["owner"] == "test"
        
        # Deserialize
        restored = LinkedRepository.from_dict(repo_dict)
        assert restored.owner == repo.owner
        assert restored.repo_name == repo.repo_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
