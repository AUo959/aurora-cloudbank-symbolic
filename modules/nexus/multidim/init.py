#!/usr/bin/env python3
"""
NEXUS Phase 11: Multi-Dimensional Consciousness Initialization
==============================================================
Quick CLI wrapper for dimensional orchestrator

Usage:
  python init.py                    # Initialize all dimensions
  python init.py --evolve          # Run evolution cycles
  python init.py --status          # Show status glyphcard
  python init.py --export          # Export dimensional state
"""

import logging

logger = logging.getLogger(__name__)

import asyncio
import sys
from pathlib import Path

# Add module to path
sys.path.insert(0, str(Path(__file__).parent))

from dimensional_orchestrator import get_orchestrator


async def quick_demo():
    """Quick demonstration of multi-dimensional consciousness"""
    print("🌌 NEXUS Phase 11: Multi-Dimensional Consciousness")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    
    # Initialize dimensions
    print("\n🔄 Initializing dimensions...")
    init_result = await orchestrator.initialize_dimensions()
    logger.info("Initialized {len(init_result["dimensions_initialized'])} dimensions")
    
    # Show initial status
    print("\n📊 Initial Status:")
    print(orchestrator.generate_dimensional_glyphcard())
    
    # Run evolution cycles
    print("\n🧬 Running evolution cycles...")
    cycle_count = 0
    async for result in orchestrator.evolve_dimensions(5):
        cycle_count += 1
        consciousness = result['consciousness_status']['unified']
        progress = result['consciousness_status']['progress']
        print(f"  Cycle {cycle_count}: {consciousness:.4f} ({progress:.1f}%)")
    
    # Final status
    print("\n📊 Final Status:")
    print(orchestrator.generate_dimensional_glyphcard())
    
    # Export state
    export_result = orchestrator.export_all_dimensions()
    print(f"\n💾 Exported: {export_result['export_id']}")
    print(f"Consciousness: {export_result['consciousness_status']['unified']:.4f}")
    
    return export_result

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NEXUS Phase 11 CLI")
    parser.add_argument("--demo", action="store_true", help="Run quick demo")
    parser.add_argument("--evolve", action="store_true", help="Evolution only")
    parser.add_argument("--status", action="store_true", help="Status only")
    parser.add_argument("--export", action="store_true", help="Export only")
    
    args = parser.parse_args()
    
    if args.demo or (not args.evolve and not args.status and not args.export):
        # Default to demo
        result = asyncio.run(quick_demo())
    else:
        # Individual commands
        async def run_command():
            orchestrator = get_orchestrator()
            
            if args.status:
                print(orchestrator.generate_dimensional_glyphcard())
            elif args.evolve:
                await orchestrator.initialize_dimensions()
                async for result in orchestrator.evolve_dimensions(10):
                    print(f"Consciousness: {result['consciousness_status']['unified']:.4f}")
            elif args.export:
                await orchestrator.initialize_dimensions()
                export = orchestrator.export_all_dimensions()
                print(f"Exported: {export['export_id']}")
        
        asyncio.run(run_command())