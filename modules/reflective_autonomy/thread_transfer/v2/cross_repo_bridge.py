"""
Cross-Repository Bridge Module - Thread Transfer Bridge v2
=========================================================

Cross-repository thread continuity bridge with 7-stage handshake.

Features:
- Repository-to-repository thread transfer
- 7-stage handshake protocol (extends v1's 5 stages)
- Cross-repo anchor synchronization
- Repository bridging with validation
- Multi-repository thread tracking

Thread: T1→BRIDGE_V2→CROSS_REPO
DLP: context_tag=bridge_v2_cross_repo_bridge
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from .repo_sync import (
    RepositorySynchronizer,
    get_repository_synchronizer,
    SyncDirection
)
from .anchor_propagation import (
    AnchorPropagator,
    get_anchor_propagator
)

logger = logging.getLogger(__name__)


class CrossRepoHandshakeStage(Enum):
    """Cross-repository handshake stages (7-stage protocol)."""
    REPO_DISCOVERY = "repo_discovery"              # Stage 1: Discover target repository
    ANCHOR_VALIDATION = "anchor_validation"        # Stage 2: Validate source anchor
    SYNC_PREPARATION = "sync_preparation"          # Stage 3: Prepare synchronization
    ANCHOR_PROPAGATION = "anchor_propagation"      # Stage 4: Propagate anchor
    THREAD_TRANSFER = "thread_transfer"            # Stage 5: Transfer thread context
    SYNC_EXECUTION = "sync_execution"              # Stage 6: Execute repository sync
    VERIFICATION = "verification"                  # Stage 7: Verify transfer integrity


class CrossRepoBridgeStatus(Enum):
    """Cross-repository bridge status."""
    IDLE = "idle"
    ACTIVE = "active"
    SYNCING = "syncing"
    TRANSFERRING = "transferring"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CrossRepoBridge:
    """Cross-repository bridge information."""
    bridge_id: str
    source_repo_id: str
    target_repo_id: str
    thread_id: str
    status: CrossRepoBridgeStatus = CrossRepoBridgeStatus.IDLE
    current_stage: Optional[CrossRepoHandshakeStage] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    anchor_hash: Optional[str] = None
    drift_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bridge_id": self.bridge_id,
            "source_repo_id": self.source_repo_id,
            "target_repo_id": self.target_repo_id,
            "thread_id": self.thread_id,
            "status": self.status.value,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "anchor_hash": self.anchor_hash,
            "drift_percentage": self.drift_percentage,
            "metadata": self.metadata
        }


class CrossRepositoryBridge:
    """
    Cross-repository bridge manager.
    
    Manages thread transfer between repositories using 7-stage handshake protocol.
    Integrates repository synchronization and anchor propagation.
    """
    
    def __init__(
        self,
        synchronizer: Optional[RepositorySynchronizer] = None,
        propagator: Optional[AnchorPropagator] = None
    ):
        """Initialize cross-repository bridge."""
        self.synchronizer = synchronizer or get_repository_synchronizer()
        self.propagator = propagator or get_anchor_propagator()
        self.bridges: Dict[str, CrossRepoBridge] = {}
        self._bridge_lock = asyncio.Lock()

    async def create_bridge(
        self,
        bridge_id: str,
        source_repo_id: str,
        target_repo_id: str,
        thread_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CrossRepoBridge:
        """
        Create a cross-repository bridge.

        Args:
            bridge_id: Unique bridge identifier
            source_repo_id: Source repository ID
            target_repo_id: Target repository ID
            thread_id: Thread identifier
            metadata: Optional metadata

        Returns:
            CrossRepoBridge object

        Raises:
            ValueError: If repositories not registered
        """
        # Validate repositories exist
        source_repo = self.synchronizer.get_repository(source_repo_id)
        target_repo = self.synchronizer.get_repository(target_repo_id)
        
        if not source_repo:
            raise ValueError(f"Source repository not registered: {source_repo_id}")
        if not target_repo:
            raise ValueError(f"Target repository not registered: {target_repo_id}")
        
        bridge = CrossRepoBridge(
            bridge_id=bridge_id,
            source_repo_id=source_repo_id,
            target_repo_id=target_repo_id,
            thread_id=thread_id,
            metadata=metadata or {}
        )
        
        self.bridges[bridge_id] = bridge
        logger.info(
            f"Created cross-repo bridge {bridge_id}: "
            f"{source_repo_id} → {target_repo_id}"
        )
        
        return bridge

    async def execute_handshake(
        self,
        bridge_id: str,
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """
        Execute 7-stage cross-repository handshake.

        Args:
            bridge_id: Bridge identifier
            auto_sync: Automatically sync repositories (default: True)

        Returns:
            Handshake result with status and details
        """
        if bridge_id not in self.bridges:
            return {
                "success": False,
                "error": f"Bridge not found: {bridge_id}"
            }
        
        bridge = self.bridges[bridge_id]
        
        async with self._bridge_lock:
            try:
                bridge.status = CrossRepoBridgeStatus.ACTIVE
                
                # Stage 1: Repository Discovery
                stage1_result = await self._stage1_repo_discovery(bridge)
                if not stage1_result["success"]:
                    bridge.status = CrossRepoBridgeStatus.FAILED
                    return stage1_result
                
                # Stage 2: Anchor Validation
                stage2_result = await self._stage2_anchor_validation(bridge)
                if not stage2_result["success"]:
                    bridge.status = CrossRepoBridgeStatus.FAILED
                    return stage2_result
                
                # Stage 3: Sync Preparation
                stage3_result = await self._stage3_sync_preparation(bridge, auto_sync)
                if not stage3_result["success"]:
                    bridge.status = CrossRepoBridgeStatus.FAILED
                    return stage3_result
                
                # Stage 4: Anchor Propagation
                bridge.status = CrossRepoBridgeStatus.TRANSFERRING
                stage4_result = await self._stage4_anchor_propagation(bridge)
                if not stage4_result["success"]:
                    bridge.status = CrossRepoBridgeStatus.FAILED
                    return stage4_result
                
                # Stage 5: Thread Transfer
                stage5_result = await self._stage5_thread_transfer(bridge)
                if not stage5_result["success"]:
                    bridge.status = CrossRepoBridgeStatus.FAILED
                    return stage5_result
                
                # Stage 6: Sync Execution
                if auto_sync:
                    bridge.status = CrossRepoBridgeStatus.SYNCING
                    stage6_result = await self._stage6_sync_execution(bridge)
                    if not stage6_result["success"]:
                        bridge.status = CrossRepoBridgeStatus.FAILED
                        return stage6_result
                
                # Stage 7: Verification
                bridge.status = CrossRepoBridgeStatus.VERIFYING
                stage7_result = await self._stage7_verification(bridge)
                if not stage7_result["success"]:
                    bridge.status = CrossRepoBridgeStatus.FAILED
                    return stage7_result
                
                # Mark completed
                bridge.status = CrossRepoBridgeStatus.COMPLETED
                bridge.completed_at = datetime.now()
                
                logger.info(
                    f"Cross-repo handshake completed for bridge {bridge_id}: "
                    f"drift={bridge.drift_percentage:.3f}%"
                )
                
                return {
                    "success": True,
                    "bridge_id": bridge_id,
                    "anchor_hash": bridge.anchor_hash,
                    "drift_percentage": bridge.drift_percentage,
                    "duration_seconds": (
                        bridge.completed_at - bridge.created_at
                    ).total_seconds(),
                    "stages_completed": 7 if auto_sync else 6
                }
                
            except Exception as e:
                bridge.status = CrossRepoBridgeStatus.FAILED
                logger.error(f"Cross-repo handshake failed for {bridge_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    async def _stage1_repo_discovery(self, bridge: CrossRepoBridge) -> Dict[str, Any]:
        """Stage 1: Repository Discovery."""
        bridge.current_stage = CrossRepoHandshakeStage.REPO_DISCOVERY
        
        try:
            # Verify both repositories are accessible
            source_repo = self.synchronizer.get_repository(bridge.source_repo_id)
            target_repo = self.synchronizer.get_repository(bridge.target_repo_id)
            
            if not source_repo or not target_repo:
                return {
                    "success": False,
                    "stage": "repo_discovery",
                    "error": "Repository not accessible"
                }
            
            bridge.metadata["source_repo_path"] = source_repo.repo_path
            bridge.metadata["target_repo_path"] = target_repo.repo_path
            bridge.metadata["source_branch"] = source_repo.branch
            bridge.metadata["target_branch"] = target_repo.branch
            
            logger.info(f"Stage 1 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "repo_discovery"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "repo_discovery",
                "error": str(e)
            }

    async def _stage2_anchor_validation(self, bridge: CrossRepoBridge) -> Dict[str, Any]:
        """Stage 2: Anchor Validation."""
        bridge.current_stage = CrossRepoHandshakeStage.ANCHOR_VALIDATION
        
        try:
            source_repo_path = bridge.metadata["source_repo_path"]
            source_branch = bridge.metadata["source_branch"]
            
            # Read and validate source anchor
            source_anchor = await self.propagator.read_anchor(
                source_repo_path,
                source_branch
            )
            
            if not source_anchor:
                return {
                    "success": False,
                    "stage": "anchor_validation",
                    "error": "No anchor found in source repository"
                }
            
            # Verify anchor integrity
            verification = await self.propagator.verify_anchor_integrity(
                source_repo_path,
                source_anchor.anchor_hash,
                source_branch
            )
            
            if not verification["valid"]:
                return {
                    "success": False,
                    "stage": "anchor_validation",
                    "error": "Anchor integrity check failed"
                }
            
            bridge.anchor_hash = source_anchor.anchor_hash
            bridge.metadata["source_anchor"] = source_anchor.to_dict()
            
            logger.info(f"Stage 2 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "anchor_validation"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "anchor_validation",
                "error": str(e)
            }

    async def _stage3_sync_preparation(
        self,
        bridge: CrossRepoBridge,
        auto_sync: bool
    ) -> Dict[str, Any]:
        """Stage 3: Sync Preparation."""
        bridge.current_stage = CrossRepoHandshakeStage.SYNC_PREPARATION
        
        try:
            if not auto_sync:
                logger.info(f"Stage 3 skipped (auto_sync=False) for bridge {bridge.bridge_id}")
                return {"success": True, "stage": "sync_preparation", "skipped": True}
            
            # Prepare both repositories for sync
            # This would typically check for uncommitted changes, conflicts, etc.
            source_repo = self.synchronizer.get_repository(bridge.source_repo_id)
            target_repo = self.synchronizer.get_repository(bridge.target_repo_id)
            
            if not source_repo or not target_repo:
                return {
                    "success": False,
                    "stage": "sync_preparation",
                    "error": "Repository not found"
                }
            
            bridge.metadata["sync_prepared"] = True
            bridge.metadata["source_remote"] = source_repo.remote_url
            bridge.metadata["target_remote"] = target_repo.remote_url
            
            logger.info(f"Stage 3 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "sync_preparation"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "sync_preparation",
                "error": str(e)
            }

    async def _stage4_anchor_propagation(self, bridge: CrossRepoBridge) -> Dict[str, Any]:
        """Stage 4: Anchor Propagation."""
        bridge.current_stage = CrossRepoHandshakeStage.ANCHOR_PROPAGATION
        
        try:
            source_repo_path = bridge.metadata["source_repo_path"]
            target_repo_path = bridge.metadata["target_repo_path"]
            source_branch = bridge.metadata["source_branch"]
            target_branch = bridge.metadata["target_branch"]
            
            # Propagate anchor from source to target
            result = await self.propagator.propagate_anchor(
                source_repo_path,
                target_repo_path,
                bridge.thread_id,
                bridge.target_repo_id,
                source_branch,
                target_branch
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "stage": "anchor_propagation",
                    "error": result.get("error", "Propagation failed")
                }
            
            bridge.metadata["propagation_result"] = result
            
            logger.info(f"Stage 4 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "anchor_propagation"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "anchor_propagation",
                "error": str(e)
            }

    async def _stage5_thread_transfer(self, bridge: CrossRepoBridge) -> Dict[str, Any]:
        """Stage 5: Thread Transfer."""
        bridge.current_stage = CrossRepoHandshakeStage.THREAD_TRANSFER
        
        try:
            # Transfer thread context (metadata, glyph chain, etc.)
            # This is placeholder logic - would integrate with actual thread transfer
            bridge.metadata["thread_context_transferred"] = True
            bridge.metadata["transfer_timestamp"] = datetime.now().isoformat()
            
            logger.info(f"Stage 5 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "thread_transfer"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "thread_transfer",
                "error": str(e)
            }

    async def _stage6_sync_execution(self, bridge: CrossRepoBridge) -> Dict[str, Any]:
        """Stage 6: Sync Execution."""
        bridge.current_stage = CrossRepoHandshakeStage.SYNC_EXECUTION
        
        try:
            # Sync both repositories
            source_sync = await self.synchronizer.sync_repository(
                bridge.source_repo_id,
                SyncDirection.PUSH
            )
            
            if not source_sync["success"]:
                return {
                    "success": False,
                    "stage": "sync_execution",
                    "error": f"Source sync failed: {source_sync.get('error')}"
                }
            
            target_sync = await self.synchronizer.sync_repository(
                bridge.target_repo_id,
                SyncDirection.PULL
            )
            
            if not target_sync["success"]:
                return {
                    "success": False,
                    "stage": "sync_execution",
                    "error": f"Target sync failed: {target_sync.get('error')}"
                }
            
            bridge.metadata["source_sync"] = source_sync
            bridge.metadata["target_sync"] = target_sync
            
            logger.info(f"Stage 6 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "sync_execution"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "sync_execution",
                "error": str(e)
            }

    async def _stage7_verification(self, bridge: CrossRepoBridge) -> Dict[str, Any]:
        """Stage 7: Verification."""
        bridge.current_stage = CrossRepoHandshakeStage.VERIFICATION
        
        try:
            target_repo_path = bridge.metadata["target_repo_path"]
            target_branch = bridge.metadata["target_branch"]
            
            # Verify target anchor matches source
            target_anchor = await self.propagator.read_anchor(
                target_repo_path,
                target_branch
            )
            
            if not target_anchor:
                return {
                    "success": False,
                    "stage": "verification",
                    "error": "Target anchor not found after transfer"
                }
            
            if target_anchor.anchor_hash != bridge.anchor_hash:
                # Calculate drift
                bridge.drift_percentage = 0.05  # Placeholder - would calculate actual drift
                return {
                    "success": False,
                    "stage": "verification",
                    "error": "Anchor hash mismatch",
                    "drift_percentage": bridge.drift_percentage
                }
            
            bridge.drift_percentage = 0.0  # Perfect transfer
            
            logger.info(f"Stage 7 complete for bridge {bridge.bridge_id}")
            return {"success": True, "stage": "verification"}
            
        except Exception as e:
            return {
                "success": False,
                "stage": "verification",
                "error": str(e)
            }

    def get_bridge(self, bridge_id: str) -> Optional[CrossRepoBridge]:
        """Get bridge information."""
        return self.bridges.get(bridge_id)

    def list_bridges(
        self,
        status: Optional[CrossRepoBridgeStatus] = None
    ) -> List[CrossRepoBridge]:
        """
        List bridges.

        Args:
            status: Optional status filter

        Returns:
            List of bridges
        """
        bridges = list(self.bridges.values())
        
        if status:
            bridges = [b for b in bridges if b.status == status]
        
        return bridges


# Global bridge instance
_cross_repo_bridge = None


def get_cross_repository_bridge() -> CrossRepositoryBridge:
    """Get global cross-repository bridge instance."""
    global _cross_repo_bridge
    if _cross_repo_bridge is None:
        _cross_repo_bridge = CrossRepositoryBridge()
    return _cross_repo_bridge
