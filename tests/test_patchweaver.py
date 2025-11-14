"""
Tests for PatchWeaver - Ethics-gated state patching engine

Tests cover:
- Set-only patches
- Delete-only patches
- Mixed set+delete patches
- Ethics blocking scenarios
- Idempotent operations
- Hash verification
"""

import pytest
from src.aurora.patching.patchweaver import PatchWeaver, PatchResult
from src.core.native_dlp_export import NativeDLPTracker
from src.monitoring.ethics_engine import (
    EthicsEngine,
    EthicsRule,
    RuleCategory,
    ViolationSeverity
)


class TestPatchWeaver:
    """Test suite for PatchWeaver state patching"""
    
    @pytest.fixture
    def initial_state(self):
        """Provide initial state for testing"""
        return {
            "config": {
                "setting1": "value1",
                "setting2": "value2"
            },
            "data": {
                "item1": 100,
                "item2": 200
            },
            "deprecated_key": "old_value"
        }
    
    @pytest.fixture
    def state_container(self, initial_state):
        """Provide a mutable state container for testing"""
        return {"state": initial_state.copy()}
    
    @pytest.fixture
    def permissive_ethics(self):
        """Provide ethics engine that allows all operations"""
        engine = EthicsEngine()
        # Clear default rules for permissive mode
        engine.rules.clear()
        return engine
    
    @pytest.fixture
    def blocking_ethics(self):
        """Provide ethics engine that blocks state patches"""
        engine = EthicsEngine()
        # Add rule that blocks state patches
        blocking_rule = EthicsRule(
            id="TEST_BLOCK_001",
            name="Block State Patches",
            description="Test rule that blocks all state patches",
            category=RuleCategory.SAFETY,
            severity=ViolationSeverity.CRITICAL,
            auto_block=True,
            conditions=["state_patch"]
        )
        engine.rules.clear()
        engine.rules[blocking_rule.id] = blocking_rule
        return engine
    
    @pytest.fixture
    def patchweaver(self, state_container, permissive_ethics):
        """Provide PatchWeaver instance with permissive ethics"""
        return PatchWeaver(
            load_state=lambda: state_container["state"],
            save_state=lambda s: state_container.update({"state": s}),
            ethics_gate=permissive_ethics
        )
    
    @pytest.fixture
    def blocking_patchweaver(self, state_container, blocking_ethics):
        """Provide PatchWeaver instance with blocking ethics"""
        return PatchWeaver(
            load_state=lambda: state_container["state"],
            save_state=lambda s: state_container.update({"state": s}),
            ethics_gate=blocking_ethics
        )
    
    def test_set_only_patch(self, patchweaver, state_container):
        """Test applying set-only patch"""
        patch = {
            "set": {
                "config/setting1": "new_value1",
                "config/new_setting": "new_value"
            }
        }
        
        context = {"agent_id": "test_agent"}
        result = patchweaver.apply_patch(patch, context)
        
        assert result.applied is True
        assert result.reason == "ok"
        assert result.before_hash != result.after_hash
        assert len(result.modified_paths) == 2
        assert "set:config/setting1" in result.modified_paths
        assert "set:config/new_setting" in result.modified_paths
        
        # Verify state was updated
        state = state_container["state"]
        assert state["config"]["setting1"] == "new_value1"
        assert state["config"]["new_setting"] == "new_value"
    
    def test_delete_only_patch(self, patchweaver, state_container):
        """Test applying delete-only patch"""
        patch = {
            "delete": [
                "deprecated_key",
                "data/item1"
            ]
        }
        
        context = {"agent_id": "test_agent"}
        result = patchweaver.apply_patch(patch, context)
        
        assert result.applied is True
        assert result.reason == "ok"
        assert result.before_hash != result.after_hash
        assert len(result.modified_paths) == 2
        assert "delete:deprecated_key" in result.modified_paths
        assert "delete:data/item1" in result.modified_paths
        
        # Verify keys were deleted
        state = state_container["state"]
        assert "deprecated_key" not in state
        assert "item1" not in state["data"]
        assert "item2" in state["data"]  # Other keys remain
    
    def test_mixed_set_delete_patch(self, patchweaver, state_container):
        """Test applying mixed set+delete patch"""
        patch = {
            "set": {
                "config/setting2": "updated_value",
                "new_top_level": "top_value"
            },
            "delete": [
                "deprecated_key"
            ]
        }
        
        context = {"agent_id": "test_agent"}
        result = patchweaver.apply_patch(patch, context)
        
        assert result.applied is True
        assert len(result.modified_paths) == 3
        
        # Verify changes
        state = state_container["state"]
        assert state["config"]["setting2"] == "updated_value"
        assert state["new_top_level"] == "top_value"
        assert "deprecated_key" not in state
    
    def test_ethics_blocked_patch(self, blocking_patchweaver, state_container, initial_state):
        """Test that ethics gate blocks patches when configured"""
        patch = {
            "set": {
                "config/setting1": "should_not_apply"
            }
        }
        
        context = {
            "agent_id": "test_agent",
            "state_patch": True  # Triggers blocking rule
        }
        result = blocking_patchweaver.apply_patch(patch, context)
        
        assert result.applied is False
        assert "Ethics gate blocked" in result.reason
        assert result.before_hash == result.after_hash  # State unchanged
        
        # Verify state was NOT modified
        state = state_container["state"]
        assert state == initial_state
    
    def test_idempotent_deletion(self, patchweaver, state_container):
        """Test that deleting non-existent keys doesn't error"""
        patch = {
            "delete": [
                "nonexistent_key",
                "also/does/not/exist"
            ]
        }
        
        context = {"agent_id": "test_agent"}
        result = patchweaver.apply_patch(patch, context)
        
        # Should succeed even though keys don't exist
        assert result.applied is True
        assert result.reason == "ok"
        # No paths modified since keys didn't exist
        assert len(result.modified_paths) == 0
    
    def test_nested_path_creation(self, patchweaver, state_container):
        """Test that set creates intermediate dicts as needed"""
        patch = {
            "set": {
                "deeply/nested/new/path": "value"
            }
        }
        
        context = {"agent_id": "test_agent"}
        result = patchweaver.apply_patch(patch, context)
        
        assert result.applied is True
        
        # Verify nested structure was created
        state = state_container["state"]
        assert state["deeply"]["nested"]["new"]["path"] == "value"
    
    def test_hash_verification(self, patchweaver, state_container):
        """Test state hash verification"""
        # Get initial hash
        initial_state = state_container["state"]
        initial_hash = patchweaver._compute_hash(initial_state)
        
        # Verify current state matches
        assert patchweaver.verify_state_hash(initial_hash) is True
        
        # Apply patch
        patch = {"set": {"config/setting1": "modified"}}
        result = patchweaver.apply_patch(patch, {"agent_id": "test"})
        
        # Old hash should no longer match
        assert patchweaver.verify_state_hash(initial_hash) is False
        
        # New hash should match
        assert patchweaver.verify_state_hash(result.after_hash) is True
    
    def test_dlp_tagging(self, patchweaver):
        """Test that patches create proper DLP tags"""
        patch = {"set": {"test_key": "test_value"}}
        context = {"agent_id": "test_agent", "context_tag": "test_operation"}
        
        result = patchweaver.apply_patch(patch, context)
        assert result.applied is True
        
        # Check DLP tags were created
        assert len(patchweaver.dlp_tracker.tags) > 0
        
        # Find the state_patch tag
        patch_tags = [
            tag for tag in patchweaver.dlp_tracker.tags.values()
            if tag.operation == "state_patch"
        ]
        assert len(patch_tags) > 0
        
        tag = patch_tags[-1]  # Get most recent
        
        # Verify anchor protocols
        assert "EOS_SEED_ORION" in tag.anchor_protocols
        assert "Picard_Delta_3" in tag.anchor_protocols
        assert "PATCHWEAVER_CORE" in tag.anchor_protocols
        
        # Verify T1/SRB anchors
        assert "T1" in tag.t1_srb_anchors
        assert "SRB" in tag.t1_srb_anchors
        
        # Verify symbolic patterns
        assert "patch_metadata" in tag.symbolic_patterns
        metadata = tag.symbolic_patterns["patch_metadata"]
        assert "before_hash" in metadata
        assert "after_hash" in metadata
        assert "modified_paths" in metadata
    
    def test_patch_history(self, patchweaver):
        """Test retrieving patch history"""
        # Apply multiple patches
        patch1 = {"set": {"key1": "value1"}}
        patch2 = {"set": {"key2": "value2"}}
        
        patchweaver.apply_patch(patch1, {"agent_id": "test"})
        patchweaver.apply_patch(patch2, {"agent_id": "test"})
        
        # Get history
        history = patchweaver.get_patch_history()
        assert len(history) >= 2
        
        # Verify history entries
        for entry in history:
            assert entry["operation"] == "state_patch"
            assert "timestamp" in entry
            assert "data_hash" in entry
    
    def test_result_serialization(self, patchweaver):
        """Test that PatchResult can be serialized to dict/JSON"""
        patch = {"set": {"test": "value"}}
        result = patchweaver.apply_patch(patch, {"agent_id": "test"})
        
        # Should convert to dict without errors
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "applied" in result_dict
        assert "reason" in result_dict
        assert "before_hash" in result_dict
        assert "after_hash" in result_dict
        assert "modified_paths" in result_dict
        assert "timestamp" in result_dict
    
    def test_empty_patch(self, patchweaver):
        """Test applying empty patch"""
        patch = {}
        result = patchweaver.apply_patch(patch, {"agent_id": "test"})
        
        # Should succeed but make no changes
        assert result.applied is True
        assert result.before_hash == result.after_hash
        assert len(result.modified_paths) == 0
    
    def test_set_overwrites_non_dict(self, patchweaver, state_container):
        """Test that set can overwrite non-dict intermediate values"""
        # Set up state with a non-dict value
        state_container["state"]["scalar_key"] = "scalar_value"
        
        # Try to set a nested path under the scalar
        patch = {"set": {"scalar_key/nested": "new_value"}}
        result = patchweaver.apply_patch(patch, {"agent_id": "test"})
        
        assert result.applied is True
        
        # Scalar should be replaced with dict
        state = state_container["state"]
        assert isinstance(state["scalar_key"], dict)
        assert state["scalar_key"]["nested"] == "new_value"


