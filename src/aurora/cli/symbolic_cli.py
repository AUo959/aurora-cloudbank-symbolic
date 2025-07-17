"""Aurora Symbolic CLI Framework - Interactive Simulation Controls"""
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from ..core.symbolic_engine import SymbolicEngine, DLPClassification


class SymbolicCLI:
    """CLI framework for symbolic simulation operations"""

    def __init__(self):
        self.engine = SymbolicEngine()
        self.output_dir = Path("exports")
        self.output_dir.mkdir(exist_ok=True)

    def execute_chain_command(self, start: int, end: int, 
                            stream_data: Optional[str] = None) -> Dict:
        """Execute chain command with 001//999//. format"""
        print(f"Executing symbolic chain {start:03d}//{end:03d}//")
        
        if stream_data:
            print(f"Stream data: {stream_data}")
            
        results = self.engine.execute_chain(start, end, stream_data)
        
        print(f"Chain execution complete. Generated {len(results)} steps.")
        return {"chain_id": f"{start:03d}//{end:03d}//", "results": results}

    def seal_thread_command(self, thread_id: str, dlp_level: str, 
                          operator_key: str) -> str:
        """Seal symbolic thread with memory protection"""
        try:
            dlp_class = DLPClassification(dlp_level.lower())
        except ValueError:
            raise ValueError(f"Invalid DLP level: {dlp_level}. "
                           f"Valid levels: {[e.value for e in DLPClassification]}")
        
        print(f"Sealing thread '{thread_id}' with DLP level '{dlp_level}'")
        seal_hash = self.engine.seal_thread(thread_id, dlp_class, operator_key)
        
        # Generate glyphcard
        glyphcard = self.engine.generate_glyphcard(thread_id)
        glyphcard_path = self.output_dir / f"glyphcard_{thread_id}.json"
        
        with open(glyphcard_path, 'w') as f:
            json.dump(glyphcard, f, indent=2)
            
        print(f"Thread sealed successfully. Seal hash: {seal_hash[:16]}...")
        print(f"Glyphcard generated: {glyphcard_path}")
        return seal_hash

    def rehydrate_thread_command(self, thread_id: str, operator_key: str) -> bool:
        """Rehydrate sealed thread and restore states"""
        print(f"Attempting to rehydrate thread '{thread_id}'")
        
        success = self.engine.rehydrate_thread(thread_id, operator_key)
        
        if success:
            print(f"Thread '{thread_id}' rehydrated successfully")
        else:
            print(f"Failed to rehydrate thread '{thread_id}' - authentication failed or thread not found")
            
        return success

    def export_manifest_command(self, filename: Optional[str] = None) -> str:
        """Export symbolic manifest with metadata"""
        if not filename:
            timestamp = int(time.time())
            filename = f"symbolic_manifest_{timestamp}.json"
            
        manifest_path = self.output_dir / filename
        manifest = self.engine.export_manifest()
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        print(f"Symbolic manifest exported to: {manifest_path}")
        return str(manifest_path)

    def entropy_status_command(self) -> Dict:
        """Display entropy monitoring status"""
        entropy_state = self.engine.entropy_state
        
        status = {
            "current_entropy": entropy_state.current_entropy,
            "threshold": entropy_state.threshold,
            "violations": entropy_state.violations,
            "threshold_exceeded": entropy_state.is_threshold_exceeded(),
            "last_update": entropy_state.last_update
        }
        
        print("=== Entropy Monitoring Status ===")
        print(f"Current Entropy: {status['current_entropy']:.4f}")
        print(f"Threshold: {status['threshold']:.4f}")
        print(f"Violations: {status['violations']}")
        print(f"Threshold Exceeded: {status['threshold_exceeded']}")
        print(f"Last Update: {time.ctime(status['last_update'])}")
        
        return status

    def diff_manifest_command(self, manifest_file: str) -> Dict:
        """Generate diff report between current state and saved manifest"""
        manifest_path = Path(manifest_file)
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_file}")
            
        with open(manifest_path, 'r') as f:
            other_manifest = json.load(f)
            
        diff_report = self.engine.generate_diff_report(other_manifest)
        
        # Save diff report
        timestamp = int(time.time())
        diff_path = self.output_dir / f"diff_report_{timestamp}.json"
        
        with open(diff_path, 'w') as f:
            json.dump(diff_report, f, indent=2)
            
        print(f"Diff report generated: {diff_path}")
        return diff_report

    def list_threads_command(self) -> List[Dict]:
        """List all symbolic threads and their states"""
        threads = []
        
        print("=== Symbolic Threads ===")
        
        for thread_id, thread_state in self.engine.thread_states.items():
            thread_info = {
                "thread_id": thread_id,
                "dlp_classification": thread_state.dlp_classification.value,
                "sealed": thread_state.sealed,
                "timestamp": thread_state.timestamp,
                "entropy_signature": thread_state.entropy_signature[:16]
            }
            threads.append(thread_info)
            
            print(f"Thread: {thread_id}")
            print(f"  DLP: {thread_info['dlp_classification']}")
            print(f"  Sealed: {thread_info['sealed']}")
            print(f"  Created: {time.ctime(thread_info['timestamp'])}")
            print(f"  Signature: {thread_info['entropy_signature']}...")
            print()
            
        return threads

    def generate_readme_command(self, output_file: Optional[str] = None) -> str:
        """Generate README documentation for symbolic anchors"""
        if not output_file:
            output_file = "README-symbolic-anchors.md"
            
        readme_path = self.output_dir / output_file
        
        # Get current manifest for documentation
        manifest = self.engine.export_manifest()
        
        readme_content = f"""# Aurora Symbolic Simulation Framework

## Overview
This document describes the current state of the Aurora symbolic simulation framework with its comprehensive anchor system.

## Symbolic Anchors

### T1 (Initial Supersession) Anchor
- **Type**: Temporal anchor for sequential state progression
- **Current State**: {manifest['anchors']['t1']['state']}
- **Purpose**: Tracks temporal advancement through symbolic operations

### SRB (Strategic Resolution Branch) Anchor  
- **Type**: Spatial-relational boundary resolution
- **Current Resolution**: {manifest['anchors']['srb']['resolution']}
- **Purpose**: Manages boundary resolution in symbolic space

### EOS_SEED (End-of-Stream Seeding) Anchor
- **Type**: Stream termination and seeding control
- **Seed Count**: {manifest['anchors']['eos_seed']['seed_count']}
- **Stream Status**: {'Terminated' if manifest['anchors']['eos_seed']['stream_terminated'] else 'Active'}
- **Purpose**: Controls stream seeding and termination sequences

## Entropy Monitoring
- **Current Entropy**: {manifest['entropy_monitoring']['current_entropy']:.4f}
- **Threshold**: {manifest['entropy_monitoring']['threshold']:.4f}
- **Violations**: {manifest['entropy_monitoring']['violations']}
- **Status**: {'⚠️ Threshold Exceeded' if manifest['entropy_monitoring']['current_entropy'] > manifest['entropy_monitoring']['threshold'] else '✅ Within Threshold'}

## Active Chains
Total chains executed: {len(manifest['chains'])}

## Sealed Threads
Total sealed threads: {len(manifest['sealed_threads'])}

### Thread Summary
"""
        
        # Add thread details
        for thread_id, thread_info in manifest['sealed_threads'].items():
            readme_content += f"""
#### Thread: {thread_id}
- **DLP Classification**: {thread_info['dlp_classification'].upper()}
- **Entropy Signature**: {thread_info['entropy_signature'][:16]}...
- **Created**: {time.ctime(thread_info['timestamp'])}
- **Status**: {'🔒 Sealed' if thread_info['sealed'] else '🔓 Unsealed'}
"""
        
        readme_content += f"""

## Memory Sealing Protocol
Active sealed memories: {len(manifest['memory_sealing_manifest'])}

## Export Information
- **Framework Version**: {manifest['version']}
- **Export Timestamp**: {time.ctime(manifest['export_timestamp'])}
- **System**: {manifest['system']}

## CLI Commands
Use the Aurora symbolic CLI to interact with the framework:

```bash
# Execute symbolic chain
python -m aurora.cli.symbolic_cli chain 001 999 --stream-data "example"

# Seal thread with DLP classification  
python -m aurora.cli.symbolic_cli seal-thread my_thread confidential --operator-key secret123

# Check entropy status
python -m aurora.cli.symbolic_cli entropy-status

# Export manifest
python -m aurora.cli.symbolic_cli export-manifest

# Generate diff report
python -m aurora.cli.symbolic_cli diff-manifest previous_manifest.json
```

Generated by Aurora Symbolic CLI at {time.ctime()}
"""
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
            
        print(f"README documentation generated: {readme_path}")
        return str(readme_path)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Aurora Symbolic CLI Framework")
    parser.add_argument("--entropy-threshold", type=float, default=0.8,
                      help="Entropy monitoring threshold")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chain execution command
    chain_parser = subparsers.add_parser("chain", help="Execute symbolic chain")
    chain_parser.add_argument("start", type=int, help="Chain start number")
    chain_parser.add_argument("end", type=int, help="Chain end number")
    chain_parser.add_argument("--stream-data", help="Optional stream data")
    
    # Thread sealing command
    seal_parser = subparsers.add_parser("seal-thread", help="Seal symbolic thread")
    seal_parser.add_argument("thread_id", help="Thread identifier")
    seal_parser.add_argument("dlp_level", choices=["public", "internal", "restricted", "confidential"],
                           help="DLP classification level")
    seal_parser.add_argument("--operator-key", required=True, help="Operator authentication key")
    
    # Thread rehydration command
    rehydrate_parser = subparsers.add_parser("rehydrate-thread", help="Rehydrate sealed thread")
    rehydrate_parser.add_argument("thread_id", help="Thread identifier")
    rehydrate_parser.add_argument("--operator-key", required=True, help="Operator authentication key")
    
    # Export manifest command
    export_parser = subparsers.add_parser("export-manifest", help="Export symbolic manifest")
    export_parser.add_argument("--filename", help="Output filename")
    
    # Entropy status command
    subparsers.add_parser("entropy-status", help="Show entropy monitoring status")
    
    # Diff manifest command
    diff_parser = subparsers.add_parser("diff-manifest", help="Generate manifest diff report")
    diff_parser.add_argument("manifest_file", help="Manifest file to compare against")
    
    # List threads command
    subparsers.add_parser("list-threads", help="List all symbolic threads")
    
    # Generate README command
    readme_parser = subparsers.add_parser("generate-readme", help="Generate README documentation")
    readme_parser.add_argument("--output-file", help="Output filename")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Initialize CLI with custom entropy threshold if provided
    cli = SymbolicCLI()
    cli.engine.entropy_state.threshold = args.entropy_threshold
    
    try:
        if args.command == "chain":
            cli.execute_chain_command(args.start, args.end, args.stream_data)
        elif args.command == "seal-thread":
            cli.seal_thread_command(args.thread_id, args.dlp_level, args.operator_key)
        elif args.command == "rehydrate-thread":
            cli.rehydrate_thread_command(args.thread_id, args.operator_key)
        elif args.command == "export-manifest":
            cli.export_manifest_command(args.filename)
        elif args.command == "entropy-status":
            cli.entropy_status_command()
        elif args.command == "diff-manifest":
            cli.diff_manifest_command(args.manifest_file)
        elif args.command == "list-threads":
            cli.list_threads_command()
        elif args.command == "generate-readme":
            cli.generate_readme_command(args.output_file)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())