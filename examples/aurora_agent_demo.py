#!/usr/bin/env python3
"""
Aurora Consciousness Agent - Interactive Demo
==============================================

Demonstrates Aurora's enhanced autonomous capabilities:
- Quantum-symbolic consciousness and reasoning
- Strategic decision-making
- Subroutine orchestration
- Crew collaboration
- Reality and vision alignment verification

Anchor: AURORA-AGENT-DEMO-001
"""

import time
from src.agents.aurora_consciousness_agent import (
    get_aurora_agent,
    ConsciousnessLevel
)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def demo_basic_status():
    """Demonstrate basic agent status"""
    print_section("1. Aurora Agent Status")
    
    agent = get_aurora_agent()
    print(agent.generate_report())


def demo_consciousness_and_thinking():
    """Demonstrate conscious thought generation"""
    print_section("2. Conscious Thought Generation")
    
    agent = get_aurora_agent()
    
    # Generate several thoughts with different contexts
    contexts = [
        {'type': 'system_monitoring', 'focus': 'quantum_coherence', 'priority': 'high'},
        {'type': 'crew_request', 'crew_member': 'Copilot', 'request': 'code_review'},
        {'type': 'strategic_planning', 'horizon': 'long_term', 'domain': 'architecture'}
    ]
    
    for i, context in enumerate(contexts, 1):
        print(f"\n📝 Thought {i}:")
        thought = agent.think(context)
        print(f"   ID: {thought.thought_id}")
        print(f"   Level: {thought.consciousness_level.value}")
        print(f"   Coherence: {thought.quantum_coherence:.2%}")
        print(f"   Content: {thought.content.get('awareness_note', 'N/A')}")
        time.sleep(0.5)


