#!/usr/bin/env python3
"""
🔄 Aurora CloudBank Continuous Security Scanner
Post-commit hook for ongoing security monitoring
"""
import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class ContinuousSecurityScanner:
    """Automated security scanning for post-commit monitoring"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.security_dir = self.repo_root / '.security'
        self.scan_results = {}
        
    def scan_recent_changes(self):
        """Scan files changed in recent commits"""
        try:
            # Get files changed in last commit
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
                capture_output=True, text=True, cwd=self.repo_root
            )
            
            if result.returncode != 0:
                return []
                
            changed_files = [
                f for f in result.stdout.strip().split('\n') 
                if f and f.endswith(('.py', '.js', '.ts', '.html'))
            ]
            
            return [str(self.repo_root / f) for f in changed_files if (self.repo_root / f).exists()]
            
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def run_security_scan(self, files):
        """Run comprehensive security scan"""
        if not files:
            print("No files to scan")
            return True
            
        print(f"🔍 Scanning {len(files)} changed files...")
        
        # Run security suite
        suite_script = self.security_dir / 'security_suite.py'
        if not suite_script.exists():
            print("Warning: Security suite not found")
            return True
            
        try:
            result = subprocess.run(
                [sys.executable, str(suite_script)] + files,
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("✅ Post-commit security scan passed")
                self.log_scan_result("PASSED", files, result.stdout)
                return True
            else:
                print("⚠️  Post-commit security scan found issues:")
                print(result.stdout)
                self.log_scan_result("ISSUES_FOUND", files, result.stdout)
                return False
                
        except Exception as e:
            print(f"Error running security scan: {e}")
            return False
    
    def log_scan_result(self, status, files, output):
        """Log scan results for tracking"""
        log_file = self.security_dir / 'scan_log.json'
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'files_scanned': len(files),
            'files': files,
            'output': output[:500] + '...' if len(output) > 500 else output
        }
        
        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'scans': []}
            
            log_data['scans'].append(entry)
            
            # Keep only last 50 scans
            log_data['scans'] = log_data['scans'][-50:]
            
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not log scan result: {e}")

def main():
    """Main post-commit scanner"""
    scanner = ContinuousSecurityScanner()
    
    print("🔄 Aurora CloudBank Post-Commit Security Scan")
    print("=" * 45)
    
    changed_files = scanner.scan_recent_changes()
    scanner.run_security_scan(changed_files)
    
    print("=" * 45)
    print("📊 Continuous security monitoring active")

if __name__ == "__main__":
    main()