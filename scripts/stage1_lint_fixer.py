#!/usr/bin/env python3
"""
Stage 1 Lint Fixer: Whitespace and Formatting

Automated fixes for Stage 1 lint issues:
- W293: blank line contains whitespace
- E303: too many blank lines
- E302: expected 2 blank lines

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class Stage1LintFixer:
    """Automated fixer for Stage 1 lint issues."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_processed = 0
    
    def fix_whitespace_issues(self, content: str) -> Tuple[str, List[str]]:
        """Fix whitespace-related issues."""
        fixes = []
        lines = content.split('\n')
        
        # Fix W293: blank line contains whitespace
        for i, line in enumerate(lines):
            if line.strip() == '' and line != '':
                lines[i] = ''
                fixes.append(f"Line {i+1}: Removed whitespace from blank line (W293)")
        
        return '\n'.join(lines), fixes
    
    def fix_blank_line_issues(self, content: str) -> Tuple[str, List[str]]:
        """Fix blank line issues (E302, E303)."""
        fixes = []
        lines = content.split('\n')
        
        # Track consecutive blank lines
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for too many blank lines (E303)
            if line.strip() == '':
                blank_count = 0
                start_blank = i
                
                # Count consecutive blank lines
                while i < len(lines) and lines[i].strip() == '':
                    blank_count += 1
                    i += 1
                
                # If we have more than 2 consecutive blank lines, reduce to 2
                if blank_count > 2:
                    # Keep only 2 blank lines
                    lines[start_blank:start_blank + blank_count] = ['', '']
                    fixes.append(f"Lines {start_blank+1}-{start_blank+blank_count}: Reduced {blank_count} blank lines to 2 (E303)")
                    # Adjust index since we removed lines
                    i = start_blank + 2
            else:
                i += 1
        
        # Fix E302: expected 2 blank lines before class/function definitions
        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a class or top-level function definition
            if (line.startswith('class ') or 
                (line.startswith('def ') and 
                 (i == 0 or not lines[i-1].startswith(' ')))):  # Top-level function
                
                # Count preceding blank lines
                blank_count = 0
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    blank_count += 1
                    j -= 1
                
                # Skip if this is the first line or follows an import/comment
                if i > 0 and j >= 0:
                    prev_non_blank = lines[j].strip()
                    if (not prev_non_blank.startswith('import ') and 
                        not prev_non_blank.startswith('from ') and
                        not prev_non_blank.startswith('#') and
                        not prev_non_blank.startswith('"""') and
                        not prev_non_blank.startswith("'''") and
                        blank_count < 2):
                        
                        # Add blank lines to make it 2
                        needed_blanks = 2 - blank_count
                        result_lines.extend([''] * needed_blanks)
                        fixes.append(f"Line {i+1}: Added {needed_blanks} blank lines before definition (E302)")
            
            result_lines.append(line)
            i += 1
        
        return '\n'.join(result_lines), fixes
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix a single Python file."""
        try:
            if not file_path.suffix == '.py':
                return False
            
            print(f"📝 Processing {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            all_fixes = []
            
            # Apply whitespace fixes
            content, whitespace_fixes = self.fix_whitespace_issues(content)
            all_fixes.extend(whitespace_fixes)
            
            # Apply blank line fixes
            content, blank_line_fixes = self.fix_blank_line_issues(content)
            all_fixes.extend(blank_line_fixes)
            
            # Check if changes were made
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.fixes_applied += len(all_fixes)
                print(f"  ✅ Applied {len(all_fixes)} fixes")
                
                for fix in all_fixes:
                    print(f"    - {fix}")
                
                return True
            else:
                print(f"  ℹ️  No Stage 1 issues found")
                return False
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return False
        finally:
            self.files_processed += 1
    
    def fix_directory(self, directory: Path) -> None:
        """Fix all Python files in a directory."""
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return
        
        python_files = list(directory.rglob('*.py'))
        
        if not python_files:
            print(f"ℹ️  No Python files found in {directory}")
            return
        
        print(f"🔧 Found {len(python_files)} Python files in {directory}")
        
        fixed_files = 0
        for file_path in python_files:
            if self.fix_file(file_path):
                fixed_files += 1
        
        print(f"\n📊 Summary for {directory}:")
        print(f"  - Files processed: {len(python_files)}")
        print(f"  - Files with fixes: {fixed_files}")
        print(f"  - Total fixes applied: {self.fixes_applied}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Stage 1 Lint Fixer: Whitespace and Formatting")
    parser.add_argument("target", help="Target file or directory to fix")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    
    args = parser.parse_args()
    
    target_path = Path(args.target)
    
    if not target_path.exists():
        print(f"❌ Target not found: {target_path}")
        sys.exit(1)
    
    fixer = Stage1LintFixer(dry_run=args.dry_run)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    if target_path.is_file():
        fixer.fix_file(target_path)
    else:
        fixer.fix_directory(target_path)
    
    print(f"\n🎉 Stage 1 fixing complete!")
    print(f"Files processed: {fixer.files_processed}")
    print(f"Fixes applied: {fixer.fixes_applied}")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply the fixes.")


if __name__ == "__main__":
    main()