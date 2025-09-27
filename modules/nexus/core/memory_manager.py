#!/usr/bin/env python3
"""
Symbolic Memory Manager
Anchor: T1-MEMORY-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 1.0.0
DLP Tag: CORE_INFRASTRUCTURE
"""

import hashlib
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class SymbolicMemoryManager:
    """
    Manages symbolic memory with full traceability and entropy awareness.
    Every memory operation is anchored and sealed.
    """
    
    def __init__(self, anchor: str = "T1-MEMORY-2025"):
        self.anchor = anchor
        self.seed = "EOS_SEED_ORION"
        self.memory_store = {}
        self.sealed_memories = []
        self.entropy_log = []
        self.drift_threshold = 0.1
        
    def store(self, key: str, value: Any, dlp_tag: str = "GENERAL") -> str:
        """
        Store value with symbolic anchor and DLP tag.
        Returns: Hash of sealed memory entry
        """
        entry = {
            "key": key,
            "value": value,
            "timestamp": datetime.now(UTC).isoformat(),
            "anchor": f"{self.anchor}-{key.upper()}",
            "dlp_tag": dlp_tag,
            "entropy": self._calculate_entropy(value)
        }
        
        # Seal the entry
        entry_hash = hashlib.sha256(
            json.dumps(entry, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        entry["seal"] = entry_hash
        self.memory_store[key] = entry
        self.sealed_memories.append(entry_hash)
        
        # Check for entropy drift
        self._check_entropy_drift()
        
        logger.info(f"Stored {key} with seal {entry_hash[:16]}...")
        return entry_hash
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value with seal verification"""
        if key not in self.memory_store:
            return None
            
        entry = self.memory_store[key]
        
        # Verify seal
        expected_seal = entry["seal"]
        entry_copy = entry.copy()
        del entry_copy["seal"]
        
        actual_seal = hashlib.sha256(
            json.dumps(entry_copy, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        if expected_seal != actual_seal:
            logger.error(f"Seal verification failed for {key}!")
            # Flag divergent truth
            self._flag_divergent_truth(key, expected_seal, actual_seal)
            return None
            
        return entry["value"]
    
    def _calculate_entropy(self, value: Any) -> float:
        """Calculate entropy of stored value"""
        # Simplified entropy calculation
        value_str = str(value)
        entropy = len(set(value_str)) / len(value_str) if value_str else 0
        return entropy
    
    def _check_entropy_drift(self):
        """Monitor for entropy drift"""
        if not self.entropy_log:
            return
            
        recent_entropy = [e["entropy"] for e in list(self.memory_store.values())[-10:]]
        if recent_entropy:
            avg_entropy = sum(recent_entropy) / len(recent_entropy)
            drift = abs(avg_entropy - 0.5)
            
            if drift > self.drift_threshold:
                logger.warning(f"Entropy drift detected: {drift:.3f}")
                self._trigger_entropy_alert(drift)
    
    def _flag_divergent_truth(self, key: str, expected: str, actual: str):
        """Flag divergent truth for arbitration"""
        divergence = {
            "key": key,
            "expected_seal": expected,
            "actual_seal": actual,
            "timestamp": datetime.now(UTC).isoformat(),
            "requires_arbitration": True
        }
        
        # Save for review
        divergence_path = Path(f".nexus/divergences/{key}_{datetime.now(UTC).timestamp()}.json")
        divergence_path.parent.mkdir(parents=True, exist_ok=True)
        divergence_path.write_text(json.dumps(divergence, indent=2))
        
        logger.error(f"DIVERGENT TRUTH: {key} requires arbitration")
    
    def _trigger_entropy_alert(self, drift: float):
        """Trigger entropy drift alert"""
        alert = {
            "type": "entropy_drift",
            "drift": drift,
            "timestamp": datetime.now(UTC).isoformat(),
            "anchor": self.anchor
        }
        
        self.entropy_log.append(alert)
        logger.warning(f"ENTROPY ALERT: Drift {drift:.3f} exceeds threshold")
    
    def export_manifest(self) -> Dict:
        """Export complete memory manifest"""
        manifest = {
            "manifest_version": "1.0.0",
            "anchor": self.anchor,
            "seed": self.seed,
            "export_time": datetime.now(UTC).isoformat(),
            "team": "Aurora Core",
            "memory_count": len(self.memory_store),
            "sealed_count": len(self.sealed_memories),
            "entropy_alerts": len(self.entropy_log),
            "dlp_classification": "INTERNAL_USE"
        }
        
        # Seal the manifest
        manifest_seal = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest()
        
        manifest["seal"] = manifest_seal
        
        return manifest

# Module-level initialization
memory_manager = SymbolicMemoryManager()

def get_memory_manager() -> SymbolicMemoryManager:
    """Get singleton memory manager instance"""
    return memory_manager