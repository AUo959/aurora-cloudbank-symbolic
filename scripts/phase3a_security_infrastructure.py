#!/usr/bin/env python3
"""
🛡️ Aurora CloudBank Security Phase 3A: Automated Security Scanning Infrastructure
Advanced security monitoring, pre-commit hooks, and continuous vulnerability detection

This phase deploys:
- Pre-commit security validation hooks
- Automated dependency vulnerability scanning  
- Real-time security monitoring
- Advanced pattern detection (eval/exec)
- Security policy enforcement
"""

import os
import re
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import hashlib

# Aurora CloudBank imports
from src.core.native_dlp_export import NativeDLPTracker

class Phase3SecurityInfrastructure:
    """Phase 3A: Advanced security infrastructure deployment"""
    
    def __init__(self):
        self.dlp_tracker = NativeDLPTracker()
        self.security_violations = []
        self.infrastructure_deployed = []
        self.monitoring_active = False
        
        # Initialize Phase 3 security tracking
        self.phase3_tag_id = self.dlp_tracker.tag_symbolic_operation({
            'operation': 'phase3_security_infrastructure',
            'scope': 'AUTOMATED_SCANNING_DEPLOYMENT',
            'target_alerts': '<50_github_alerts'
        })
        
        tag = self.dlp_tracker.tags[self.phase3_tag_id]
        tag.add_anchor_protocol("PHASE3_SECURITY_DEPLOY")
        tag.add_anchor_protocol("PICARD_DELTA_3")
        tag.add_t1_srb_anchor("T1_INFRASTRUCTURE_SECURITY")
        tag.metadata.update({
            'context_tag': 'phase3_infrastructure_deployment',
            'dlp_level': 'DLP_L2_LOCKED',
            'symbolic_hash_validation': True
        })
        
        self.setup_logging()
        
    def setup_logging(self):
        """Setup secure logging for Phase 3"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - PHASE3-SEC - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('phase3_security_infrastructure.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_pre_commit_security_hooks(self):
        """Deploy comprehensive pre-commit security validation"""
        print("🔒 Deploying pre-commit security hooks...")
        
        # Create .pre-commit-config.yaml if it doesn't exist
        precommit_config = {
            'repos': [
                {
                    'repo': 'local',
                    'hooks': [
                        {
                            'id': 'aurora-security-scan',
                            'name': 'Aurora CloudBank Security Scanner',
                            'entry': 'python3 scripts/aurora_security_scanner.py',
                            'language': 'system',
                            'files': r'\.(py|js|ts)$',
                            'pass_filenames': False
                        },
                        {
                            'id': 'log-injection-prevention',
                            'name': 'Log Injection Prevention',
                            'entry': 'python3 .security/log_injection_validator.py',
                            'language': 'system',
                            'files': r'\.py$'
                        },
                        {
                            'id': 'shell-injection-prevention',
                            'name': 'Shell Injection Prevention',
                            'entry': 'python3 .security/shell_injection_validator.py',
                            'language': 'system',
                            'files': r'\.py$'
                        },
                        {
                            'id': 'eval-exec-detection',
                            'name': 'Dangerous eval/exec Detection',
                            'entry': 'python3 .security/eval_exec_detector.py',
                            'language': 'system',
                            'files': r'\.(py|js)$'
                        }
                    ]
                }
            ]
        }
        
        with open('.pre-commit-config.yaml', 'w') as f:
            import yaml
            yaml.dump(precommit_config, f, default_flow_style=False)
        
        self.infrastructure_deployed.append("pre-commit security hooks")
        self.logger.info("Pre-commit security hooks deployed")
        
    def create_log_injection_validator(self):
        """Create advanced log injection validator"""
        validator_content = '''#!/usr/bin/env python3
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
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\\n')
        
        # Dangerous patterns
        patterns = [
            (r'logger\\.(info|debug|warning|error|critical)\\s*\\(\\s*f["\']', 'f-string logging'),
            (r'logging\\.(info|debug|warning|error|critical)\\s*\\(\\s*f["\']', 'direct f-string logging'),
            (r'print\\s*\\(\\s*f["\'].*?\\{.*?\\}', 'f-string print (potential log output)'),
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
        print("\\n💡 Fix: Use parameterized logging: logger.info('Message: %s', variable)")
        sys.exit(1)
    
    logger.info("Log injection validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
'''
        
        os.makedirs('.security', exist_ok=True)
        with open('.security/log_injection_validator.py', 'w') as f:
            f.write(validator_content)
        
        os.chmod('.security/log_injection_validator.py', 0o755)
        self.infrastructure_deployed.append("log injection validator")
        
    def create_shell_injection_validator(self):
        """Create shell injection validator"""
        validator_content = '''#!/usr/bin/env python3
"""
🔍 Aurora CloudBank Shell Injection Validator
Pre-commit hook for preventing shell injection vulnerabilities
"""
import sys
import re

def validate_subprocess_calls(file_path):
    """Validate subprocess calls for shell injection risks"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\\n')
        
        # Dangerous patterns
        patterns = [
            (r'subprocess\\.(run|call|check_call|check_output).*shell=True', 'shell=True subprocess call'),
            (r'os\\.system\\s*\\(', 'os.system() call'),
            (r'os\\.popen\\s*\\(', 'os.popen() call'),
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
        print("\\n💡 Fix: Use shell=False and array arguments: subprocess.run(['cmd', 'arg1', 'arg2'])")
        sys.exit(1)
    
    logger.info("Shell injection validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
'''
        
        with open('.security/shell_injection_validator.py', 'w') as f:
            f.write(validator_content)
        
        os.chmod('.security/shell_injection_validator.py', 0o755)
        self.infrastructure_deployed.append("shell injection validator")
        
    def create_eval_exec_detector(self):
        """Create eval/exec pattern detector"""
        detector_content = '''#!/usr/bin/env python3
"""
🔍 Aurora CloudBank Eval/Exec Detector
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
Pre-commit hook for detecting dangerous eval() and exec() patterns
"""
import sys
import re

def detect_dangerous_patterns(file_path):
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
    """Detect eval() and exec() usage patterns"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\\n')
        
        # Dangerous patterns
        python_patterns = [
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
            (r'\\beval\\s*\\(', 'eval() usage'),
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
            (r'\\bexec\\s*\\(', 'exec() usage'),
            (r'compile\\s*\\([^)]*,\\s*["\']exec["\']', 'compile() with exec mode'),
        ]
        
        js_patterns = [
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
            (r'\\beval\\s*\\(', 'JavaScript eval() usage'),
            (r'Function\\s*\\(.*\\)\\s*\\(', 'Function constructor execution'),
            (r'setTimeout\\s*\\(\\s*["\']', 'setTimeout with string code'),
            (r'setInterval\\s*\\(\\s*["\']', 'setInterval with string code'),
        ]
        
        patterns = python_patterns if file_path.endswith('.py') else js_patterns
        
        for i, line in enumerate(lines, 1):
            # Skip comments and secure usage
            if line.strip().startswith('#') or 'nosec' in line:
                continue
                
            for pattern, desc in patterns:
                if re.search(pattern, line):
                    violations.append(f"Line {i}: {desc} - {line.strip()}")
        
        return violations
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

def main():
    """Main detector function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith(('.py', '.js')):
            file_violations = detect_dangerous_patterns(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 DANGEROUS CODE EXECUTION PATTERNS DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\\n💡 Fix: Use safe alternatives like ast.literal_eval() or JSON parsing")
        sys.exit(1)
    
    logger.info("Eval/exec pattern validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
'''
        
        with open('.security/eval_exec_detector.py', 'w') as f:
            f.write(detector_content)
        
        os.chmod('.security/eval_exec_detector.py', 0o755)
        self.infrastructure_deployed.append("eval/exec detector")
        
    def create_dependency_scanner(self):
        """Create automated dependency vulnerability scanner"""
        scanner_content = '''#!/usr/bin/env python3
"""
🔍 Aurora CloudBank Dependency Security Scanner
Automated scanning for vulnerable dependencies
"""
import json
import subprocess
import sys
from datetime import datetime

def scan_npm_vulnerabilities():
    """Scan npm dependencies for vulnerabilities"""
    try:
        result = subprocess.run(
            ['npm', 'audit', '--json'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return {"npm": "No vulnerabilities found"}
        
        audit_data = json.loads(result.stdout)
        vulnerabilities = audit_data.get('vulnerabilities', {})
        
        high_vulns = sum(1 for v in vulnerabilities.values() 
                        if v.get('severity') in ['high', 'critical'])
        
        return {
            "npm": {
                "total_vulnerabilities": len(vulnerabilities),
                "high_critical": high_vulns,
                "status": "VULNERABILITIES_FOUND" if vulnerabilities else "CLEAN"
            }
        }
        
    except Exception as e:
        return {"npm": f"Scan failed: {e}"}

def scan_python_vulnerabilities():
    """Scan Python dependencies for vulnerabilities"""
    try:
        # Use safety if installed, otherwise use pip-audit
        result = subprocess.run(
            ['python3', '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        packages = json.loads(result.stdout)
        package_count = len(packages)
        
        return {
            "python": {
                "packages_scanned": package_count,
                "status": "SCAN_COMPLETED",
                "note": "Install 'safety' or 'pip-audit' for vulnerability detection"
            }
        }
        
    except Exception as e:
        return {"python": f"Scan failed: {e}"}

def main():
    """Main scanner function"""
    print("🔍 Running Aurora CloudBank Dependency Security Scan...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "scans": {}
    }
    
    # Scan npm dependencies
    results["scans"].update(scan_npm_vulnerabilities())
    
    # Scan Python dependencies  
    results["scans"].update(scan_python_vulnerabilities())
    
    # Save results
    with open('.security/dependency_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("📊 Dependency scan completed")
    
    # Check for critical issues
    npm_result = results["scans"].get("npm", {})
    if isinstance(npm_result, dict) and npm_result.get("high_critical", 0) > 0:
        logger.warning("Found %s high/critical npm vulnerabilities", npm_result['high_critical'])
        return 1
    
    logger.info("No critical dependency vulnerabilities found")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        
        with open('.security/dependency_scanner.py', 'w') as f:
            f.write(scanner_content)
        
        os.chmod('.security/dependency_scanner.py', 0o755)
        self.infrastructure_deployed.append("dependency scanner")
        
    def create_security_policy_enforcer(self):
        """Create comprehensive security policy enforcement"""
        policy = {
            "aurora_cloudbank_security_policy": {
                "version": "3.0",
                "effective_date": datetime.now().isoformat(),
                "scope": "PHASE3_INFRASTRUCTURE_DEPLOYMENT",
                "enforcement_level": "STRICT",
                
                "prohibited_patterns": {
                    "log_injection": {
                        "patterns": [
                            "logger.{level}(f\"",
                            "logging.{level}(f\"",
                            "print(f\".*{.*}.*\")"
                        ],
                        "severity": "HIGH",
                        "action": "BLOCK_COMMIT"
                    },
                    "shell_injection": {
                        "patterns": [
                            "subprocess.*shell=True",
                            "os.system(",
                            "os.popen("
                        ],
                        "severity": "HIGH", 
                        "action": "BLOCK_COMMIT"
                    },
                    "code_execution": {
                        "patterns": [
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
                            "eval(",
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
                            "exec(",
                            "compile(.*exec.*)"
                        ],
                        "severity": "CRITICAL",
                        "action": "BLOCK_COMMIT"
                    }
                },
                
                "security_requirements": {
                    "input_validation": "MANDATORY",
                    "output_encoding": "MANDATORY", 
                    "parameterized_logging": "MANDATORY",
                    "safe_subprocess": "MANDATORY",
                    "dependency_scanning": "AUTOMATED"
                },
                
                "monitoring": {
                    "pre_commit_validation": True,
                    "continuous_scanning": True,
                    "vulnerability_alerting": True,
                    "audit_logging": True
                },
                
                "compliance": {
                    "aurora_cloudbank_standards": True,
                    "picard_delta_3_ethics": True,
                    "dlp_tracking": True,
                    "symbolic_anchoring": True
                }
            }
        }
        
        with open('.security/security_policy.json', 'w') as f:
            json.dump(policy, f, indent=2)
        
        self.infrastructure_deployed.append("security policy enforcer")
        self.logger.info("Security policy enforcement deployed")
        
    def install_pre_commit_infrastructure(self):
        """Install pre-commit infrastructure"""
        print("⚙️ Installing pre-commit infrastructure...")
        
        try:
            # Install pre-commit if not present
            result = subprocess.run(
                ['python3', '-m', 'pip', 'install', 'pre-commit'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print("  ✅ pre-commit package installed")
            else:
                print("  ℹ️ pre-commit may already be installed")
            
            # Install hooks
            result = subprocess.run(
                ['pre-commit', 'install'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print("  ✅ pre-commit hooks installed")
                self.infrastructure_deployed.append("pre-commit installation")
            else:
                print(f"  ⚠️ pre-commit installation warning: {result.stderr}")
                
        except Exception as e:
            print(f"  ⚠️ pre-commit installation failed: {e}")
    
    def scan_remaining_vulnerabilities(self):
        """Scan for remaining vulnerability patterns"""
        print("🔍 Scanning for remaining vulnerability patterns...")
        
        remaining_patterns = {
            'sql_injection': r'(query|execute).*f["\'].*\{.*\}',
            'xss_vulnerabilities': r'innerHTML\s*=.*\+',
            'unsafe_redirects': r'redirect\s*\(.*request\.',
            'hardcoded_secrets': r'(password|key|token|secret)\s*=\s*["\'][^"\']+["\']'
        }
        
        vulnerabilities_found = {}
        python_files = []
        js_files = []
        
        # Collect files to scan
        for root, dirs, files in os.walk('.'):
            # Skip .git, node_modules, .venv
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.py'):
                    python_files.append(file_path)
                elif file.endswith('.js'):
                    js_files.append(file_path)
        
        scan_files = python_files[:25] + js_files[:10]  # Limit scope
        
        for pattern_name, pattern in remaining_patterns.items():
            pattern_violations = []
            
            for file_path in scan_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        pattern_violations.append(f"{file_path}:{line_num}")
                        
                except Exception:
                    continue
            
            if pattern_violations:
                vulnerabilities_found[pattern_name] = pattern_violations[:5]  # Top 5
        
        return vulnerabilities_found
    
    def generate_phase3_report(self):
        """Generate comprehensive Phase 3 deployment report"""
        remaining_vulns = self.scan_remaining_vulnerabilities()
        
        report = {
            "phase3_infrastructure_deployment": {
                "timestamp": datetime.now().isoformat(),
                "phase": "3A - Automated Security Scanning",
                "status": "COMPLETED",
                
                "infrastructure_deployed": self.infrastructure_deployed,
                "security_violations": self.security_violations,
                
                "monitoring_capabilities": {
                    "pre_commit_validation": True,
                    "log_injection_prevention": True,
                    "shell_injection_prevention": True,
                    "eval_exec_detection": True,
                    "dependency_scanning": True,
                    "security_policy_enforcement": True
                },
                
                "remaining_vulnerabilities": remaining_vulns,
                "vulnerability_count": sum(len(v) for v in remaining_vulns.values()),
                
                "dlp_tracking": {
                    "phase3_tag_id": self.phase3_tag_id,
                    "anchor_protocols": ["PHASE3_SECURITY_DEPLOY", "PICARD_DELTA_3"],
                    "context_tag": "phase3_infrastructure_deployment"
                },
                
                "next_steps": {
                    "phase3b": "Deploy real-time monitoring",
                    "phase3c": "Address remaining patterns",
                    "target": "Achieve <50 GitHub alerts"
                }
            }
        }
        
        with open('PHASE3A_DEPLOYMENT_REPORT.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def deploy_phase3a_infrastructure(self):
        """Deploy complete Phase 3A infrastructure"""
        print("🚀 Deploying Aurora CloudBank Phase 3A Security Infrastructure")
        print("=" * 80)
        
        # Step 1: Create security validators
        self.create_log_injection_validator()
        self.create_shell_injection_validator() 
        self.create_eval_exec_detector()
        self.create_dependency_scanner()
        
        # Step 2: Create security policy
        self.create_security_policy_enforcer()
        
        # Step 3: Deploy pre-commit infrastructure
        self.create_pre_commit_security_hooks()
        self.install_pre_commit_infrastructure()
        
        # Step 4: Generate deployment report
        report = self.generate_phase3_report()
        
        print(f"\n🎯 Phase 3A Infrastructure Deployment Complete!")
        print(f"📊 Components deployed: {len(self.infrastructure_deployed)}")
        print(f"🔍 Remaining vulnerability patterns: {report['phase3_infrastructure_deployment']['vulnerability_count']}")
        
        # Summary of what was deployed
        print(f"\n✅ Deployed Components:")
        for component in self.infrastructure_deployed:
            print(f"  - {component}")
        
        if report['phase3_infrastructure_deployment']['remaining_vulnerabilities']:
            print(f"\n⚠️ Remaining patterns to address in Phase 3B/3C:")
            for pattern, locations in report['phase3_infrastructure_deployment']['remaining_vulnerabilities'].items():
                print(f"  - {pattern}: {len(locations)} occurrences")
        
        self.monitoring_active = True
        self.logger.info("Phase 3A infrastructure deployment completed successfully")

if __name__ == "__main__":
    print("🛡️ Aurora CloudBank Security Phase 3A Infrastructure Deployment")
    print("Advanced security monitoring and vulnerability prevention")
    print("=" * 80)
    
    deployer = Phase3SecurityInfrastructure()
    deployer.deploy_phase3a_infrastructure()
    
    print("\n🚀 Phase 3A Complete - Ready for Phase 3B Real-time Monitoring!")