#!/usr/bin/env python3
"""
🔍 Aurora CloudBank Log Injection Validator
Pre-commit hook for preventing log injection vulnerabilities
"""
import sys
import re
from pathlib import Path

def validate_log_statements(file_path):
    """Validate that log statements don't contain f-strings or unsafe patterns"""
    violations = []

    # Skip security validators themselves (they use print for reporting)
    if 'validator.py' in file_path or '.security/' in file_path:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Dangerous patterns
        patterns = [
            (r'logger\.(info|debug|warning|error|critical)\s*\(\s*f["\']', 'f-string logging'),
            (r'logging\.(info|debug|warning|error|critical)\s*\(\s*f["\']', 'direct f-string logging'),
            (r'print\s*\(\s*f["\'].*?\{.*?\}', 'f-string print (potential log output)'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in patterns:
                if re.search(pattern, line):
                    violations.append(f"Line {i}: {desc} - {line.strip()}")
        
        return violations
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

def main():
    """Main validator function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith('.py'):
            file_violations = validate_log_statements(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 LOG INJECTION VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Use parameterized logging: logger.info('Message: %s', variable)")
        sys.exit(1)
    
    print("✅ Log injection validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()