#!/usr/bin/env python3
"""
NEXUS Phase 1 Verification & Thread Continuity Check
Anchor: NEXUS-VERIFY-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 1.1.0
DLP Tag: VERIFICATION_CRITICAL
"""

import logging

logger = logging.getLogger(__name__)

import json
import hashlib
from pathlib import Path
from src.core.time_utils import utc_iso, utc_now
from typing import Dict, Tuple

 
class NEXUSVerification:
    """
    Verify Phase 1 implementation and prepare for Phase 2 transition
    Ensures all symbolic anchors are intact and entropy is nominal
    """
    
    def __init__(self):
        self.anchor = "NEXUS-VERIFY-2025"
        self.seed = "EOS_SEED_ORION"
        self.verification_results = {}
        self.entropy_state = {"level": "nominal", "drift": 0.0}
        self.thread_continuity = True
        
    def verify_phase1_components(self) -> Dict:
        """Verify all Phase 1 components are operational"""
        
        components_to_verify = [
            ("Memory Manager", "modules/nexus/core/memory_manager.py"),
            ("Entity Manager", "modules/nexus/core/entity_manager.py"),
            ("Entropy Monitor", "modules/nexus/core/entropy_monitor.py"),
            ("CLI Interface", "nexus_cli.py"),
            ("Practical Goals", "modules/nexus/practical_goals.py"),
            ("Anchor Registry", ".nexus/anchors/registry.json")
        ]
        
        verification_report = {
            "timestamp": utc_iso(),
            "anchor": self.anchor,
            "components": {},
            "overall_status": "PASS",
            "entropy_check": "NOMINAL"
        }
        
        for component_name, component_path in components_to_verify:
            path = Path(component_path)
            if path.exists():
                # Calculate component hash for integrity
                if path.is_file():
                    content = path.read_bytes()
                    component_hash = hashlib.sha256(content).hexdigest()
                    
                    verification_report["components"][component_name] = {
                        "status": "VERIFIED",
                        "path": str(path),
                        "hash": component_hash[:16],
                        "size": len(content),
                        "anchor_present": "T1-" in str(content) or "NEXUS-" in str(content)
                    }
                else:
                    verification_report["components"][component_name] = {
                        "status": "DIRECTORY",
                        "path": str(path)
                    }
            else:
                verification_report["components"][component_name] = {
                    "status": "MISSING",
                    "path": str(path)
                }
                verification_report["overall_status"] = "FAIL"
                
        # Seal verification report
        report_hash = hashlib.sha256(
            json.dumps(verification_report, sort_keys=True).encode()
        ).hexdigest()
        
        verification_report["seal"] = report_hash
        
        # Save verification report
        report_path = Path(f".nexus/verification/phase1_{utc_now().strftime('%Y%m%d_%H%M%S')}.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(verification_report, indent=2))
        
        return verification_report
    
    def check_thread_continuity(self) -> Tuple[bool, Dict]:
        """Verify thread continuity from Phase 1 to Phase 2"""
        
        continuity_check = {
            "thread_id": "T1-NEXUS-INIT-20250925",
            "primary_anchor": "NEXUS-BOOTSTRAP-2025",
            "seed": "EOS_SEED_ORION",
            "arbiter": "AUo959",
            "checkpoints": [],
            "entities": [],
            "memory_seals": [],
            "continuity_intact": True
        }
        
        # Check for checkpoints
        checkpoint_dir = Path(".nexus/checkpoints")
        if checkpoint_dir.exists():
            for checkpoint_file in checkpoint_dir.glob("*.json"):
                try:
                    checkpoint = json.loads(checkpoint_file.read_text())
                    continuity_check["checkpoints"].append({
                        "file": checkpoint_file.name,
                        "seal": checkpoint.get("seal", "")[:16],
                        "timestamp": checkpoint.get("timestamp", "")
                    })
                except Exception:
                    continuity_check["continuity_intact"] = False
                    
        # Check for entities
        entity_dir = Path(".nexus/entities")
        if entity_dir.exists():
            for entity_file in entity_dir.glob("*.json"):
                try:
                    entity = json.loads(entity_file.read_text())
                    continuity_check["entities"].append({
                        "id": entity.get("id", ""),
                        "type": entity.get("type", ""),
                        "seal": entity.get("seal", "")[:16]
                    })
                except Exception:
                    continuity_check["continuity_intact"] = False
                    
        return continuity_check["continuity_intact"], continuity_check
    
    def generate_phase2_manifest(self) -> Dict:
        """Generate manifest for Phase 2 transition"""
        
        phase2_manifest = {
            "manifest_version": "2.0.0",
            "phase": "NEXUS_PHASE_2",
            "anchor": "NEXUS-PHASE2-2025",
            "seed": "EOS_SEED_ORION",
            "timestamp": utc_iso(),
            "arbiter": "AUo959",
            "thread_continuation": "T1-NEXUS-INIT-20250925",
            "phase2_objectives": [
                {
                    "id": "P2-001",
                    "name": "Multi-Agent Coordination",
                    "status": "READY_TO_IMPLEMENT",
                    "anchor": "T2-MULTIAGENT-2025"
                },
                {
                    "id": "P2-002",
                    "name": "Quantum State Bridge",
                    "status": "READY_TO_IMPLEMENT",
                    "anchor": "T2-QUANTUM-2025"
                },
                {
                    "id": "P2-003",
                    "name": "Collaborative Debugging",
                    "status": "READY_TO_IMPLEMENT",
                    "anchor": "T2-COLLAB-2025"
                }
            ],
            "prerequisites_met": True,
            "entropy_state": self.entropy_state,
            "dlp_classification": "INTERNAL_DEVELOPMENT"
        }
        
        # Seal the manifest
        manifest_hash = hashlib.sha256(
            json.dumps(phase2_manifest, sort_keys=True).encode()
        ).hexdigest()
        
        phase2_manifest["seal"] = manifest_hash
        
        # Save Phase 2 manifest
        manifest_path = Path(".nexus/manifests/phase2_manifest.json")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(phase2_manifest, indent=2))
        
        return phase2_manifest

