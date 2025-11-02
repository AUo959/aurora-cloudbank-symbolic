#!/usr/bin/env python3
"""
Capsule Export Script

Export Aurora capsule context for cross-repository collaboration.

Usage:
    python export_capsule.py --repo-url https://github.com/example/repo --agents R-2,Copilot
    python export_capsule.py --repo-url https://github.com/example/repo --agents R-2 --output capsule.json
    
Thread: T1→COLLAB→EXPORT
DLP: context_tag=collab_capsule_export
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
    LinkedRepository,
    create_shared_anchor,
    CapsuleVersion
)
from src.core.native_dlp_export import NativeDLPTracker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def parse_repo_url(repo_url: str) -> tuple:
    """Parse GitHub repository URL into owner and repo name."""
    # Handle both HTTPS and SSH URLs
    if repo_url.startswith('https://github.com/'):
        parts = repo_url.replace('https://github.com/', '').rstrip('/').split('/')
    elif repo_url.startswith('git@github.com:'):
        parts = repo_url.replace('git@github.com:', '').rstrip('.git').split('/')
    else:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    if len(parts) < 2:
        raise ValueError(f"Could not parse owner/repo from URL: {repo_url}")
    
    return parts[0], parts[1]


def export_capsule(
    repo_url: str,
    agents: List[str],
    output_file: Optional[str] = None,
    validate_anchors: bool = True
) -> dict:
    """
    Export capsule for cross-repository collaboration.
    
    Args:
        repo_url: Target repository URL
        agents: List of agent names for the collaboration
        output_file: Optional output file path
        validate_anchors: Whether to validate anchor integrity
        
    Returns:
        Export result dictionary
    """
    logger.info("🚀 Starting capsule export for %s", repo_url)
    
    # Parse repository URL
    try:
        owner, repo_name = parse_repo_url(repo_url)
        logger.info("   Target: %s/%s", owner, repo_name)
    except ValueError as e:
        logger.error("❌ %s", e)
        return {"success": False, "error": str(e)}
    
    # Initialize DLP tracker
    dlp_tracker = NativeDLPTracker()
    
    # Create multi-repo capsule
    capsule_id = f"COLLAB_{owner}_{repo_name}_{int(datetime.now().timestamp())}"
    capsule = MultiRepoCapsule(
        capsule_id=capsule_id,
        capsule_version=CapsuleVersion.CURRENT.value,
        title=f"Cross-Repo Collaboration with {owner}/{repo_name}",
        anchor_seed="EOS_SEED_ORION",
        ethics_protocol="Picard_Delta_3",
        agent_roster=agents
    )
    
    # Add linked repository
    linked_repo = LinkedRepository(
        repo_url=repo_url,
        owner=owner,
        repo_name=repo_name,
        narrative_timestamp=datetime.now().isoformat(),
        accepted_agents=agents,
        trust_level="pending",
        metadata={
            "export_timestamp": datetime.now().isoformat(),
            "export_source": "aurora-cloudbank-symbolic"
        }
    )
    capsule.add_linked_repo(linked_repo)
    
    # Create shared anchor
    shared_anchor = create_shared_anchor(
        anchor_name="CROSS_REPO_ANCHOR",
        anchor_seed="EOS_SEED_ORION",
        metadata={
            "created_by": "export_capsule.py",
            "target_repo": f"{owner}/{repo_name}"
        }
    )
    capsule.add_shared_anchor(shared_anchor)
    
    # Add glyph chain for continuity
    capsule.glyph_chain = [
        {"name": "Glyphon", "role": "drift aligned"},
        {"name": "Axiomera", "role": "ethics sealed"},
        {"name": "Sentari", "role": "resonance stabilized"},
        {"name": "Caelion", "role": "nexus locked"},
        {"name": "Velatrix", "role": "continuity pulse"},
        {"name": "Harmion", "role": "symbolic compression"}
    ]
    
    # Validate anchor integrity
    if validate_anchors:
        if not capsule.verify_anchor_integrity():
            logger.error("❌ Anchor integrity validation failed")
            return {"success": False, "error": "Anchor integrity validation failed"}
        logger.info("✅ Anchor integrity verified")
    
    # Tag with DLP
    capsule_data = capsule.to_dict()
    tag_id = dlp_tracker.create_tag("capsule_export", capsule_data)
    tag = dlp_tracker.tags[tag_id]
    tag.add_anchor_protocol("CROSS_REPO_BRIDGE")
    tag.add_anchor_protocol("EOS_SEED_ORION")
    tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
    tag.metadata.update({
        "target_repo": f"{owner}/{repo_name}",
        "agent_roster": agents,
        "ethics_protocol": "Picard_Delta_3"
    })
    
    # Create DLP manifest
    manifest = dlp_tracker.create_export_manifest(
        manifest_name=f"capsule_export_{capsule_id}",
        tag_ids=[tag_id]
    )
    
    # Prepare export payload
    export_payload = {
        "export_metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "1.0.0",
            "dlp_tag_id": tag_id,
            "manifest_id": manifest["manifest_id"]
        },
        "capsule": capsule_data,
        "dlp_manifest": manifest
    }
    
    # Write to file if specified
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_payload, f, indent=2)
        logger.info("✅ Capsule exported to: %s", output_path)
    else:
        # Print to stdout
        print(json.dumps(export_payload, indent=2))
    
    logger.info("✅ Export completed successfully")
    logger.info("   Capsule ID: %s", capsule_id)
    logger.info("   Agents: %s", ", ".join(agents))
    logger.info("   Shared Anchors: %d", len(capsule.shared_anchors))
    
    return {
        "success": True,
        "capsule_id": capsule_id,
        "output_file": output_file,
        "dlp_tag_id": tag_id,
        "manifest_id": manifest["manifest_id"]
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export Aurora capsule for cross-repository collaboration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export for external repo with R-2 and Copilot agents
  python export_capsule.py --repo-url https://github.com/example/repo --agents R-2,Copilot
  
  # Export to specific file
  python export_capsule.py --repo-url https://github.com/example/repo --agents R-2 --output /tmp/capsule.json
  
  # Skip anchor validation (not recommended)
  python export_capsule.py --repo-url https://github.com/example/repo --agents R-2 --no-validate-anchors
        """
    )
    
    parser.add_argument(
        '--repo-url',
        required=True,
        help='Target repository URL (e.g., https://github.com/owner/repo)'
    )
    
    parser.add_argument(
        '--agents',
        required=True,
        help='Comma-separated list of agent names (e.g., R-2,Copilot,Aurora)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--no-validate-anchors',
        action='store_true',
        help='Skip anchor integrity validation'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse agents
    agents = [agent.strip() for agent in args.agents.split(',')]
    
    # Export capsule
    result = export_capsule(
        repo_url=args.repo_url,
        agents=agents,
        output_file=args.output,
        validate_anchors=not args.no_validate_anchors
    )
    
    if not result["success"]:
        logger.error("❌ Export failed: %s", result.get("error", "Unknown error"))
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
