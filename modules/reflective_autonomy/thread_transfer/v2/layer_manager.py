"""
Layer Manager Module - Thread Transfer Bridge v2
===============================================

Multi-layer hierarchy management for thread bridges.

Layers:
- L1: Thread-to-thread (5 stages, Δ=0.0%)
- L2: Repository-to-repository (7 stages, Δ≤0.1%)
- L3: Cluster-to-cluster (9 stages, Δ≤0.5%, PKI required)

Features:
- Layer orchestration and coordination
- Layer-specific protocol enforcement
- Cascading validation across layers
- Layer transition management

Thread: T1→BRIDGE_V2→LAYER_MGR
DLP: context_tag=bridge_v2_layer_manager
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum

logger = logging.getLogger(__name__)


class BridgeLayer(Enum):
    """Bridge hierarchy layers."""
    L1 = "L1"  # Thread-to-thread
    L2 = "L2"  # Repository-to-repository
    L3 = "L3"  # Cluster-to-cluster


@dataclass
class LayerConfiguration:
    """Layer-specific configuration."""
    layer: BridgeLayer
    handshake_stages: int           # Number of stages in handshake
    max_drift_percentage: float     # Maximum allowed drift
    requires_pki: bool              # PKI requirement
    min_nodes: int                  # Minimum nodes required
    verification_depth: int         # Verification thoroughness (1-5)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "layer": self.layer.value,
            "handshake_stages": self.handshake_stages,
            "max_drift_percentage": self.max_drift_percentage,
            "requires_pki": self.requires_pki,
            "min_nodes": self.min_nodes,
            "verification_depth": self.verification_depth,
            "metadata": self.metadata
        }


# Pre-defined layer configurations
LAYER_CONFIGS = {
    BridgeLayer.L1: LayerConfiguration(
        layer=BridgeLayer.L1,
        handshake_stages=5,
        max_drift_percentage=0.0,
        requires_pki=False,
        min_nodes=1,
        verification_depth=3,
        metadata={"description": "Thread-to-thread bridge within single repository"}
    ),
    BridgeLayer.L2: LayerConfiguration(
        layer=BridgeLayer.L2,
        handshake_stages=7,
        max_drift_percentage=0.1,
        requires_pki=False,
        min_nodes=2,
        verification_depth=4,
        metadata={"description": "Repository-to-repository bridge across projects"}
    ),
    BridgeLayer.L3: LayerConfiguration(
        layer=BridgeLayer.L3,
        handshake_stages=9,
        max_drift_percentage=0.5,
        requires_pki=True,
        min_nodes=3,
        verification_depth=5,
        metadata={"description": "Cluster-to-cluster bridge across organizations"}
    )
}


@dataclass
class LayerBridge:
    """Multi-layer bridge information."""
    bridge_id: str
    layer: BridgeLayer
    source_id: str
    target_id: str
    thread_id: str
    status: str = "idle"
    current_stage: int = 0
    drift_percentage: float = 0.0
    pki_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bridge_id": self.bridge_id,
            "layer": self.layer.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "thread_id": self.thread_id,
            "status": self.status,
            "current_stage": self.current_stage,
            "drift_percentage": self.drift_percentage,
            "pki_verified": self.pki_verified,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class LayerValidationError(Exception):
    """Layer validation error."""
    pass


class LayerManager:
    """
    Multi-layer bridge manager.
    
    Manages L1/L2/L3 bridge hierarchies with cascading validation.
    """
    
    def __init__(self):
        """Initialize layer manager."""
        self.bridges: Dict[str, LayerBridge] = {}
        self.layer_dependencies: Dict[BridgeLayer, Set[BridgeLayer]] = {
            BridgeLayer.L1: set(),                          # L1 standalone
            BridgeLayer.L2: {BridgeLayer.L1},              # L2 requires L1
            BridgeLayer.L3: {BridgeLayer.L1, BridgeLayer.L2}  # L3 requires L1 & L2
        }
        self._manager_lock = asyncio.Lock()

    async def create_bridge(
        self,
        bridge_id: str,
        layer: BridgeLayer,
        source_id: str,
        target_id: str,
        thread_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LayerBridge:
        """
        Create a layer bridge.

        Args:
            bridge_id: Unique bridge identifier
            layer: Bridge layer (L1/L2/L3)
            source_id: Source identifier
            target_id: Target identifier
            thread_id: Thread identifier
            metadata: Optional metadata

        Returns:
            LayerBridge object

        Raises:
            LayerValidationError: If layer requirements not met
        """
        # Validate layer dependencies
        await self._validate_layer_dependencies(layer, thread_id)
        
        bridge = LayerBridge(
            bridge_id=bridge_id,
            layer=layer,
            source_id=source_id,
            target_id=target_id,
            thread_id=thread_id,
            metadata=metadata or {}
        )
        
        self.bridges[bridge_id] = bridge
        
        logger.info(
            f"Created {layer.value} bridge {bridge_id}: "
            f"{source_id} → {target_id}"
        )
        
        return bridge

    async def execute_layered_handshake(
        self,
        bridge_id: str,
        enable_pki: bool = True
    ) -> Dict[str, Any]:
        """
        Execute layer-specific handshake.

        Args:
            bridge_id: Bridge identifier
            enable_pki: Enable PKI verification for L3

        Returns:
            Handshake result
        """
        if bridge_id not in self.bridges:
            return {
                "success": False,
                "error": f"Bridge not found: {bridge_id}"
            }
        
        bridge = self.bridges[bridge_id]
        config = LAYER_CONFIGS[bridge.layer]
        
        async with self._manager_lock:
            try:
                bridge.status = "active"
                
                # Execute layer-specific handshake stages
                for stage in range(1, config.handshake_stages + 1):
                    bridge.current_stage = stage
                    
                    logger.info(
                        f"{bridge.layer.value} bridge {bridge_id}: "
                        f"stage {stage}/{config.handshake_stages}"
                    )
                    
                    stage_result = await self._execute_stage(
                        bridge,
                        stage,
                        config,
                        enable_pki
                    )
                    
                    if not stage_result["success"]:
                        bridge.status = "failed"
                        return stage_result
                    
                    # Simulate stage processing
                    await asyncio.sleep(0.01)
                
                # Final validation
                validation_result = await self._validate_bridge(bridge, config)
                
                if not validation_result["success"]:
                    bridge.status = "failed"
                    return validation_result
                
                bridge.status = "completed"
                
                logger.info(
                    f"{bridge.layer.value} bridge {bridge_id} completed: "
                    f"drift={bridge.drift_percentage:.4f}%"
                )
                
                return {
                    "success": True,
                    "bridge_id": bridge_id,
                    "layer": bridge.layer.value,
                    "stages_completed": config.handshake_stages,
                    "drift_percentage": bridge.drift_percentage,
                    "pki_verified": bridge.pki_verified
                }
                
            except Exception as e:
                bridge.status = "error"
                logger.error(f"{bridge.layer.value} handshake failed: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    async def _validate_layer_dependencies(
        self,
        layer: BridgeLayer,
        thread_id: str
    ):
        """
        Validate that required lower layers exist.

        Raises:
            LayerValidationError: If dependencies not met
        """
        required_layers = self.layer_dependencies[layer]
        
        if not required_layers:
            return  # No dependencies
        
        # Check if lower-layer bridges exist for this thread
        existing_layers = set()
        for bridge in self.bridges.values():
            if bridge.thread_id == thread_id and bridge.status == "completed":
                existing_layers.add(bridge.layer)
        
        missing_layers = required_layers - existing_layers
        
        if missing_layers:
            raise LayerValidationError(
                f"{layer.value} requires {', '.join(layer_obj.value for layer_obj in missing_layers)} "
                f"bridges to be completed first"
            )

    async def _execute_stage(
        self,
        bridge: LayerBridge,
        stage: int,
        config: LayerConfiguration,
        enable_pki: bool
    ) -> Dict[str, Any]:
        """Execute a handshake stage."""
        # Layer-specific stage logic
        if bridge.layer == BridgeLayer.L1:
            return await self._execute_l1_stage(bridge, stage)
        elif bridge.layer == BridgeLayer.L2:
            return await self._execute_l2_stage(bridge, stage)
        elif bridge.layer == BridgeLayer.L3:
            return await self._execute_l3_stage(bridge, stage, enable_pki)
        else:
            return {"success": False, "error": f"Unknown layer: {bridge.layer}"}

    async def _execute_l1_stage(
        self,
        bridge: LayerBridge,
        stage: int
    ) -> Dict[str, Any]:
        """Execute L1 (thread-to-thread) stage."""
        stage_names = [
            "initialize",
            "authenticate",
            "transfer_context",
            "validate",
            "finalize"
        ]
        
        if stage > len(stage_names):
            return {"success": False, "error": "Invalid stage"}
        
        stage_name = stage_names[stage - 1]
        
        logger.debug(f"L1 stage {stage}: {stage_name}")
        
        # Simulate stage processing
        bridge.drift_percentage = min(0.0, bridge.drift_percentage + 0.0001)
        
        return {"success": True, "stage": stage_name}

    async def _execute_l2_stage(
        self,
        bridge: LayerBridge,
        stage: int
    ) -> Dict[str, Any]:
        """Execute L2 (repo-to-repo) stage."""
        stage_names = [
            "repo_discovery",
            "anchor_validation",
            "sync_preparation",
            "anchor_propagation",
            "thread_transfer",
            "sync_execution",
            "verification"
        ]
        
        if stage > len(stage_names):
            return {"success": False, "error": "Invalid stage"}
        
        stage_name = stage_names[stage - 1]
        
        logger.debug(f"L2 stage {stage}: {stage_name}")
        
        # Simulate stage processing with slight drift
        bridge.drift_percentage = min(0.1, bridge.drift_percentage + 0.01)
        
        return {"success": True, "stage": stage_name}

    async def _execute_l3_stage(
        self,
        bridge: LayerBridge,
        stage: int,
        enable_pki: bool
    ) -> Dict[str, Any]:
        """Execute L3 (cluster-to-cluster) stage."""
        stage_names = [
            "cluster_discovery",
            "pki_verification",
            "trust_establishment",
            "multi_repo_sync",
            "anchor_federation",
            "thread_federation",
            "consistency_check",
            "distributed_validation",
            "final_verification"
        ]
        
        if stage > len(stage_names):
            return {"success": False, "error": "Invalid stage"}
        
        stage_name = stage_names[stage - 1]
        
        logger.debug(f"L3 stage {stage}: {stage_name}")
        
        # PKI verification required at stage 2
        if stage == 2 and LAYER_CONFIGS[BridgeLayer.L3].requires_pki:
            if not enable_pki:
                return {
                    "success": False,
                    "error": "PKI verification required for L3 bridges"
                }
            bridge.pki_verified = True
        
        # Simulate stage processing with moderate drift
        bridge.drift_percentage = min(0.5, bridge.drift_percentage + 0.05)
        
        return {"success": True, "stage": stage_name}

    async def _validate_bridge(
        self,
        bridge: LayerBridge,
        config: LayerConfiguration
    ) -> Dict[str, Any]:
        """Validate completed bridge."""
        # Check drift against layer maximum
        if bridge.drift_percentage > config.max_drift_percentage:
            return {
                "success": False,
                "error": f"Drift exceeded layer maximum: "
                        f"{bridge.drift_percentage:.3f}% > {config.max_drift_percentage}%"
            }
        
        # Check PKI requirement
        if config.requires_pki and not bridge.pki_verified:
            return {
                "success": False,
                "error": f"{bridge.layer.value} requires PKI verification"
            }
        
        return {"success": True}

    async def cascade_validation(
        self,
        thread_id: str
    ) -> Dict[str, Any]:
        """
        Perform cascading validation across all layers for a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            Validation result with layer-by-layer status
        """
        thread_bridges = [
            b for b in self.bridges.values()
            if b.thread_id == thread_id
        ]
        
        if not thread_bridges:
            return {
                "success": False,
                "error": f"No bridges found for thread {thread_id}"
            }
        
        # Group by layer
        by_layer = {
            BridgeLayer.L1: [],
            BridgeLayer.L2: [],
            BridgeLayer.L3: []
        }
        
        for bridge in thread_bridges:
            by_layer[bridge.layer].append(bridge)
        
        results = {}
        
        # Validate each layer in order (L1 → L2 → L3)
        for layer in [BridgeLayer.L1, BridgeLayer.L2, BridgeLayer.L3]:
            bridges = by_layer[layer]
            
            if not bridges:
                results[layer.value] = {"status": "not_present"}
                continue
            
            config = LAYER_CONFIGS[layer]
            
            # Check all bridges at this layer
            layer_valid = True
            layer_issues = []
            
            for bridge in bridges:
                if bridge.status != "completed":
                    layer_valid = False
                    layer_issues.append(f"{bridge.bridge_id} not completed")
                
                if bridge.drift_percentage > config.max_drift_percentage:
                    layer_valid = False
                    layer_issues.append(
                        f"{bridge.bridge_id} drift too high: "
                        f"{bridge.drift_percentage:.3f}%"
                    )
                
                if config.requires_pki and not bridge.pki_verified:
                    layer_valid = False
                    layer_issues.append(f"{bridge.bridge_id} missing PKI verification")
            
            results[layer.value] = {
                "status": "valid" if layer_valid else "invalid",
                "bridge_count": len(bridges),
                "issues": layer_issues
            }
        
        overall_valid = all(
            r["status"] in ["valid", "not_present"]
            for r in results.values()
        )
        
        logger.info(
            f"Cascade validation for thread {thread_id}: "
            f"{'VALID' if overall_valid else 'INVALID'}"
        )
        
        return {
            "success": overall_valid,
            "thread_id": thread_id,
            "layers": results
        }

    def get_bridge(self, bridge_id: str) -> Optional[LayerBridge]:
        """Get bridge information."""
        return self.bridges.get(bridge_id)

    def list_bridges(
        self,
        layer: Optional[BridgeLayer] = None,
        thread_id: Optional[str] = None
    ) -> List[LayerBridge]:
        """
        List bridges with optional filters.

        Args:
            layer: Optional layer filter
            thread_id: Optional thread filter

        Returns:
            List of bridges
        """
        bridges = list(self.bridges.values())
        
        if layer:
            bridges = [b for b in bridges if b.layer == layer]
        
        if thread_id:
            bridges = [b for b in bridges if b.thread_id == thread_id]
        
        return bridges

    def get_layer_statistics(self) -> Dict[str, Any]:
        """Get layer statistics."""
        stats = {
            "total_bridges": len(self.bridges),
            "by_layer": {
                "L1": 0,
                "L2": 0,
                "L3": 0
            },
            "by_status": {
                "idle": 0,
                "active": 0,
                "completed": 0,
                "failed": 0,
                "error": 0
            }
        }
        
        for bridge in self.bridges.values():
            stats["by_layer"][bridge.layer.value] += 1
            stats["by_status"][bridge.status] += 1
        
        return stats


# Global layer manager instance
_layer_manager = None


def get_layer_manager() -> LayerManager:
    """Get global layer manager instance."""
    global _layer_manager
    if _layer_manager is None:
        _layer_manager = LayerManager()
    return _layer_manager
