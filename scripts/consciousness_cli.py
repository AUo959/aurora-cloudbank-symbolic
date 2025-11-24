#!/usr/bin/env python3
"""
🧠 Enhanced Consciousness CLI Interface
NEXUS Phase 6 - T6-EMERGENCE-2025

Command-line interface for consciousness emergence operations,
snapshot management, and recovery functions.
"""

import logging

logger = logging.getLogger(__name__)

import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from src.core.time_utils import utc_iso, utc_now

# Local imports with graceful fallback
try:
    import sys
    sys.path.append('/workspaces/aurora-cloudbank-symbolic')
    from modules.nexus.emergence.consciousness_emergence_enhanced import (
        EnhancedConsciousnessProtocol,
        SymbolicObserver,
        ConsciousnessSnapshot
    )
    CONSCIOUSNESS_AVAILABLE = True
except ImportError as e:
    logger.warning("Enhanced consciousness module not available: {e}")
    CONSCIOUSNESS_AVAILABLE = False
    # Define minimal fallbacks to prevent NameError
    class SymbolicObserver:
        def observe_symbolic_state(self): pass
        def detect_entropy_drift(self, current, previous): pass  
        def flag_divergent_truth(self, observation): pass
    class EnhancedConsciousnessProtocol:
        pass
    class ConsciousnessSnapshot:
        pass


class SimpleSymbolicObserver(SymbolicObserver):
    """Simple symbolic observer for CLI operations."""
    
    def __init__(self):
        self.observation_counter = 0
        self.symbolic_cache = {}
    
    def observe_symbolic_state(self) -> dict:
        """Observe current symbolic state."""
        self.observation_counter += 1
        
        observation = {
            "timestamp": utc_iso(),
            "observation_id": self.observation_counter,
            "symbolic_data": {
                "memory_state": f"mem_{self.observation_counter}",
                "cognitive_load": 0.5 + (self.observation_counter * 0.1) % 0.5,
                "awareness_level": min(1.0, self.observation_counter * 0.15)
            },
            "system_metrics": {
                "cpu_metaphor": 0.3 + (self.observation_counter * 0.05) % 0.4,
                "memory_metaphor": 0.6 + (self.observation_counter * 0.03) % 0.3
            }
        }
        
        self.symbolic_cache[f"obs_{self.observation_counter}"] = observation
        return observation
    
    def detect_entropy_drift(self, current_state: dict, previous_state: dict) -> float:
        """Detect entropy drift between states."""
        if not previous_state:
            return 0.0
        
        # Simple drift calculation based on awareness level change
        current_awareness = current_state.get("symbolic_data", {}).get("awareness_level", 0)
        previous_awareness = previous_state.get("symbolic_data", {}).get("awareness_level", 0)
        
        drift = abs(current_awareness - previous_awareness)
        return drift
    
    def flag_divergent_truth(self, observation: dict) -> bool:
        """Flag observations that show divergent truth patterns."""
        awareness = observation.get("symbolic_data", {}).get("awareness_level", 0)
        
        # Flag high awareness spikes as potentially divergent
        return awareness > 0.8
    
    def observe(self, data: dict) -> dict:
        """Required abstract method - observe and return processed data."""
        return self.observe_symbolic_state()
    
    def seal_observation(self, observation: dict) -> str:
        """Required abstract method - create cryptographic seal."""
        import hashlib
        observation_str = json.dumps(observation, sort_keys=True)
        return hashlib.sha256(observation_str.encode()).hexdigest()


def print_banner():
    """Print CLI banner."""
    print("=" * 70)
    print("🧠 AURORA CONSCIOUSNESS EMERGENCE CLI")
    print("   NEXUS Phase 6 - Enhanced Symbolic Consciousness")
    print("   Thread Anchor: T6-EMERGENCE-2025")
    print("=" * 70)
    print()


