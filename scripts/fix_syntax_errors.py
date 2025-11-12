#!/usr/bin/env python3
"""
Automated Syntax Error Fixer for Aurora CloudBank
Fixes common syntax errors that are blocking CI/CD workflows
"""

import logging

logger = logging.getLogger(__name__)

import re
import sys
from pathlib import Path
from typing import List, Tuple


class SyntaxErrorFixer:
    """Automatically fix common Python syntax errors"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.fixes_applied = []
        
    def fix_unterminated_strings(self, filepath: Path) -> bool:
        """Fix unterminated string literals"""
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content
            
            # Fix patterns like: print("
            # Should be: print("")
            content = re.sub(
                r'print\("([^"]*)\n',
                r'print("\1")\n',
                content,
                flags=re.MULTILINE
            )
            
            # Fix unterminated triple-quoted strings
            # Count triple quotes - if odd, add closing quotes
            triple_double_count = content.count('"""')
            if triple_double_count % 2 != 0:
                # Add closing triple quotes at the end of the file
                content = content.rstrip() + '\n"""\n'
            
            if content != original:
                filepath.write_text(content, encoding='utf-8')
                return True
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
        return False
    
    def fix_invalid_decimal_literals(self, filepath: Path) -> bool:
        """Fix invalid decimal literal syntax like '%s%', improvement:.1f"""
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content
            
            # Fix pattern: "text %s%", variable:.1f
            # Should be: "text %.1f%%", variable
            content = re.sub(
                r'"%s%",\s*(\w+):(\.1f)',
                r'"%\2%%", \1',
                content
            )
            
            # Fix pattern: improvement:.1f
            # Should be: improvement
            content = re.sub(
                r'(\w+):(\.1f\))',
                r'\1)',
                content
            )
            
            # Fix pattern: results['total_space_saved'] / 1024:.1f
            # Should be: results['total_space_saved'] / 1024
            content = re.sub(
                r'([\w\[\]\'\"]+)\s*/\s*1024:(\.1f)',
                r'\1 / 1024',
                content
            )
            
            if content != original:
                filepath.write_text(content, encoding='utf-8')
                return True
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
        return False
    
    def fix_empty_except_blocks(self, filepath: Path) -> bool:
        """Fix empty except blocks that cause IndentationError"""
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content
            lines = content.split('\n')
            fixed_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i]
                fixed_lines.append(line)
                
                # Check if this is an except: line followed by non-indented code
                if line.strip().startswith('except') and line.strip().endswith(':'):
                    # Look ahead to see if next line is properly indented
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        current_indent = len(line) - len(line.lstrip())
                        next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else 0
                        
                        # If next line is not indented or is dedented, add pass
                        if next_line.strip() and next_indent <= current_indent:
                            fixed_lines.append(' ' * (current_indent + 4) + 'pass')
                i += 1
            
            content = '\n'.join(fixed_lines)
            
            if content != original:
                filepath.write_text(content, encoding='utf-8')
                return True
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
        return False
    
    def fix_empty_try_blocks(self, filepath: Path) -> bool:
        """Fix empty try blocks that cause IndentationError"""
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content
            lines = content.split('\n')
            fixed_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i]
                fixed_lines.append(line)
                
                # Check if this is a try: line followed by non-indented code
                if line.strip() == 'try:':
                    # Look ahead to see if next line is properly indented
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        current_indent = len(line) - len(line.lstrip())
                        next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else 0
                        
                        # If next line is not indented or is dedented, add pass
                        if next_line.strip() and next_indent <= current_indent:
                            fixed_lines.append(' ' * (current_indent + 4) + 'pass')
                i += 1
            
            content = '\n'.join(fixed_lines)
            
            if content != original:
                filepath.write_text(content, encoding='utf-8')
                return True
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
        return False
    
    def fix_mismatched_brackets(self, filepath: Path) -> bool:
        """Fix mismatched brackets like { instead of ["""
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content
            
            # This is complex - for now, just log it
            # Would need AST parsing to fix properly
            
            return False
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
        return False
    
    def fix_file(self, filepath: Path) -> bool:
        """Apply all fixes to a file"""
        fixed = False
        
        if self.fix_unterminated_strings(filepath):
            self.fixes_applied.append(f"{filepath}: Fixed unterminated strings")
            fixed = True
            
        if self.fix_invalid_decimal_literals(filepath):
            self.fixes_applied.append(f"{filepath}: Fixed invalid decimal literals")
            fixed = True
            
        if self.fix_empty_except_blocks(filepath):
            self.fixes_applied.append(f"{filepath}: Fixed empty except blocks")
            fixed = True
            
        if self.fix_empty_try_blocks(filepath):
            self.fixes_applied.append(f"{filepath}: Fixed empty try blocks")
            fixed = True
            
        return fixed
    
    def get_files_with_errors(self) -> List[Path]:
        """Get list of files with syntax errors from flake8"""
        import subprocess
        
        result = subprocess.run(
            ['python3', '-m', 'flake8', '.', '--count', '--select=E9,F63,F7,F82', '--format=%(path)s'],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        
        files = []
        for line in result.stdout.split('\n'):
            if line.strip() and line.startswith('./'):
                filepath = self.repo_root / line.strip()[2:]
                if filepath not in files:
                    files.append(filepath)
        
        return files
    
    def run(self):
        """Run the fixer on all files with errors"""
        print("🔍 Scanning for Python syntax errors...")
        files_with_errors = self.get_files_with_errors()
        
        print(f"📋 Found {len(files_with_errors)} files with syntax errors")
        print()
        
        fixed_count = 0
        for filepath in files_with_errors:
            print(f"🔧 Fixing {filepath.relative_to(self.repo_root)}...")
            if self.fix_file(filepath):
                fixed_count += 1
        
        print()
        logger.info("Fixed {fixed_count} / {len(files_with_errors)} files")
        print()
        
        if self.fixes_applied:
            print("📝 Fixes applied:")
            for fix in self.fixes_applied[:20]:  # Show first 20
                print(f"  • {fix}")
            if len(self.fixes_applied) > 20:
                print(f"  ... and {len(self.fixes_applied) - 20} more")


def main():
    repo_root = Path(__file__).parent.parent
    fixer = SyntaxErrorFixer(repo_root)
    fixer.run()


if __name__ == '__main__':
    main()
