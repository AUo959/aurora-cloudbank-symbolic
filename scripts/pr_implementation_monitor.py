#!/usr/bin/env python3

"""
Aurora CloudBank - PR Implementation Monitor
Real-time monitoring and validation for PR integration phases
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class PRImplementationMonitor:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.start_time = datetime.now()
        
    def get_git_status(self) -> Dict:
        """Get comprehensive git repository status"""
        try:
            # Current branch
            current_branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_root,
                text=True
            ).strip()
            
            # Current commit
            current_commit = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.repo_root,
                text=True
            ).strip()
            
            # Get branch info
            branches_output = subprocess.check_output(
                ['git', 'branch', '-r'],
                cwd=self.repo_root,
                text=True
            )
            
            remote_branches = []
            for line in branches_output.strip().split('\n'):
                branch = line.strip()
                if branch and not branch.startswith('origin/HEAD'):
                    remote_branches.append(branch.replace('origin/', ''))
            
            # Check for uncommitted changes
            status_output = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_root,
                text=True
            )
            
            has_changes = bool(status_output.strip())
            
            return {
                'current_branch': current_branch,
                'current_commit': current_commit,
                'remote_branches': len(remote_branches),
                'has_uncommitted_changes': has_changes,
                'status': 'clean' if not has_changes else 'modified'
            }
            
        except subprocess.CalledProcessError as e:
            return {'error': f'Git command failed: {e}'}
    
    def validate_workflows(self) -> Dict:
        """Validate all GitHub Actions workflows"""
        workflow_dir = self.repo_root / '.github' / 'workflows'
        
        if not workflow_dir.exists():
            return {'error': 'No workflows directory found'}
        
        workflow_files = list(workflow_dir.glob('*.yml'))
        valid_count = 0
        invalid_files = []
        
        for workflow_file in workflow_files:
            try:
                import yaml
                with open(workflow_file) as f:
                    yaml.safe_load(f)
                valid_count += 1
            except Exception as e:
                invalid_files.append({
                    'file': workflow_file.name,
                    'error': str(e)
                })
        
        return {
            'total_workflows': len(workflow_files),
            'valid_workflows': valid_count,
            'invalid_workflows': len(invalid_files),
            'invalid_files': invalid_files,
            'status': 'healthy' if len(invalid_files) == 0 else 'issues'
        }
    
    def run_test_suite(self) -> Dict:
        """Run the test suite and return results"""
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            # Parse pytest output for test counts
            output_lines = result.stdout.split('\n')
            test_summary = None
            
            for line in reversed(output_lines):
                if 'passed' in line or 'failed' in line or 'error' in line:
                    test_summary = line.strip()
                    break
            
            return {
                'exit_code': result.returncode,
                'execution_time': round(execution_time, 2),
                'summary': test_summary,
                'status': 'passed' if result.returncode == 0 else 'failed',
                'output_length': len(result.stdout) + len(result.stderr)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'error': 'Test suite timed out after 5 minutes',
                'status': 'timeout'
            }
        except Exception as e:
            return {
                'error': f'Test execution failed: {e}',
                'status': 'error'
            }
    
    def check_core_imports(self) -> Dict:
        """Validate core system imports"""
        core_modules = [
            'aurora_api',
            'src.aurora.core.symbolic_engine',
            'modules.symbolic_core.geometric_algebra',
            'src.core.native_dlp_export'
        ]
        
        import_results = {}
        
        for module in core_modules:
            try:
                __import__(module)
                import_results[module] = 'success'
            except ImportError as e:
                import_results[module] = f'import_error: {e}'
            except Exception as e:
                import_results[module] = f'error: {e}'
        
        successful_imports = sum(1 for status in import_results.values() if status == 'success')
        
        return {
            'total_modules': len(core_modules),
            'successful_imports': successful_imports,
            'import_results': import_results,
            'status': 'healthy' if successful_imports == len(core_modules) else 'partial'
        }
    
    def analyze_pr_branches(self) -> Dict:
        """Analyze PR branches and categorize them"""
        try:
            # Get all remote branches
            branches_output = subprocess.check_output(
                ['git', 'branch', '-r'],
                cwd=self.repo_root,
                text=True
            )
            
            branches = []
            for line in branches_output.strip().split('\n'):
                branch = line.strip()
                if branch and not branch.startswith('origin/HEAD'):
                    clean_branch = branch.replace('origin/', '')
                    branches.append(clean_branch)
            
            # Categorize branches
            categories = {
                'copilot_fixes': [],
                'ai_generation': [],
                'dependency_updates': [],
                'feature_branches': [],
                'fix_branches': [],
                'other': []
            }
            
            for branch in branches:
                if branch == 'main':
                    continue
                    
                if branch.startswith('copilot/'):
                    categories['copilot_fixes'].append(branch)
                elif branch.startswith('ai/') or 'generation' in branch:
                    categories['ai_generation'].append(branch)
                elif 'dependabot' in branch or 'dependency' in branch or 'deps' in branch:
                    categories['dependency_updates'].append(branch)
                elif branch.startswith('feature/'):
                    categories['feature_branches'].append(branch)
                elif branch.startswith('fix/'):
                    categories['fix_branches'].append(branch)
                else:
                    categories['other'].append(branch)
            
            total_branches = len(branches) - 1  # Exclude main
            
            return {
                'total_branches': total_branches,
                'categories': categories,
                'category_counts': {k: len(v) for k, v in categories.items()},
                'status': 'analyzed'
            }
            
        except subprocess.CalledProcessError as e:
            return {'error': f'Branch analysis failed: {e}'}
    
    def get_system_health_score(self, git_status: Dict, workflow_status: Dict, 
                               test_status: Dict, import_status: Dict) -> float:
        """Calculate overall system health score"""
        score = 0.0
        max_score = 100.0
        
        # Git status (20 points)
        if git_status.get('status') == 'clean':
            score += 20
        elif git_status.get('status') == 'modified':
            score += 10
        
        # Workflow status (25 points)
        if workflow_status.get('status') == 'healthy':
            score += 25
        elif workflow_status.get('invalid_workflows', 0) < 2:
            score += 15
        
        # Test status (35 points)
        if test_status.get('status') == 'passed':
            score += 35
        elif test_status.get('status') == 'failed':
            score += 10  # Some credit for running
        
        # Import status (20 points)
        if import_status.get('status') == 'healthy':
            score += 20
        elif import_status.get('status') == 'partial':
            ratio = import_status.get('successful_imports', 0) / import_status.get('total_modules', 1)
            score += 20 * ratio
        
        return min(score, max_score)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive system status report"""
        print("🔍 Aurora CloudBank - System Health Monitor")
        print("=" * 50)
        print(f"Scan started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        report = {
            'timestamp': self.start_time.isoformat(),
            'scan_duration': 0
        }
        
        # Git status
        print("📊 Git Repository Status")
        print("-" * 25)
        git_status = self.get_git_status()
        report['git_status'] = git_status
        
        if 'error' not in git_status:
            print(f"Current branch: {git_status['current_branch']}")
            print(f"Current commit: {git_status['current_commit']}")
            print(f"Remote branches: {git_status['remote_branches']}")
            print(f"Status: {git_status['status']}")
        else:
            print(f"❌ Error: {git_status['error']}")
        print()
        
        # Workflow validation
        print("⚙️ GitHub Actions Workflows")
        print("-" * 28)
        workflow_status = self.validate_workflows()
        report['workflow_status'] = workflow_status
        
        if 'error' not in workflow_status:
            print(f"Total workflows: {workflow_status['total_workflows']}")
            print(f"Valid workflows: {workflow_status['valid_workflows']}")
            print(f"Status: {workflow_status['status']}")
            if workflow_status['invalid_files']:
                print("❌ Invalid files:")
                for invalid in workflow_status['invalid_files']:
                    print(f"  • {invalid['file']}: {invalid['error']}")
        else:
            print(f"❌ Error: {workflow_status['error']}")
        print()
        
        # Test suite
        print("🧪 Test Suite Validation")
        print("-" * 24)
        test_status = self.run_test_suite()
        report['test_status'] = test_status
        
        if 'error' not in test_status:
            print(f"Status: {test_status['status']}")
            print(f"Execution time: {test_status['execution_time']}s")
            if test_status.get('summary'):
                print(f"Summary: {test_status['summary']}")
        else:
            print(f"❌ Error: {test_status['error']}")
        print()
        
        # Core imports
        print("🔧 Core System Imports")
        print("-" * 22)
        import_status = self.check_core_imports()
        report['import_status'] = import_status
        
        print(f"Successful imports: {import_status['successful_imports']}/{import_status['total_modules']}")
        print(f"Status: {import_status['status']}")
        for module, status in import_status['import_results'].items():
            status_icon = "✅" if status == "success" else "❌"
            print(f"  {status_icon} {module}")
        print()
        
        # PR branch analysis
        print("🌿 PR Branch Analysis")
        print("-" * 21)
        branch_analysis = self.analyze_pr_branches()
        report['branch_analysis'] = branch_analysis
        
        if 'error' not in branch_analysis:
            print(f"Total branches: {branch_analysis['total_branches']}")
            for category, count in branch_analysis['category_counts'].items():
                if count > 0:
                    print(f"  • {category.replace('_', ' ').title()}: {count}")
        else:
            print(f"❌ Error: {branch_analysis['error']}")
        print()
        
        # Calculate health score
        health_score = self.get_system_health_score(
            git_status, workflow_status, test_status, import_status
        )
        report['health_score'] = health_score
        
        # Summary
        scan_duration = (datetime.now() - self.start_time).total_seconds()
        report['scan_duration'] = scan_duration
        
        print("📋 System Health Summary")
        print("-" * 24)
        print(f"Overall Health Score: {health_score:.1f}/100.0")
        print(f"Scan Duration: {scan_duration:.2f}s")
        
        if health_score >= 90:
            print("🎉 System Status: EXCELLENT - Ready for PR integration")
        elif health_score >= 75:
            print("✅ System Status: GOOD - Minor issues, safe to proceed")
        elif health_score >= 60:
            print("⚠️ System Status: FAIR - Review issues before proceeding")
        else:
            print("❌ System Status: POOR - Address critical issues first")
        
        return report

def main():
    """Main entry point"""
    monitor = PRImplementationMonitor()
    
    try:
        report = monitor.generate_report()
        
        # Save report to file
        report_file = Path('SYSTEM_HEALTH_REPORT.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
        
        # Return appropriate exit code
        health_score = report.get('health_score', 0)
        if health_score >= 75:
            sys.exit(0)  # Success
        elif health_score >= 60:
            sys.exit(1)  # Warning
        else:
            sys.exit(2)  # Critical issues
            
    except KeyboardInterrupt:
        print("\n⚠️ Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Monitor failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()