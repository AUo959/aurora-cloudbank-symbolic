#!/usr/bin/env python3
"""
Subroutine System Demo
======================
Demonstrates Reality Sim Monitor and Subroutine Registry usage.

Usage:
    python examples/subroutine_demo.py
"""

from src.subroutines.reality_sim_monitor import RealitySimMonitor
from src.subroutines.registry import get_subroutine_registry


def demo_reality_sim_monitor():
    """Demonstrate Reality Sim Monitor"""
    print("=" * 70)
    print("Reality Sim Monitor Demo")
    print("=" * 70)
    
    # Initialize monitor
    monitor = RealitySimMonitor()
    print("\n✅ RealitySimMonitor initialized")
    
    # Example 1: Successful validation
    print("\n📋 Test 1: Verified Simulation")
    sim_id = "quantum_optimization_001"
    input_data = {
        'scenario': 'quantum_circuit_optimization',
        'parameters': {'qubits': 50, 'depth': 100, 'gates': ['H', 'CNOT', 'RZ']}
    }
    results = {
        'status': 'verified',
        'output': {
            'optimal_depth': 87,
            'gate_count': 450,
            'fidelity': 0.987
        },
        'verification': {
            'method': 'cross_validation',
            'confidence': 0.95,
            'trials': 1000
        }
    }
    
    result = monitor.enforce_principles(sim_id, input_data, results)
    
    if result.success:
        print(f"   ✅ Reality Check PASSED")
        print(f"   ✓ Checks Passed: {', '.join(result.checks_passed)}")
    else:
        print(f"   ❌ Reality Check FAILED")
        print(f"   ✗ Failed: {', '.join(result.checks_failed)}")
    
    # Example 2: Failed validation (speculative)
    print("\n📋 Test 2: Speculative Simulation (should fail)")
    sim_id_2 = "speculative_test_002"
    results_speculative = {
        'status': 'speculative',  # This will fail reality check
        'output': {'prediction': 'high_performance'},
    }
    
    result2 = monitor.enforce_principles(sim_id_2, input_data, results_speculative)
    
    if result2.success:
        print(f"   ✅ Reality Check PASSED")
    else:
        print(f"   ❌ Reality Check FAILED (as expected)")
        print(f"   ✗ Failed: {', '.join(result2.checks_failed)}")
    
    # Show statistics
    print("\n📊 Monitor Statistics:")
    stats = monitor.get_stats()
    print(f"   Total Executions: {stats['total_executions']}")
    print(f"   Successful: {stats['successful']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Success Rate: {stats['success_rate']:.1%}")


def demo_subroutine_registry():
    """Demonstrate Subroutine Registry"""
    print("\n" + "=" * 70)
    print("Subroutine Registry Demo")
    print("=" * 70)
    
    # Get global registry
    registry = get_subroutine_registry()
    print(f"\n✅ Registry initialized with {len(registry._subroutines)} subroutines")
    
    # List all subroutines
    print("\n📋 Registered Subroutines:")
    for subroutine in registry.list_all():
        print(f"\n   ID: {subroutine.id}")
        print(f"   Name: {subroutine.name} v{subroutine.version}")
        print(f"   Category: {subroutine.category.value}")
        print(f"   Status: {subroutine.status.value}")
        print(f"   Author: {subroutine.author.name} ({subroutine.author.team})")
        print(f"   Executions: {subroutine.total_executions}")
        if subroutine.total_executions > 0:
            print(f"   Success Rate: {subroutine.success_rate:.1%}")
        print(f"   Tags: {', '.join(subroutine.tags)}")
    
    # Search functionality
    print("\n🔍 Search Results for 'reality':")
    results = registry.search(query="reality")
    for sub in results:
        print(f"   • {sub.name} ({sub.id})")
    
    # Get statistics
    print("\n📊 Registry Statistics:")
    stats = registry.get_stats()
    print(f"   Total Subroutines: {stats['total_subroutines']}")
    print(f"   Active: {stats['active_subroutines']}")
    print(f"   Total Executions: {stats['total_executions']}")
    
    print("\n   By Category:")
    for category, count in stats['by_category'].items():
        if count > 0:
            print(f"     • {category}: {count}")
    
    print("\n   By Status:")
    for status, count in stats['by_status'].items():
        if count > 0:
            print(f"     • {status}: {count}")


def main():
    """Run all demos"""
    print("\n🚀 Aurora Subroutine System Demo")
    print("=" * 70)
    
    try:
        # Demo Reality Sim Monitor
        demo_reality_sim_monitor()
        
        # Demo Subroutine Registry
        demo_subroutine_registry()
        
        print("\n" + "=" * 70)
        print("✅ Demo Complete!")
        print("=" * 70)
        print("\nFor more information, see: docs/SUBROUTINE_SYSTEM.md")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
