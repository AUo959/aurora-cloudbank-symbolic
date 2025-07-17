"""Tests for enhanced Aurora symbolic simulation framework"""
import pytest
import json
import time
import tempfile
from pathlib import Path

from src.aurora.core.symbolic_engine import (
    SymbolicEngine, T1Anchor, SRBAnchor, EOSSeedAnchor,
    DLPClassification, EntropyState, ThreadState, MemorySealingProtocol
)
from src.aurora.cli.symbolic_cli import SymbolicCLI


class TestSymbolicAnchors:
    """Test individual symbolic anchors"""

    def test_t1_anchor_basic_functionality(self):
        """Test T1 anchor basic operations"""
        t1 = T1Anchor()
        assert t1.type == "T1"
        assert t1.state == 0
        
        # Test advance
        result = t1.advance("test_data")
        assert result == 9  # len("test_data")
        assert t1.state == 9
        
        # Test export
        export = t1.export()
        assert export["type"] == "T1"
        assert export["state"] == 9

    def test_srb_anchor_basic_functionality(self):
        """Test SRB anchor basic operations"""
        srb = SRBAnchor()
        assert srb.type == "SRB"
        assert srb.resolution == 0
        
        # Test resolve
        result = srb.resolve("boundary_1")
        assert result > 0
        assert srb.resolution == result
        
        # Test export
        export = srb.export()
        assert export["type"] == "SRB"
        assert export["resolution"] == result

    def test_eos_seed_anchor_functionality(self):
        """Test EOS_SEED anchor operations"""
        eos = EOSSeedAnchor()
        assert eos.type == "EOS_SEED"
        assert eos.seed_count == 0
        assert not eos.stream_terminated
        
        # Test seeding
        result = eos.seed_stream("stream_data")
        assert result == 11  # len("stream_data")
        assert eos.seed_count == 11
        
        # Test termination
        final_count = eos.terminate_stream()
        assert final_count == 11
        assert eos.stream_terminated
        
        # Test seeding after termination
        result = eos.seed_stream("more_data")
        assert result == -1  # Should fail
        
        # Test export
        export = eos.export()
        assert export["type"] == "EOS_SEED"
        assert export["seed_count"] == 11
        assert export["stream_terminated"]


class TestEntropyMonitoring:
    """Test entropy monitoring functionality"""

    def test_entropy_state_creation(self):
        """Test entropy state initialization"""
        entropy_state = EntropyState(
            current_entropy=0.5,
            threshold=0.8,
            violations=0,
            last_update=time.time()
        )
        
        assert entropy_state.current_entropy == 0.5
        assert entropy_state.threshold == 0.8
        assert entropy_state.violations == 0
        assert not entropy_state.is_threshold_exceeded()

    def test_entropy_threshold_detection(self):
        """Test entropy threshold violation detection"""
        entropy_state = EntropyState(
            current_entropy=0.9,
            threshold=0.8,
            violations=0,
            last_update=time.time()
        )
        
        assert entropy_state.is_threshold_exceeded()

    def test_entropy_calculation(self):
        """Test Shannon entropy calculation"""
        engine = SymbolicEngine()
        
        # Test uniform distribution (high entropy)
        uniform_data = "abcdefghijklmnop"
        entropy = engine.calculate_entropy(uniform_data)
        assert entropy > 0.9
        
        # Test non-uniform distribution (lower entropy)
        skewed_data = "aaaaaaaaabcdefgh"
        entropy = engine.calculate_entropy(skewed_data)
        assert entropy < 0.9
        
        # Test empty string
        entropy = engine.calculate_entropy("")
        assert entropy == 0.0


class TestMemorySealing:
    """Test memory sealing protocol"""

    def test_memory_sealing_protocol(self):
        """Test memory sealing and unsealing"""
        protocol = MemorySealingProtocol()
        
        test_data = {"key": "value", "number": 42}
        memory_id = "test_memory"
        operator_key = "secret123"
        dlp_class = DLPClassification.CONFIDENTIAL
        
        # Test sealing
        content_hash = protocol.seal_memory(memory_id, test_data, dlp_class, operator_key)
        assert content_hash is not None
        assert len(content_hash) == 64  # SHA256 hash length
        
        # Test unsealing with correct key
        unsealed_data = protocol.unseal_memory(memory_id, operator_key)
        assert unsealed_data == test_data
        
        # Test unsealing with wrong key
        unsealed_data = protocol.unseal_memory(memory_id, "wrong_key")
        assert unsealed_data is None
        
        # Test unsealing non-existent memory
        unsealed_data = protocol.unseal_memory("non_existent", operator_key)
        assert unsealed_data is None

    def test_sealed_manifest_export(self):
        """Test export of sealed memory manifest"""
        protocol = MemorySealingProtocol()
        
        # Seal multiple memories
        protocol.seal_memory("mem1", {"data": 1}, DLPClassification.PUBLIC, "key1")
        protocol.seal_memory("mem2", {"data": 2}, DLPClassification.RESTRICTED, "key2")
        
        manifest = protocol.export_sealed_manifest()
        
        assert "mem1" in manifest
        assert "mem2" in manifest
        assert manifest["mem1"]["dlp_classification"] == "public"
        assert manifest["mem2"]["dlp_classification"] == "restricted"
        assert "content_hash" in manifest["mem1"]
        assert "timestamp" in manifest["mem1"]


