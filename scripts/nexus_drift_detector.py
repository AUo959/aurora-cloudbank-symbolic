#!/usr/bin/env python3
"""
NEXUS Drift Detection and Audit Trail Generator
Anchor: T6-DRIFT-DETECT-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 1.0.0
DLP Tag: MONITORING_CRITICAL
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import subprocess

class NEXUSDriftDetector:
    """
    Comprehensive drift detection and audit trail generation
    for the complete NEXUS system
    """
    
    def __init__(self):
        self.anchor = "T6-DRIFT-DETECT-2025"
        self.seed = "EOS_SEED_ORION"
        self.arbiter = "AUo959"
        self.drift_events = []
        self.audit_trail = []
        
    def detect_anchor_drift(self) -> Dict:
        """Detect any drift in symbolic anchors across the system"""
        
        expected_anchors = [
            "NEXUS-BOOTSTRAP-2025",
            "T1-NEXUS-INIT-20250925",
            "T2-MULTIAGENT-2025",
            "T3-QUANTUM-2025",
            "T4-MEMORY-WEAVE-2025",
            "T5-REALITY-FORK-2025",
            "T6-EMERGENCE-2025"
        ]
        
        drift_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "anchor": self.anchor,
            "expected_anchors": expected_anchors,
            "found_anchors": [],
            "missing_anchors": [],
            "unexpected_anchors": [],
            "drift_detected": False
        }
        
        # Scan for anchors in codebase
        for module_path in Path("modules/nexus").rglob("*.py"):
            try:
                content = module_path.read_text()
                for line in content.split('\n'):
                    if 'Anchor:' in line or 'anchor =' in line:
                        # Extract anchor
                        if '"' in line:
                            anchor = line.split('"')[1] if '"' in line else None
                        elif "'" in line:
                            anchor = line.split("'")[1] if "'" in line else None
                        else:
                            continue
                            
                        if anchor and anchor.startswith(('T', 'NEXUS')):
                            if anchor not in drift_report["found_anchors"]:
                                drift_report["found_anchors"].append(anchor)
            except:
                continue
                
        # Check for missing anchors
        drift_report["missing_anchors"] = [
            a for a in expected_anchors if a not in drift_report["found_anchors"]
        ]
        
        # Check for unexpected anchors
        drift_report["unexpected_anchors"] = [
            a for a in drift_report["found_anchors"] if a not in expected_anchors
        ]
        
        # Determine if drift detected
        if drift_report["missing_anchors"] or drift_report["unexpected_anchors"]:
            drift_report["drift_detected"] = True
            self.drift_events.append({
                "type": "anchor_drift",
                "details": drift_report,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        return drift_report
        
    def detect_entropy_drift(self) -> Dict:
        """Detect entropy drift across all components"""
        
        entropy_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "global_entropy": 0.0,
            "drift_threshold": 0.1,
            "components_in_drift": []
        }
        
        # Check each component's entropy state
        entropy_files = list(Path(".nexus").rglob("*entropy*.json"))
        
        for entropy_file in entropy_files:
            try:
                data = json.loads(entropy_file.read_text())
                component = entropy_file.stem
                
                if "entropy" in data or "entropy_state" in data:
                    entropy_data = data.get("entropy_state", data.get("entropy", {}))
                    
                    if isinstance(entropy_data, dict):
                        current = entropy_data.get("current", 0.5)
                        baseline = entropy_data.get("baseline", 0.5)
                        drift = entropy_data.get("drift", abs(current - baseline))
                        
                        entropy_report["components"][component] = {
                            "current": current,
                            "baseline": baseline,
                            "drift": drift
                        }
                        
                        if drift > entropy_report["drift_threshold"]:
                            entropy_report["components_in_drift"].append(component)
                            
                        entropy_report["global_entropy"] += current
                        
            except:
                continue
                
        # Calculate average global entropy
        if entropy_report["components"]:
            entropy_report["global_entropy"] /= len(entropy_report["components"])
            
        # Check for systemic drift
        if entropy_report["components_in_drift"]:
            self.drift_events.append({
                "type": "entropy_drift",
                "details": entropy_report,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        return entropy_report
        
    def generate_audit_trail(self) -> Dict:
        """Generate comprehensive audit trail for all NEXUS operations"""
        
        audit_trail = {
            "trail_id": f"AUDIT-{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat(),
            "anchor": self.anchor,
            "seed": self.seed,
            "arbiter": self.arbiter,
            "git_history": [],
            "component_changes": [],
            "sealed_states": [],
            "divergent_truths": [],
            "emergence_events": []
        }
        
        # Get git history
        try:
            git_log = subprocess.check_output(
                ["git", "log", "--oneline", "-20"],
                text=True
            ).strip().split('\n')
            
            for line in git_log:
                if line:
                    parts = line.split(' ', 1)
                    audit_trail["git_history"].append({
                        "commit": parts[0],
                        "message": parts[1] if len(parts) > 1 else ""
                    })
        except:
            pass
            
        # Check for sealed states
        sealed_states = list(Path(".nexus").rglob("*seal*.json"))
        for sealed_file in sealed_states:
            try:
                data = json.loads(sealed_file.read_text())
                if "seal" in data:
                    audit_trail["sealed_states"].append({
                        "file": str(sealed_file),
                        "seal": data["seal"][:16] + "...",
                        "timestamp": data.get("timestamp", "unknown")
                    })
            except:
                continue
                
        # Check for divergent truths
        divergent_files = list(Path(".nexus/divergences").glob("*.json")) if Path(".nexus/divergences").exists() else []
        for div_file in divergent_files:
            try:
                data = json.loads(div_file.read_text())
                audit_trail["divergent_truths"].append({
                    "file": div_file.name,
                    "type": data.get("type", "unknown"),
                    "requires_arbitration": data.get("requires_arbitration", False)
                })
            except:
                continue
                
        # Check for emergence events
        emergence_files = list(Path(".nexus/emergence/events").glob("*.json")) if Path(".nexus/emergence/events").exists() else []
        for emrg_file in emergence_files:
            try:
                data = json.loads(emrg_file.read_text())
                audit_trail["emergence_events"].append({
                    "event_id": data.get("event_id", "unknown"),
                    "type": data.get("type", "unknown"),
                    "timestamp": data.get("timestamp", "unknown")
                })
            except:
                continue
                
        # Record audit trail
        self.audit_trail.append(audit_trail)
        
        # Seal audit trail
        audit_seal = hashlib.sha256(
            json.dumps(audit_trail, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        audit_trail["seal"] = audit_seal
        
        # Save audit trail
        audit_path = Path(f".nexus/audit/{audit_trail['trail_id']}.json")
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(json.dumps(audit_trail, indent=2))
        
        return audit_trail
        
    def generate_drift_report(self) -> str:
        """Generate human-readable drift report"""
        
        anchor_drift = self.detect_anchor_drift()
        entropy_drift = self.detect_entropy_drift()
        audit_trail = self.generate_audit_trail()
        
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║                    🔍 NEXUS DRIFT DETECTION REPORT                 ║
║                                                                     ║
║  Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}                            ║
║  Anchor: {self.anchor}                                ║
║  Arbiter: {self.arbiter}                                                ║
║                                                                     ║
║  ┌───────────────────────────────────────────────────────────┐     ║
║  │                  ANCHOR DRIFT ANALYSIS                     │     ║
║  │                                                            │     ║
║  │  Expected Anchors: {len(anchor_drift['expected_anchors'])}                                │     ║
║  │  Found Anchors:    {len(anchor_drift['found_anchors'])}                                │     ║
║  │  Missing:          {len(anchor_drift['missing_anchors'])}                                 │     ║
║  │  Unexpected:       {len(anchor_drift['unexpected_anchors'])}                                 │     ║
║  │  Drift Detected:   {'YES ⚠️' if anchor_drift['drift_detected'] else 'NO ✅'}                         │     ║
║  └───────────────────────────────────────────────────────────┘     ║
║                                                                     ║
║  ┌───────────────────────────────────────────────────────────┐     ║
║  │                  ENTROPY DRIFT ANALYSIS                    │     ║
║  │                                                            │     ║
║  │  Components Monitored: {len(entropy_drift['components'])}                             │     ║
║  │  Global Entropy:       {entropy_drift['global_entropy']:.3f}                         │     ║
║  │  Components in Drift:  {len(entropy_drift['components_in_drift'])}                              │     ║
║  │  Drift Threshold:      {entropy_drift['drift_threshold']}                          │     ║
║  └───────────────────────────────────────────────────────────┘     ║
║                                                                     ║
║  ┌───────────────────────────────────────────────────────────┐     ║
║  │                     AUDIT TRAIL SUMMARY                    │     ║
║  │                                                            │     ║
║  │  Git Commits:       {len(audit_trail['git_history'])}                                │     ║
║  │  Sealed States:     {len(audit_trail['sealed_states'])}                                │     ║
║  │  Divergent Truths:  {len(audit_trail['divergent_truths'])}                                 │     ║
║  │  Emergence Events:  {len(audit_trail['emergence_events'])}                                 │     ║
║  └───────────────────────────────────────────────────────────┘     ║
║                                                                     ║
║  Trail ID: {audit_trail['trail_id']}                       ║
║  Seal: {audit_trail['seal'][:32]}...                    ║
╚════════════════════════════════════════════════════════════════════╝
        """
        
        return report

def main():
    """Run drift detection and generate reports"""
    
    detector = NEXUSDriftDetector()
    
    print("🔍 NEXUS Drift Detection & Audit Trail Generation")
    print("="*60)
    
    # Generate and display report
    report = detector.generate_drift_report()
    print(report)
    
    # Check for critical drift
    if detector.drift_events:
        print("\n⚠️ DRIFT EVENTS DETECTED:")
        for event in detector.drift_events:
            print(f"  - {event['type']}: {event['timestamp']}")
            
        print("\n📋 Drift events require arbitration")
    else:
        print("\n✅ No drift detected - system stable")
        
    print(f"\n📁 Audit trail saved to: .nexus/audit/")

if __name__ == "__main__":
    main()