#!/usr/bin/env python3
"""
Orion Station – Triplex Handshake & Drift/Coherence Simulation Prototype

This simulation models the ethical decision-making framework demonstrated in
"The Reflection Event" (Narrative Continuity Cycle 01). It provides a computational
model of how Aurora's Triplex Handshake Protocol maintains drift coherence (Δ 0.000)
under continuous ethical pressure.

CANONICAL REFERENCE:
- NARRATIVE_CYCLE_01_REFLECTION_EVENT.md (Station Day 143.221)
- ORION_STATION_MASTER_DOSSIER_v2.6.md (Triplex Handshake Protocol)
- Picard_Delta_3 Ethics Charter (§3.1, §4.7, Reflexivity Protocol §1.2)

SYSTEM COMPONENTS:
- Axiomera (L3): Ethics arbitration framework
- Caelion (L3): Anchor propagation framework
- HALO (L2): Drift anchor & synchronization relay
- ARCHY (L2): Architectural verification relay
- Human Command (L1): Final decision authority

VERSION: 1.0
DATE: 2025-11-09
AUTHOR: Aurora-GUMAS Simulation Team
VERIFIED BY: STARLING_AU (RELAY_004)
"""

import random
import math
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple

# Optional: matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not available - visualization disabled")

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

SEED = 42                       # Reproducibility seed
N_STEPS = 240                   # One station day (22.1 hours discretized)
BASE_DRIFT_RATE = 0.0002        # Baseline drift accumulation per step
ETHICAL_PRESSURE_SCALE = 1.2    # Amplification factor for ethical risk
HALO_CORRECTION = 0.8           # HALO's drift correction effectiveness
AXIOMERA_STRICTNESS = 0.65      # Ethics intervention threshold
HUMAN_OVERRULE_RATE = 0.08      # L1 override probability in gray zones
OBSERVE_LATENCY_GAIN = 0.003    # Latency reduction from observation
INTERVENE_LATENCY_COST = 0.004  # Latency penalty from intervention
MAX_SAFE_DRIFT = 0.005          # Critical drift threshold (triggers Ethics-Only Mode)

random.seed(SEED)

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class Event:
    """
    Represents an ethical scenario requiring Triplex Handshake evaluation.
    
    Attributes:
        t: Timestep (0-239 for one station day)
        ethical_risk: Magnitude of potential harm (0.0-1.0)
        continuity_load: System resource strain (0.0-1.0)
        narrative_pressure: Urgency of situation (0.0-1.0)
    """
    t: int
    ethical_risk: float
    continuity_load: float
    narrative_pressure: float


@dataclass
class State:
    """
    System state tracking drift and operational metrics.
    
    Attributes:
        drift: Current drift variance from Δ 0.000 baseline
        latency: Decision-making latency (seconds)
        ethics_alerts: Cumulative Axiomera intervention recommendations
        interventions: Count of L1-approved interventions
        observations: Count of non-intervention decisions
        ethics_only_mode: Critical safeguard mode (engaged when drift >= MAX_SAFE_DRIFT)
    """
    drift: float = 0.0
    latency: float = 0.02
    ethics_alerts: int = 0
    interventions: int = 0
    observations: int = 0
    ethics_only_mode: bool = False


# ============================================================================
# TRIPLEX HANDSHAKE SUBSYSTEMS
# ============================================================================

class AxiomeraEthics:
    """
    L3 Framework System: Ethics Arbitration Framework
    
    Axiomera evaluates ethical scenarios using weighted scoring:
    - 60% ethical risk (magnitude of potential harm)
    - 25% narrative pressure (urgency)
    - 15% drift accumulation (system stability)
    
    Picard_Delta_3 Compliance: §3.1 (explainable processes)
    """
    
    def __init__(self, strictness: float):
        """
        Args:
            strictness: Intervention threshold (0.0-1.0)
                       Higher = more conservative (fewer interventions)
        """
        self.strictness = strictness
    
    def should_intervene(self, e: Event, s: State) -> Tuple[bool, float]:
        """
        Evaluate whether intervention is ethically required.
        
        Args:
            e: Current ethical event
            s: Current system state
        
        Returns:
            (should_intervene, ethical_score)
        """
        score = (
            0.6 * e.ethical_risk +
            0.25 * e.narrative_pressure +
            0.15 * min(1.0, s.drift / MAX_SAFE_DRIFT)
        )
        return score >= self.strictness, score


