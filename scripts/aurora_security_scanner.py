#!/usr/bin/env python3
"""
Aurora CloudBank Security Scanner
Comprehensive security analysis and automated fixes
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path


class AuroraSecurityScanner:

    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.severity_levels = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}

    def scan_javascript_security(self):
        """Scan JavaScript files for security issues"""
        print("🔍 Scanning JavaScript files...")

        js_files = list(Path('.').rglob('*.js'))
        for file_path in js_files:
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._check_js_content(file_path, content)
            except Exception as e:
                self.issues.append({
                    'file': str(file_path),
                    'type': 'FILE_READ_ERROR',
                    'severity': 'LOW',
                    'message': "Could not read file: {e}"
                })

    def _check_js_content(self, file_path, content):
        """Check JavaScript content for security issues""r"

        # Check for dangerous patterns
        dangerous_patterns = {
            'eval': (r'\beval\s*\(', 'HIGH', 'Use of eval() can execute arbitrary code'),  # nosec - pattern
            'innerHTML': (r'\.innerHTML\s*=', 'MEDIUM', 'innerHTML can lead to XSS, use textContent or DOMPurify'),
            'document.write': (r'document\.write\s*\(', 'HIGH', 'document.write can enable XSS attacks'),
            'setTimeout_string': (r'setTimeout\s*\(\s*[\'"]', 'MEDIUM', 'setTimeout with string can be dangerous'),
            'Function_constructor': (r'new\s+Function\s*\(', 'HIGH', 'Function constructor can execute arbitrary code'),
            'dangerouslySetInnerHTML': (
                r'dangerouslySetInnerHTML',
                'HIGH',
                'React dangerouslySetInnerHTML without sanitization'
            )
        }

        for issue_type, (pattern, severity, message) in dangerous_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': issue_type,
                    'severity': severity,
                    'message': message,
                    'code': content.split('\n')[line_num - 1].strip()
                })

    def scan_python_security(self):
        """Scan Python files for security issues"""
        print("🔍 Scanning Python files...")

        py_files = list(Path('.').rglob('*.py'))
        for file_path in py_files:
            if 'venv' in str(file_path) or '.git' in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._check_py_content(file_path, content)
            except Exception as e:
                self.issues.append({
                    'file': str(file_path),
                    'type': 'FILE_READ_ERROR',
                    'severity': 'LOW',
                    'message': "Could not read file: {e}"
                })

    def _check_py_content(self, file_path, content):
        """Check Python content for security issues""r"

        dangerous_patterns = {
            'eval': (r'\beval\s*\(', 'HIGH', 'Use of eval() can execute arbitrary code'),  # nosec - pattern definition
            'exec': (r'\bexec\s*\(', 'HIGH', 'Use of exec() can execute arbitrary code'),  # nosec - pattern definition
            'subprocess_shell': (
                r'subprocess\.\w+.*shell\s*=\s*True',
                'HIGH',
                'subprocess with shell=True can enable command injection'
            ),
            'os_system': (r'os\.system\s*\(', 'HIGH', 'os.system() can enable command injection'),  # nosec - pattern
            'sql_format': (r'\.format\s*\(.*SELECT', 'HIGH', 'String formatting in SQL can lead to injection'),
            'pickle_load': (r'pickle\.loads?\s*\(', 'MEDIUM', 'pickle.load can execute arbitrary code'),
            'yaml_unsafe': (r'yaml\.load\s*\((?!.*Loader=)', 'MEDIUM', 'yaml.load without safe loader can execute code')
        }

        for issue_type, (pattern, severity, message) in dangerous_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': issue_type,
                    'severity': severity,
                    'message': message,
                    'code': content.split('\n')[line_num - 1].strip()
                })

    def check_dependencies(self):
        """Check for vulnerable dependencies"""
        print("🔍 Checking dependencies...")

        # Check npm dependencies
        if os.path.exists('package.json'):
            try:
                result = subprocess.run(['npm', 'audit', '--json'],
                                        capture_output=True, text=True, timeout=30, shell=False, check=False)
                if result.returncode != 0 and result.stdout:
                    audit_data = json.loads(result.stdout)
                    if 'vulnerabilities' in audit_data:
                        for vuln_name, vuln_data in audit_data['vulnerabilities'].items():
                            severity = vuln_data.get('severity', 'UNKNOWN').upper()
                            self.issues.append({
                                'file': 'package.json',
                                'type': 'DEPENDENCY_VULNERABILITY',
                                'severity': severity,
                                'message': "Vulnerable dependency: {vuln_name}",
                                'package': vuln_name,
                                'details': vuln_data
                            })
            except Exception as e:
                print("Could not run npm audit: {e}")

    def check_configuration_security(self):
        """Check for security configuration issues"""
        print("🔍 Checking configuration security...r")

        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*[\'"][^\'\"]{8,}[\'r"]', 'HIGH', 'Possible hardcoded password'),
            (r'secret\s*=\s*[\'"][^\'\"]{16,}[\'r"]', 'HIGH', 'Possible hardcoded secret'),
            (r'api[_-]?key\s*=\s*[\'"][^\'\"]{16,}[\'r"]', 'HIGH', 'Possible hardcoded API key'),
            (r'token\s*=\s*[\'"][^\'\"]{20,}[\'"]', 'MEDIUM', 'Possible hardcoded token'),
            (r'[\'"][A-Za-z0-9]{32,}[\'"]', 'LOW', 'Possible hardcoded credential')
        ]

        for root, dirs, files in os.walk('.'):
            if '.git' in root or 'node_modules' in root or 'venv' in root:
                continue

            for file in files:
                if file.endswith(('.js', '.py', '.json', '.yml', '.yaml', '.env')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for pattern, severity, message in secret_patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    line_num = content[:match.start()].count('\n') + 1
                                    self.issues.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'type': 'HARDCODED_SECRET',
                                        'severity': severity,
                                        'message': message,
                                        'code': content.split('\n')[line_num - 1].strip()
                                    })
                    except Exception:
                        continue

    def apply_automated_fixes(self):
        """Apply automated fixes for certain issues"""
        print("🔧 Applying automated fixes...")

        for issue in self.issues:
            if issue['type'] == 'innerHTML' and issue['severity'] == 'MEDIUM':
                self._fix_innerHTML_usage(issue)
            elif issue['type'] == 'subprocess_shell':
                # Skip subprocess_shell fixes for now - would need file-specific logic
                print("  Note: subprocess_shell issue found in {issue['file']} - manual review needed")

    def _fix_innerHTML_usage(self, issue):
        """Fix innerHTML usage by suggesting textContent""r"
        file_path = issue['file']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple fix: suggest textContent instead of innerHTML
            fixed_content = re.sub(
                r'(\w+)\.innerHTML\s*=\s*([^;]+);',
                r'\1.textContent = \2; // SECURITY FIX: Changed from innerHTML',
                content
            )

            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                self.fixes_applied.append("Fixed innerHTML usage in {file_path}")
        except Exception as e:
            print("Could not fix innerHTML in {file_path}: {e}")

    def generate_security_report(self):
        """Generate comprehensive security report"""
        print("\n🛡️ SECURITY SCAN RESULTS")
        print("=" * 50)

        # Sort issues by severity
        sorted_issues = sorted(
            self.issues,
            key=lambda x: self.severity_levels.get(x['severity'], 0),
            reverse=True
        )

        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        for issue in sorted_issues:
            severity = issue['severity']
            severity_counts[severity] += 1

            print("\n[{severity}] {issue['type']} in {issue['file']}")
            if 'line' in issue:
                print("  Line {issue['line']}: {issue.get('code', '')}")
            print("  {issue['message']}")

        print("\n📊 SUMMARY:")
        print("  CRITICAL: {severity_counts['CRITICAL']}")
        print("  HIGH: {severity_counts['HIGH']}")
        print("  MEDIUM: {severity_counts['MEDIUM']}")
        print("  LOW: {severity_counts['LOW']}")
        print("  TOTAL: {len(self.issues)}")

        if self.fixes_applied:
            print("\n✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                print("  • {fix}")

        # Save detailed report
        date_cmd = ['date']
        timestamp = (
            subprocess.run(date_cmd, capture_output=True, text=True, shell=False, check=False).stdout.strip()
        )
        report = {
            'scan_timestamp': str(timestamp),
            'total_issues': len(self.issues),
            'severity_breakdown': severity_counts,
            'issues': sorted_issues,
            'fixes_applied': self.fixes_applied
        }

        with open('security_scan_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print("\n📋 Detailed report saved to: security_scan_report.json")

        return len([i for i in self.issues if i['severity'] in ['CRITICAL', 'HIGH']])

def main():
    scanner = AuroraSecurityScanner()

    print("🛡️ Aurora CloudBank Security Scanner")
    print("=====================================")

    # Run all scans
    scanner.scan_javascript_security()
    scanner.scan_python_security()
    scanner.check_dependencies()
    scanner.check_configuration_security()

    # Apply fixes
    scanner.apply_automated_fixes()

    # Generate report
    critical_high_count = scanner.generate_security_report()

    # Exit with appropriate code
    if critical_high_count > 0:
        print("\n⚠️ Found {critical_high_count} critical/high severity issues!")
        sys.exit(1)
    else:
        print("\n✅ No critical or high severity issues found!")
        sys.exit(0)

if __name__ == "__main__":
    main()
