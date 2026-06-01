"""
PatchWeaver - Controlled, DLP-aware, ethics-gated state patching engine

This module provides controlled state patching with:
- Hash-sealed state before/after for traceability
- DLP tagging with Aurora anchors (T1/SRB, EOS_SEED_ORION, Picard_Delta_3)
- Ethics gate integration for safety validation
- Flexible state management via injected load/save callables
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable

from src.core.native_dlp_export import NativeDLPTag, NativeDLPTracker
from src.monitoring.ethics_engine import EthicsEngine, ActionContext

logger = logging.getLogger(__name__)


@dataclass
class PatchResult:
    """Result of a patch operation"""
    applied: bool
    reason: str
    before_hash: str
    after_hash: str
    modified_paths: List[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.modified_paths is None:
            self.modified_paths = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class PatchWeaver:
    """
    PatchWeaver - Ethics-gated state patching with DLP tracking
    
    Enables fine-grained modifications to simulation or narrative state (L2/L3)
    while preserving Aurora/GUMAS continuity, anchor, and ethics guarantees.
    
    Features:
    - Structured patch operations (set/delete on nested dicts)
    - Hash-seal state before and after for recovery
    - DLP tagging with full anchor protocols
    - Ethics gate validation before applying patches
    - Flexible state backends via dependency injection
    
    Usage:
        # Create with injected state backend and ethics gate
        weaver = PatchWeaver(
            load_state=lambda: {"key": "value"},
            save_state=lambda s: None,
            ethics_gate=ethics_engine
        )
        
        # Apply patch with context
        patch = {"set": {"path/to/key": "new_value"}, "delete": ["old/key"]}
        result = weaver.apply_patch(patch, context={"agent_id": "admin"})
    """
    
    def __init__(
        self,
        load_state: Callable[[], Dict[str, Any]],
        save_state: Callable[[Dict[str, Any]], None],
        ethics_gate: EthicsEngine,
        dlp_tracker: Optional[NativeDLPTracker] = None
    ):
        """
        Initialize PatchWeaver
        
        Args:
            load_state: Callable that returns current state dict
            save_state: Callable that persists state dict
            ethics_gate: EthicsEngine instance for validation
            dlp_tracker: Optional DLP tracker (creates new one if not provided)
        """
        self.load_state = load_state
        self.save_state = save_state
        self.ethics_gate = ethics_gate
        self.dlp_tracker = dlp_tracker or NativeDLPTracker()
        self.patch_counter = 0
        
        logger.info("PatchWeaver initialized with ethics gate and DLP tracking")
    
    def apply_patch(
        self,
        patch: Dict[str, Any],
        context: Dict[str, Any]
    ) -> PatchResult:
        """
        Apply a structured patch to state with ethics validation
        
        Patch format:
            {
                "set": {
                    "path/to/key": value,
                    "another/nested/key": value2
                },
                "delete": [
                    "path/to/remove",
                    "another/key"
                ]
            }
        
        Args:
            patch: Structured patch with 'set' and/or 'delete' operations
            context: Context dict with at least 'agent_id' for ethics evaluation
        
        Returns:
            PatchResult with applied status, hashes, and metadata
        """
        self.patch_counter += 1
        operation_id = f"patch_{self.patch_counter:06d}_{int(time.time() * 1000)}"
        
        logger.info("PatchWeaver operation %s starting", operation_id)
        
        # Step 1: Load current state
        try:
            state = self.load_state()
        except Exception as e:
            logger.error("Failed to load state: %s", e)
            return PatchResult(
                applied=False,
                reason=f"State load failed: {str(e)}",
                before_hash="",
                after_hash=""
            )
        
        # Step 2: Compute before_hash
        before_hash = self._compute_hash(state)
        
        # Step 3: Ethics gate evaluation
        action_context = ActionContext(
            agent_id=context.get("agent_id", "unknown"),
            action_type="state_patch",
            parameters={
                "patch": patch,
                "operation_id": operation_id,
                **context
            },
            context_tag=context.get("context_tag", f"patchweaver::{operation_id}")
        )
        
        violations = self.ethics_gate.evaluate_action(action_context)
        
        if violations and self.ethics_gate.check_should_block(violations):
            blocked_reasons = [
                f"{v.rule_name} ({v.severity.value}): {v.description}"
                for v in violations if v.blocked
            ]
            reason = "Ethics gate blocked: " + "; ".join(blocked_reasons)
            logger.warning("Patch operation %s blocked by ethics gate", operation_id)
            
            return PatchResult(
                applied=False,
                reason=reason,
                before_hash=before_hash,
                after_hash=before_hash
            )
        
        # Step 4: Apply patch operations
        modified_paths = []
        
        try:
            # Process 'set' operations
            if "set" in patch:
                for path, value in patch["set"].items():
                    self._set_path(state, path, value)
                    modified_paths.append(f"set:{path}")
            
            # Process 'delete' operations
            if "delete" in patch:
                for path in patch["delete"]:
                    if self._delete_path(state, path):
                        modified_paths.append(f"delete:{path}")
        
        except Exception as e:
            logger.error("Failed to apply patch: %s", e)
            return PatchResult(
                applied=False,
                reason=f"Patch application failed: {str(e)}",
                before_hash=before_hash,
                after_hash=before_hash
            )
        
        # Step 5: Compute after_hash
        after_hash = self._compute_hash(state)
        
        # Step 6: Create DLP tag
        dlp_tag_id = self.dlp_tracker.create_tag("state_patch", patch)
        dlp_tag = self.dlp_tracker.tags[dlp_tag_id]
        
        # Add anchor protocols
        dlp_tag.add_anchor_protocol("EOS_SEED_ORION")
        dlp_tag.add_anchor_protocol("Picard_Delta_3")
        dlp_tag.add_anchor_protocol("PATCHWEAVER_CORE")
        
        # Add T1/SRB anchors
        dlp_tag.add_t1_srb_anchor("T1")
        dlp_tag.add_t1_srb_anchor("SRB")
        
        # Add symbolic patterns with patch metadata
        dlp_tag.set_symbolic_pattern("patch_metadata", {
            "operation_id": operation_id,
            "modified_paths": modified_paths,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": context.get("agent_id", "unknown"),
            "context_tag": action_context.context_tag
        })
        
        # Add metadata
        dlp_tag.metadata.update({
            "operation_type": "patchweaver_state_patch",
            "operation_id": operation_id,
            "paths_modified": len(modified_paths),
            "ethics_validated": True,
            "violations_count": len(violations)
        })
        
        # Step 7: Log the operation
        logger.info(
            "Patch operation %s completed: modified %d paths, before_hash=%s, after_hash=%s",
            operation_id,
            len(modified_paths),
            before_hash[:12],
            after_hash[:12]
        )
        
        # Step 8: Persist the new state
        try:
            self.save_state(state)
        except Exception as e:
            logger.error("Failed to save state: %s", e)
            return PatchResult(
                applied=False,
                reason=f"State save failed: {str(e)}",
                before_hash=before_hash,
                after_hash=after_hash,
                modified_paths=modified_paths
            )
        
        # Step 9: Return success result
        return PatchResult(
            applied=True,
            reason="ok",
            before_hash=before_hash,
            after_hash=after_hash,
            modified_paths=modified_paths
        )
    
    def _compute_hash(self, state: Dict[str, Any]) -> str:
        """
        Compute SHA256 hash of state for integrity checking
        
        Args:
            state: State dictionary
        
        Returns:
            Hex-encoded SHA256 hash
        """
        # Use canonical JSON representation for deterministic hashing
        state_str = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(state_str.encode('utf-8')).hexdigest()
    
    def _set_path(self, state: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a value at a nested path in the state dict
        
        Path format: "key1/key2/key3" sets state["key1"]["key2"]["key3"] = value
        Creates intermediate dicts as needed.
        
        Args:
            state: State dictionary (modified in place)
            path: Slash-separated key path
            value: Value to set
        """
        keys = path.split('/')
        current = state
        
        # Navigate to parent of target key, creating dicts as needed
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # If intermediate key exists but isn't a dict, replace it
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def _delete_path(self, state: Dict[str, Any], path: str) -> bool:
        """
        Delete a key at a nested path in the state dict
        
        Path format: "key1/key2/key3" deletes state["key1"]["key2"]["key3"]
        Idempotent: returns False if path doesn't exist, True if deleted.
        
        Args:
            state: State dictionary (modified in place)
            path: Slash-separated key path
        
        Returns:
            True if key was deleted, False if it didn't exist
        """
        keys = path.split('/')
        current = state
        
        # Navigate to parent of target key
        try:
            for key in keys[:-1]:
                current = current[key]
        except (KeyError, TypeError):
            # Path doesn't exist or intermediate value isn't a dict
            return False
        
        # Delete the final key if it exists
        if keys[-1] in current:
            del current[keys[-1]]
            return True
        
        return False
    
    def get_patch_history(self) -> List[Dict[str, Any]]:
        """
        Get history of patch operations from DLP tracker
        
        Returns:
            List of patch operation metadata
        """
        history = []
        
        for tag_id, tag in self.dlp_tracker.tags.items():
            if tag.operation == "state_patch":
                patch_info = tag.to_dict()
                history.append(patch_info)
        
        return history
    
    def verify_state_hash(self, expected_hash: str) -> bool:
        """
        Verify current state matches expected hash
        
        Args:
            expected_hash: Expected SHA256 hash of state
        
        Returns:
            True if state hash matches
        """
        try:
            state = self.load_state()
            current_hash = self._compute_hash(state)
            return current_hash == expected_hash
        except Exception as e:
            logger.error("Failed to verify state hash: %s", e)
            return False
