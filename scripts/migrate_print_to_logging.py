#!/usr/bin/env python3
"""
Automated Print-to-Logging Migration Script
Part of: Issue #320 Phase 1 Code Quality Sprint

Systematically replaces print statements with proper logging calls.
Patterns handled:
- logger.info("Success") → logger.info("Success")
- logger.error("Error") → logger.error("Error")
- logger.warning("Warning") → logger.warning("Warning")
- print(f"Debug: {var}") → logger.debug(f"Debug: {var}")

Usage:
    python scripts/migrate_print_to_logging.py --dry-run  # Preview changes
    python scripts/migrate_print_to_logging.py            # Apply changes
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
import argparse


class PrintToLoggingMigrator:
    """Migrate print statements to proper logging"""
    
    # Files to exclude from migration
    EXCLUDE_PATTERNS = [
        "*/test_*",
        "*/tests/*",
        "*/__pycache__/*",
        "*/venv/*",
        "*/node_modules/*",
        "*.pyc",
        "*migration*.py",  # Don't modify migration scripts themselves
    ]
    
    # Print patterns to detect and their logging equivalents
    PATTERNS = [
        # Success patterns (✅, SUCCESS, OK)
        (
            r'print\s*\(\s*[f]?["\']✅\s*(.+?)["\']',
            r'logger.info("\1"'
        ),
        (
            r'print\s*\(\s*[f]?["\']SUCCESS:\s*(.+?)["\']',
            r'logger.info("Success: \1"'
        ),
        # Error patterns (❌, ERROR, FAILED)
        (
            r'print\s*\(\s*[f]?["\']❌\s*(.+?)["\']',
            r'logger.error("\1"'
        ),
        (
            r'print\s*\(\s*[f]?["\']ERROR:\s*(.+?)["\']',
            r'logger.error("\1"'
        ),
        (
            r'print\s*\(\s*[f]?["\']FAILED:\s*(.+?)["\']',
            r'logger.error("\1"'
        ),
        # Warning patterns (⚠️, WARNING)
        (
            r'print\s*\(\s*[f]?["\']⚠️\s*(.+?)["\']',
            r'logger.warning("\1"'
        ),
        (
            r'print\s*\(\s*[f]?["\']WARNING:\s*(.+?)["\']',
            r'logger.warning("\1"'
        ),
        # Debug patterns
        (
            r'print\s*\(\s*[f]?["\']DEBUG:\s*(.+?)["\']',
            r'logger.debug("\1"'
        ),
        # Generic info patterns
        (
            r'print\s*\(\s*[f]?["\']INFO:\s*(.+?)["\']',
            r'logger.info("\1"'
        ),
    ]
    
    def __init__(self, workspace_root: Path, dry_run: bool = False):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.changes: List[Tuple[Path, int, str, str]] = []
        self.files_modified = 0
        self.lines_modified = 0
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from migration"""
        for pattern in self.EXCLUDE_PATTERNS:
            if file_path.match(pattern):
                return True
        return False
    
    def needs_logging_import(self, content: str) -> bool:
        """Check if file needs logging import added"""
        return "import logging" not in content
    
    def add_logging_import(self, content: str) -> str:
        """Add logging import and logger initialization"""
        lines = content.split('\n')
        
        # Find appropriate position (after docstring, before first code)
        insert_pos = 0
        in_docstring = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip docstrings
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue
            
            if in_docstring:
                continue
            
            # Skip shebang and encoding
            if stripped.startswith('#'):
                insert_pos = i + 1
                continue
            
            # Found first import or code
            if stripped.startswith('import ') or stripped.startswith('from '):
                insert_pos = i
                break
            
            if stripped and not stripped.startswith('#'):
                insert_pos = i
                break
        
        # Insert logging import
        logging_lines = [
            "import logging",
            "",
            "logger = logging.getLogger(__name__)",
            ""
        ]
        
        lines = lines[:insert_pos] + logging_lines + lines[insert_pos:]
        return '\n'.join(lines)
    
    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single file from print to logging"""
        try:
            content = file_path.read_text(encoding='utf-8')
            file_modified = False
            
            # Apply each pattern replacement
            for pattern, replacement in self.PATTERNS:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    # Count changes
                    old_lines = content.split('\n')
                    new_lines = new_content.split('\n')
                    for line_num, (old, new) in enumerate(zip(old_lines, new_lines), 1):
                        if old != new:
                            self.changes.append((file_path, line_num, old.strip(), new.strip()))
                            self.lines_modified += 1
                    
                    content = new_content
                    file_modified = True
            
            # If file was modified and needs logging import
            if file_modified:
                if self.needs_logging_import(content):
                    content = self.add_logging_import(content)
                
                if not self.dry_run:
                    file_path.write_text(content, encoding='utf-8')
                
                self.files_modified += 1
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def migrate_workspace(self) -> None:
        """Migrate all Python files in workspace"""
        print(f"🔍 Scanning workspace: {self.workspace_root}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print()
        
        # Find all Python files
        python_files = list(self.workspace_root.rglob("*.py"))
        python_files = [f for f in python_files if not self.should_exclude(f)]
        
        print(f"Found {len(python_files)} Python files to process")
        print()
        
        # Process each file
        for file_path in python_files:
            if self.migrate_file(file_path):
                rel_path = file_path.relative_to(self.workspace_root)
                logger.info("Modified: {rel_path}")
        
        # Print summary
        print()
        print("=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Files scanned:     {len(python_files)}")
        print(f"Files modified:    {self.files_modified}")
        print(f"Lines changed:     {self.lines_modified}")
        print(f"Mode:              {'DRY RUN' if self.dry_run else 'LIVE'}")
        print()
        
        if self.changes and self.dry_run:
            print("Sample changes (first 10):")
            print()
            for file_path, line_num, old, new in self.changes[:10]:
                rel_path = file_path.relative_to(self.workspace_root)
                print(f"📄 {rel_path}:{line_num}")
                print(f"  - {old}")
                print(f"  + {new}")
                print()
        
        if self.dry_run:
            print("ℹ️  This was a dry run. Run without --dry-run to apply changes.")
        else:
            logger.info("Migration complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate print statements to proper logging"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Workspace root directory"
    )
    
    args = parser.parse_args()
    
    migrator = PrintToLoggingMigrator(
        workspace_root=args.workspace,
        dry_run=args.dry_run
    )
    
    try:
        migrator.migrate_workspace()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
