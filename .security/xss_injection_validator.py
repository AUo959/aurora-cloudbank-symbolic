#!/usr/bin/env python3
"""
🔒 Aurora CloudBank XSS/Injection Validator  
Pre-commit hook for preventing XSS and injection vulnerabilities
"""
import sys
import re

def validate_xss_injection(file_path):
    """Validate for XSS and injection vulnerabilities"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Dangerous patterns
        patterns = [
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
            (r'eval\s*\(', 'eval() call - code injection risk'),
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
            (r'exec\s*\(', 'exec() call - code injection risk'),
            (r'\.innerHTML\s*=', 'innerHTML assignment - XSS risk'),
            (r'document\.write\s*\(', 'document.write() - XSS risk'),
            (r'\$\{.*\}', 'Template literal without validation'),
            (r'f["\'].*\{.*\}.*["\'](?!\s*\.\s*format)', 'F-string in sensitive context'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip comments and safe contexts
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
                
            for pattern, desc in patterns:
                if re.search(pattern, line):
                    # Additional context checks
                    if 'logging' in line.lower() and 'f"' in line:
                        violations.append(f"Line {i}: F-string in logging - use logger.info('%s', variable)")
                    elif pattern.startswith('eval') or pattern.startswith('exec'):
                        violations.append(f"Line {i}: {desc} - {line.strip()}")
                    elif 'innerHTML' in pattern and not 'textContent' in line:
                        violations.append(f"Line {i}: {desc} - use textContent instead")
        
        return violations
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

def main():
    """Main validator function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith(('.py', '.js', '.html', '.ts')):
            file_violations = validate_xss_injection(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 XSS/INJECTION VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Use parameterized queries, escape user input, avoid eval/exec")
        sys.exit(1)
    
    print("✅ XSS/Injection validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()