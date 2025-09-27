#!/usr/bin/env python3
"""
CodeQL Security Issues Fixer for Aurora
Symbolic Anchor: T1-SECURITY-FIX-2025
Automatically fixes common security patterns flagged by CodeQL
"""

import os
import re
import ast
from pathlib import Path
from datetime import datetime
import hashlib
import json
from typing import List, Dict, Tuple

class CodeQLSecurityFixer:
    def __init__(self):
        self.anchor = "T1-SECURITY-FIX-2025"
        self.fixes_applied = []
        self.backup_dir = Path("security_fixes_backup")
        
    def backup_file(self, file_path: Path) -> str:
        """Create backup of file before modification"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.backup_dir.mkdir(exist_ok=True)
        
        backup_path = self.backup_dir / f"{file_path.name}_{timestamp}.bak"
        
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
            
        return str(backup_path)
    
    def fix_yaml_load_issues(self) -> List[Dict]:
        """Fix unsafe yaml.load() calls"""
        fixes = []
        
        for py_file in Path('.').rglob('*.py'):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for unsafe yaml.load patterns
                unsafe_patterns = [
                    (r'yaml\.load\s*\(\s*([^,)]+)\s*\)', r'yaml.safe_load(\1)'),
                    (r'yaml\.load\s*\(\s*([^,)]+)\s*,\s*Loader\s*=\s*yaml\.Loader\s*\)', r'yaml.safe_load(\1)')
                ]
                
                modified = False
                original_content = content
                
                for pattern, replacement in unsafe_patterns:
                    if re.search(pattern, content):
                        backup_path = self.backup_file(py_file)
                        content = re.sub(pattern, replacement, content)
                        modified = True
                        
                        fixes.append({
                            "file": str(py_file),
                            "issue": "Unsafe yaml.load()",
                            "fix": "Replaced with yaml.safe_load()",
                            "backup": backup_path,
                            "anchor": f"FIX-YAML-{py_file.stem.upper()}"
                        })
                
                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"🔧 Fixed yaml.load() in: {py_file}")
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                
        return fixes
    
    def fix_subprocess_shell_issues(self) -> List[Dict]:
        """Fix subprocess calls with shell=True"""
        fixes = []
        
        for py_file in Path('.').rglob('*.py'):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for subprocess.call/run with shell=True
                shell_patterns = [
                    r'subprocess\.(call|run)\s*\([^)]*shell\s*=\s*True[^)]*\)'
                ]
                
                for pattern in shell_patterns:
                    matches = re.finditer(pattern, content)
                    if matches:
                        backup_path = self.backup_file(py_file)
                        
                        # Add comment warning about shell=True usage
                        warning_comment = "# WARNING: shell=True usage detected - review for security implications"
                        
                        # Find the line and add warning
                        lines = content.split('\n')
                        new_lines = []
                        
                        for i, line in enumerate(lines):
                            if re.search(pattern, line) and warning_comment not in line:
                                new_lines.append(f"        {warning_comment}")
                            new_lines.append(line)
                        
                        content = '\n'.join(new_lines)
                        
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        fixes.append({
                            "file": str(py_file),
                            "issue": "subprocess shell=True usage",
                            "fix": "Added security warning comment",
                            "backup": backup_path,
                            "anchor": f"FIX-SHELL-{py_file.stem.upper()}"
                        })
                        
                        print(f"🔧 Added shell=True warning in: {py_file}")
                        break  # Only process once per file
                        
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                
        return fixes
    
    def fix_hardcoded_secrets(self) -> List[Dict]:
        """Fix or flag hardcoded secrets"""
        fixes = []
        
        for py_file in Path('.').rglob('*.py'):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for potential hardcoded secrets
                secret_patterns = [
                    r'(password|token|secret|key)\s*=\s*["\'][^"\']{8,}["\']'
                ]
                
                modified = False
                
                for pattern in secret_patterns:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        backup_path = self.backup_file(py_file)
                        
                        # Add security comment
                        security_comment = "# SECURITY: Review hardcoded credentials - consider environment variables"
                        
                        lines = content.split('\n')
                        new_lines = []
                        
                        for i, line in enumerate(lines):
                            if re.search(pattern, line, re.IGNORECASE) and security_comment not in line:
                                new_lines.append(f"        {security_comment}")
                            new_lines.append(line)
                        
                        content = '\n'.join(new_lines)
                        modified = True
                        
                        fixes.append({
                            "file": str(py_file),
                            "issue": "Potential hardcoded credentials",
                            "fix": "Added security review comment",
                            "backup": backup_path,
                            "anchor": f"FIX-CREDS-{py_file.stem.upper()}"
                        })
                
                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"🔧 Added credential warning in: {py_file}")
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                
        return fixes
    
    def fix_eval_exec_usage(self) -> List[Dict]:
        """Fix dangerous eval/exec usage"""
        fixes = []
        
        for py_file in Path('.').rglob('*.py'):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for eval/exec usage
                dangerous_patterns = [
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
                    (r'\beval\s*\(', "eval() usage"),
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
                    (r'\bexec\s*\(', "exec() usage")
                ]
                
                modified = False
                
                for pattern, issue_name in dangerous_patterns:
                    if re.search(pattern, content):
                        backup_path = self.backup_file(py_file)
                        
                        # Add critical security warning
                        warning = f"# CRITICAL SECURITY: {issue_name} detected - high code injection risk"
                        
                        lines = content.split('\n')
                        new_lines = []
                        
                        for line in lines:
                            if re.search(pattern, line) and warning not in line:
                                new_lines.append(f"        {warning}")
                            new_lines.append(line)
                        
                        content = '\n'.join(new_lines)
                        modified = True
                        
                        fixes.append({
                            "file": str(py_file),
                            "issue": issue_name,
                            "fix": "Added critical security warning",
                            "backup": backup_path,
                            "anchor": f"FIX-DANGEROUS-{py_file.stem.upper()}"
                        })
                
                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"🔧 Added dangerous function warning in: {py_file}")
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                
        return fixes
    
    def apply_all_fixes(self):
        """Apply all security fixes"""
        print("🔒 Aurora CodeQL Security Fixer")
        print(f"📌 Anchor: {self.anchor}")
        print("="*50)
        
        all_fixes = []
        
        print("\n🔧 Step 1: Fixing unsafe yaml.load() calls...")
        yaml_fixes = self.fix_yaml_load_issues()
        all_fixes.extend(yaml_fixes)
        
        print(f"\n🔧 Step 2: Reviewing subprocess shell=True usage...")
        shell_fixes = self.fix_subprocess_shell_issues()
        all_fixes.extend(shell_fixes)
        
        print(f"\n🔧 Step 3: Reviewing hardcoded credentials...")
        cred_fixes = self.fix_hardcoded_secrets()
        all_fixes.extend(cred_fixes)
        
        print(f"\n🔧 Step 4: Reviewing eval/exec usage...")
        exec_fixes = self.fix_eval_exec_usage()
        all_fixes.extend(exec_fixes)
        
        # Generate fixes manifest
        fixes_manifest = {
            "anchor": self.anchor,
            "timestamp": datetime.utcnow().isoformat(),
            "total_fixes": len(all_fixes),
            "fixes_by_type": {
                "yaml_load": len(yaml_fixes),
                "subprocess_shell": len(shell_fixes),
                "hardcoded_creds": len(cred_fixes),
                "eval_exec": len(exec_fixes)
            },
            "fixes_applied": all_fixes,
            "backup_directory": str(self.backup_dir),
            "dlp_tag": "SECURITY_FIXES",
            "thread_seal": hashlib.sha256(
                json.dumps(all_fixes, sort_keys=True).encode()
            ).hexdigest()
        }
        
        with open("security_fixes_manifest.json", "w") as f:
            json.dump(fixes_manifest, f, indent=2)
        
        print(f"\n✅ Security fixes complete!")
        print(f"📊 Total fixes applied: {len(all_fixes)}")
        print(f"🔒 Thread sealed: {fixes_manifest['thread_seal'][:16]}...")
        print(f"💾 Manifest saved to: security_fixes_manifest.json")
        
        if all_fixes:
            print(f"\n🔧 Fixes summary:")
            for fix_type, count in fixes_manifest["fixes_by_type"].items():
                if count > 0:
                    print(f"  - {fix_type.replace('_', ' ').title()}: {count} fixes")
        else:
            print(f"\n✨ No security issues found requiring automatic fixes!")
            
        return fixes_manifest

if __name__ == "__main__":
    fixer = CodeQLSecurityFixer()
    fixer.apply_all_fixes()