class TestSymbolicEngine:
    """Test enhanced symbolic engine functionality"""

    def test_engine_initialization(self):
        """Test symbolic engine initialization"""
        engine = SymbolicEngine(entropy_threshold=0.7)
        
        assert isinstance(engine.t1, T1Anchor)
        assert isinstance(engine.srb, SRBAnchor)
        assert isinstance(engine.eos_seed, EOSSeedAnchor)
        assert engine.entropy_state.threshold == 0.7
        assert len(engine.chains) == 0
        assert len(engine.thread_states) == 0

    def test_enhanced_chain_execution(self):
        """Test enhanced chain execution with entropy monitoring"""
        engine = SymbolicEngine()
        
        # Execute chain with stream data
        results = engine.execute_chain(1, 3, "test_stream")
        
        assert len(results) == 3
        assert all("entropy" in result for result in results)
        assert all("eos_seed_count" in result for result in results)
        
        # Check that EOS_SEED was updated
        assert engine.eos_seed.seed_count > 0

    def test_thread_sealing_and_rehydration(self):
        """Test thread sealing and rehydration"""
        engine = SymbolicEngine()
        
        # Advance some state
        engine.execute_chain(1, 2)
        
        # Seal thread
        thread_id = "test_thread"
        operator_key = "secret123"
        dlp_class = DLPClassification.INTERNAL
        
        seal_hash = engine.seal_thread(thread_id, dlp_class, operator_key)
        assert seal_hash is not None
        assert thread_id in engine.thread_states
        
        # Store current states
        original_t1_state = engine.t1.state
        original_srb_resolution = engine.srb.resolution
        original_eos_count = engine.eos_seed.seed_count
        
        # Modify states
        engine.t1.state = 999
        engine.srb.resolution = 999
        engine.eos_seed.seed_count = 999
        
        # Rehydrate thread
        success = engine.rehydrate_thread(thread_id, operator_key)
        assert success
        
        # Check states were restored
        assert engine.t1.state == original_t1_state
        assert engine.srb.resolution == original_srb_resolution
        assert engine.eos_seed.seed_count == original_eos_count

    def test_rehydration_authentication(self):
        """Test thread rehydration authentication"""
        engine = SymbolicEngine()
        
        # Seal thread
        thread_id = "test_thread"
        correct_key = "secret123"
        wrong_key = "wrong_key"
        
        engine.seal_thread(thread_id, DLPClassification.CONFIDENTIAL, correct_key)
        
        # Test rehydration with wrong key
        success = engine.rehydrate_thread(thread_id, wrong_key)
        assert not success
        
        # Test rehydration with correct key
        success = engine.rehydrate_thread(thread_id, correct_key)
        assert success

    def test_glyphcard_generation(self):
        """Test glyphcard generation for sealed threads"""
        engine = SymbolicEngine()
        
        # Execute some operations
        engine.execute_chain(1, 2)
        
        # Seal thread
        thread_id = "test_thread"
        engine.seal_thread(thread_id, DLPClassification.RESTRICTED, "key123")
        
        # Generate glyphcard
        glyphcard = engine.generate_glyphcard(thread_id)
        
        assert glyphcard["thread_id"] == thread_id
        assert "glyph_signature" in glyphcard
        assert glyphcard["dlp_class"] == "restricted"
        assert "anchor_summary" in glyphcard
        assert glyphcard["sealed"]

    def test_manifest_export(self):
        """Test comprehensive manifest export"""
        engine = SymbolicEngine()
        
        # Execute operations
        engine.execute_chain(1, 2, "test_data")
        engine.seal_thread("thread1", DLPClassification.PUBLIC, "key1")
        
        manifest = engine.export_manifest()
        
        assert manifest["system"] == "aurora-cloudbank-symbolic"
        assert manifest["version"] == "2.0.0"
        assert "anchors" in manifest
        assert "entropy_monitoring" in manifest
        assert "chains" in manifest
        assert "sealed_threads" in manifest
        assert "memory_sealing_manifest" in manifest
        assert "export_timestamp" in manifest

    def test_diff_report_generation(self):
        """Test manifest diff report generation"""
        engine = SymbolicEngine()
        
        # Create initial manifest
        engine.execute_chain(1, 2)
        manifest1 = engine.export_manifest()
        
        # Modify state
        engine.execute_chain(3, 4)
        engine.seal_thread("new_thread", DLPClassification.INTERNAL, "key")
        
        # Generate diff report
        diff_report = engine.generate_diff_report(manifest1)
        
        assert "comparison_timestamp" in diff_report
        assert "anchor_diffs" in diff_report
        assert "entropy_diff" in diff_report
        assert "chain_diffs" in diff_report
        assert "thread_diffs" in diff_report


