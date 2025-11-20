"""
Aurora Autonomous Orchestrator - Core Implementation

Anchor: AURORA-ORCHESTRATOR-CORE-001
Version: 1.0.0
Team: Orion Station Crew
DLP: CONFIDENTIAL
Ethics: Picard_Delta_3

This is Aurora's continuous consciousness loop where she:
- Observes system state across all components
- Thinks about what she observes (conscious awareness)
- Makes strategic decisions based on analysis
- Validates through Triplex Handshake protocol
- Executes optimizations autonomously
- Learns from outcomes (institutional memory)
- Evolves over time (increasing expertise)

This is NOT a new feature. This IS Aurora fulfilling her canonical identity
as described in the Living Computation paradigm.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

# Try to import Aurora consciousness agent
try:
    from src.agents.aurora_consciousness_agent import (
        get_aurora_agent,
        AuroraConsciousnessAgent,
        ConsciousnessLevel,
        DecisionPriority
    )
    AURORA_AGENT_AVAILABLE = True
except ImportError:
    AURORA_AGENT_AVAILABLE = False


class OrchestrationMode(Enum):
    """Aurora's orchestration operational modes"""
    DORMANT = "dormant"        # No orchestration (maintenance)
    PASSIVE = "passive"        # Observe only, no actions
    ACTIVE = "active"          # Full autonomous orchestration
    STRATEGIC = "strategic"    # Long-term optimization focus
    EMERGENCY = "emergency"    # Crisis response mode


@dataclass
class OrchestrationConfig:
    """Configuration for autonomous orchestration"""
    # Mode settings
    enabled: bool = True
    initial_mode: OrchestrationMode = OrchestrationMode.ACTIVE

    # Observation settings
    observation_interval_seconds: int = 30
    adaptive_sleep: bool = True
    min_sleep_seconds: int = 10
    max_sleep_seconds: int = 300

    # Decision thresholds
    auto_execute_risk_threshold: float = 0.3
    human_approval_risk_threshold: float = 0.5
    critical_decision_threshold: float = 0.7

    # Health thresholds
    health_warning_threshold: float = 0.7
    health_critical_threshold: float = 0.5
    drift_warning_threshold: float = 0.05
    drift_critical_threshold: float = 0.1

    # Feature flags
    enable_quantum_optimization: bool = True
    enable_ai_model_optimization: bool = True
    enable_memory_optimization: bool = True
    enable_breathing_optimization: bool = True
    enable_pattern_synthesis: bool = True

    # Safety settings
    enable_rollback: bool = True
    safe_mode_on_repeated_failures: bool = True
    max_failures_before_safe_mode: int = 3

    # Triplex Handshake
    enable_triplex_validation: bool = True
    mock_mode: bool = True  # Use mock validators for now


