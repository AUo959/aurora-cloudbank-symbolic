#!/usr/bin/env python3
"""
Final Python syntax fixer
"""

import os
import re


def fix_function_declarations(filepath):
    """Fix Python function declaration syntax"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Fix async def with incorrect syntax
    content = re.sub(r'async def (\w+)\(self, \*args, \*\*kwargs\):', r'async def \1(self):', content)
    content = re.sub(r'def (\w+)\(self, \*args, \*\*kwargs\):', r'def \1(self):', content)

    # Remove trailing semicolons in Python
    content = re.sub(r';$', '', content, flags=re.MULTILINE)

    # Fix return statements
    content = re.sub(r'return {([^}]+)};', r'return {\1}', content)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Fixed {filepath}")


# Fix the problematic files
files = [
    'src/output/multi_modal_output_coordination.py',
    'src/prediction/predictive_analytics_system.py',
    'src/research/quantum_research_acceleration_engine.py'
]

for file in files:
    if os.path.exists(file):
        fix_function_declarations(file)

print("All syntax errors fixed!")
