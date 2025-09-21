#!/usr/bin/env python3
"""
Stage 2 Lint Fixer: Import Issues
Fixes F401 (unused imports) and F811 (redefined imports)
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple, Set, Dict


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze import usage."""
    
    def __init__(self):
        self.imports = {}  # name -> (line_number, import_statement)
        self.used_names = set()
        self.redefined_imports = []  # List of (name, line1, line2)
    
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            line_num = node.lineno
            
            # Check for redefinition
            if name in self.imports:
                self.redefined_imports.append((name, self.imports[name][0], line_num))
            
            self.imports[name] = (line_num, f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            line_num = node.lineno
            
            # Check for redefinition  
            if name in self.imports:
                self.redefined_imports.append((name, self.imports[name][0], line_num))
            
            module = node.module or ""
            self.imports[name] = (line_num, f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
        self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        # Handle cases like module.function
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)


def analyze_imports(file_path: str) -> Tuple[List[str], List[Tuple[str, int, int]]]:
    """
    Analyze imports in a Python file.
    
    Returns:
        Tuple of (unused_imports, redefined_imports)
        where unused_imports is list of import names
        and redefined_imports is list of (name, first_line, second_line)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        
        # Find unused imports
        unused_imports = []
        for name, (line_num, import_stmt) in analyzer.imports.items():
            if name not in analyzer.used_names:
                unused_imports.append(name)
        
        return unused_imports, analyzer.redefined_imports
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")
        return [], []


def fix_import_issues(file_path: str) -> Tuple[bool, List[str]]:
    """
    Fix import issues in a Python file.
    
    Returns:
        Tuple of (was_modified, list_of_fixes_applied)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        lines = content.split('\n')
        
        # Analyze imports
        unused_imports, redefined_imports = analyze_imports(file_path)
        
        # Fix redefined imports (F811) - remove the later import
        for name, first_line, second_line in redefined_imports:
            # Find and remove the second import
            for i, line in enumerate(lines):
                if i + 1 == second_line:  # Line numbers are 1-based
                    # Check if this line contains the import
                    if (f"import {name}" in line or 
                        f"from " in line and f" {name}" in line):
                        lines[i] = ""  # Remove the line
                        fixes_applied.append(f"Line {second_line}: Removed redefined import '{name}' (F811)")
                        break
        
        # Fix unused imports (F401) - be conservative, only remove obvious cases
        for name in unused_imports:
            # Find the import line and check if it's safe to remove
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Simple case: standalone import
                if line_stripped == f"import {name}":
                    lines[i] = ""
                    fixes_applied.append(f"Line {i+1}: Removed unused import '{name}' (F401)")
                    break
                elif line_stripped.startswith(f"from ") and line_stripped.endswith(f" import {name}"):
                    lines[i] = ""
                    fixes_applied.append(f"Line {i+1}: Removed unused import '{name}' (F401)")
                    break
                elif f"import {name}," in line_stripped:
                    # Multiple imports on one line - just remove this one
                    new_line = line.replace(f"{name}, ", "").replace(f", {name}", "").replace(f"import {name}", "import")
                    if new_line.strip().endswith("import"):
                        lines[i] = ""  # If it was the only import, remove the line
                    else:
                        lines[i] = new_line
                    fixes_applied.append(f"Line {i+1}: Removed unused import '{name}' from multi-import (F401)")
                    break
        
        # Clean up empty lines that were left behind
        cleaned_lines = []
        for line in lines:
            if line.strip() == "" and len(cleaned_lines) > 0 and cleaned_lines[-1].strip() == "":
                continue  # Skip duplicate empty lines
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Write back if modified
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes_applied
        
        return False, []
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, []


def process_directory(directory: str) -> None:
    """Process all Python files in a directory."""
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"⚠️  Directory not found: {directory}")
        return
    
    python_files = list(directory_path.rglob("*.py"))
    if not python_files:
        print(f"⚠️  No Python files found in {directory}")
        return
    
    print(f"🔧 Processing {len(python_files)} Python files in {directory}...")
    
    total_modified = 0
    total_fixes = 0
    
    for file_path in python_files:
        was_modified, fixes = fix_import_issues(str(file_path))
        if was_modified:
            total_modified += 1
            total_fixes += len(fixes)
            print(f"✅ Fixed {file_path.relative_to(directory_path)}: {len(fixes)} fixes")
            for fix in fixes:
                print(f"   - {fix}")
        else:
            print(f"✨ Clean {file_path.relative_to(directory_path)}")
    
    print(f"\n📊 Stage 2 Summary for {directory}:")
    print(f"   Files modified: {total_modified}")
    print(f"   Total fixes applied: {total_fixes}")


def main():
    """Main function to process all target areas."""
    print("🧹 Stage 2: Import Issues Cleanup")
    print("=" * 50)
    
    target_areas = [
        "modules/opal2",
        "modules/cask", 
        "src/core",
        "src/bridges",
        "src/servers"
    ]
    
    for area in target_areas:
        print(f"\n🎯 Processing {area}...")
        process_directory(area)
        
    print("\n🎉 Stage 2 import cleanup complete!")


if __name__ == "__main__":
    main()