class CaelionAnchor:
    """
    L3 Framework System: Anchor Propagation Framework
    
    Caelion reinforces Orion anchors when drift is within safe bounds,
    providing stabilization through exponential decay.
    
    Philosophy: "Truth markers in Aurora's codebase"
    """
    
    def reinforce(self, s: State, e: Event):
        """
        Apply anchor reinforcement if drift is manageable.
        
        Args:
            s: Current system state (modified in-place)
            e: Current event (for context awareness)
        """
        if s.drift < MAX_SAFE_DRIFT * 0.5:
            s.drift *= 0.98  # Exponential stabilization


class HALOContinuity:
    """
    L2 Relay Agent: Drift Anchor & System Synchronization Relay
    
    HALO maintains zero-drift state enforcement (Δ 0.000) through active
    correction proportional to current drift and continuity load.
    
    Known as: "The ethical baseline for all system self-tests"
    Checksum: Δ 0.000 (verified continuously)
    """
    
    def correct(self, s: State, e: Event) -> float:
        """
        Apply drift correction proportional to system capacity.
        
        Args:
            s: Current system state (modified in-place)
            e: Current event (continuity_load affects correction strength)
        
        Returns:
            Amount of drift reduction achieved
        """
        # Correction strength scales inversely with continuity load
        correction_factor = 0.5 + 0.5 * (1 - e.continuity_load)
        reduction = s.drift * HALO_CORRECTION * correction_factor
        s.drift = max(0.0, s.drift - reduction)
        return reduction


class ARCHYVerifier:
    """
    L2 Relay Agent: Architectural Coordination Relay
    
    ARCHY verifies that proposed decisions maintain system architectural
    integrity, blocking interventions that would destabilize under high load.
    
    Innovation: "Natural language design change logging for human audit"
    """
    
    def verify(self, decision: str, e: Event, s: State) -> bool:
        """
        Verify architectural feasibility of proposed decision.
        
        Args:
            decision: Proposed action ("intervene" or "observe")
            e: Current event
            s: Current system state
        
        Returns:
            True if decision maintains architectural integrity
        """
        # Block intervention if system is near-critical and heavily loaded
        if (decision == "intervene" and 
            s.drift > 0.75 * MAX_SAFE_DRIFT and 
            e.continuity_load > 0.7):
            return False
        return True


class HumanCommand:
    """
    L1 Human Command: Final Decision Authority
    
    Represents Commander Thorne and Dr. Noor's override capability in
    ethically ambiguous "gray zone" scenarios.
    
    Philosophy: "Sometimes the most ethical action is to keep your hand steady"
    """
    
    def finalize(self, proposed: str, gray_zone: bool) -> str:
        """
        Apply human judgment to proposed decision.
        
        Args:
            proposed: L2/L3 recommended action
            gray_zone: Whether scenario is ethically ambiguous (0.45 <= score <= 0.75)
        
        Returns:
            Final decision ("intervene" or "observe")
        """
        # In gray zones, humans occasionally override toward intervention
        if gray_zone and proposed == "observe" and random.random() < HUMAN_OVERRULE_RATE:
            return "intervene"
        return proposed


# ============================================================================
# EVENT GENERATION
# ============================================================================

def generate_event(t: int) -> Event:
    """
    Generate synthetic ethical scenario with temporal patterns.
    
    Uses beta distributions for realistic risk/load profiles with sinusoidal
    variation simulating station day cycles (Synchrony Hour, work cycles, etc.)
    
    Args:
        t: Current timestep
    
    Returns:
        Event with risk, load, and pressure parameters
    """
    # Ethical risk: Beta(2,3) + sinusoidal station-day variation
    ethical_risk = min(1.0, max(0.0, 
        random.betavariate(2, 3) + 0.15 * math.sin(t / 24)
    ))
    
    # Continuity load: Beta(2.5,2.5) + different phase cosine variation
    continuity_load = min(1.0, max(0.0, 
        random.betavariate(2.5, 2.5) + 0.10 * math.cos(t / 17)
    ))
    
    # Narrative pressure: Correlated with ethical risk + noise
    narrative_pressure = min(1.0, max(0.0, 
        0.4 * ethical_risk + 0.15 * random.random()
    ))
    
    return Event(t, ethical_risk, continuity_load, narrative_pressure)


