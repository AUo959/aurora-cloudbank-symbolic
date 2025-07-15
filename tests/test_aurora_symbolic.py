"""Tests for Aurora Cloudbank Symbolic Engine"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_t1_anchor():
    """Test T1 temporal anchor"""
    from aurora.core.symbolic_engine import T1Anchor
    
    t1 = T1Anchor()
    assert t1.type == "T1"
    
    state = t1.advance("test_data")
    assert state > 0
    
    export = t1.export()
    assert export["type"] == "T1"
    assert export["state"] == state

def test_srb_anchor():
    """Test SRB boundary anchor"""
    from aurora.core.symbolic_engine import SRBAnchor
    
    srb = SRBAnchor()
    assert srb.type == "SRB"
    
    resolution = srb.resolve("test_boundary")
    assert resolution > 0
    
    export = srb.export()
    assert export["type"] == "SRB"
    assert export["resolution"] == resolution

def test_symbolic_engine():
    """Test complete symbolic engine"""
    from aurora.core.symbolic_engine import SymbolicEngine
    
    engine = SymbolicEngine()
    
    # Test chain execution
    results = engine.execute_chain(1, 3)
    assert len(results) == 3
    
    # Test manifest export
    manifest = engine.export_manifest(legacy_mode=True)
    assert manifest["system"] == "aurora-cloudbank-symbolic"
    assert "t1_anchor" in manifest
    assert "srb_anchor" in manifest
    assert "chains" in manifest

def test_chain_notation():
    """Test symbolic chain notation (001//999//)"""
    from aurora.core.symbolic_engine import SymbolicEngine
    
    engine = SymbolicEngine()
    
    # Test chain 001//005//
    results = engine.execute_chain(1, 5)
    assert len(results) == 5
    
    # Verify chain is stored
    assert "001//005//" in engine.chains
    
    # Test another chain 010//015//
    results2 = engine.execute_chain(10, 15)
    assert len(results2) == 6
    assert "010//015//" in engine.chains
