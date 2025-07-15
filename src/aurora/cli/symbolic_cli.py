#!/usr/bin/env python3
"""Aurora Cloudbank Symbolic CLI - Advanced Chain Operations"""
import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from aurora.core.symbolic_engine import SymbolicEngine


class SymbolicCLI:
    """CLI interface for advanced symbolic operations"""
    
    def __init__(self):
        self.engine = SymbolicEngine()
        self.checkpoints = {}
    
    def execute_chain(self, start: int, end: int, branch_id: str = None):
        """Execute chain with optional branching"""
        result = self.engine.execute_chain(start, end, branch_id)
        print(f"Chain executed: {start:03d}//{end:03d}//{branch_id or ''}")
        print(f"Steps completed: {len(result)}")
        return result
    
    def create_checkpoint(self, checkpoint_name: str):
        """Create a checkpoint for rollback capability"""
        snapshot = self.engine.create_snapshot(f"checkpoint_{checkpoint_name}")
        self.checkpoints[checkpoint_name] = snapshot
        print(f"Checkpoint '{checkpoint_name}' created")
        return checkpoint_name
    
    def rollback_to_checkpoint(self, checkpoint_name: str):
        """Rollback to a previous checkpoint"""
        if checkpoint_name not in self.checkpoints:
            print(f"Error: Checkpoint '{checkpoint_name}' not found")
            return False
        
        checkpoint = self.checkpoints[checkpoint_name]
        
        # Restore engine state from checkpoint
        self.engine.t1.state = checkpoint["t1_anchor"]["state"]
        self.engine.t1.entropy = checkpoint["t1_anchor"]["entropy"]
        self.engine.srb.resolution = checkpoint["srb_anchor"]["resolution"]
        self.engine.srb.entropy = checkpoint["srb_anchor"]["entropy"]
        self.engine.chains = checkpoint["chains"]
        
        print(f"Rolled back to checkpoint '{checkpoint_name}'")
        return True
    
    def execute_parallel_chains(self, chain_specs: list):
        """Execute multiple chains in parallel notation"""
        results = {}
        for spec in chain_specs:
            start, end, branch_id = spec
            result = self.engine.execute_chain(start, end, branch_id)
            results[f"{start:03d}//{end:03d}//{branch_id}//"] = result
        
        print(f"Executed {len(chain_specs)} parallel chains")
        return results
    
    def export_status(self):
        """Export comprehensive symbolic status"""
        manifest = self.engine.export_manifest()
        entropy_summary = manifest["entropy_summary"]
        
        status = {
            "system_version": manifest["version"],
            "anchor_states": {
                "t1_state": manifest["t1_anchor"]["state"],
                "srb_resolution": manifest["srb_anchor"]["resolution"]
            },
            "entropy_status": entropy_summary,
            "chain_count": len(manifest["chains"]),
            "sealed_threads": manifest["sealed_threads_count"],
            "snapshots": manifest["snapshots_count"],
            "dlp_tags": len(manifest["dlp_tags"]),
            "checkpoints": list(self.checkpoints.keys())
        }
        
        return status


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Aurora Cloudbank Symbolic CLI")
    parser.add_argument("--version", action="version", version="2.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chain execution
    chain_parser = subparsers.add_parser("chain", help="Execute symbolic chain")
    chain_parser.add_argument("start", type=int, help="Chain start number")
    chain_parser.add_argument("end", type=int, help="Chain end number")
    chain_parser.add_argument("--branch", help="Branch identifier")
    
    # Checkpoint operations
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Checkpoint operations")
    checkpoint_parser.add_argument("action", choices=["create", "rollback", "list"])
    checkpoint_parser.add_argument("--name", help="Checkpoint name")
    
    # Parallel execution
    parallel_parser = subparsers.add_parser("parallel", help="Execute parallel chains")
    parallel_parser.add_argument("chains", help="JSON string with chain specifications")
    
    # Status export
    status_parser = subparsers.add_parser("status", help="Export system status")
    status_parser.add_argument("--format", choices=["json", "text"], default="text")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SymbolicCLI()
    
    if args.command == "chain":
        cli.execute_chain(args.start, args.end, args.branch)
    
    elif args.command == "checkpoint":
        if args.action == "create":
            if not args.name:
                print("Error: --name required for checkpoint creation")
                return
            cli.create_checkpoint(args.name)
        elif args.action == "rollback":
            if not args.name:
                print("Error: --name required for rollback")
                return
            cli.rollback_to_checkpoint(args.name)
        elif args.action == "list":
            checkpoints = list(cli.checkpoints.keys())
            print(f"Available checkpoints: {checkpoints}")
    
    elif args.command == "parallel":
        try:
            chain_specs = json.loads(args.chains)
            cli.execute_parallel_chains(chain_specs)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for chain specifications")
    
    elif args.command == "status":
        status = cli.export_status()
        if args.format == "json":
            print(json.dumps(status, indent=2))
        else:
            print("=== Aurora Cloudbank Symbolic Status ===")
            print(f"System Version: {status['system_version']}")
            print(f"T1 State: {status['anchor_states']['t1_state']}")
            print(f"SRB Resolution: {status['anchor_states']['srb_resolution']}")
            print(f"Entropy Warnings: T1={status['entropy_status']['t1_warning']}, SRB={status['entropy_status']['srb_warning']}")
            print(f"Active Chains: {status['chain_count']}")
            print(f"Sealed Threads: {status['sealed_threads']}")
            print(f"Snapshots: {status['snapshots']}")
            print(f"DLP Tags: {status['dlp_tags']}")
            print(f"Checkpoints: {status['checkpoints']}")


if __name__ == "__main__":
    main()