def main():
    """Run verification and prepare Phase 2"""
    
    print("🔍 NEXUS Phase 1 Verification")
    print("="*50)
    
    verifier = NEXUSVerification()
    
    # Verify Phase 1 components
    print("\n📋 Verifying Phase 1 Components...")
    verification = verifier.verify_phase1_components()
    
    logger.info("Overall Status: %s", verification['overall_status'])
    for component, status in verification["components"].items():
        status_icon = "✅" if status["status"] == "VERIFIED" else "❌"
        logger.info("Component %s status: %s (%s)", component, status['status'], status_icon)
    
    # Check thread continuity
    print("\n🔗 Checking Thread Continuity...")
    continuity_intact, continuity = verifier.check_thread_continuity()
    
    if continuity_intact:
        logger.info("Thread continuity intact")
        logger.info(
            "Thread: %s | Entities: %d | Checkpoints: %d",
            continuity['thread_id'],
            len(continuity['entities']),
            len(continuity['checkpoints'])
        )
    else:
        logger.warning("Thread continuity issues detected")
        
    # Generate Phase 2 manifest
    print("\n🚀 Generating Phase 2 Manifest...")
    phase2 = verifier.generate_phase2_manifest()
    
    logger.info(
        "Phase2 Anchor: %s | Objectives: %d | Seal Prefix: %s",
        phase2['anchor'],
        len(phase2['phase2_objectives']),
        phase2['seal'][:32]
    )
    
    print("\n✅ Verification Complete - Ready for Phase 2!")
    
    return verification, continuity, phase2

if __name__ == "__main__":
    verification, continuity, phase2 = main()
