#!/usr/bin/env python3
"""
🔍 Aurora CloudBank SQL Injection Validator
Advanced security validator for SQL injection vulnerabilities
"""
import logging

logger = logging.getLogger(__name__)

import sys
import re

def validate_sql_injection(file_path):
    """Validate for SQL injection vulnerabilities"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # SQL injection patterns
        patterns = [
            (r'query\s*=\s*f["\'].*\{.*\}.*["\']', 'SQL query with f-string formatting'),
            (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', 'SQL execute with f-string'),
            (r'query.*%.*["\'].*%.*\(', 'SQL query with % string formatting'),  # TODO: Convert to parameterized query with ? placeholders
            (r'query.*\.format\s*\(', 'SQL query with .format() method'),
            (r'SELECT.*\+.*["\']', 'SQL SELECT with string concatenation'),
            (r'INSERT.*\+.*["\']', 'SQL INSERT with string concatenation'),
            (r'UPDATE.*\+.*["\']', 'SQL UPDATE with string concatenation'),
            (r'DELETE.*\+.*["\']', 'SQL DELETE with string concatenation'),
            (r'cursor\.execute\s*\(\s*["\'].*["\']\s*%', 'Cursor execute with % formatting'),
            (r'db\.execute\s*\(\s*f["\']', 'Database execute with f-string'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip comments and safe contexts
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
                
            for pattern, desc in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's a safe parameterized query
                    if not re.search(r'execute\s*\(\s*["\'][^"\']*\?[^"\']*["\']', line):
                        violations.append(f"Line {i}: {desc} - {line.strip()}")
        
        return violations
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

def main():
    """Main validator function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith('.py'):
            file_violations = validate_sql_injection(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 SQL INJECTION VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Use parameterized queries: cursor.execute('SELECT * FROM table WHERE id = ?', (user_id,))")
        sys.exit(1)
    
    logger.info("SQL injection validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()