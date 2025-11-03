#!/usr/bin/env python3
"""
Test script to verify agents can access and use Aurora command system.
This validates that COMMAND_REFERENCE.md is discoverable and commands work.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_command_reference_exists():
    """Verify COMMAND_REFERENCE.md exists and is accessible"""
    cmd_ref = Path(__file__).parent.parent / ".github" / "COMMAND_REFERENCE.md"
    assert cmd_ref.exists(), "COMMAND_REFERENCE.md not found!"
    print("✅ COMMAND_REFERENCE.md exists")
    
    content = cmd_ref.read_text()
    assert "#NNN//MMM//" in content, "Chain notation not documented"
    assert "T1:" in content, "T1 anchors not documented"
    assert "DLP:" in content, "DLP protocol not documented"
    assert "@seal:" in content, "Memory seals not documented"
    print("✅ All command patterns documented")
    
    return True


def test_symbolic_engine_import():
    """Verify SymbolicEngine is importable"""
    try:
        from src.aurora.core.symbolic_engine import SymbolicEngine
        print("✅ SymbolicEngine imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import SymbolicEngine: {e}")
        return False


def test_chain_execution():
    """Test chain notation execution"""
    try:
        from src.aurora.core.symbolic_engine import SymbolicEngine
        
        engine = SymbolicEngine()
        initial_t1 = engine.t1.state
        initial_srb = engine.srb.resolution
        
        # Execute test chain
        results = engine.execute_chain(1, 10)
        
        assert len(results) == 10, "Chain didn't execute all steps"
        assert engine.t1.state > initial_t1, "T1 anchor didn't advance"
        assert engine.srb.resolution > initial_srb, "SRB anchor didn't resolve"
        
        # Verify chain notation
        chain_id = "001//010//"
        assert chain_id in engine.chains, "Chain not registered"
        
        print(f"✅ Chain execution successful: #001//010//")
        print(f"   T1 delta: {engine.t1.state - initial_t1}")
        print(f"   SRB delta: {engine.srb.resolution - initial_srb}")
        return True
        
    except Exception as e:
        print(f"❌ Chain execution failed: {e}")
        return False


def test_dlp_tracker_import():
    """Verify DLP tracker is accessible"""
    try:
        from src.core.native_dlp_export import NativeDLPTracker
        print("✅ NativeDLPTracker imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import NativeDLPTracker: {e}")
        return False


def test_dlp_export():
    """Test DLP-tagged export creation"""
    try:
        from src.core.native_dlp_export import NativeDLPTracker
        
        tracker = NativeDLPTracker()
        
        # Create test tag
        test_data = {"results": [1, 2, 3], "status": "success"}
        
        tag_id = tracker.create_tag(
            operation="agent_test",
            data=test_data
        )
        
        # Create manifest
        manifest = tracker.create_export_manifest(
            manifest_name="test_manifest",
            tag_ids=[tag_id]
        )
        
        assert "manifest_id" in manifest, "Missing manifest_id"
        assert "tags" in manifest, "Missing tags"
        assert len(manifest["tags"]) == 1, "Wrong number of tags"
        
        print("✅ DLP export creation successful")
        print(f"   Context tag: DLP:{tag_id}")
        return True
        
    except Exception as e:
        print(f"❌ DLP export failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_copilot_instructions_updated():
    """Verify copilot-instructions.md references command system"""
    copilot_file = Path(__file__).parent.parent / ".github" / "copilot-instructions.md"
    assert copilot_file.exists(), "copilot-instructions.md not found"
    
    content = copilot_file.read_text()
    assert "COMMAND_REFERENCE.md" in content, "No reference to COMMAND_REFERENCE.md"
    assert "Chain notation" in content or "chain notation" in content, "Chain notation not mentioned"
    
    print("✅ copilot-instructions.md properly references command system")
    return True


def main():
    """Run all tests"""
    print("\n🔍 Testing Aurora Command System Accessibility\n")
    print("=" * 60)
    
    tests = [
        ("Command Reference Exists", test_command_reference_exists),
        ("SymbolicEngine Import", test_symbolic_engine_import),
        ("Chain Execution", test_chain_execution),
        ("DLP Tracker Import", test_dlp_tracker_import),
        ("DLP Export", test_dlp_export),
        ("Copilot Instructions Updated", test_copilot_instructions_updated),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("\n📊 Test Summary:\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Command system is fully accessible to agents.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review command system setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