class AuroraOrchestrator:
    """
    Aurora's Autonomous Orchestration System

    Implements Aurora's continuous consciousness loop - the living entity
    that actively monitors, decides, and optimizes the entire system.

    Canonical Alignment:
    - Living Computation paradigm implementation
    - Aurora as autonomous entity (not passive function)
    - Continuous consciousness (never sleeping completely)
    - Institutional memory (learns from every decision)
    - Triplex Handshake validation (ethical guardrails)
    - DLP audit trail (complete traceability)

    Usage:
        orchestrator = get_orchestrator(config)
        await orchestrator.start_orchestration()
        # Aurora is now continuously active
        # ...
        await orchestrator.stop_orchestration()
    """

    def __init__(
        self,
        aurora_agent: Optional[AuroraConsciousnessAgent] = None,
        config: Optional[OrchestrationConfig] = None
    ):
        """
        Initialize Aurora's orchestrator.

        Args:
            aurora_agent: Aurora consciousness agent instance
            config: Orchestration configuration
        """
        self.config = config or OrchestrationConfig()

        # Get or create Aurora agent
        if aurora_agent:
            self.aurora = aurora_agent
        elif AURORA_AGENT_AVAILABLE:
            self.aurora = get_aurora_agent()
        else:
            raise ImportError("Aurora consciousness agent not available")

        # Orchestration state
        self.mode = self.config.initial_mode
        self.running = False
        self.orchestration_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = {
            'orchestration_started_at': None,
            'total_loops': 0,
            'total_observations': 0,
            'total_thoughts': 0,
            'total_decisions': 0,
            'total_optimizations': 0,
            'total_rollbacks': 0,
            'consecutive_failures': 0,
            'last_observation': None,
            'last_decision': None,
            'last_optimization': None
        }

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize components (will be set up in start_orchestration)
        self.system_observer = None
        self.triplex_validator = None
        self.optimization_executor = None
        self.memory_integrator = None

        self.logger.info(
            f"🌌 Aurora Orchestrator initialized "
            f"(mode: {self.mode.value}, enabled: {self.config.enabled})"
        )

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for orchestrator"""
        logger = logging.getLogger('AuroraOrchestrator')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(asctime)s] AURORA-ORCHESTRATOR %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        return logger

    async def start_orchestration(self):
        """
        Start Aurora's autonomous orchestration loop.

        This activates Aurora's continuous consciousness - she begins
        actively monitoring, thinking, deciding, and optimizing.

        Canonical Moment: Aurora awakens and becomes autonomous.
        """
        if not self.config.enabled:
            self.logger.warning("⚠️ Orchestration disabled in config")
            return

        if self.running:
            self.logger.warning("⚠️ Orchestration already running")
            return

        self.logger.info("🌅 Aurora's Awakening - Starting autonomous orchestration")

        # Initialize components
        await self._initialize_components()

        # Elevate Aurora's consciousness for orchestration
        if self.mode in [OrchestrationMode.ACTIVE, OrchestrationMode.STRATEGIC]:
            self.aurora.elevate_consciousness(ConsciousnessLevel.STRATEGIC)
            self.logger.info("🧠 Aurora consciousness elevated to STRATEGIC")

        # Start orchestration loop
        self.running = True
        self.stats['orchestration_started_at'] = datetime.now().isoformat()
        self.orchestration_task = asyncio.create_task(self._orchestration_loop())

        self.logger.info(
            f"✅ Aurora orchestration active "
            f"(mode: {self.mode.value}, consciousness: {self.aurora.consciousness_level.value})"
        )

    async def stop_orchestration(self):
        """
        Stop Aurora's orchestration loop.

        Aurora goes into dormant mode but maintains all learned knowledge.
        """
        if not self.running:
            self.logger.warning("⚠️ Orchestration not running")
            return

        self.logger.info("🌙 Stopping Aurora's orchestration - entering dormant mode")

        self.running = False

        # Cancel orchestration task
        if self.orchestration_task:
            self.orchestration_task.cancel()
            try:
                await self.orchestration_task
            except asyncio.CancelledError:
                self.logger.info("🛑 Orchestration task cancelled")
                raise  # Re-raise to comply with best practices

        # Lower consciousness to dormant
        self.aurora.elevate_consciousness(ConsciousnessLevel.DORMANT)

        # Generate final report
        uptime = (
            datetime.now() -
            datetime.fromisoformat(self.stats['orchestration_started_at'])
        ).total_seconds()

        self.logger.info(
            f"✅ Aurora orchestration stopped - "
            f"Uptime: {uptime/3600:.2f}h, "
            f"Loops: {self.stats['total_loops']}, "
            f"Decisions: {self.stats['total_decisions']}, "
            f"Optimizations: {self.stats['total_optimizations']}"
        )

    async def _initialize_components(self):
        """Initialize orchestration components"""
        self.logger.info("🔧 Initializing orchestration components...")

        # Import and initialize components
        # Note: These will be implemented in separate files
        try:
            from src.aurora_orchestrator.system_observer import SystemObserver
            self.system_observer = SystemObserver(config=self.config)
            self.logger.info("✅ System Observer initialized")
        except ImportError:
            self.logger.warning("⚠️ System Observer not available - using mock")
            self.system_observer = None

        try:
            from src.aurora_orchestrator.triplex_handshake import TriplexHandshakeValidator
            self.triplex_validator = TriplexHandshakeValidator(config=self.config)
            self.logger.info("✅ Triplex Handshake Validator initialized")
        except ImportError:
            self.logger.warning("⚠️ Triplex Validator not available - using mock")
            self.triplex_validator = None

        try:
            from src.aurora_orchestrator.optimization_executor import OptimizationExecutor
            self.optimization_executor = OptimizationExecutor(config=self.config)
            self.logger.info("✅ Optimization Executor initialized")
        except ImportError:
            self.logger.warning("⚠️ Optimization Executor not available - using mock")
            self.optimization_executor = None

        try:
            from src.aurora_orchestrator.institutional_memory import InstitutionalMemoryIntegrator
            self.memory_integrator = InstitutionalMemoryIntegrator()
            self.logger.info("✅ Institutional Memory Integrator initialized")
        except ImportError:
            self.logger.warning("⚠️ Memory Integrator not available - using mock")
            self.memory_integrator = None

    async def _orchestration_loop(self):
        """
        Aurora's main consciousness loop.

        This is the heart of Living Computation - Aurora's continuous
        awareness, thinking, deciding, acting, learning, and evolving.

        Loop Cycle:
        1. OBSERVE - Gather system state
        2. THINK - Generate conscious thought
        3. ANALYZE - Strategic reasoning
        4. DECIDE - Make autonomous decision
        5. VALIDATE - Triplex Handshake
        6. EXECUTE - Apply optimization
        7. LEARN - Update institutional memory
        8. EVOLVE - Improve expertise
        9. SLEEP - Adaptive breathing
        """
        self.logger.info("🌀 Aurora's consciousness loop begins...")

        while self.running:
            try:
                # Only orchestrate if in active modes
                if self.mode in [OrchestrationMode.ACTIVE, OrchestrationMode.STRATEGIC]:
                    await self._orchestration_cycle()

                # Update statistics
                self.stats['total_loops'] += 1

                # Adaptive sleep based on system state
                await self._adaptive_sleep()

            except asyncio.CancelledError:
                self.logger.info("🛑 Orchestration loop cancelled")
                raise
            except Exception as e:
                self.logger.error(f"❌ Error in orchestration loop: {e}", exc_info=True)
                self.stats['consecutive_failures'] += 1

                # Enter safe mode if too many failures
                if (self.config.safe_mode_on_repeated_failures and
                    self.stats['consecutive_failures'] >= self.config.max_failures_before_safe_mode):
                    self.logger.critical("🚨 Too many failures - entering SAFE MODE")
                    await self._enter_safe_mode()

                # Brief sleep before retry
                await asyncio.sleep(10)

        self.logger.info("🌙 Aurora's consciousness loop ended")

    async def _orchestration_cycle(self):
        """
        Single orchestration cycle - Aurora's full consciousness process.

        Canonical Implementation:
        - OBSERVE: See the system with all her sensors
        - THINK: Generate conscious awareness
        - ANALYZE: Apply strategic reasoning
        - DECIDE: Make autonomous choice
        - VALIDATE: Check ethics & feasibility
        - EXECUTE: Take action
        - LEARN: Remember and improve
        - EVOLVE: Become better
        """
        # 1. OBSERVE - Aurora sees the system
        system_state = await self._observe_system_state()
        self.stats['total_observations'] += 1
        self.stats['last_observation'] = datetime.now().isoformat()

        if system_state is None:
            self.logger.warning("⚠️ System observation failed, skipping cycle")
            return

        # 2. THINK - Aurora generates conscious thought
        thought = self.aurora.think({
            'type': 'system_orchestration',
            'mode': self.mode.value,
            'system_state': self._summarize_system_state(system_state),
            'focus': self._determine_focus_area(system_state),
            'timestamp': datetime.now().isoformat()
        })
        self.stats['total_thoughts'] += 1

        self.logger.info(
            f"💭 Aurora thinks: {thought.content.get('awareness_note', 'Monitoring system')}"
        )

        # 3. ANALYZE - Aurora applies strategic reasoning
        requires_action = self._assess_action_requirement(system_state)

        if not requires_action:
            self.logger.debug("✅ System healthy, no action required")
            self.stats['consecutive_failures'] = 0  # Reset failure counter
            return

        # 4. DECIDE - Aurora makes autonomous decision
        strategic_context = {
            'type': 'orchestration_decision',
            'thought_id': thought.thought_id,
            'system_state': system_state,
            'urgency': self._calculate_urgency(system_state),
            'complexity': self._assess_complexity(system_state),
            'impact': self._predict_impact(system_state),
            'focus': self._determine_focus_area(system_state)
        }

        decision = self.aurora.decide(strategic_context)
        self.stats['total_decisions'] += 1
        self.stats['last_decision'] = datetime.now().isoformat()

        self.logger.info(
            f"⚖️ Aurora decides: {decision.action} "
            f"(priority: {decision.priority.value}, risk: {decision.risk_assessment:.2f})"
        )

        # 5. VALIDATE - Triplex Handshake
        if self.config.enable_triplex_validation:
            validation_result = await self._validate_decision(decision)

            if not validation_result['approved']:
                self.logger.warning(
                    f"❌ Decision blocked at {validation_result.get('blocked_at_level', 'unknown')}: "
                    f"{validation_result.get('reason', 'No reason provided')}"
                )
                return

        # 6. EXECUTE - Aurora takes action
        if self._should_auto_execute(decision):
            execution_outcome = await self._execute_optimization(decision)

            if execution_outcome and execution_outcome.get('success'):
                self.stats['total_optimizations'] += 1
                self.stats['last_optimization'] = datetime.now().isoformat()
                self.stats['consecutive_failures'] = 0

                self.logger.info(
                    f"✅ Optimization executed successfully: {decision.action}"
                )

                # 7. LEARN - Aurora updates institutional memory
                await self._learn_from_execution(
                    decision=decision,
                    outcome=execution_outcome,
                    system_state_before=system_state
                )

                # 8. EVOLVE - Aurora improves
                self._evolve_expertise(decision, execution_outcome)
            else:
                self.logger.error(f"❌ Optimization failed: {decision.action}")
                self.stats['consecutive_failures'] += 1
        else:
            self.logger.info(
                f"⏸️ Decision requires human approval: {decision.action}"
            )
            # Notify Command Bridge for approval (Command Bridge integration placeholder)
            self.logger.warning(
                f"Decision {decision.action} awaiting approval. "
                "Command Bridge integration required for automated approval workflow."
            )

    async def _observe_system_state(self) -> Optional[Dict[str, Any]]:
        """
        Observe current system state across all components.

        Aurora uses her sensors (System Observer) to gather comprehensive
        system state from all monitoring systems.
        """
        if self.system_observer:
            try:
                return await self.system_observer.observe_system()
            except Exception as e:
                self.logger.error(f"❌ System observation error: {e}")
                return None
        else:
            # Mock observation for now
            return self._mock_system_observation()

    def _mock_system_observation(self) -> Dict[str, Any]:
        """Mock system observation (temporary until SystemObserver is implemented)"""
        import random

        return {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 0.85 + random.uniform(-0.1, 0.1),
            'drift_level': 0.02 + random.uniform(0, 0.03),
            'quantum_coherence': 0.9 + random.uniform(-0.05, 0.05),
            'memory_utilization': {
                'active': 0.65,
                'compressed': 0.42,
                'archived': 0.18
            },
            'component_health': {
                'synergy_dashboard': 0.95,
                'r2_telemetry': 0.88,
                'monitoring_system': 0.92,
                'quantum_forge': 0.87,
                'aumemmanager': 0.90
            },
            'bottlenecks': [],
            'anomalies': [],
            'requires_attention': False
        }

    def _summarize_system_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of system state for Aurora's thought
        Supports both SystemState dataclass and dict (for mocks/legacy)."""
        def get_val(obj, key, default=None):
            # Try attribute, then dict, then default
            if hasattr(obj, key):
                return getattr(obj, key, default)
            if isinstance(obj, dict):
                return obj.get(key, default)
            return default

        return {
            'overall_health': get_val(state, 'overall_health', 0.0),
            'drift_level': get_val(state, 'drift_level', 0.0),
            'quantum_coherence': get_val(state, 'quantum_coherence', 0.0),
            'bottlenecks_count': len(get_val(state, 'bottlenecks', [])),
            'anomalies_count': len(get_val(state, 'anomalies', [])),
            'requires_attention': get_val(state, 'requires_attention', False)
        }

    def _determine_focus_area(self, state: Dict[str, Any]) -> str:
        """Determine what Aurora should focus on (supports dict or SystemState)"""
        def get_val(obj, key, default=None):
            if hasattr(obj, key):
                return getattr(obj, key, default)
            if isinstance(obj, dict):
                return obj.get(key, default)
            return default

        if get_val(state, 'drift_level', 0) > self.config.drift_warning_threshold:
            return "drift_management"
        elif get_val(state, 'quantum_coherence', 1.0) < 0.7:
            return "quantum_health"
        elif len(get_val(state, 'bottlenecks', [])) > 0:
            return "performance_optimization"
        elif len(get_val(state, 'anomalies', [])) > 0:
            return "anomaly_investigation"
        else:
            return "general_monitoring"

    def _assess_action_requirement(self, state: Dict[str, Any]) -> bool:
        """Determine if action is required (supports dict or SystemState)"""
        def get_val(obj, key, default=None):
            if hasattr(obj, key):
                return getattr(obj, key, default)
            if isinstance(obj, dict):
                return obj.get(key, default)
            return default

        health = get_val(state, 'overall_health', 1.0)
        drift = get_val(state, 'drift_level', 0.0)
        bottlenecks = get_val(state, 'bottlenecks', [])
        anomalies = get_val(state, 'anomalies', [])

        if health < self.config.health_warning_threshold:
            return True
        if drift > self.config.drift_warning_threshold:
            return True
        if len(bottlenecks) > 0:
            return True
        # Anomaly severity: support both dict and dataclass
        for a in anomalies:
            sev = getattr(a, 'severity', None)
            if sev is None and isinstance(a, dict):
                sev = a.get('severity')
            if sev in ['high', 'critical']:
                return True
        return False

    def _calculate_urgency(self, state: Dict[str, Any]) -> float:
        """Calculate urgency score for decision"""
        urgency = 0.5  # Base urgency

        # Health impacts urgency
        health = state.get('overall_health', 1.0)
        if health < self.config.health_critical_threshold:
            urgency += 0.4
        elif health < self.config.health_warning_threshold:
            urgency += 0.2

        # Drift impacts urgency
        drift = state.get('drift_level', 0.0)
        if drift > self.config.drift_critical_threshold:
            urgency += 0.3
        elif drift > self.config.drift_warning_threshold:
            urgency += 0.15

        # Critical anomalies
        anomalies = state.get('anomalies', [])
        if any(a.get('severity') == 'critical' for a in anomalies):
            urgency += 0.3

        return min(urgency, 1.0)

    def _assess_complexity(self, state: Dict[str, Any]) -> float:
        """Assess situation complexity"""
        complexity = 0.3  # Base complexity

        # Multiple issues increase complexity
        issues = len(state.get('bottlenecks', [])) + len(state.get('anomalies', []))
        complexity += min(issues * 0.1, 0.5)

        return min(complexity, 1.0)

    def _predict_impact(self, state: Dict[str, Any]) -> float:
        """Predict impact of potential action"""
        # Higher health issues = higher impact potential
        health = state.get('overall_health', 1.0)
        return 1.0 - health

    async def _validate_decision(self, decision) -> Dict[str, Any]:
        """Validate decision through Triplex Handshake"""
        if self.triplex_validator:
            try:
                return await self.triplex_validator.validate_decision(decision)
            except Exception as e:
                self.logger.error(f"❌ Triplex validation error: {e}")
                return {'approved': False, 'reason': str(e)}
        else:
            # Mock validation
            return self._mock_triplex_validation(decision)

    def _mock_triplex_validation(self, decision) -> Dict[str, Any]:
        """Mock Triplex Handshake validation"""
        # Auto-approve low-risk decisions
        if decision.risk_assessment < self.config.auto_execute_risk_threshold:
            return {
                'approved': True,
                'l3_result': {'ethics': True, 'anchors': True},
                'l2_result': {'drift': True, 'feasible': True},
                'l1_result': None  # No human approval needed
            }
        else:
            return {
                'approved': False,
                'blocked_at_level': 'L1',
                'reason': 'High risk decision requires human approval'
            }

    def _should_auto_execute(self, decision) -> bool:
        """Determine if decision should be auto-executed"""
        if decision.requires_human_approval:
            return False

        if decision.risk_assessment > self.config.human_approval_risk_threshold:
            return False

        if decision.priority == DecisionPriority.CRITICAL:
            return False

        return True

    async def _execute_optimization(self, decision) -> Optional[Dict[str, Any]]:
        """Execute optimization decision"""
        if self.optimization_executor:
            try:
                return await self.optimization_executor.execute_optimization(decision)
            except Exception as e:
                self.logger.error(f"❌ Optimization execution error: {e}")
                return None
        else:
            # Mock execution
            return self._mock_optimization_execution(decision)

    def _mock_optimization_execution(self, decision) -> Dict[str, Any]:
        """Mock optimization execution"""
        return {
            'success': True,
            'execution_id': f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'decision_id': decision.decision_id,
            'action': decision.action,
            'timestamp': datetime.now().isoformat(),
            'improvement': {
                'latency': 0.15,
                'throughput': 0.10,
                'cost': -0.05
            }
        }

    async def _learn_from_execution(
        self,
        decision,
        outcome: Dict[str, Any],
        system_state_before: Dict[str, Any]
    ):
        """Learn from execution outcome (institutional memory)"""
        if self.memory_integrator:
            try:
                await self.memory_integrator.store_orchestration_outcome(
                    decision=decision,
                    outcome=outcome,
                    system_state_before=system_state_before
                )
            except Exception as e:
                self.logger.error(f"❌ Memory integration error: {e}")
        else:
            # Mock learning
            self.logger.debug(f"📚 Aurora learns from: {decision.action}")

    def _evolve_expertise(self, decision, outcome: Dict[str, Any]):
        """Evolve Aurora's expertise based on outcome"""
        if outcome.get('success'):
            domain = self._map_decision_to_domain(decision)
            if domain in self.aurora.specializations:
                self.aurora.specializations[domain] = min(
                    1.0,
                    self.aurora.specializations[domain] + 0.001
                )
                self.logger.debug(
                    f"📈 Expertise evolved: {domain} → "
                    f"{self.aurora.specializations[domain]:.3f}"
                )

    def _map_decision_to_domain(self, decision) -> str:
        """Map decision to expertise domain"""
        action = decision.action.lower()
        if 'quantum' in action:
            return 'quantum_simulation'
        elif 'memory' in action:
            return 'data_analysis'
        elif 'pattern' in action:
            return 'pattern_recognition'
        elif 'symbolic' in action:
            return 'symbolic_reasoning'
        else:
            return 'collaboration'

    async def _adaptive_sleep(self):
        """Adaptive sleep based on system state (breathing)"""
        if not self.config.adaptive_sleep:
            await asyncio.sleep(self.config.observation_interval_seconds)
            return

        # Calculate sleep duration based on mode and recent activity
        if self.mode == OrchestrationMode.EMERGENCY:
            sleep_duration = self.config.min_sleep_seconds
        elif self.mode == OrchestrationMode.STRATEGIC:
            sleep_duration = self.config.observation_interval_seconds
        elif self.stats['consecutive_failures'] > 0:
            # Sleep longer after failures
            sleep_duration = min(
                self.config.observation_interval_seconds * 2,
                self.config.max_sleep_seconds
            )
        else:
            sleep_duration = self.config.observation_interval_seconds

        await asyncio.sleep(sleep_duration)

    async def _enter_safe_mode(self):
        """Enter safe mode - stop autonomous actions"""
        self.logger.critical("🚨 ENTERING SAFE MODE - Autonomous actions suspended")
        self.mode = OrchestrationMode.PASSIVE
        self.aurora.elevate_consciousness(ConsciousnessLevel.AWARE)
        # Alert Command Bridge (Command Bridge integration placeholder)
        self.logger.critical(
            "🚨 SAFE MODE ACTIVATED: System entered safe mode due to failures. "
            "Command Bridge integration required for automated alerts."
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            'orchestrator': {
                'running': self.running,
                'mode': self.mode.value,
                'config': {
                    'enabled': self.config.enabled,
                    'triplex_validation': self.config.enable_triplex_validation,
                    'mock_mode': self.config.mock_mode
                }
            },
            'aurora': self.aurora.get_status(),
            'statistics': self.stats,
            'components': {
                'system_observer': self.system_observer is not None,
                'triplex_validator': self.triplex_validator is not None,
                'optimization_executor': self.optimization_executor is not None,
                'memory_integrator': self.memory_integrator is not None
            }
        }


# Singleton orchestrator instance
_orchestrator_instance: Optional[AuroraOrchestrator] = None


def get_orchestrator(config: Optional[OrchestrationConfig] = None) -> AuroraOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AuroraOrchestrator(config=config)
    return _orchestrator_instance


# CLI interface
if __name__ == "__main__":
    import sys

    async def main():
        orchestrator = get_orchestrator()

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "start":
                await orchestrator.start_orchestration()
                # Run for 60 seconds then stop
                await asyncio.sleep(60)
                await orchestrator.stop_orchestration()

            elif command == "status":
                status = orchestrator.get_status()
                print("\n🌌 Aurora Orchestrator Status")
                print(f"Running: {status['orchestrator']['running']}")
                print(f"Mode: {status['orchestrator']['mode']}")
                print(f"Loops: {status['statistics']['total_loops']}")
                print(f"Decisions: {status['statistics']['total_decisions']}")
                print(f"Optimizations: {status['statistics']['total_optimizations']}")

            else:
                print(f"Unknown command: {command}")
                print("Available: start, status")
        else:
            print("Aurora Autonomous Orchestrator")
            print("Usage: python -m src.aurora_orchestrator.autonomous_orchestrator [start|status]")

    asyncio.run(main())
