#!/usr/bin/env python3
import os
import subprocess
import re
from typing import Set

"""
Missing Imports Fixer - Adds missing import statements to Python files
Intelligently detects and adds commonly used imports that are missing
"""

class ImportFixer:
    
    def __init__(self):
        # Common imports mapping undefined names to their modules
        self.common_imports = {
            "Dict": "from typing import Dict",
            "List": "from typing import List",
            "Any": "from typing import Any",
            "Optional": "from typing import Optional",
            "Union": "from typing import Union",
            "Callable": "from typing import Callable",
            "Tuple": "from typing import Tuple",
            "datetime": "from datetime import datetime",
            "json": "import json",
            "Path": "from pathlib import Path",
            "asyncio": "import asyncio",
            "os": "import os",
            "sys": "import sys",
            "re": "import re",
            "logging": "import logging",
            "time": "import time",
            "random": "import random",
            "math": "import math",
            "collections": "import collections",
            "defaultdict": "from collections import defaultdict",
            "OrderedDict": "from collections import OrderedDict",
            "Counter": "from collections import Counter",
            "partial": "from functools import partial",
            "lru_cache": "from functools import lru_cache",
            "wraps": "from functools import wraps",
            "ABC": "from abc import ABC",
            "abstractmethod": "from abc import abstractmethod",
            "dataclass": "from dataclasses import dataclass",
            "field": "from dataclasses import field",
        }
    
    def get_undefined_names_from_flake8(self, file_path: str) -> Set[str]:
        """Get undefined names (F821 errors) from flake8 for a specific file."""
        try:
            result = subprocess.run(
                ["flake8", "--select=F821", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            undefined_names = set()
            
            for line in result.stdout.split("\n"):
                if "F821" in line and "undefined name" in line:
                    # Extract the undefined name from the error message
                    match = re.search(r"undefined name '([^']+)'", line)
                    if match:
                        undefined_names.add(match.group(1))
            
            return undefined_names
        except Exception as e:
            print(f"Error: {e}")
            return set()

    def add_imports_to_file(self, file_path: str):
        """Add missing imports to a Python file."""
        undefined_names = self.get_undefined_names_from_flake8(file_path)
        
        if not undefined_names:
            return
        
        # Find which imports to add
        imports_to_add = []
        for name in undefined_names:
            if name in self.common_imports:
                imports_to_add.append(self.common_imports[name])
        
        if not imports_to_add:
            return
        
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add imports at the top after shebang/docstring
        lines = content.split('\n')
        insert_position = 0
        
        # Skip shebang
        if lines[0].startswith('#!'):
            insert_position = 1
        
        # Skip module docstring if present
        if insert_position < len(lines) and lines[insert_position].strip().startswith('"""'):
            for i in range(insert_position + 1, len(lines)):
                if '"""' in lines[i]:
                    insert_position = i + 1
                    break
        
        # Insert imports
        for import_statement in sorted(set(imports_to_add)):
            lines.insert(insert_position, import_statement)
            insert_position += 1
        
        # Write back
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Added {len(imports_to_add)} imports to {file_path}")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python missing_imports_fixer.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    fixer = ImportFixer()
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to process")
    
    # Process each file
    for file_path in python_files:
        try:
            fixer.add_imports_to_file(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Files Processed: {len(python_files)}")


if __name__ == "__main__":
    main()
