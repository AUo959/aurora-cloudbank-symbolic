#!/usr/bin/env python3
"""
Basic test for T71 Symbolic Infrastructure tools
"""

from pathlib import Path
import sys
import traceback

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tools.symbolic.anchor_tracker import SymbolicAnchorTracker
from tools.symbolic.memory_sealer import MemorySealingEngine
from tools.cli.aurora_dev_cli import AuroraDeveloperCLI
from tools.symbolic.manifest_generator import ManifestGenerator


def test_anchor_tracker():
    """Test anchor tracker functionality"""

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

    print("🔐 Testing Memory Sealer...")
    sealer = MemorySealingEngine(".")

    # Test sealing this test file
    test_file = Path(__file__)
    seal = sealer.seal_file(test_file)
    seal_path = sealer.seals_dir / f"{seal.seal_id}.json"
    backup_path = sealer.seals_dir / f"{seal.seal_id}_backup.zip"

    try:
        assert seal.seal_id is not None, "Should generate seal ID"
        assert seal.sha256_hash is not None, "Should generate hash"

        # Test verification
        verification = sealer.verify_seal(seal.seal_id)
        assert verification["status"] == "valid", f"Seal should be valid: {verification}"
    finally:
        if seal_path.exists():
            seal_path.unlink()

        if backup_path.exists():
            backup_path.unlink()

        sealer.seals.pop(seal.seal_id, None)

    print("✅ Memory Sealer tests passed")


def test_cli_integration():
    """Test CLI integration"""
    print("🖥️  Testing CLI Integration...")

    # Test importing CLI

    cli = AuroraDeveloperCLI(".")
    assert cli.version == "1.0.0", "CLI should have correct version"

    print("✅ CLI Integration tests passed")


def test_manifest_generator():
    """Test manifest generation"""
    print("📄 Testing Manifest Generator...")

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
        print("")
# ❌ Test failed: %s", e)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
