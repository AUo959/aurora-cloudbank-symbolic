#!/usr/bin/env python3
"""
Critical Issue Resolver for Aurora CloudBank
Fixes syntax errors and critical issues in the codebase.
"""

import logging

logger = logging.getLogger(__name__)

import re
import sys
from pathlib import Path


def fix_critical_syntax_errors():
    """Fix critical syntax errors in Python files."""
    print("🔧 Fixing critical syntax errors...")
    
    fixes_applied = 0
    
    # Fix fix_code_quality.py
    file_path = Path("fix_code_quality.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix unterminated string literal
            content = content.replace(
                "content = re.sub(r'from typing import Any,",
                "content = re.sub(r'from typing import Any'"
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed {file_path}")
            fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    # Fix gitwiz_precommit_audit.py
    file_path = Path("gitwiz_precommit_audit.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix syntax error around line 194
            content = content.replace(
                "available=result.returncode == 0",
                "available=(result.returncode == 0)"
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed {file_path}")
            fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    # Fix fix_all_syntax_errors.py
    file_path = Path("fix_all_syntax_errors.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix invalid regex pattern
            content = content.replace(
                "content = re.sub(rrrr'function\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*\\{', r'def \\1(\\2):', content)",
                "content = re.sub(r'function\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*\\{', r'def \\1(\\2):', content)"
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed {file_path}")
            fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    return fixes_applied


def fix_undefined_imports():
    """Fix undefined imports in key files."""
    print("🔧 Fixing undefined imports...")
    
    fixes_applied = 0
    
    # Fix tools/integration/ci_helpers.py
    file_path = Path("tools/integration/ci_helpers.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add missing imports at the top
            imports_to_add = [
                "import sys",
                "import argparse"
            ]
            
            for imp in imports_to_add:
                if imp not in content:
                    # Add after existing imports
                    if "import os" in content:
                        content = content.replace("import os", f"import os\n{imp}")
                    else:
                        content = f"{imp}\n{content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed imports in {file_path}")
            fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    # Fix tools/symbolic/memory_sealer.py
    file_path = Path("tools/symbolic/memory_sealer.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add missing shutil import
            if "import shutil" not in content and "shutil" in content:
                if "import os" in content:
                    content = content.replace("import os", "import os\nimport shutil")
                else:
                    content = f"import shutil\n{content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed imports in {file_path}")
            fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    return fixes_applied


def fix_unterminated_strings():
    """Fix unterminated string literals."""
    print("🔧 Fixing unterminated strings...")
    
    fixes_applied = 0
    
    # Fix tools/cli/aurora_dev_cli.py
    file_path = Path("tools/cli/aurora_dev_cli.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find and fix unterminated strings around line 347
            for i, line in enumerate(lines):
                if i >= 340 and i <= 350:  # Around line 347
                    if line.strip().startswith('"') and not line.strip().endswith('"'):
                        # Simple fix: close the string
                        lines[i] = line.rstrip() + '"\n'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            logger.info("Fixed unterminated strings in {file_path}")
            fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    # Fix tools/symbolic/anchor_tracker.py
    file_path = Path("tools/symbolic/anchor_tracker.py")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix unterminated triple quotes around line 291
            lines = content.split('\n')
            in_triple_quote = False
            quote_type = None
            
            for i, line in enumerate(lines):
                if '"""' in line:
                    if not in_triple_quote:
                        in_triple_quote = True
                        quote_type = '"""'
                    elif quote_type == '"""':
                        in_triple_quote = False
                        quote_type = None
                elif "'''" in line:
                    if not in_triple_quote:
                        in_triple_quote = True
                        quote_type = "'''"
                    elif quote_type == "'''":
                        in_triple_quote = False
                        quote_type = None
            
            # If we end with an unterminated triple quote, close it
            if in_triple_quote:
                lines.append(quote_type)
                content = '\n'.join(lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info("Fixed unterminated triple quotes in {file_path}")
                fixes_applied += 1
            
        except Exception as e:
            logger.error("Error fixing {file_path}: {e}")
    
    return fixes_applied


def main():
    """Main function to run all fixes."""
    print("🚀 Aurora CloudBank Critical Issue Resolver")
    print("=" * 50)
    
    total_fixes = 0
    
    try:
        # Run all fix functions
        total_fixes += fix_critical_syntax_errors()
        total_fixes += fix_undefined_imports()
        total_fixes += fix_unterminated_strings()
        
        print("=" * 50)
        logger.info("Applied {total_fixes} fixes successfully!")
        
        if total_fixes > 0:
            print("\n🔍 Recommended next steps:")
            print("1. Run: python3 -m py_compile <fixed_file> to verify syntax")
            print("2. Run: python3 -m flake8 . --count to check remaining issues")
            print("3. Run: git add . && git commit -m 'Fix critical syntax errors'")
        
        return True
        
    except Exception as e:
        logger.error("Critical error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
