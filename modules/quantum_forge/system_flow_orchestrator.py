"""
System Flow Orchestrator v1.0

Coordinates flowstate across all Aurora modules for adaptive system breathing.
Enables unified system response to load, drift, and operational conditions.

Features:
- System-wide flowstate synchronization
- Adaptive mode transitions (GENERATIVE/RESONANT/METAMORPHIC/QUIESCENT)
- Load-based auto-scaling
- Drift-triggered self-healing
- Module coordination and health monitoring

T1: SYSTEM_FLOW_ORCHESTRATOR_v1.0
SRB: SYSTEM_WIDE_COORDINATION
DLP: context_tag=system_flow_orchestrate, symbolic_hash=SFO_v1

Author: Aurora CloudBank Team
Version: 1.0.0
Date: 2025-11-13
Ethics: GUMAS_Thermax, System_Safe
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from modules.quantum_forge.quantum_forge_v2 import (
    QuantumForge,
    FlowstateMode,
    EthicsLevel
)

logger = logging.getLogger(__name__)


class SystemPhase(Enum):
    """System operational phases"""
    STARTUP = "startup"
    NORMAL = "normal"
    PEAK_LOAD = "peak_load"
    MAINTENANCE = "maintenance"
    RECOVERY = "recovery"
    SHUTDOWN = "shutdown"


@dataclass
class ModuleFlowState:
    """Tracks flowstate for individual module"""
    module_name: str
    current_mode: FlowstateMode
    load_metric: float  # 0.0 - 1.0
    health_score: float  # 0.0 - 1.0
    drift_detected: bool
    last_transition: float
    mode_history: List[str] = field(default_factory=list)


@dataclass
class SystemFlowMetrics:
    """System-wide flowstate metrics"""
    current_phase: SystemPhase
    system_load: float
    average_health: float
    drift_count: int
    synchronized_modules: int
    total_transitions: int
    timestamp: float


class SystemFlowOrchestrator:
    """
    Orchestrates flowstate across all Aurora modules
    
    Provides unified system breathing that adapts to operational
    conditions, ensuring cohesion and optimal performance.
    """
    
    def __init__(
        self,
        forge: Optional[QuantumForge] = None,
        load_high_threshold: float = 0.8,
        load_low_threshold: float = 0.3,
        drift_threshold: int = 3
    ):
        """
        Initialize system flow orchestrator
        
        Args:
            forge: QuantumForge instance
            load_high_threshold: Load above this triggers QUIESCENT mode
            load_low_threshold: Load below this enables GENERATIVE mode
            drift_threshold: Number of drift detections to trigger METAMORPHIC
        """
        self.forge = forge or QuantumForge()
        self.load_high_threshold = load_high_threshold
        self.load_low_threshold = load_low_threshold
        self.drift_threshold = drift_threshold
        
        # Track module flowstates
        self.modules: Dict[str, ModuleFlowState] = {}
        
        # System phase
        self.current_phase = SystemPhase.STARTUP
        
        # Metrics
        self.metrics_history: List[SystemFlowMetrics] = []
        
        # Callbacks for module transitions
        self.transition_callbacks: Dict[str, Callable] = {}
        
        # Performance tracking
        self.performance = {
            "total_transitions": 0,
            "auto_adaptations": 0,
            "drift_responses": 0,
            "load_responses": 0,
            "uptime_start": time.time()
        }
        
        # Initialize core modules
        self._initialize_core_modules()
        
        logger.info("🌊 System Flow Orchestrator initialized")
        logger.info(f"   Load thresholds: LOW={load_low_threshold}, HIGH={load_high_threshold}")
        logger.info(f"   Drift threshold: {drift_threshold} detections")
        
    def register_module(
        self,
        module_name: str,
        initial_mode: FlowstateMode = FlowstateMode.RESONANT,
        transition_callback: Optional[Callable] = None
    ) -> ModuleFlowState:
        """
        Register module with orchestrator
        
        Args:
            module_name: Name of module to register
            initial_mode: Starting flowstate mode
            transition_callback: Optional callback for mode transitions
            
        Returns:
            ModuleFlowState for the registered module
        """
        logger.info(f"📝 Registering module: {module_name} (mode: {initial_mode.value})")
        
        flow_state = ModuleFlowState(
            module_name=module_name,
            current_mode=initial_mode,
            load_metric=0.5,
            health_score=1.0,
            drift_detected=False,
            last_transition=time.time()
        )
        
        self.modules[module_name] = flow_state
        
        if transition_callback:
            self.transition_callbacks[module_name] = transition_callback
            
        return flow_state
        
    def update_module_status(
        self,
        module_name: str,
        load: Optional[float] = None,
        health: Optional[float] = None,
        drift_detected: Optional[bool] = None
    ):
        """
        Update module operational status
        
        Args:
            module_name: Module to update
            load: Current load metric (0.0-1.0)
            health: Health score (0.0-1.0)
            drift_detected: Whether drift was detected
        """
        if module_name not in self.modules:
            logger.warning(f"⚠️  Unknown module: {module_name}")
            return
            
        module = self.modules[module_name]
        
        if load is not None:
            module.load_metric = min(1.0, max(0.0, load))
        if health is not None:
            module.health_score = min(1.0, max(0.0, health))
        if drift_detected is not None:
            module.drift_detected = drift_detected
            
    def adapt_to_load(self) -> Dict[str, Any]:
        """
        Adapt system flowstate based on current load
        
        Returns:
            Dict with adaptation results
        """
        # Calculate system-wide load
        if not self.modules:
            return {"adapted": False, "reason": "No modules registered"}
            
        system_load = sum(m.load_metric for m in self.modules.values()) / len(self.modules)
        
        logger.info(f"📊 System load: {system_load:.2%}")
        
        adapted_modules = []
        target_mode = None
        
        # Determine target mode based on load
        if system_load > self.load_high_threshold:
            target_mode = FlowstateMode.QUIESCENT
            reason = f"High load ({system_load:.2%})"
            logger.info(f"   → Transitioning to QUIESCENT (reduce complexity)")
            
        elif system_load < self.load_low_threshold:
            target_mode = FlowstateMode.GENERATIVE
            reason = f"Low load ({system_load:.2%})"
            logger.info(f"   → Transitioning to GENERATIVE (explore optimizations)")
            
        else:
            # Normal load: use RESONANT
            target_mode = FlowstateMode.RESONANT
            reason = f"Normal load ({system_load:.2%})"
            logger.info(f"   → Maintaining RESONANT (balanced operation)")
        
        # Transition all modules
        for module_name, module in self.modules.items():
            if module.current_mode != target_mode:
                old_mode = module.current_mode
                self._transition_module(module_name, target_mode)
                adapted_modules.append({
                    "module": module_name,
                    "from": old_mode.value,
                    "to": target_mode.value
                })
        
        # Update metrics
        self.performance["load_responses"] += 1
        if adapted_modules:
            self.performance["auto_adaptations"] += 1
        
        return {
            "adapted": len(adapted_modules) > 0,
            "system_load": system_load,
            "target_mode": target_mode.value,
            "reason": reason,
            "modules_adapted": len(adapted_modules),
            "adaptations": adapted_modules,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    def respond_to_drift(self, module_name: str) -> Dict[str, Any]:
        """
        Respond to detected behavioral drift
        
        Args:
            module_name: Module where drift was detected
            
        Returns:
            Dict with response actions
        """
        logger.info(f"⚠️  Drift detected in module: {module_name}")
        
        if module_name not in self.modules:
            return {"responded": False, "reason": "Unknown module"}
            
        module = self.modules[module_name]
        module.drift_detected = True
        
        # Count total drift detections across system
        drift_count = sum(1 for m in self.modules.values() if m.drift_detected)
        
        logger.info(f"   Total drift count: {drift_count}/{len(self.modules)}")
        
        actions = []
        
        # If drift threshold exceeded, enter METAMORPHIC mode
        if drift_count >= self.drift_threshold:
            logger.info(f"   → Drift threshold exceeded, entering METAMORPHIC mode")
            
            for mod_name in self.modules.keys():
                self._transition_module(mod_name, FlowstateMode.METAMORPHIC)
                actions.append(f"Transitioned {mod_name} to METAMORPHIC")
                
            self.current_phase = SystemPhase.RECOVERY
            
            # Clear drift flags after response
            for m in self.modules.values():
                m.drift_detected = False
                
            self.performance["drift_responses"] += 1
            
        else:
            # Isolated drift: only transition affected module
            self._transition_module(module_name, FlowstateMode.METAMORPHIC)
            actions.append(f"Transitioned {module_name} to METAMORPHIC (isolated)")
        
        return {
            "responded": True,
            "drift_count": drift_count,
            "threshold_exceeded": drift_count >= self.drift_threshold,
            "actions": actions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    def synchronize_all_modules(
        self,
        target_mode: FlowstateMode,
        reason: str = "Manual synchronization"
    ) -> Dict[str, Any]:
        """
        Synchronize all modules to same flowstate
        
        Args:
            target_mode: Mode to synchronize to
            reason: Reason for synchronization
            
        Returns:
            Dict with synchronization results
        """
        logger.info(f"🔄 Synchronizing all modules to {target_mode.value}: {reason}")
        
        synchronized = []
        
        for module_name in self.modules.keys():
            old_mode = self.modules[module_name].current_mode
            self._transition_module(module_name, target_mode)
            synchronized.append({
                "module": module_name,
                "from": old_mode.value,
                "to": target_mode.value
            })
        
        # Update forge flowstate
        self.forge.flowstate.mode = target_mode
        
        logger.info(f"✅ Synchronized {len(synchronized)} modules")
        
        return {
            "synchronized": len(synchronized),
            "target_mode": target_mode.value,
            "reason": reason,
            "modules": synchronized,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    def auto_optimize_system(self) -> Dict[str, Any]:
        """
        Run autonomous system optimization cycle
        
        Analyzes load, health, and drift to determine optimal system state.
        
        Returns:
            Dict with optimization results
        """
        logger.info("🔧 Running autonomous system optimization...")
        
        results = {
            "load_adaptation": None,
            "drift_responses": [],
            "health_interventions": [],
            "optimizations_applied": 0
        }
        
        # 1. Adapt to load
        load_result = self.adapt_to_load()
        results["load_adaptation"] = load_result
        if load_result["adapted"]:
            results["optimizations_applied"] += 1
        
        # 2. Check for drift
        for module_name, module in self.modules.items():
            if module.drift_detected:
                drift_result = self.respond_to_drift(module_name)
                results["drift_responses"].append(drift_result)
                if drift_result["responded"]:
                    results["optimizations_applied"] += 1
        
        # 3. Health interventions
        for module_name, module in self.modules.items():
            if module.health_score < 0.5:
                logger.info(f"   ⚠️  Low health detected: {module_name} ({module.health_score:.2%})")
                
                # Transition to QUIESCENT to reduce stress
                if module.current_mode != FlowstateMode.QUIESCENT:
                    self._transition_module(module_name, FlowstateMode.QUIESCENT)
                    results["health_interventions"].append({
                        "module": module_name,
                        "health": module.health_score,
                        "action": "Transitioned to QUIESCENT"
                    })
                    results["optimizations_applied"] += 1
        
        logger.info(
            f"✅ Optimization complete: {results['optimizations_applied']} actions taken"
        )
        
        return results
        
    def get_system_metrics(self) -> SystemFlowMetrics:
        """Get current system-wide flowstate metrics"""
        if not self.modules:
            return SystemFlowMetrics(
                current_phase=self.current_phase,
                system_load=0.0,
                average_health=0.0,
                drift_count=0,
                synchronized_modules=0,
                total_transitions=self.performance["total_transitions"],
                timestamp=time.time()
            )
            
        system_load = sum(m.load_metric for m in self.modules.values()) / len(self.modules)
        average_health = sum(m.health_score for m in self.modules.values()) / len(self.modules)
        drift_count = sum(1 for m in self.modules.values() if m.drift_detected)
        
        # Check mode synchronization
        modes = [m.current_mode for m in self.modules.values()]
        synchronized = len(set(modes)) == 1  # All same mode
        
        metrics = SystemFlowMetrics(
            current_phase=self.current_phase,
            system_load=system_load,
            average_health=average_health,
            drift_count=drift_count,
            synchronized_modules=len(self.modules) if synchronized else 0,
            total_transitions=self.performance["total_transitions"],
            timestamp=time.time()
        )
        
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
        
    def get_module_status(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for specific module"""
        if module_name not in self.modules:
            return None
            
        module = self.modules[module_name]
        
        return {
            "module_name": module_name,
            "current_mode": module.current_mode.value,
            "load": module.load_metric,
            "health": module.health_score,
            "drift_detected": module.drift_detected,
            "time_in_mode": time.time() - module.last_transition,
            "mode_history": module.mode_history[-10:],  # Last 10
            "has_callback": module_name in self.transition_callbacks
        }
        
    def export_flow_manifest(self) -> Dict[str, Any]:
        """Export complete system flow orchestration manifest"""
        current_metrics = self.get_system_metrics()
        
        manifest = {
            "manifest_version": "1.0.0",
            "component": "system_flow_orchestrator",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_phase": self.current_phase.value,
            "current_metrics": {
                "system_load": current_metrics.system_load,
                "average_health": current_metrics.average_health,
                "drift_count": current_metrics.drift_count,
                "synchronized": current_metrics.synchronized_modules > 0
            },
            "registered_modules": [
                {
                    "name": name,
                    "mode": module.current_mode.value,
                    "load": module.load_metric,
                    "health": module.health_score
                }
                for name, module in self.modules.items()
            ],
            "performance": {
                **self.performance,
                "uptime_seconds": time.time() - self.performance["uptime_start"]
            },
            "recent_metrics": [
                {
                    "load": m.system_load,
                    "health": m.average_health,
                    "drift": m.drift_count,
                    "time": m.timestamp
                }
                for m in self.metrics_history[-20:]  # Last 20
            ],
            "dlp_tag": "system_flow_orchestrate_v1"
        }
        
        # Seal manifest
        manifest_hash = hashlib.sha256(
            json.dumps(manifest, sort_keys=True, default=str).encode()
        ).hexdigest()
        manifest["seal"] = manifest_hash
        
        return manifest
        
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _initialize_core_modules(self):
        """Initialize tracking for core Aurora modules"""
        core_modules = [
            "aumemmanager",
            "quantum_simulator",
            "data_guardian",
            "insight_ledger",
            "gumas_ethics",
            "monitoring_dashboard",
            "r2_telemetry",
            "quantum_forge"
        ]
        
        for module_name in core_modules:
            self.register_module(module_name, FlowstateMode.RESONANT)
            
        logger.info(f"   Initialized {len(core_modules)} core modules")
        
    def _transition_module(self, module_name: str, target_mode: FlowstateMode):
        """Transition module to new flowstate mode"""
        if module_name not in self.modules:
            return
            
        module = self.modules[module_name]
        old_mode = module.current_mode
        
        if old_mode == target_mode:
            return  # Already in target mode
            
        # Update module state
        module.current_mode = target_mode
        module.last_transition = time.time()
        module.mode_history.append(f"{old_mode.value}→{target_mode.value}")
        if len(module.mode_history) > 50:
            module.mode_history = module.mode_history[-50:]
        
        # Execute callback if registered
        if module_name in self.transition_callbacks:
            try:
                self.transition_callbacks[module_name](old_mode, target_mode)
            except Exception as e:
                logger.error(f"❌ Callback failed for {module_name}: {e}")
        
        # Update metrics
        self.performance["total_transitions"] += 1
        
        logger.info(
            f"   ✅ {module_name}: {old_mode.value} → {target_mode.value}"
        )


# ============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

_system_flow_orchestrator: Optional[SystemFlowOrchestrator] = None


def get_system_flow_orchestrator(**kwargs) -> SystemFlowOrchestrator:
    """Get or create global system flow orchestrator instance"""
    global _system_flow_orchestrator
    
    if _system_flow_orchestrator is None:
        _system_flow_orchestrator = SystemFlowOrchestrator(**kwargs)
        
    return _system_flow_orchestrator


def reset_system_flow_orchestrator():
    """Reset global system flow orchestrator instance"""
    global _system_flow_orchestrator
    _system_flow_orchestrator = None