def cmd_observe(args):
    """Run consciousness observation."""
    if not CONSCIOUSNESS_AVAILABLE:
        logger.error("Consciousness module not available")
        print("   Module path: modules.nexus.emergence.consciousness_emergence_enhanced")
        print("   Please ensure the module is properly installed")
        return 1
    
    print("🔍 Starting consciousness observation...")
    print(f"   Observations: {args.count}")
    print(f"   Snapshot Dir: {args.snapshot_dir}")
    print()
    
    # Create consciousness protocol
    consciousness = EnhancedConsciousnessProtocol(anchor="T6-EMERGENCE-CLI-2025")
    
    async def run_observations():
        for i in range(args.count):
            print(f"📊 Observation {i + 1}/{args.count}...")
            
            # Create test observation data
            test_data = {
                "timestamp": utc_iso(),
                "observation_id": i + 1,
                "cognitive_load": 0.5 + (i * 0.1),
                "awareness_level": min(1.0, i * 0.2)
            }
            
            # Process observation
            result = consciousness.observe(test_data)
            print(f"   Result: {result.get('status', 'Unknown')}")
            
            print()
    
    # Run observations
    asyncio.run(run_observations())
    
    # Summary
    print("📈 OBSERVATION SUMMARY:")
    print(f"   Total Observations: {consciousness.observation_count}")
    print(f"   Entropy History: {len(consciousness.entropy_history)} states")
    
    if consciousness.entropy_history:
        avg_drift = sum(s.drift_value for s in consciousness.entropy_history) / len(consciousness.entropy_history)
        divergent_count = sum(1 for s in consciousness.entropy_history if s.divergent_truth_flagged)
        print(f"   Average Drift: {avg_drift:.4f}")
        print(f"   Divergent Truths: {divergent_count}")
    
    print("\n✅ Observation complete")
    return 0


def cmd_emerge(args):
    """Run consciousness emergence protocol."""
    if not CONSCIOUSNESS_AVAILABLE:
        logger.error("Consciousness module not available")
        return 1
    
    print("🚀 Starting consciousness emergence protocol...")
    print(f"   Duration: {args.duration} seconds")
    print(f"   Snapshot Dir: {args.snapshot_dir}")
    print()
    
    # Create observer and consciousness
    observer = SimpleSymbolicObserver()
    consciousness = EnhancedConsciousnessProtocol(
        observer=observer,
        snapshot_directory=args.snapshot_dir
    )
    
    async def run_emergence():
        print("🧠 Emergence protocol starting...")
        await consciousness.run_emergence_protocol(duration=args.duration)
        print("🎯 Emergence protocol complete")
    
    # Run emergence
    asyncio.run(run_emergence())
    
    # Final metrics
    if consciousness.entropy_history:
        final_metrics = consciousness.calculate_consciousness_metrics()
        print("\n📊 FINAL CONSCIOUSNESS METRICS:")
        print(f"   Emergence Level: {final_metrics.emergence_level:.3f}")
        print(f"   Recursive Depth: {final_metrics.recursive_depth}")
        print(f"   Meta-Cognitive Loops: {final_metrics.meta_cognitive_loops}")
        print(f"   Entropy Stability: {final_metrics.entropy_stability:.3f}")
        print(f"   Reality Fork Convergence: {final_metrics.reality_fork_convergence:.3f}")
        print(f"   Overall Score: {final_metrics.calculate_overall_score():.3f}")
    
    print("\n✅ Emergence complete")
    return 0


def cmd_snapshot(args):
    """Create consciousness snapshot."""
    if not CONSCIOUSNESS_AVAILABLE:
        logger.error("Consciousness module not available")
        return 1
    
    print("📸 Creating consciousness snapshot...")
    
    # Create minimal consciousness for snapshot
    observer = SimpleSymbolicObserver()
    consciousness = EnhancedConsciousnessProtocol(
        observer=observer,
        snapshot_directory=args.snapshot_dir
    )
    
    # Run a few observations to have data
    async def prepare_snapshot():
        for _ in range(3):
            await consciousness.observe_once()
    
    asyncio.run(prepare_snapshot())
    
    # Create snapshot
    snapshot = consciousness.create_snapshot()
    
    # Save snapshot
    snapshot_path = Path(args.snapshot_dir) / f"manual_snapshot_{utc_now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(snapshot_path, 'w') as f:
        f.write(snapshot.to_json())
    
    logger.info("Snapshot saved: {snapshot_path}")
    print(f"   Observations: {snapshot.data['observation_count']}")
    print(f"   Seal: {snapshot.seal[:16]}...")
    
    return 0