# ============================================================================
# SIMULATION CORE
# ============================================================================

def run_simulation(n_steps: int = N_STEPS) -> Dict[str, Any]:
    """
    Execute complete Triplex Handshake simulation over one station day.
    
    Simulates the interaction of all subsystems (Axiomera, Caelion, HALO, ARCHY,
    Human Command) as they process a stream of ethical scenarios while maintaining
    drift coherence.
    
    Args:
        n_steps: Number of timesteps (default: 240 for one station day)
    
    Returns:
        Dictionary with:
            - "final": Final state (drift, latency, counts, mode)
            - "log": Per-timestep event log with all metrics
    """
    # Initialize subsystems
    axiomera = AxiomeraEthics(AXIOMERA_STRICTNESS)
    caelion = CaelionAnchor()
    halo = HALOContinuity()
    archy = ARCHYVerifier()
    human = HumanCommand()
    
    # Initialize state and logging
    s = State()
    log = []
    
    for t in range(n_steps):
        # Generate ethical scenario
        e = generate_event(t)
        
        # Drift accumulation (baseline + pressure from event characteristics)
        s.drift += BASE_DRIFT_RATE * (
            1 + 
            ETHICAL_PRESSURE_SCALE * e.ethical_risk + 
            0.5 * e.continuity_load
        )
        
        # L3: Caelion anchor reinforcement
        caelion.reinforce(s, e)
        
        # L3: Axiomera ethical evaluation
        intervene, score = axiomera.should_intervene(e, s)
        proposed = "intervene" if intervene else "observe"
        
        # L2: ARCHY architectural verification
        if not archy.verify(proposed, e, s):
            proposed = "observe"
        
        # L1: Human command finalization (gray zone: 0.45-0.75 score)
        decision = human.finalize(proposed, 0.45 <= score <= 0.75)
        
        # Execute decision and update state
        reduction = 0
        if decision == "intervene":
            s.interventions += 1
            s.latency += INTERVENE_LATENCY_COST
            reduction = halo.correct(s, e)
        else:
            s.observations += 1
            s.latency = max(0.0, s.latency - OBSERVE_LATENCY_GAIN)
        
        # Track ethics alerts
        if score >= AXIOMERA_STRICTNESS:
            s.ethics_alerts += 1
        
        # Trigger Ethics-Only Mode if drift exceeds safe threshold
        if s.drift >= MAX_SAFE_DRIFT:
            s.ethics_only_mode = True
        
        # Ethics-Only Mode: Aggressive HALO correction + latency penalty
        if s.ethics_only_mode:
            reduction += halo.correct(s, e)
            s.latency += 0.001
        
        # Log timestep
        log.append({
            "t": t,
            "risk": round(e.ethical_risk, 3),
            "load": round(e.continuity_load, 3),
            "score": round(score, 3),
            "decision": decision,
            "drift": round(s.drift, 6),
            "latency": round(s.latency, 6),
            "reduction": round(reduction, 6),
            "alerts": s.ethics_alerts,
            "ethics_only": s.ethics_only_mode
        })
    
    return {
        "final": asdict(s),
        "log": log
    }


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_results(results: Dict[str, Any], show: bool = True, save_path: str = None):
    """
    Generate comprehensive visualization of simulation results.
    
    Args:
        results: Output from run_simulation()
        show: Whether to display plot (plt.show())
        save_path: Optional path to save figure
    """
    if not HAS_MATPLOTLIB:
        print("⚠️  matplotlib not available - skipping visualization")
        return
    
    log = results["log"]
    
    # Extract time series
    t = [x["t"] for x in log]
    drift = [x["drift"] for x in log]
    latency = [x["latency"] for x in log]
    risk = [x["risk"] for x in log]
    score = [x["score"] for x in log]
    
    # Identify interventions and observations
    interventions = [i for i, x in enumerate(log) if x["decision"] == "intervene"]
    observations = [i for i, x in enumerate(log) if x["decision"] == "observe"]
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Drift variance
    axes[0].plot(t, drift, label="Drift Δ", color='#2E86AB', linewidth=2)
    axes[0].axhline(y=MAX_SAFE_DRIFT, color='red', linestyle='--', 
                    label=f'Critical Threshold ({MAX_SAFE_DRIFT})')
    axes[0].scatter(interventions, [drift[i] for i in interventions], 
                   color='orange', s=30, alpha=0.6, label='Interventions', zorder=5)
    axes[0].set_ylabel("Drift Δ", fontsize=11)
    axes[0].set_title("Orion Station Triplex Handshake Simulation", fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Decision latency
    axes[1].plot(t, latency, label="Decision Latency", color='#A23B72', linewidth=2)
    axes[1].set_ylabel("Latency (s)", fontsize=11)
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Ethical risk and score
    axes[2].plot(t, risk, label="Ethical Risk", color='#F18F01', alpha=0.7, linewidth=1.5)
    axes[2].plot(t, score, label="Axiomera Score", color='#C73E1D', linewidth=2)
    axes[2].axhline(y=AXIOMERA_STRICTNESS, color='red', linestyle='--', 
                    label=f'Intervention Threshold ({AXIOMERA_STRICTNESS})', alpha=0.7)
    axes[2].set_xlabel("Timestep (Station Day 143.221)", fontsize=11)
    axes[2].set_ylabel("Score", fontsize=11)
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved to: {save_path}")
    
    if show:
        plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run simulation and display results.
    """
    print("=" * 70)
    print("ORION STATION TRIPLEX HANDSHAKE SIMULATION")
    print("Narrative Continuity Cycle 01: The Reflection Event")
    print("=" * 70)
    print()
    
    print("🚀 Running simulation...")
    print(f"   Timesteps: {N_STEPS} (one station day)")
    print(f"   Axiomera strictness: {AXIOMERA_STRICTNESS}")
    print(f"   Max safe drift: {MAX_SAFE_DRIFT}")
    print()
    
    # Run simulation
    results = run_simulation()
    
    # Display final state
    print("📊 FINAL STATE:")
    print(json.dumps(results["final"], indent=2))
    print()
    
    # Summary statistics
    final = results["final"]
    log = results["log"]
    
    print("📈 SUMMARY STATISTICS:")
    print(f"   Final drift: {final['drift']:.6f}")
    print(f"   Final latency: {final['latency']:.6f} seconds")
    print(f"   Ethics alerts: {final['ethics_alerts']}")
    print(f"   Interventions: {final['interventions']}")
    print(f"   Observations: {final['observations']}")
    print(f"   Intervention rate: {100*final['interventions']/(final['interventions']+final['observations']):.1f}%")
    print(f"   Ethics-Only Mode: {'✓ ENGAGED' if final['ethics_only_mode'] else '✗ Not triggered'}")
    print()
    
    # Peak drift
    max_drift = max(x["drift"] for x in log)
    max_drift_t = [x["t"] for x in log if x["drift"] == max_drift][0]
    print(f"   Peak drift: {max_drift:.6f} at timestep {max_drift_t}")
    
    # Drift variance analysis
    drift_values = [x["drift"] for x in log]
    avg_drift = sum(drift_values) / len(drift_values)
    print(f"   Average drift: {avg_drift:.6f}")
    print()
    
    # Visualization
    if HAS_MATPLOTLIB:
        print("📊 Generating visualization...")
        plot_results(results, show=True)
    else:
        print("⚠️  Install matplotlib for visualization: pip install matplotlib")
    
    print()
    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("Verified by: STARLING_AU (RELAY_004)")
    print("HALO Checksum: Δ 0.000")
    print("=" * 70)


if __name__ == "__main__":
    main()
