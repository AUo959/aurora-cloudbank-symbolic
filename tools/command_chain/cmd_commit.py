#!/usr/bin/env python3
"""
#COMMIT//. - Stage and Commit Only

Stage changes and commit without syncing to remote.
Phases 1-3 from #321//. - check, stage, commit.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.command_chain.comprehensive_sync_321 import (  # noqa: E402
    ComprehensiveSync,
    SyncConfig,
    SyncResult
)


def execute_commit(config_path: Optional[str] = None, workspace_path: Optional[str] = None) -> SyncResult:
    """
    Execute stage and commit (Phases 1-3 only).
    
    Args:
        config_path: Path to configuration file (optional)
        workspace_path: Path to workspace directory (optional)
    
    Returns:
        SyncResult with phases 1-3 executed
    """
    # Load configuration
    if config_path and Path(config_path).exists():
        config = SyncConfig.load(Path(config_path))
    elif Path(".aurora/sync_config.json").exists():
        config = SyncConfig.load(Path(".aurora/sync_config.json"))
    else:
        config = SyncConfig()
    
    # Set workspace
    if workspace_path:
        workspace = Path(workspace_path)
    else:
        workspace = Path.cwd()
    
    # Create sync instance
    sync = ComprehensiveSync(config, workspace)
    
    print("\n💾 #COMMIT//. - Stage and Commit\n")
    print("=" * 60)
    
    phases = []
    
    # Phase 1: Check for changes
    print("Phase 1: Checking for pending changes...")
    phase1 = sync._phase1_check_changes()
    phases.append(phase1)
    
    if not phase1.success:
        print(f"❌ {phase1.message}")
        return SyncResult(
            success=False,
            phases=phases,
            commit_sha=None,
            files_changed=0,
            total_duration=phase1.duration_seconds
        )
    
    if phase1.details.get('files_changed', 0) == 0:
        print("✅ No changes to commit")
        return SyncResult(
            success=True,
            phases=phases,
            commit_sha=None,
            files_changed=0,
            total_duration=phase1.duration_seconds
        )
    
    print(f"✅ {phase1.message}")
    
    # Phase 2: Stage changes
    print("Phase 2: Staging changes intelligently...")
    phase2 = sync._phase2_intelligent_staging(phase1.details['categories'])
    phases.append(phase2)
    
    if not phase2.success:
        print(f"❌ {phase2.message}")
        return SyncResult(
            success=False,
            phases=phases,
            commit_sha=None,
            files_changed=phase1.details['files_changed'],
            total_duration=sum(p.duration_seconds for p in phases)
        )
    
    print(f"✅ {phase2.message}")
    
    # Phase 3: Commit
    print("Phase 3: Generating commit message and committing...")
    phase3 = sync._phase3_generate_commit(
        phase1.details['categories'],
        phase1.details.get('is_docs_only', False),
        phase1.details.get('is_config_only', False)
    )
    phases.append(phase3)
    
    if not phase3.success:
        print(f"❌ {phase3.message}")
        return SyncResult(
            success=False,
            phases=phases,
            commit_sha=None,
            files_changed=phase1.details['files_changed'],
            total_duration=sum(p.duration_seconds for p in phases)
        )
    
    print(f"✅ {phase3.message}")
    
    # Build result
    result = SyncResult(
        success=True,
        phases=phases,
        commit_sha=phase3.details.get('commit_sha'),
        files_changed=phase1.details['files_changed'],
        total_duration=sum(p.duration_seconds for p in phases)
    )
    
    print("\n" + "=" * 60)
    print("✅ #COMMIT//. COMPLETE")
    print(f"   Files: {result.files_changed}")
    print(f"   Commit: {result.commit_sha}")
    print(f"   Time: {result.total_duration:.1f}s")
    print("=" * 60)
    
    print("\nℹ️  Changes committed locally. Use #SYNC//. or git push to sync to remote.")
    
    return result


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage and commit changes - Phases 1-3 of #321//.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Commit with default config
  %(prog)s --config custom.json  # Use custom configuration
  %(prog)s --workspace /path/to/repo  # Commit in specific repository

This command stages and commits changes without syncing to remote.
Use #SYNC//. afterwards to push to remote.
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: .aurora/sync_config.json)'
    )
    
    parser.add_argument(
        '--workspace',
        type=str,
        help='Path to workspace directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    try:
        result = execute_commit(
            config_path=args.config,
            workspace_path=args.workspace
        )
        
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Commit interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
