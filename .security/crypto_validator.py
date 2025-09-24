#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Cryptography Validator
Security validator for cryptographic vulnerabilities and weak encryption
"""
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
            # Weak encryption
            (r'DES\(', 'Weak DES encryption algorithm'),
            (r'MD5\(', 'Weak MD5 hash algorithm'),
            (r'SHA1\(', 'Weak SHA1 hash algorithm'),
            (r'rc4', 'Weak RC4 encryption'),
            (r'random\.random\(\)', 'Weak random number generation'),
            
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
            # Skip comments and safe contexts
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
                
            for pattern, desc in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check for secure alternatives
                    if not any(safe_pattern in line.lower() for safe_pattern in [
                        'sha256', 'sha384', 'sha512', 'aes', 'rsa', 'secrets.', 
                        'cryptography.', 'bcrypt', 'scrypt', 'pbkdf2'
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
            file_violations = validate_cryptography(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 CRYPTOGRAPHY VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Use strong encryption (AES, SHA-256+), secure random generators (secrets module), proper key management")
        sys.exit(1)
    
    print("✅ Cryptography validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()