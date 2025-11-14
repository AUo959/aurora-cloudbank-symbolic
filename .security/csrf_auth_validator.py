#!/usr/bin/env python3
"""
🔐 Aurora CloudBank CSRF & Authentication Validator
Security validator for CSRF, authentication, and session vulnerabilities
"""
import logging

logger = logging.getLogger(__name__)

import sys
import re

def validate_csrf_auth(file_path):
    """Validate for CSRF and authentication vulnerabilities"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # CSRF and authentication patterns
        patterns = [
            # CSRF patterns
            (r'@app\.route.*methods=.*POST.*\)', 'POST route without CSRF protection'),
            (r'app\.post\s*\(\s*["\']', 'POST endpoint without CSRF token validation'),
            (r'fetch\s*\(\s*["\'][^"\']*["\'],\s*\{.*method.*["\']POST["\']', 'POST fetch without CSRF token'),
            (r'request\.form\[.*\]', 'Form data access without CSRF validation'),
            
            # Authentication patterns
            (r'password.*==.*["\'].*["\']', 'Hardcoded password comparison'),
            (r'token.*==.*["\'].*["\']', 'Hardcoded token comparison'),
            (r'session\[.*\].*=.*input\(\)', 'Direct user input to session'),
            (r'login.*without.*hash', 'Login without password hashing'),
            (r'jwt\.decode.*verify=False', 'JWT verification disabled'),
            (r'session\.permanent.*=.*True', 'Permanent session without expiry'),
            
            # Session management
            (r'session_id.*=.*random\(', 'Weak session ID generation'),
            (r'cookie.*secure=False', 'Insecure cookie settings'),
            (r'cookie.*httponly=False', 'Cookie without HTTPOnly flag'),
            (r'session.*timeout.*=.*None', 'Session without timeout'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip comments and safe contexts
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
                
            for pattern, desc in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check for security measures
                    if not any(safe_pattern in line.lower() for safe_pattern in [
                        'csrf_token', '@csrf.exempt', 'verify_csrf', 'bcrypt', 'scrypt', 
                        'pbkdf2', 'secure=true', 'httponly=true', 'samesite'
                    ]):
                        violations.append(f"Line {i}: {desc} - {line.strip()}")
        
        return violations
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

def main():
    """Main validator function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith(('.py', '.js', '.ts')):
            file_violations = validate_csrf_auth(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 CSRF/AUTHENTICATION VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Implement CSRF tokens, use secure session management, hash passwords with bcrypt")
        sys.exit(1)
    
    logger.info("CSRF/Authentication validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()