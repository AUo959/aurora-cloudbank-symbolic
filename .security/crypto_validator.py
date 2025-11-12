#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Cryptography Validator
Security validator for cryptographic vulnerabilities and weak encryption
"""
import logging

logger = logging.getLogger(__name__)

import sys
import re

def validate_cryptography(file_path):
    """Validate for cryptographic vulnerabilities"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Cryptography vulnerability patterns
        patterns = [
            # Weak encryption (word boundaries to avoid false positives like .includes())
            (r'\bDES\s*\(', 'Weak DES encryption algorithm'),
            (r'\bMD5\s*\(', 'Weak MD5 hash algorithm'),
            (r'\bSHA1\s*\(', 'Weak SHA1 hash algorithm'),
            (r'\bRC4\b', 'Weak RC4 encryption'),
            (r'\brandom\.random\s*\(\)', 'Weak random number generation'),
            
            # Hardcoded secrets
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
            (r'secret_key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret key'),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded token'),
            (r'private_key\s*=\s*["\']', 'Hardcoded private key'),
            
            # Insecure random
            (r'random\.choice.*password', 'Weak password generation'),
            (r'random\.randint.*token', 'Weak token generation'),
            (r'time\(\).*seed', 'Predictable random seed'),
            
            # SSL/TLS issues
            (r'ssl_verify\s*=\s*False', 'SSL verification disabled'),
            (r'verify=False', 'Certificate verification disabled'),
            (r'PROTOCOL_TLS.*=.*ssl\.PROTOCOL_SSLv', 'Deprecated SSL protocol'),
            (r'check_hostname\s*=\s*False', 'Hostname verification disabled'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip comments, docstrings, and safe contexts
            stripped = line.strip()
            if (stripped.startswith('#') or stripped.startswith('//') or
                    stripped.startswith('"""') or stripped.startswith("'''")):
                continue

            # Skip pattern definition lines (avoid meta-detection)
            if '(r\'' in line or '(r"' in line or 'patterns = [' in line:
                continue

            for pattern, desc in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check for secure alternatives or pattern definitions
                    safe_patterns = [
                        'sha256', 'sha384', 'sha512', 'aes', 'rsa', 'secrets.',
                        'cryptography.', 'bcrypt', 'scrypt', 'pbkdf2', 'pattern', 'regex'
                    ]
                    if not any(safe in line.lower() for safe in safe_patterns):
                        violations.append(f"Line {i}: {desc} - {line.strip()}")

        return violations

    except Exception as e:
        return [f"Error reading {file_path}: {e}"]


def main():
    """Main validator function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith(('.py', '.js', '.ts')):
            file_violations = validate_cryptography(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 CRYPTOGRAPHY VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Use strong encryption (AES, SHA-256+), "
              "secure random generators (secrets module), proper key management")
        sys.exit(1)

    logger.info("Cryptography validation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
