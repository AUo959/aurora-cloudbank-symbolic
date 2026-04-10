#!/usr/bin/env python3
"""
Quantum Forge v3.0 - Verification and Health Check

Verifies all v3.0 components are properly installed and operational.

Usage:
    python scripts/verify_quantum_forge_v3.py

T1: QF_V3_VERIFICATION
SRB: HEALTH_CHECK_SYSTEM
DLP: context_tag=qf_v3_health, symbolic_hash=QFV3_HEALTH
"""

import sys
from typing import Dict, Any


def check_imports() -> Dict[str, bool]:
    """Verify all v3.0 imports are available"""
    results = {}
    
    print("🔍 Checking Quantum Forge v3.0 imports...")
    
    # Core v2.0
    try:
        from modules.quantum_forge import QuantumForge, EthicsLevel, FlowstateMode
        results['core_v2'] = True
        print("  ✅ Core v2.0 (QuantumForge, EthicsLevel, FlowstateMode)")
    except ImportError as e:
        results['core_v2'] = False
        print(f"  ❌ Core v2.0 failed: {e}")
    
    # Quantum Integration (Phase 1)
    try:
        from modules.quantum_forge import (
            get_quantum_integration,
            QuantumForgeIntegration,
            AgentQuantumState
        )
        results['quantum_integration'] = True
        print("  ✅ Quantum Integration (Phase 1)")
    except ImportError as e:
        results['quantum_integration'] = False
        print(f"  ❌ Quantum Integration failed: {e}")
    
    # Entanglement Network (Phase 2)
    try:
        from modules.quantum_forge import (
            get_entanglement_network,
            EntanglementNetwork,
            EntanglementLink,
            EntanglementCluster
        )
        results['entanglement_network'] = True
        print("  ✅ Entanglement Network (Phase 2)")
    except ImportError as e:
        results['entanglement_network'] = False
        print(f"  ❌ Entanglement Network failed: {e}")
    
    # Quantum Memory (Phase 3)
    try:
        from modules.quantum_forge import (
            get_quantum_memory_enhancer,
            QuantumMemoryEnhancer,
            QuantumMemoryMetadata
        )
        results['quantum_memory'] = True
        print("  ✅ Quantum Memory Enhancer (Phase 3)")
    except ImportError as e:
        results['quantum_memory'] = False
        print(f"  ❌ Quantum Memory failed: {e}")
    
    # System Orchestration (Phase 4)
    try:
        from modules.quantum_forge import (
            get_system_flow_orchestrator,
            SystemFlowOrchestrator,
            ModuleFlowState,
            SystemPhase
        )
        results['system_orchestration'] = True
        print("  ✅ System Flow Orchestrator (Phase 4)")
    except ImportError as e:
        results['system_orchestration'] = False
        print(f"  ❌ System Orchestration failed: {e}")
    
    # Ethics Operations (Phase 5)
    try:
        from modules.quantum_forge import (
            get_ethics_quantum_gate,
            EthicsAwareQuantumGate,
            GateRiskLevel
        )
        results['ethics_operations'] = True
        print("  ✅ Ethics-Aware Quantum Operations (Phase 5)")
    except ImportError as e:
        results['ethics_operations'] = False
        print(f"  ❌ Ethics Operations failed: {e}")
    
    return results


def check_version() -> bool:
    """Verify module version is 3.0.0"""
    print("\n📦 Checking module version...")
    
    try:
        from modules.quantum_forge import __version__
        if __version__ == "3.0.0":
            print(f"  ✅ Version: {__version__}")
            return True
        else:
            print(f"  ⚠️  Version: {__version__} (expected 3.0.0)")
            return False
    except ImportError:
        print("  ❌ Could not import __version__")
        return False


def functional_test() -> bool:
    """Run basic functional test"""
    print("\n🧪 Running functional test...")
    
    try:
        from modules.quantum_forge import (
            QuantumForge,
            EthicsLevel,
            get_quantum_integration,
            get_system_flow_orchestrator
        )
        
        # Initialize core with BALANCED ethics for testing
        forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)
        print("  ✅ QuantumForge initialized")
        
        # Create agent
        agent = forge.generate_agent(
            intent_query="Verify quantum forge system operational status and capabilities",
            constellation_targets=["ORION"]
        )
        print(f"  ✅ Agent created: {agent.agent_id[:12]}...")
        
        # Test quantum integration
        integration = get_quantum_integration(forge=forge)
        agent_qstate = integration.agent_to_quantum(agent)
        print(f"  ✅ Quantum Integration: {agent_qstate.quantum_state.num_qubits} qubits, fidelity={agent_qstate.fidelity:.4f}")
        
        # Test orchestrator
        orchestrator = get_system_flow_orchestrator(forge=forge)
        print(f"  ✅ System Orchestrator ready ({len(orchestrator.modules)} modules)")
        
        # Check metrics
        metrics = orchestrator.get_system_metrics()
        print(f"  ✅ System metrics: Load={metrics.system_load:.2%}, Health={metrics.average_health:.2%}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Functional test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_documentation() -> Dict[str, bool]:
    """Verify documentation files exist"""
    import os
    
    print("\n📚 Checking documentation...")
    
    docs = {
        "Complete Guide": "docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md",
        "Quick Reference": "docs/QUANTUM_FORGE_V3_QUICK_REFERENCE.md",
        "Implementation Summary": "docs/QUANTUM_FORGE_V3_IMPLEMENTATION_SUMMARY.md",
        "Complete Demo": "examples/quantum_forge_v3_complete_demo.py"
    }
    
    results = {}
    for name, path in docs.items():
        exists = os.path.exists(path)
        results[name] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path}")
    
    return results


def main():
    """Run complete verification"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║         🌟 QUANTUM FORGE v3.0 - VERIFICATION & HEALTH CHECK 🌟              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check imports
    import_results = check_imports()
    import_pass = all(import_results.values())
    
    # Check version
    version_pass = check_version()
    
    # Check documentation
    doc_results = check_documentation()
    doc_pass = all(doc_results.values())
    
    # Functional test
    functional_pass = functional_test()
    
    # Summary
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    total_checks = len(import_results) + 1 + len(doc_results) + 1
    passed_checks = (
        sum(import_results.values()) +
        (1 if version_pass else 0) +
        sum(doc_results.values()) +
        (1 if functional_pass else 0)
    )
    
    print(f"\nTotal Checks: {passed_checks}/{total_checks}")
    print(f"Success Rate: {passed_checks/total_checks*100:.1f}%")
    
    print("\n🔍 Component Status:")
    print(f"  - Core Imports: {'✅ PASS' if import_pass else '❌ FAIL'}")
    print(f"  - Module Version: {'✅ PASS' if version_pass else '❌ FAIL'}")
    print(f"  - Documentation: {'✅ PASS' if doc_pass else '❌ FAIL'}")
    print(f"  - Functional Test: {'✅ PASS' if functional_pass else '❌ FAIL'}")
    
    if import_pass and version_pass and doc_pass and functional_pass:
        print("\n🎯 STATUS: ✅ ALL SYSTEMS OPERATIONAL")
        print("\n✨ Quantum Forge v3.0 is ready for production deployment!")
        print("\n📖 Next Steps:")
        print("   1. Review docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md")
        print("   2. Run examples/quantum_forge_v3_complete_demo.py")
        print("   3. Initialize with scripts/init_quantum_forge_v3.py")
        return 0
    else:
        print("\n⚠️  STATUS: ❌ VERIFICATION FAILED")
        print("\nSome components are not operational. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
