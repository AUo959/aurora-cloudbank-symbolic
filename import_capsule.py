#!/usr/bin/env python3
"""
Capsule Import Script

Import and validate Aurora capsule for cross-repository collaboration.

Usage:
    python import_capsule.py --capsule capsule.json --validate-anchors
    python import_capsule.py --capsule capsule.json --accept-agents R-2,Copilot
    
Thread: T1→COLLAB→IMPORT
DLP: context_tag=collab_capsule_import
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.collab.capsule_schema import (
    MultiRepoCapsule,
    validate_capsule_compatibility
)
from src.core.native_dlp_export import NativeDLPTracker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def import_capsule(
    capsule_file: str,
    validate_anchors: bool = True,
    validate_ethics: bool = True,
    accept_agents: Optional[List[str]] = None,
    trust_level: str = "pending"
) -> dict:
    """
    Import and validate capsule from external repository.
    
    Args:
        capsule_file: Path to capsule JSON file
        validate_anchors: Whether to validate anchor integrity
        validate_ethics: Whether to validate ethics compliance
        accept_agents: List of agents to accept (None = accept all)
        trust_level: Trust level to assign (pending, trusted, verified)
        
    Returns:
        Import result dictionary
    """
    logger.info("🚀 Starting capsule import from %s", capsule_file)
    
    # Load capsule file
    capsule_path = Path(capsule_file)
    if not capsule_path.exists():
        logger.error("❌ Capsule file not found: %s", capsule_file)
        return {"success": False, "error": "Capsule file not found"}
    
    try:
        with open(capsule_path, 'r') as f:
            capsule_payload = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("❌ Invalid JSON in capsule file: %s", e)
        return {"success": False, "error": f"Invalid JSON: {e}"}
    
    # Extract capsule data
    if "capsule" not in capsule_payload:
        logger.error("❌ Missing 'capsule' field in payload")
        return {"success": False, "error": "Missing capsule data"}
    
    capsule_data = capsule_payload["capsule"]
    
    # Parse capsule
    try:
        capsule = MultiRepoCapsule.from_dict(capsule_data)
        logger.info("✅ Capsule parsed: %s", capsule.capsule_id)
    except Exception as e:
        logger.error("❌ Failed to parse capsule: %s", e)
        return {"success": False, "error": f"Capsule parsing failed: {e}"}
    
    # Validation results
    validation_results = {
        "anchor_integrity": None,
        "ethics_compliance": None,
        "agent_verification": None,
        "drift_check": None,
        "signature_check": None
    }
    
    # Validate anchor integrity
    if validate_anchors:
        logger.info("🔍 Validating anchor integrity...")
        anchor_valid = capsule.verify_anchor_integrity()
        validation_results["anchor_integrity"] = anchor_valid
        
        if not anchor_valid:
            logger.error("❌ Anchor integrity validation failed")
            return {
                "success": False,
                "error": "Anchor integrity validation failed",
                "validation_results": validation_results
            }
        logger.info("✅ Anchor integrity verified")
    
    # Validate ethics compliance
    if validate_ethics:
        logger.info("🔍 Validating ethics compliance...")
        ethics_valid = capsule.verify_ethics_compliance()
        validation_results["ethics_compliance"] = ethics_valid
        
        if not ethics_valid:
            logger.warning("⚠️  Ethics compliance check failed (some repos pending)")
            # Don't fail import, but log warning
        else:
            logger.info("✅ Ethics compliance verified")
    
    # Verify agent roster
    if accept_agents:
        logger.info("🔍 Verifying agent roster...")
        unknown_agents = [a for a in capsule.agent_roster if a not in accept_agents]
        
        if unknown_agents:
            logger.warning("⚠️  Unknown agents in roster: %s", ", ".join(unknown_agents))
            validation_results["agent_verification"] = False
        else:
            logger.info("✅ All agents verified: %s", ", ".join(capsule.agent_roster))
            validation_results["agent_verification"] = True
    
    # Check symbolic drift
    logger.info("🔍 Checking symbolic drift...")
    if capsule.symbolic_drift > 0.002:  # 0.2% threshold
        logger.error("❌ Symbolic drift too high: %.4f (>0.002)", capsule.symbolic_drift)
        validation_results["drift_check"] = False
        return {
            "success": False,
            "error": f"Symbolic drift too high: {capsule.symbolic_drift}",
            "validation_results": validation_results
        }
    else:
        logger.info("✅ Drift acceptable: %.4f", capsule.symbolic_drift)
        validation_results["drift_check"] = True
    
    # Verify capsule signature
    logger.info("🔍 Verifying capsule signature...")
    expected_signature = capsule.compute_signature()
    provided_signature = capsule_data.get("signature", "")
    
    if expected_signature == provided_signature:
        logger.info("✅ Signature verified")
        validation_results["signature_check"] = True
    else:
        logger.warning("⚠️  Signature mismatch (capsule may have been modified)")
        validation_results["signature_check"] = False
    
    # Initialize DLP tracker for import
    dlp_tracker = NativeDLPTracker()
    
    # Tag import with DLP
    tag_id = dlp_tracker.create_tag("capsule_import", capsule_data)
    tag = dlp_tracker.tags[tag_id]
    tag.add_anchor_protocol("CROSS_REPO_BRIDGE")
    tag.add_anchor_protocol("EOS_SEED_ORION")
    tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
    tag.metadata.update({
        "import_timestamp": datetime.now().isoformat(),
        "capsule_id": capsule.capsule_id,
        "agent_roster": capsule.agent_roster,
        "validation_results": validation_results
    })
    
    # Update linked repos trust level
    for repo in capsule.linked_repos:
        repo.trust_level = trust_level
        repo.last_sync = datetime.now().isoformat()
    
    # Generate activation report
    activation_report = {
        "success": True,
        "capsule_id": capsule.capsule_id,
        "capsule_version": capsule.capsule_version,
        "anchor_seed": capsule.anchor_seed,
        "ethics_protocol": capsule.ethics_protocol,
        "symbolic_drift": capsule.symbolic_drift,
        "agent_roster": capsule.agent_roster,
        "linked_repos": len(capsule.linked_repos),
        "shared_anchors": len(capsule.shared_anchors),
        "validation_results": validation_results,
        "import_timestamp": datetime.now().isoformat(),
        "dlp_tag_id": tag_id,
        "trust_level": trust_level
    }
    
    logger.info("✅ Import completed successfully")
    logger.info("   Capsule ID: %s", capsule.capsule_id)
    logger.info("   Version: %s", capsule.capsule_version)
    logger.info("   Agents: %s", ", ".join(capsule.agent_roster))
    logger.info("   Linked Repos: %d", len(capsule.linked_repos))
    logger.info("   Shared Anchors: %d", len(capsule.shared_anchors))
    logger.info("   Trust Level: %s", trust_level)
    
    # Print drift statistics
    logger.info("\n📊 Drift Statistics:")
    logger.info("   Symbolic Drift: %.4f%%", capsule.symbolic_drift * 100)
    logger.info("   Status: %s", "🟢 GREEN" if capsule.symbolic_drift < 0.001 else "🟡 YELLOW")
    
    return activation_report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import and validate Aurora capsule from external repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import and validate capsule
  python import_capsule.py --capsule capsule.json --validate-anchors
  
  # Import with specific accepted agents
  python import_capsule.py --capsule capsule.json --accept-agents R-2,Copilot
  
  # Import and mark as trusted
  python import_capsule.py --capsule capsule.json --trust-level trusted
  
  # Skip validation (not recommended)
  python import_capsule.py --capsule capsule.json --no-validate
        """
    )
    
    parser.add_argument(
        '--capsule',
        required=True,
        help='Path to capsule JSON file'
    )
    
    parser.add_argument(
        '--validate-anchors',
        action='store_true',
        default=True,
        help='Validate anchor integrity (default: True)'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip all validation (not recommended)'
    )
    
    parser.add_argument(
        '--accept-agents',
        help='Comma-separated list of accepted agent names'
    )
    
    parser.add_argument(
        '--trust-level',
        choices=['pending', 'trusted', 'verified'],
        default='pending',
        help='Trust level to assign to imported capsule (default: pending)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse accepted agents
    accept_agents = None
    if args.accept_agents:
        accept_agents = [agent.strip() for agent in args.accept_agents.split(',')]
    
    # Import capsule
    result = import_capsule(
        capsule_file=args.capsule,
        validate_anchors=args.validate_anchors and not args.no_validate,
        validate_ethics=not args.no_validate,
        accept_agents=accept_agents,
        trust_level=args.trust_level
    )
    
    if not result["success"]:
        logger.error("❌ Import failed: %s", result.get("error", "Unknown error"))
        if "validation_results" in result:
            logger.error("   Validation Results: %s", json.dumps(result["validation_results"], indent=2))
        sys.exit(1)
    
    # Print activation report
    print("\n" + "="*60)
    print("CAPSULE ACTIVATION REPORT")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
