#!/usr/bin/env python3
"""
🛡️ Aurora CloudBank Pre-Commit Security Suite
Orchestrates all security validators for comprehensive protection
"""
import sys
import subprocess
import os
from pathlib import Path

class SecurityValidationSuite:
    """Complete security validation orchestrator"""
    
    def __init__(self):
        self.security_dir = Path(__file__).parent
        self.validators = [
            ('log_injection_validator.py', 'Log Injection'),
            ('shell_injection_validator.py', 'Shell Injection'), 
            ('xss_injection_validator.py', 'XSS/Code Injection'),
            ('sql_injection_validator.py', 'SQL Injection'),
            ('path_traversal_validator.py', 'Path Traversal'),
            ('csrf_auth_validator.py', 'CSRF/Authentication'),
            ('crypto_validator.py', 'Cryptography'),
        ]
        
    def run_validator(self, validator_script, description, files):
        """Run individual security validator"""
        validator_path = self.security_dir / validator_script
        
        if not validator_path.exists():
            print(f"⚠️  Warning: {validator_script} not found")
            return True
            
        try:
            cmd = [sys.executable, str(validator_path)] + files
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {description}: PASSED")
                return True
            else:
                print(f"❌ {description}: FAILED")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"⚠️  Error running {description} validator: {e}")
            return False
    
    def validate_all(self, files):
        """Run all security validators"""
        print("🛡️  Aurora CloudBank Security Validation Suite")
        print("=" * 50)
        
        all_passed = True
        
        for validator_script, description in self.validators:
            passed = self.run_validator(validator_script, description, files)
            if not passed:
                all_passed = False
        
        print("=" * 50)
        
        if all_passed:
            print("🎉 ALL SECURITY VALIDATIONS PASSED!")
            return True
        else:
            print("🚨 SECURITY VALIDATION FAILED - Please fix issues above")
            return False

def main():
    """Main pre-commit hook entry point"""
    if len(sys.argv) < 2:
        print("Usage: python security_suite.py <file1> <file2> ...")
        sys.exit(1)
    
    files = sys.argv[1:]
    suite = SecurityValidationSuite()
    
    if suite.validate_all(files):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()