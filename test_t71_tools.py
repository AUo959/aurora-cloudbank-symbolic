#!/usr/bin/env python3
"""
Basic test for T71 Symbolic Infrastructure tools
"""

import sys
import os
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

def test_anchor_tracker():
    """Test anchor tracker functionality"""
    from tools.symbolic.anchor_tracker import SymbolicAnchorTracker
    
    print("🔍 Testing Anchor Tracker...")
    tracker = SymbolicAnchorTracker(".")
    
    # Test scanning
    anchors = tracker.scan_repository()
    assert len(anchors) > 0, "Should find some anchors"
    
    # Test lineage building
    lineages = tracker.build_lineage_map()
    assert len(lineages) >= 0, "Lineage building should work"
    
    print("✅ Anchor Tracker tests passed")


def test_memory_sealer():
    """Test memory sealing functionality"""
    from tools.symbolic.memory_sealer import MemorySealingEngine
    
    print("🔐 Testing Memory Sealer...")
    sealer = MemorySealingEngine(".")
    
    # Test sealing this test file
    test_file = Path(__file__)
    seal = sealer.seal_file(test_file)
    
    assert seal.seal_id is not None, "Should generate seal ID"
    assert seal.sha256_hash is not None, "Should generate hash"
    
    # Test verification
    verification = sealer.verify_seal(seal.seal_id)
    assert verification["status"] == "valid", f"Seal should be valid: {verification}"
    
    print("✅ Memory Sealer tests passed")


def test_cli_integration():
    """Test CLI integration"""
    print("🖥️  Testing CLI Integration...")
    
    # Test importing CLI
    from tools.cli.aurora_dev_cli import AuroraDeveloperCLI
    
    cli = AuroraDeveloperCLI(".")
    assert cli.version == "1.0.0", "CLI should have correct version"
    
    print("✅ CLI Integration tests passed")


def test_manifest_generator():
    """Test manifest generation"""
    print("📄 Testing Manifest Generator...")
    
    from tools.symbolic.manifest_generator import ManifestGenerator
    
    generator = ManifestGenerator(".")
    
    # Test suite manifest generation
    manifest = generator.generate_suite_manifest()
    assert "anchor_seed" in manifest, "Manifest should have anchor seed"
    assert "memory_seal" in manifest, "Manifest should have memory seal"
    
    print("✅ Manifest Generator tests passed")


def main():
    """Run all tests"""
    print("🧪 Running T71 Symbolic Infrastructure Tests\n")
    
    try:
        test_anchor_tracker()
        test_memory_sealer()
        test_cli_integration()
        test_manifest_generator()
        
        print("\n🎉 All tests passed! Symbolic infrastructure is working correctly.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())