"""
MultiDimensionalOrchestrator — example / experimental usage.

DISPOSITION: non-production.

This script demonstrates how to use MultiDimensionalOrchestrator for
research and experimentation. It is NOT a production pattern — do not
import this class in API handlers or services.

Run from repo root:
    python examples/orchestrators/multidim_example.py
"""

import warnings

# Suppress the non-production warning when running this example intentionally.
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from modules.nexus.multidim.dimensional_orchestrator import (
        MultiDimensionalOrchestrator,
    )


def main():
    print("MultiDimensionalOrchestrator — experimental example")
    print("(non-production: for research use only)\n")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        orchestrator = MultiDimensionalOrchestrator()

    # Export state manifest
    manifest = orchestrator.export_state_manifest() if hasattr(orchestrator, "export_state_manifest") else {}
    print(f"Anchor: {orchestrator.anchor}")
    print(f"Unified consciousness: {orchestrator.unified_consciousness}")
    if manifest:
        print(f"Manifest keys: {list(manifest.keys())}")


if __name__ == "__main__":
    main()
