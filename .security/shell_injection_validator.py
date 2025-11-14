#!/usr/bin/env python3
"""
🔍 Aurora CloudBank Shell Injection Validator
Pre-commit hook for preventing shell injection vulnerabilities
"""
import logging

logger = logging.getLogger(__name__)

import sys
import re

def validate_subprocess_calls(file_path):
    """Validate subprocess calls for shell injection risks"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Dangerous patterns
        patterns = [
            (r'subprocess\.(run|call|check_call|check_output).*shell=True', 'shell=True subprocess call'),
            (r'os\.system\s*\(', 'os.system() call'),
            (r'os\.popen\s*\(', 'os.popen() call'),
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
            file_violations = validate_subprocess_calls(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 SHELL INJECTION VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Use shell=False and array arguments: subprocess.run(['cmd', 'arg1', 'arg2'])")
        sys.exit(1)
    
    logger.info("Shell injection validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()