@pytest.mark.unit
class TestPatchWeaverUnit:
    """Fast unit tests for PatchWeaver helpers"""
    
    def test_compute_hash_deterministic(self):
        """Test that hash computation is deterministic"""
        state1 = {"a": 1, "b": 2, "c": 3}
        state2 = {"c": 3, "a": 1, "b": 2}  # Different order
        
        # Create minimal PatchWeaver for hash testing
        weaver = PatchWeaver(
            load_state=lambda: {},
            save_state=lambda s: None,
            ethics_gate=EthicsEngine()
        )
        
        hash1 = weaver._compute_hash(state1)
        hash2 = weaver._compute_hash(state2)
        
        # Hashes should be identical despite different key order
        assert hash1 == hash2
    
    def test_set_path_simple(self):
        """Test simple path setting"""
        state = {}
        weaver = PatchWeaver(
            load_state=lambda: state,
            save_state=lambda s: None,
            ethics_gate=EthicsEngine()
        )
        
        weaver._set_path(state, "key", "value")
        assert state["key"] == "value"
    
    def test_set_path_nested(self):
        """Test nested path setting"""
        state = {}
        weaver = PatchWeaver(
            load_state=lambda: state,
            save_state=lambda s: None,
            ethics_gate=EthicsEngine()
        )
        
        weaver._set_path(state, "a/b/c", "value")
        assert state["a"]["b"]["c"] == "value"
    
    def test_delete_path_simple(self):
        """Test simple path deletion"""
        state = {"key": "value"}
        weaver = PatchWeaver(
            load_state=lambda: state,
            save_state=lambda s: None,
            ethics_gate=EthicsEngine()
        )
        
        result = weaver._delete_path(state, "key")
        assert result is True
        assert "key" not in state
    
    def test_delete_path_nested(self):
        """Test nested path deletion"""
        state = {"a": {"b": {"c": "value"}}}
        weaver = PatchWeaver(
            load_state=lambda: state,
            save_state=lambda s: None,
            ethics_gate=EthicsEngine()
        )
        
        result = weaver._delete_path(state, "a/b/c")
        assert result is True
        assert "c" not in state["a"]["b"]
    
    def test_delete_path_nonexistent(self):
        """Test deleting non-existent path"""
        state = {"a": {}}
        weaver = PatchWeaver(
            load_state=lambda: state,
            save_state=lambda s: None,
            ethics_gate=EthicsEngine()
        )
        
        result = weaver._delete_path(state, "a/b/c")
        assert result is False  # Path didn't exist