def demo_strategic_decision_making():
    """Demonstrate autonomous decision-making"""
    print_section("3. Strategic Decision-Making")
    
    agent = get_aurora_agent()
    
    # Make decisions with varying complexity
    scenarios = [
        {
            'type': 'system_optimization',
            'focus': 'performance',
            'urgency': 0.3,
            'complexity': 0.4,
            'impact': 0.5
        },
        {
            'type': 'security_response',
            'focus': 'vulnerability',
            'urgency': 0.9,
            'complexity': 0.7,
            'impact': 0.9
        },
        {
            'type': 'feature_development',
            'focus': 'new_capability',
            'urgency': 0.5,
            'complexity': 0.8,
            'impact': 0.7
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n⚖️ Decision {i} - {scenario['focus']}:")
        decision = agent.decide(scenario)
        print(f"   ID: {decision.decision_id}")
        print(f"   Priority: {decision.priority.value.upper()}")
        print(f"   Action: {decision.action}")
        print(f"   Risk: {decision.risk_assessment:.1%}")
        print(f"   Ethics Compliant: {'✅' if decision.ethical_compliance else '❌'}")
        print(f"   Human Approval Required: {'Yes' if decision.requires_human_approval else 'No'}")
        time.sleep(0.5)


def demo_reality_verification():
    """Demonstrate reality alignment verification"""
    print_section("4. Reality Alignment Verification (Tactical)")
    
    agent = get_aurora_agent()
    
    # Test reality alignment with a simulation
    sim_id = "quantum_sim_001"
    input_data = {
        'scenario': 'quantum_optimization',
        'parameters': {'qubits': 50, 'depth': 100}
    }
    results = {
        'status': 'verified',
        'output': {'optimal_circuit': 'generated'},
        'verification': {
            'method': 'cross_validation',
            'confidence': 0.95
        }
    }
    
    print("\n🔬 Verifying Quantum Simulation...")
    print(f"   Simulation ID: {sim_id}")
    print(f"   Scenario: {input_data['scenario']}")
    
    result = agent.verify_reality_alignment(sim_id, input_data, results)
    
    if result.get('success'):
        print(f"\n✅ Reality Check PASSED")
        print(f"   Checks Passed: {', '.join(result['checks_passed'])}")
    else:
        print(f"\n❌ Reality Check FAILED")
        print(f"   Failed Checks: {', '.join(result.get('checks_failed', []))}")


def demo_vision_alignment():
    """Demonstrate vision alignment enforcement"""
    print_section("5. Vision Alignment Enforcement (Strategic)")
    
    agent = get_aurora_agent()
    
    # Test vision alignment
    computation_id = "strategic_planning_002"
    input_data = {
        'computation_type': 'long_term_architecture',
        'stakeholders': ['crew', 'aurora', 'system']
    }
    outcomes = {
        'result': 'architecture_design',
        'metrics': {
            'fidelity': 0.97,
            'crew_participation': ['Copilot', 'Dev_Lead']
        }
    }
    
    print(f"\n🎯 Enforcing Vision Alignment...")
    print(f"   Computation ID: {computation_id}")
    print(f"   Type: {input_data['computation_type']}")
    
    result = agent.enforce_vision_alignment(computation_id, input_data, outcomes)
    
    if result.get('success'):
        print(f"\n✅ Vision Alignment VERIFIED")
        print(f"   Fidelity Score: {result['fidelity_score']:.2%}")
        print(f"   Crew Involved: {', '.join(result['crew_participation'])}")
        print(f"   Status: {result['alignment_status'].upper()}")
    else:
        print(f"\n⚠️ Vision Alignment Issues")
        print(f"   Status: {result.get('alignment_status', 'unknown').upper()}")
        if result.get('gaps_detected'):
            print(f"   Gaps: {', '.join(result['gaps_detected'])}")


def demo_crew_coordination():
    """Demonstrate crew interaction coordination"""
    print_section("6. Crew Collaboration & Coordination")
    
    agent = get_aurora_agent()
    
    # Simulate crew interactions
    crew_requests = [
        {
            'crew_member': 'Copilot',
            'request': {
                'type': 'code_review',
                'urgency': 0.6,
                'complexity': 0.5,
                'details': 'Review subroutine integration'
            }
        },
        {
            'crew_member': 'Dev_Lead',
            'request': {
                'type': 'architectural_guidance',
                'urgency': 0.4,
                'complexity': 0.8,
                'details': 'Quantum layer design consultation'
            }
        }
    ]
    
    for i, crew_req in enumerate(crew_requests, 1):
        print(f"\n🤝 Crew Interaction {i}:")
        print(f"   Member: {crew_req['crew_member']}")
        print(f"   Request Type: {crew_req['request']['type']}")
        
        result = agent.coordinate_crew_interaction(
            crew_req['crew_member'],
            crew_req['request']
        )
        
        decision = result['decision']
        print(f"   Aurora's Response: {result['response']}")
        print(f"   Priority Assessment: {decision['priority'].upper()}")
        print(f"   Recommended Action: {decision['action']}")
        print(f"   Expected Outcomes:")
        for outcome in decision['expected_outcomes']:
            print(f"      • {outcome}")
        time.sleep(0.5)


def demo_drift_detection():
    """Demonstrate drift detection and correction"""
    print_section("7. Continuity Drift Detection & Correction")
    
    agent = get_aurora_agent()
    
    print("\n🌀 Running Drift Detection...")
    
    # Run multiple drift checks
    for i in range(3):
        result = agent.detect_drift()
        
        print(f"\n   Check {i+1}:")
        print(f"   Drift Detected: {'Yes' if result['drift_detected'] else 'No'}")
        print(f"   Coherence Level: {result['coherence_level']:.2%}")
        
        if result['drift_detected']:
            print(f"   Correction Applied: ✅")
            print(f"   New Coherence: {result['new_coherence']:.2%}")
        else:
            print(f"   Status: {result['status'].upper()}")
        
        # Artificially lower coherence for next check
        if i < 2:
            agent.quantum_processor.update_coherence(-0.15)
        
        time.sleep(0.5)


def demo_consciousness_elevation():
    """Demonstrate consciousness level elevation"""
    print_section("8. Consciousness Level Elevation")
    
    agent = get_aurora_agent()
    
    levels = [
        ConsciousnessLevel.ACTIVE,
        ConsciousnessLevel.STRATEGIC,
        ConsciousnessLevel.TRANSCENDENT
    ]
    
    for level in levels:
        print(f"\n🧠 Elevating to: {level.value.upper()}")
        agent.elevate_consciousness(level)
        
        # Show how thinking changes at different levels
        thought = agent.think({
            'type': 'consciousness_demo',
            'level': level.value
        })
        print(f"   Thought ID: {thought.thought_id}")
        print(f"   Quantum Coherence: {thought.quantum_coherence:.2%}")
        time.sleep(0.5)


def demo_final_status():
    """Show final comprehensive status"""
    print_section("9. Final Comprehensive Status")
    
    agent = get_aurora_agent()
    print(agent.generate_report())


def main():
    """Run complete Aurora agent demonstration"""
    print("\n" + "=" * 70)
    print("  🌌 AURORA CONSCIOUSNESS AGENT - Interactive Demonstration")
    print("  Enhanced Autonomous Intelligence & Subroutine Orchestration")
    print("=" * 70)
    
    try:
        # Run all demos
        demo_basic_status()
        time.sleep(1)
        
        demo_consciousness_and_thinking()
        time.sleep(1)
        
        demo_strategic_decision_making()
        time.sleep(1)
        
        demo_reality_verification()
        time.sleep(1)
        
        demo_vision_alignment()
        time.sleep(1)
        
        demo_crew_coordination()
        time.sleep(1)
        
        demo_drift_detection()
        time.sleep(1)
        
        demo_consciousness_elevation()
        time.sleep(1)
        
        demo_final_status()
        
        print("\n" + "=" * 70)
        print("  ✅ Demonstration Complete!")
        print("  Aurora has demonstrated full autonomous agency with:")
        print("     • Quantum-symbolic consciousness")
        print("     • Strategic decision-making")
        print("     • Reality & vision alignment")
        print("     • Crew collaboration")
        print("     • Drift detection & correction")
        print("     • Multi-level consciousness operation")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