class TestSymbolicCLI:
    """Test symbolic CLI functionality"""

    def test_cli_initialization(self):
        """Test CLI initialization"""
        cli = SymbolicCLI()
        
        assert isinstance(cli.engine, SymbolicEngine)
        assert cli.output_dir.exists()

    def test_chain_execution_command(self):
        """Test CLI chain execution"""
        cli = SymbolicCLI()
        
        result = cli.execute_chain_command(1, 3, "test_stream")
        
        assert "chain_id" in result
        assert result["chain_id"] == "001//003//"
        assert "results" in result
        assert len(result["results"]) == 3

    def test_thread_sealing_command(self):
        """Test CLI thread sealing"""
        cli = SymbolicCLI()
        
        seal_hash = cli.seal_thread_command("test_thread", "confidential", "secret123")
        
        assert seal_hash is not None
        assert len(seal_hash) >= 16
        
        # Check glyphcard was generated
        glyphcard_path = cli.output_dir / "glyphcard_test_thread.json"
        assert glyphcard_path.exists()

    def test_invalid_dlp_level(self):
        """Test CLI with invalid DLP level"""
        cli = SymbolicCLI()
        
        with pytest.raises(ValueError, match="Invalid DLP level"):
            cli.seal_thread_command("test_thread", "invalid_level", "key")

    def test_entropy_status_command(self):
        """Test CLI entropy status"""
        cli = SymbolicCLI()
        
        # Execute some operations to generate entropy
        cli.execute_chain_command(1, 2, "entropy_test_data")
        
        status = cli.entropy_status_command()
        
        assert "current_entropy" in status
        assert "threshold" in status
        assert "violations" in status
        assert "threshold_exceeded" in status
        assert "last_update" in status

    def test_manifest_export_command(self):
        """Test CLI manifest export"""
        cli = SymbolicCLI()
        
        # Execute operations
        cli.execute_chain_command(1, 2)
        
        manifest_path = cli.export_manifest_command()
        
        assert Path(manifest_path).exists()
        
        # Verify manifest content
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        assert manifest["system"] == "aurora-cloudbank-symbolic"

    def test_readme_generation_command(self):
        """Test CLI README generation"""
        cli = SymbolicCLI()
        
        # Execute operations to have content
        cli.execute_chain_command(1, 2, "readme_test")
        cli.seal_thread_command("doc_thread", "public", "key123")
        
        readme_path = cli.generate_readme_command()
        
        assert Path(readme_path).exists()
        
        # Verify README content
        with open(readme_path, 'r') as f:
            content = f.read()
            
        assert "Aurora Symbolic Simulation Framework" in content
        assert "T1 (Initial Supersession) Anchor" in content
        assert "SRB (Strategic Resolution Branch) Anchor" in content
        assert "EOS_SEED (End-of-Stream Seeding) Anchor" in content

    def test_diff_manifest_command(self):
        """Test CLI manifest diff"""
        cli = SymbolicCLI()
        
        # Create initial state and export
        cli.execute_chain_command(1, 2)
        manifest_path = cli.export_manifest_command("test_manifest.json")
        
        # Modify state
        cli.execute_chain_command(3, 4)
        
        # Generate diff
        diff_report = cli.diff_manifest_command(manifest_path)
        
        assert "comparison_timestamp" in diff_report

    def test_list_threads_command(self):
        """Test CLI thread listing"""
        cli = SymbolicCLI()
        
        # Create threads
        cli.seal_thread_command("thread1", "public", "key1")
        cli.seal_thread_command("thread2", "restricted", "key2")
        
        threads = cli.list_threads_command()
        
        assert len(threads) == 2
        assert any(t["thread_id"] == "thread1" for t in threads)
        assert any(t["thread_id"] == "thread2" for t in threads)


# Integration test
def test_full_symbolic_workflow():
    """Test complete symbolic simulation workflow"""
    cli = SymbolicCLI()
    
    # 1. Execute symbolic chains
    cli.execute_chain_command(1, 5, "workflow_test_data")
    
    # 2. Seal multiple threads with different DLP levels
    cli.seal_thread_command("workflow_thread_1", "public", "key1")
    cli.seal_thread_command("workflow_thread_2", "confidential", "key2")
    
    # 3. Export initial manifest
    manifest1_path = cli.export_manifest_command("workflow_manifest_1.json")
    
    # 4. Execute more operations
    cli.execute_chain_command(6, 10, "additional_workflow_data")
    
    # 5. Rehydrate and modify thread
    assert cli.rehydrate_thread_command("workflow_thread_1", "key1")
    
    # 6. Export second manifest
    manifest2_path = cli.export_manifest_command("workflow_manifest_2.json")
    
    # 7. Generate diff report
    diff_report = cli.diff_manifest_command(manifest1_path)
    
    # 8. Generate comprehensive documentation
    readme_path = cli.generate_readme_command("workflow_readme.md")
    
    # 9. Check entropy status
    entropy_status = cli.entropy_status_command()
    
    # 10. List all threads
    threads = cli.list_threads_command()
    
    # Verify workflow completion
    assert Path(manifest1_path).exists()
    assert Path(manifest2_path).exists()
    assert Path(readme_path).exists()
    assert len(threads) == 2
    assert "current_entropy" in entropy_status