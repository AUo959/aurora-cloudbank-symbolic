#!/usr/bin/env python3
"""
Memory Manager Test Suite
Anchor: T1-TEST-MEMORY-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
"""

import pytest
import sys
from pathlib import Path
import json
import tempfile
import shutil

# Add module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.nexus.core.memory_manager import SymbolicMemoryManager

class TestSymbolicMemoryManager:
    """Test suite for Symbolic Memory Manager"""
    
    def setup_method(self):
        """Setup for each test"""
        self.manager = SymbolicMemoryManager()
        # Create temporary directory for divergences
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Cleanup after each test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations"""
        # Store a value
        seal = self.manager.store("test_key", "test_value", "TEST")
        assert seal is not None
        assert len(seal) == 64  # SHA256 hash length
        
        # Retrieve the value
        value = self.manager.retrieve("test_key")
        assert value == "test_value"

    def test_seal_verification(self):
        """Test seal verification on retrieval"""
        # Store a value
        seal = self.manager.store("secure_key", {"data": "sensitive"}, "CRITICAL")
        
        # Retrieve should work with valid seal
        value = self.manager.retrieve("secure_key")
        assert value == {"data": "sensitive"}
        
        # Corrupt the seal manually
        self.manager.memory_store["secure_key"]["value"] = "corrupted"
        
        # Retrieve should fail with corrupted data
        value = self.manager.retrieve("secure_key")
        assert value is None  # Seal verification failed

    def test_entropy_calculation(self):
        """Test entropy calculation"""
        # Store values with different entropy
        self.manager.store("low_entropy", "aaaaaaa", "TEST")
        self.manager.store("high_entropy", "abcdefg", "TEST")
        
        low_entry = self.manager.memory_store["low_entropy"]
        high_entry = self.manager.memory_store["high_entropy"]
        
        assert low_entry["entropy"] < high_entry["entropy"]

    def test_manifest_export(self):
        """Test manifest export"""
        # Store some values
        self.manager.store("key1", "value1")
        self.manager.store("key2", "value2")
        
        # Export manifest
        manifest = self.manager.export_manifest()
        
        assert manifest["memory_count"] == 2
        assert manifest["sealed_count"] == 2
        assert "seal" in manifest
        assert len(manifest["seal"]) == 64
        assert manifest["anchor"] == "T1-MEMORY-2025"
        assert manifest["seed"] == "EOS_SEED_ORION"

    def test_dlp_tagging(self):
        """Test DLP tag assignment"""
        # Store with different DLP tags
        self.manager.store("public_data", "public_info", "PUBLIC")
        self.manager.store("secret_data", "classified_info", "CRITICAL")
        
        public_entry = self.manager.memory_store["public_data"]
        secret_entry = self.manager.memory_store["secret_data"]
        
        assert public_entry["dlp_tag"] == "PUBLIC"
        assert secret_entry["dlp_tag"] == "CRITICAL"

    def test_anchor_assignment(self):
        """Test symbolic anchor assignment"""
        self.manager.store("test_anchor", "value", "TEST")
        
        entry = self.manager.memory_store["test_anchor"]
        assert entry["anchor"] == "T1-MEMORY-2025-TEST_ANCHOR"

    def test_timestamp_recording(self):
        """Test timestamp recording"""
        import datetime
        before = datetime.datetime.utcnow()
        
        self.manager.store("time_test", "value")
        
        after = datetime.datetime.utcnow()
        
        entry = self.manager.memory_store["time_test"]
        entry_time = datetime.datetime.fromisoformat(entry["timestamp"])
        
        assert before <= entry_time <= after

    def test_nonexistent_key_retrieval(self):
        """Test retrieving nonexistent key"""
        value = self.manager.retrieve("nonexistent")
        assert value is None

    def test_multiple_stores_different_keys(self):
        """Test storing multiple different keys"""
        seals = []
        for i in range(5):
            seal = self.manager.store(f"key_{i}", f"value_{i}")
            seals.append(seal)
        
        # All seals should be unique
        assert len(set(seals)) == 5
        
        # All values should be retrievable
        for i in range(5):
            value = self.manager.retrieve(f"key_{i}")
            assert value == f"value_{i}"

    def test_complex_data_structures(self):
        """Test storing complex data structures"""
        complex_data = {
            "list": [1, 2, 3, "four"],
            "nested": {
                "dict": {"inside": "value"},
                "number": 42
            },
            "boolean": True,
            "null": None
        }
        
        seal = self.manager.store("complex", complex_data)
        retrieved = self.manager.retrieve("complex")
        
        assert retrieved == complex_data

@pytest.mark.asyncio 
async def test_concurrent_operations():
    """Test concurrent memory operations"""
    import asyncio
    
    manager = SymbolicMemoryManager()
    
    async def store_and_retrieve(i):
        seal = manager.store(f"concurrent_{i}", f"value_{i}")
        await asyncio.sleep(0.01)  # Small delay
        value = manager.retrieve(f"concurrent_{i}")
        return value == f"value_{i}"
    
    # Run concurrent operations
    tasks = [store_and_retrieve(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    # All operations should succeed
    assert all(results)

def test_memory_manager_singleton():
    """Test that get_memory_manager returns singleton"""
    from modules.nexus.core.memory_manager import get_memory_manager
    
    manager1 = get_memory_manager()
    manager2 = get_memory_manager()
    
    assert manager1 is manager2

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])