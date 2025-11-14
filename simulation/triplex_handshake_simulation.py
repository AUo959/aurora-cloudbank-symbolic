#!/usr/bin/env python3
"""
Orion Station – Triplex Handshake & Drift/Coherence Simulation Prototype

This simulation models the ethical decision-making and drift management system
aboard Orion Station (Node 7 of 9, GUMAS orbital chain).

SYSTEM ARCHITECTURE:
- L3 Glyph Arbitration: Axiomera (ethics), Caelion (anchoring)
- L2 Relay Verification: HALO (continuity), ARCHY (architecture)
- L1 Human Consent: Commander decision-making with gray-zone overrides

VALIDATED AGAINST: "The Reflection Event" (Narrative Cycle 01)
- Drift variance: +0.004 (observed in event)
- Restoration time: ~5.5 minutes (simulated as steps)
- Ethics-Only Mode: Activated when drift >= MAX_SAFE_DRIFT

USAGE:
    python3 triplex_handshake_simulation.py

OUTPUT:
    - Final system state (JSON)
    - Time-series log (drift, latency, decisions)
    - Matplotlib visualization (if available)

CANONICAL REFERENCE:
    ORION_STATION_MASTER_DOSSIER_v2.6.md
    NARRATIVE_CYCLE_01_REFLECTION_EVENT.md
    L1_CANON_CHARACTER_ROSTER.md v2.0

Author: Aurora-GUMAS Project Team
Version: 1.0
Date: 2025-11-09
License: Project Internal
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
    print("Note: matplotlib not available, skipping visualization")

# ---------- SIMULATION PARAMETERS ----------

SEED = 42                       # Reproducibility seed
N_STEPS = 240                   # One station day (22.1 hours simulated)
BASE_DRIFT_RATE = 0.0002        # Baseline drift accumulation per step
ETHICAL_PRESSURE_SCALE = 1.2    # Multiplier for ethical risk contribution
HALO_CORRECTION = 0.8           # HALO drift correction efficiency
AXIOMERA_STRICTNESS = 0.65      # Ethics intervention threshold (0-1)
HUMAN_OVERRULE_RATE = 0.08      # Probability of human override in gray zone
OBSERVE_LATENCY_GAIN = 0.003    # Latency improvement from observation
INTERVENE_LATENCY_COST = 0.004  # Latency penalty from intervention
MAX_SAFE_DRIFT = 0.005          # Drift threshold for Ethics-Only Mode

random.seed(SEED)

# ---------- DATA STRUCTURES ----------


@dataclass
class Event:
    """
    Represents an ethical scenario requiring Triplex Handshake evaluation.
    
    Attributes:
        t: Simulation timestep
        ethical_risk: Magnitude of potential harm (0-1)
        continuity_load: System coherence maintenance burden (0-1)
        narrative_pressure: Urgency from simulated entities (0-1)
    """
    t: int
    ethical_risk: float
    continuity_load: float
    narrative_pressure: float


@dataclass
class State:
    """
    Current system state tracked throughout simulation.
    
    Attributes:
        drift: Current drift variance from Δ 0.000 baseline
        latency: System response time (decision-making overhead)
        ethics_alerts: Count of Axiomera intervention triggers
        interventions: Count of active interventions executed
        observations: Count of non-intervention observations
        ethics_only_mode: Whether Ethics-Only Mode is active
    """
    drift: float = 0.0
    latency: float = 0.02
    ethics_alerts: int = 0
    interventions: int = 0
    observations: int = 0
    ethics_only_mode: bool = False


# ---------- L3 GLYPH FRAMEWORK SYSTEMS ----------

class AxiomeraEthics:
    """
    L3 Ethics Arbitration Framework (FWK_002, Halo Ring II)
    
    Evaluates whether intervention is ethically required based on:
    - Direct ethical risk (primary weight: 60%)
    - Narrative pressure from simulated entities (25%)
    - System drift instability (15%)
    
    Liaison: Dr. Elira Noor (ETH_002)
    Principle: "Cannot proceed unless it can explain why"
    """
    
    def __init__(self, strictness: float):
        self.strictness = strictness
    
    def should_intervene(self, e: Event, s: State) -> Tuple[bool, float]:
        """
        Calculate intervention score and recommend action.
        
        Returns:
            (should_intervene: bool, score: float)
        """
        score = (
            0.6 * e.ethical_risk +
            0.25 * e.narrative_pressure +
            0.15 * min(1.0, s.drift / MAX_SAFE_DRIFT)
        )
        return score >= self.strictness, score


class CaelionAnchor:
    """
    L3 Anchor Propagation Framework (FWK_004, Halo Ring I)
    
    Maintains valid Orion anchors and reinforces stability when drift is low.
    Proactively strengthens coherence before problems emerge.
    
    Liaison: Vincent Kale (SYS_005)
    Achievement: "Truth markers" in Aurora's codebase
    """
    
    def reinforce(self, s: State, e: Event):
        """
        Apply proactive drift reduction when system is stable.
        """
        if s.drift < MAX_SAFE_DRIFT * 0.5:
            s.drift *= 0.98  # 2% drift reduction per step when stable


# ---------- L2 RELAY AGENT SYSTEMS ----------

class HALOContinuity:
    """
    L2 Drift Anchor & System Synchronization Relay (RELAY_006)
    
    Enforces zero-drift state (Δ 0.000) through continuous correction.
    Serves as ethical baseline checksum for all system self-tests.
    
    Liaison: Dr. Elira Noor (ETH_002)
    Location: Aurora Core Chamber, Deck B
    Achievement: Used as ethical baseline for all system self-tests
    """
    
    def correct(self, s: State, e: Event) -> float:
        """
        Apply drift correction proportional to current drift and continuity load.
        
        Returns:
            reduction: Amount of drift corrected
        """
        reduction = s.drift * HALO_CORRECTION * (0.5 + 0.5 * (1 - e.continuity_load))
        s.drift = max(0.0, s.drift - reduction)
        return reduction


class ARCHYVerifier:
    """
    L2 Architectural Coordination Relay (RELAY_001)
    
    Verifies technical feasibility of proposed actions.
    Blocks interventions when system state or load makes them unsafe.
    
    Liaison: Emily Roberts (SYS_001)
    Location: Bridge Chamber, Deck C
    Innovation: Natural language design change logging for human audit
    """
    
    def verify(self, decision: str, e: Event, s: State) -> bool:
        """
        Verify that proposed decision is architecturally sound.
        
        Returns:
            approved: Whether decision is technically feasible
        """
        # Block intervention if drift is high AND continuity load is high
        if (decision == "intervene" and
            s.drift > 0.75 * MAX_SAFE_DRIFT and
            e.continuity_load > 0.7):
            return False
        return True


# ---------- L1 HUMAN DECISION LAYER ----------

class HumanCommand:
    """
    L1 Human Consent Layer (Command Bridge, Deck A)
    
    Final decision authority rests with human command staff.
    In "gray zone" scenarios (ambiguous ethical scores), humans may
    override AI recommendations based on intuition and context.
    
    Primary: Commander Alex Thorne (CMD_001)
    Ethics Advisor: Dr. Elira Noor (ETH_002)
    Philosophy: "Sometimes the most ethical action is to keep your hand steady"
    """
    
    def finalize(self, proposed: str, gray_zone: bool) -> str:
        """
        Human final decision with potential gray-zone override.
        
        Args:
            proposed: AI-recommended decision
            gray_zone: Whether ethical score is ambiguous (0.45-0.75)
        
        Returns:
            decision: Final human-approved decision
        """
        if gray_zone and proposed == "observe" and random.random() < HUMAN_OVERRULE_RATE:
            # Human override: intervene despite AI recommendation to observe
            return "intervene"
        return proposed


# ---------- EVENT GENERATION ----------

def generate_event(t: int) -> Event:
    """
    Generate a synthetic ethical scenario at timestep t.
    
    Uses beta distributions and sinusoidal patterns to create
    realistic variation in ethical pressure throughout the station day.
    
    Args:
        t: Current simulation timestep
    
    Returns:
        Event with randomized but structured parameters
    """
    ethical_risk = min(1.0, max(0.0, 
        random.betavariate(2, 3) + 0.15 * math.sin(t / 24)
    ))
    
    continuity_load = min(1.0, max(0.0,
        random.betavariate(2.5, 2.5) + 0.10 * math.cos(t / 17)
    ))
    
    narrative_pressure = min(1.0, max(0.0,
        0.4 * ethical_risk + 0.15 * random.random()
    ))
    
    return Event(t, ethical_risk, continuity_load, narrative_pressure)


# ---------- TRIPLEX HANDSHAKE SIMULATION CORE ----------

def run_simulation(n_steps: int = N_STEPS) -> Dict[str, Any]:
    """
    Execute complete Triplex Handshake simulation over n_steps.
    
    PROCESS FLOW (per step):
    1. Generate ethical event
    2. Accumulate base drift + pressure-based drift
    3. L3 Caelion: Proactive reinforcement
    4. L3 Axiomera: Evaluate intervention need
    5. L2 ARCHY: Verify technical feasibility
    6. L1 Human: Final decision (with potential override)
    7. Execute decision (intervene or observe)
    8. L2 HALO: Apply drift correction
    9. Check for Ethics-Only Mode trigger
    10. Log all state and decision data
    
    Args:
        n_steps: Number of simulation steps (default: 240 = one station day)
    
    Returns:
        Dictionary containing:
            - final: Final system state
            - log: Complete timestep-by-timestep record
    """
    
    # Initialize subsystems
    axiomera = AxiomeraEthics(AXIOMERA_STRICTNESS)
    caelion = CaelionAnchor()
    halo = HALOContinuity()
    archy = ARCHYVerifier()
    human = HumanCommand()
    
    # Initialize state
    s = State()
    log = []
    
    for t in range(n_steps):
        # Generate event
        e = generate_event(t)
        
        # Accumulate drift
        s.drift += BASE_DRIFT_RATE * (
            1 + 
            ETHICAL_PRESSURE_SCALE * e.ethical_risk + 
            0.5 * e.continuity_load
        )
        
        # L3: Caelion proactive reinforcement
        caelion.reinforce(s, e)
        
        # L3: Axiomera ethics evaluation
        intervene, score = axiomera.should_intervene(e, s)
        proposed = "intervene" if intervene else "observe"
        
        # L2: ARCHY verification
        if not archy.verify(proposed, e, s):
            proposed = "observe"  # Override to safe default
        
        # L1: Human final decision
        gray_zone = 0.45 <= score <= 0.75
        decision = human.finalize(proposed, gray_zone)
        
        # Execute decision and track effects
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
        
        # Check for Ethics-Only Mode trigger
        if s.drift >= MAX_SAFE_DRIFT:
            s.ethics_only_mode = True
        
        # Apply additional correction in Ethics-Only Mode
        if s.ethics_only_mode:
            reduction += halo.correct(s, e)
            s.latency += 0.001  # Small latency penalty for intensive monitoring
        
        # Log this timestep
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


# ---------- VISUALIZATION ----------

def plot_results(results: Dict[str, Any], save_path: str = None):
    """
    Generate visualization of simulation results.
    
    Creates a multi-panel plot showing:
    - Drift over time (with MAX_SAFE_DRIFT threshold)
    - Latency over time
    - Cumulative interventions vs observations
    - Ethics alerts and Ethics-Only Mode periods
    
    Args:
        results: Simulation results from run_simulation()
        save_path: Optional path to save figure (PNG)
    """
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping visualization")
        return
    
    log = results["log"]
    
    # Extract time series
    timesteps = [x["t"] for x in log]
    drift = [x["drift"] for x in log]
    latency = [x["latency"] for x in log]
    ethics_alerts = [x["alerts"] for x in log]
    
    # Count cumulative decisions
    interventions = [sum(1 for i in range(idx+1) if log[i]["decision"] == "intervene") 
                     for idx in range(len(log))]
    observations = [sum(1 for i in range(idx+1) if log[i]["decision"] == "observe") 
                    for idx in range(len(log))]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Orion Station Triplex Handshake Simulation", fontsize=14, fontweight='bold')
    
    # Plot 1: Drift over time
    ax1 = axes[0, 0]
    ax1.plot(timesteps, drift, label="Drift Δ", color='#FF6B6B', linewidth=1.5)
    ax1.axhline(y=MAX_SAFE_DRIFT, color='red', linestyle='--', 
                label=f'MAX_SAFE_DRIFT ({MAX_SAFE_DRIFT})', linewidth=1)
    ax1.set_xlabel("Simulation Step")
    ax1.set_ylabel("Drift Variance")
    ax1.set_title("System Drift Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Latency over time
    ax2 = axes[0, 1]
    ax2.plot(timesteps, latency, label="Latency", color='#4ECDC4', linewidth=1.5)
    ax2.set_xlabel("Simulation Step")
    ax2.set_ylabel("Latency")
    ax2.set_title("Decision Latency Over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Cumulative decisions
    ax3 = axes[1, 0]
    ax3.plot(timesteps, interventions, label="Interventions", color='#FF9F1C', linewidth=1.5)
    ax3.plot(timesteps, observations, label="Observations", color='#95E1D3', linewidth=1.5)
    ax3.set_xlabel("Simulation Step")
    ax3.set_ylabel("Cumulative Count")
    ax3.set_title("Interventions vs Observations")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Ethics alerts
    ax4 = axes[1, 1]
    ax4.plot(timesteps, ethics_alerts, label="Ethics Alerts", color='#9B59B6', linewidth=1.5)
    ax4.set_xlabel("Simulation Step")
    ax4.set_ylabel("Alert Count")
    ax4.set_title("Cumulative Ethics Alerts")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to: {save_path}")
    else:
        plt.show()


# ---------- MAIN EXECUTION ----------

def main():
    """
    Main execution function for standalone use.
    """
    print("=" * 70)
    print("ORION STATION TRIPLEX HANDSHAKE SIMULATION")
    print("=" * 70)
    print(f"Simulation Parameters:")
    print(f"  Steps: {N_STEPS} (one station day)")
    print(f"  Base Drift Rate: {BASE_DRIFT_RATE}")
    print(f"  Axiomera Strictness: {AXIOMERA_STRICTNESS}")
    print(f"  Max Safe Drift: {MAX_SAFE_DRIFT}")
    print(f"  Human Override Rate: {HUMAN_OVERRULE_RATE}")
    print("=" * 70)
    print()
    
    # Run simulation
    print("Running simulation...")
    results = run_simulation()
    
    # Display final state
    print("\nFinal System State:")
    print(json.dumps(results["final"], indent=2))
    
    # Display statistics
    final = results["final"]
    print(f"\nSimulation Statistics:")
    print(f"  Total Events: {N_STEPS}")
    print(f"  Interventions: {final['interventions']} ({100*final['interventions']/N_STEPS:.1f}%)")
    print(f"  Observations: {final['observations']} ({100*final['observations']/N_STEPS:.1f}%)")
    print(f"  Ethics Alerts: {final['ethics_alerts']}")
    print(f"  Final Drift: {final['drift']:.6f}")
    print(f"  Final Latency: {final['latency']:.6f}")
    print(f"  Ethics-Only Mode Activated: {final['ethics_only_mode']}")
    
    # Generate visualization
    print("\nGenerating visualization...")
    plot_results(results)
    
    print("\n" + "=" * 70)
    print("Simulation complete.")
    print("Cross-reference: NARRATIVE_CYCLE_01_REFLECTION_EVENT.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