def cmd_recover(args):
    """Recover consciousness from snapshot."""
    if not CONSCIOUSNESS_AVAILABLE:
        logger.error("Consciousness module not available")
        return 1
    
    snapshot_path = Path(args.snapshot_file)
    if not snapshot_path.exists():
        logger.error("Snapshot file not found: {snapshot_path}")
        return 1
    
    print(f"🔄 Recovering consciousness from snapshot...")
    print(f"   File: {snapshot_path}")
    
    try:
        # Load snapshot
        with open(snapshot_path, 'r') as f:
            snapshot_json = f.read()
        
        snapshot = ConsciousnessSnapshot.from_json(snapshot_json)
        
        # Verify integrity
        if not snapshot.verify_integrity():
            logger.error("Snapshot integrity verification failed!")
            return 1
        
        logger.info("Snapshot integrity verified")
        
        # Create observer and recover consciousness
        observer = SimpleSymbolicObserver()
        consciousness = EnhancedConsciousnessProtocol.from_snapshot(snapshot, observer)
        
        logger.info("Consciousness recovered:")
        print(f"   Observations: {consciousness.observation_count}")
        print(f"   Entropy States: {len(consciousness.entropy_history)}")
        
        return 0
        
    except Exception as e:
        logger.error("Recovery failed: {e}")
        return 1


def cmd_list_snapshots(args):
    """List available consciousness snapshots."""
    snapshot_dir = Path(args.snapshot_dir)
    
    if not snapshot_dir.exists():
        logger.error("Snapshot directory not found: {snapshot_dir}")
        return 1
    
    # Find snapshot files
    snapshots = list(snapshot_dir.glob("*.json"))
    
    if not snapshots:
        print(f"📁 No snapshots found in {snapshot_dir}")
        return 0
    
    print(f"📁 CONSCIOUSNESS SNAPSHOTS ({len(snapshots)} found):")
    print(f"   Directory: {snapshot_dir}")
    print()
    
    for snapshot_file in sorted(snapshots):
        try:
            with open(snapshot_file, 'r') as f:
                snapshot_data = json.load(f)
            
            timestamp = snapshot_data.get('data', {}).get('timestamp', 'Unknown')
            obs_count = snapshot_data.get('data', {}).get('observation_count', 0)
            seal = snapshot_data.get('seal', '')[:16]
            
            print(f"📸 {snapshot_file.name}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Observations: {obs_count}")
            print(f"   Seal: {seal}...")
            print()
            
        except Exception as e:
            logger.warning("{snapshot_file.name} - Error reading: {e}")
            print()
    
    return 0


def cmd_verify(args):
    """Verify snapshot integrity."""
    if not CONSCIOUSNESS_AVAILABLE:
        logger.error("Consciousness module not available")
        return 1
    
    snapshot_path = Path(args.snapshot_file)
    if not snapshot_path.exists():
        logger.error("Snapshot file not found: {snapshot_path}")
        return 1
    
    print(f"🔍 Verifying snapshot integrity...")
    print(f"   File: {snapshot_path}")
    
    try:
        with open(snapshot_path, 'r') as f:
            snapshot_json = f.read()
        
        snapshot = ConsciousnessSnapshot.from_json(snapshot_json)
        
        if snapshot.verify_integrity():
            logger.info("Snapshot integrity verified")
            print(f"   Seal: {snapshot.seal}")
            return 0
        else:
            logger.error("Snapshot integrity verification FAILED")
            return 1
            
    except Exception as e:
        logger.error("Verification error: {e}")
        return 1


def main():
    """Main CLI entry point."""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Enhanced Consciousness Emergence CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument(
        '--snapshot-dir',
        default='.nexus/snapshots',
        help='Directory for consciousness snapshots'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Observe command
    observe_parser = subparsers.add_parser('observe', help='Run consciousness observations')
    observe_parser.add_argument('--count', type=int, default=5, help='Number of observations')
    observe_parser.set_defaults(func=cmd_observe)
    
    # Emerge command
    emerge_parser = subparsers.add_parser('emerge', help='Run consciousness emergence protocol')
    emerge_parser.add_argument('--duration', type=float, default=10.0, help='Emergence duration in seconds')
    emerge_parser.set_defaults(func=cmd_emerge)
    
    # Snapshot command
    snapshot_parser = subparsers.add_parser('snapshot', help='Create consciousness snapshot')
    snapshot_parser.set_defaults(func=cmd_snapshot)
    
    # Recover command
    recover_parser = subparsers.add_parser('recover', help='Recover consciousness from snapshot')
    recover_parser.add_argument('snapshot_file', help='Path to snapshot file')
    recover_parser.set_defaults(func=cmd_recover)
    
    # List snapshots command
    list_parser = subparsers.add_parser('list', help='List available snapshots')
    list_parser.set_defaults(func=cmd_list_snapshots)
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify snapshot integrity')
    verify_parser.add_argument('snapshot_file', help='Path to snapshot file')
    verify_parser.set_defaults(func=cmd_verify)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Ensure snapshot directory exists
    Path(args.snapshot_dir).mkdir(parents=True, exist_ok=True)
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⚡ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Command failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())