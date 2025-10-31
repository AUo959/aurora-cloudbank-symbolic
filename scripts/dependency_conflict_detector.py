#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Conflict Detector
R-2 Agent Tool for Automated Dependency & Compatibility Sweeps

Detects and reports version conflicts, compatibility issues, and provides
automated resolution suggestions for Python dependencies.

Addresses Issue #243: Cross-repo dependency mapping (Phase 1 - Single Repo)
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from urllib import request
import urllib.error


@dataclass
class DependencyConflict:
    """Represents a detected dependency conflict"""
    package_name: str
    required_version: str
    conflicting_package: str
    conflicting_requirement: str
    severity: str  # "critical", "high", "medium", "low"
    suggested_fix: Optional[str] = None
    pypi_latest: Optional[str] = None


@dataclass
class DependencyReport:
    """Complete dependency analysis report"""
    timestamp: str
    conflicts: List[DependencyConflict]
    total_packages: int
    conflict_count: int
    resolution_suggestions: List[str]
    health_status: str  # "healthy", "warning", "critical"


class DependencyConflictDetector:
    """Main dependency conflict detection and analysis engine"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.requirements_files = {
            'lock': self.project_root / 'requirements-lock.txt',
            'main': self.project_root / 'requirements.txt',
            'dev': self.project_root / 'requirements-dev.txt',
            'test': self.project_root / 'requirements-test.txt',
        }
        
    def parse_requirements_file(self, filepath: Path) -> Dict[str, str]:
        """Parse requirements file and extract package versions"""
        if not filepath.exists():
            return {}
            
        packages = {}
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Handle package==version format
                match = re.match(r'([a-zA-Z0-9_-]+)==([0-9.]+(?:[a-z0-9._-]*)?)', line)
                if match:
                    packages[match.group(1).lower()] = match.group(2)
                    
        return packages
        
    def get_pypi_package_info(self, package_name: str, version: str = None) -> Optional[Dict]:
        """Fetch package info from PyPI API"""
        try:
            if version:
                url = f'https://pypi.org/pypi/{package_name}/{version}/json'
            else:
                url = f'https://pypi.org/pypi/{package_name}/json'
                
            with request.urlopen(url, timeout=5) as response:
                return json.loads(response.read())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            return None
            
    def parse_version_spec(self, spec: str) -> Tuple[str, str, str]:
        """Parse version specification like 'starlette<0.49.0,>=0.40.0'"""
        # Extract package name and constraints
        match = re.match(r'([a-zA-Z0-9_-]+)(.*)', spec)
        if not match:
            return spec, '', ''
            
        package = match.group(1)
        constraints = match.group(2).strip()
        
        # Parse version constraints
        upper_bound = None
        lower_bound = None
        
        # Extract upper bound (< or <=)
        upper_match = re.search(r'<\s*([0-9.]+)', constraints)
        if upper_match:
            upper_bound = upper_match.group(1)
            
        # Extract lower bound (> or >=)
        lower_match = re.search(r'>=\s*([0-9.]+)', constraints)
        if lower_match:
            lower_bound = lower_match.group(1)
            
        return package, lower_bound or '', upper_bound or ''
        
    def check_version_compatibility(self, version: str, lower: str, upper: str) -> bool:
        """Check if version is within bounds"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')[:3]))
            
        try:
            ver = version_tuple(version)
            
            if lower:
                if ver < version_tuple(lower):
                    return False
                    
            if upper:
                if ver >= version_tuple(upper):
                    return False
                    
            return True
        except (ValueError, AttributeError):
            return True  # If we can't parse, assume compatible
            
    def detect_conflicts(self) -> List[DependencyConflict]:
        """Detect all dependency conflicts in requirements files"""
        conflicts = []
        
        # Load all requirements
        lock_packages = self.parse_requirements_file(self.requirements_files['lock'])
        
        # Check known critical conflicts
        critical_checks = [
            {
                'package': 'fastapi',
                'version_in_lock': lock_packages.get('fastapi'),
                'requires': 'starlette',
                'constraint': '<0.49.0,>=0.40.0',
                'current_in_lock': lock_packages.get('starlette'),
            },
            {
                'package': 'httpx',
                'version_in_lock': lock_packages.get('httpx'),
                'requires': 'httpcore',
                'constraint': '>=1.0.0',
                'current_in_lock': lock_packages.get('httpcore'),
            },
        ]
        
        for check in critical_checks:
            if not check['version_in_lock']:
                continue
                
            # Get the actual requirements for this package version
            pkg_info = self.get_pypi_package_info(check['package'], check['version_in_lock'])
            
            if pkg_info and 'info' in pkg_info:
                requires_dist = pkg_info['info'].get('requires_dist', [])
                
                # Find the specific dependency requirement
                for req in requires_dist:
                    if check['requires'] in req.lower():
                        pkg_name, lower, upper = self.parse_version_spec(req)
                        current_ver = check['current_in_lock']
                        
                        if current_ver:
                            is_compatible = self.check_version_compatibility(
                                current_ver, lower, upper
                            )
                            
                            if not is_compatible:
                                # Get latest compatible version
                                latest_info = self.get_pypi_package_info(check['requires'])
                                latest = latest_info['info']['version'] if latest_info else None
                                
                                # Determine suggested fix
                                if upper and current_ver:
                                    suggested = self._find_compatible_version(
                                        check['requires'], lower, upper
                                    )
                                else:
                                    suggested = None
                                    
                                conflict = DependencyConflict(
                                    package_name=check['requires'],
                                    required_version=current_ver,
                                    conflicting_package=check['package'],
                                    conflicting_requirement=f"{lower or ''}..{upper or ''}",
                                    severity="critical",
                                    suggested_fix=suggested,
                                    pypi_latest=latest
                                )
                                conflicts.append(conflict)
                                
        return conflicts
        
    def _find_compatible_version(self, package: str, lower: str, upper: str) -> Optional[str]:
        """Find the highest compatible version within constraints"""
        pkg_info = self.get_pypi_package_info(package)
        if not pkg_info or 'releases' not in pkg_info:
            return None
            
        # Get all releases
        releases = list(pkg_info['releases'].keys())
        
        # Filter to only versions with files (released versions)
        valid_releases = [
            v for v in releases 
            if pkg_info['releases'][v] and any(
                r['packagetype'] in ['bdist_wheel', 'sdist'] 
                for r in pkg_info['releases'][v]
            )
        ]
        
        # Filter by compatibility
        compatible = [
            v for v in valid_releases
            if self.check_version_compatibility(v, lower, upper)
        ]
        
        if not compatible:
            return None
            
        # Return the highest compatible version
        try:
            return sorted(compatible, key=lambda v: tuple(map(int, v.split('.')[:3])))[-1]
        except (ValueError, IndexError):
            return compatible[-1] if compatible else None
            
    def generate_report(self) -> DependencyReport:
        """Generate comprehensive dependency conflict report"""
        conflicts = self.detect_conflicts()
        
        # Count packages
        lock_packages = self.parse_requirements_file(self.requirements_files['lock'])
        total_packages = len(lock_packages)
        
        # Generate resolution suggestions
        suggestions = []
        for conflict in conflicts:
            if conflict.suggested_fix:
                suggestions.append(
                    f"Update {conflict.package_name} from {conflict.required_version} "
                    f"to {conflict.suggested_fix} (required by {conflict.conflicting_package})"
                )
            else:
                suggestions.append(
                    f"Review {conflict.package_name} version {conflict.required_version} "
                    f"- conflicts with {conflict.conflicting_package} requirements"
                )
                
        # Determine health status
        critical_conflicts = [c for c in conflicts if c.severity == "critical"]
        if len(critical_conflicts) > 0:
            health = "critical"
        elif len(conflicts) > 0:
            health = "warning"
        else:
            health = "healthy"
            
        return DependencyReport(
            timestamp=datetime.now().isoformat(),
            conflicts=conflicts,
            total_packages=total_packages,
            conflict_count=len(conflicts),
            resolution_suggestions=suggestions,
            health_status=health
        )
        
    def apply_automatic_fixes(self, dry_run: bool = True) -> List[str]:
        """Apply automatic fixes for detected conflicts"""
        conflicts = self.detect_conflicts()
        applied_fixes = []
        
        lock_file = self.requirements_files['lock']
        if not lock_file.exists():
            return applied_fixes
            
        # Read current content
        with open(lock_file, 'r') as f:
            content = f.read()
            
        original_content = content
        
        # Apply fixes
        for conflict in conflicts:
            if conflict.suggested_fix:
                old_line = f"{conflict.package_name}=={conflict.required_version}"
                new_line = f"{conflict.package_name}=={conflict.suggested_fix}"
                
                if old_line in content:
                    content = content.replace(old_line, new_line)
                    applied_fixes.append(
                        f"Updated {conflict.package_name}: "
                        f"{conflict.required_version} -> {conflict.suggested_fix}"
                    )
                    
        # Write back if changes were made and not dry-run
        if content != original_content and not dry_run:
            # Backup original
            backup_dir = self.project_root / '.backup' / 'requirements'
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f'requirements-lock.txt.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            
            with open(backup_file, 'w') as f:
                f.write(original_content)
                
            with open(lock_file, 'w') as f:
                f.write(content)
                
            applied_fixes.append(f"Backup created: {backup_file}")
            
        return applied_fixes
        
    def export_report(self, report: DependencyReport, output_file: Path = None):
        """Export report to JSON file"""
        if output_file is None:
            output_file = self.project_root / '.backup' / 'requirements' / \
                         f'dependency_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                         
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict
        report_dict = {
            'timestamp': report.timestamp,
            'conflicts': [asdict(c) for c in report.conflicts],
            'total_packages': report.total_packages,
            'conflict_count': report.conflict_count,
            'resolution_suggestions': report.resolution_suggestions,
            'health_status': report.health_status
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
            
        return output_file


def print_report(report: DependencyReport):
    """Pretty print dependency report"""
    status_emoji = {
        'healthy': '🟢',
        'warning': '🟡',
        'critical': '🔴'
    }
    
    print("\n" + "="*70)
    print("🔍 Aurora CloudBank Dependency Conflict Report")
    print("="*70)
    print(f"\nGenerated: {report.timestamp}")
    print(f"Status: {status_emoji[report.health_status]} {report.health_status.upper()}")
    print(f"\nTotal Packages: {report.total_packages}")
    print(f"Conflicts Detected: {report.conflict_count}")
    
    if report.conflicts:
        print("\n" + "-"*70)
        print("DETECTED CONFLICTS:")
        print("-"*70)
        
        for i, conflict in enumerate(report.conflicts, 1):
            print(f"\n{i}. {conflict.package_name}")
            print(f"   Current Version: {conflict.required_version}")
            print(f"   Conflicting With: {conflict.conflicting_package}")
            print(f"   Required Range: {conflict.conflicting_requirement}")
            print(f"   Severity: {conflict.severity.upper()}")
            
            if conflict.suggested_fix:
                print(f"   ✅ Suggested Fix: {conflict.suggested_fix}")
            if conflict.pypi_latest:
                print(f"   📦 Latest on PyPI: {conflict.pypi_latest}")
                
    if report.resolution_suggestions:
        print("\n" + "-"*70)
        print("RESOLUTION SUGGESTIONS:")
        print("-"*70)
        for i, suggestion in enumerate(report.resolution_suggestions, 1):
            print(f"{i}. {suggestion}")
            
    print("\n" + "="*70 + "\n")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Aurora Dependency Conflict Detector - R-2 Agent Tool'
    )
    parser.add_argument(
        '--scan', action='store_true',
        help='Scan for dependency conflicts'
    )
    parser.add_argument(
        '--fix', action='store_true',
        help='Apply automatic fixes (requires --apply)'
    )
    parser.add_argument(
        '--apply', action='store_true',
        help='Actually apply fixes (default is dry-run)'
    )
    parser.add_argument(
        '--export', type=str,
        help='Export report to JSON file'
    )
    parser.add_argument(
        '--project-root', type=str,
        help='Project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    
    # Create detector
    detector = DependencyConflictDetector(project_root)
    
    # Generate report
    report = detector.generate_report()
    
    # Print report
    print_report(report)
    
    # Export if requested
    if args.export:
        output_file = detector.export_report(report, Path(args.export))
        print(f"📄 Report exported to: {output_file}")
    else:
        output_file = detector.export_report(report)
        print(f"📄 Report auto-saved to: {output_file}")
        
    # Apply fixes if requested
    if args.fix:
        print("\n" + "="*70)
        print("🔧 APPLYING AUTOMATIC FIXES")
        print("="*70 + "\n")
        
        dry_run = not args.apply
        if dry_run:
            print("⚠️  DRY RUN MODE - No changes will be applied")
            print("   Use --fix --apply to actually apply changes\n")
            
        fixes = detector.apply_automatic_fixes(dry_run=dry_run)
        
        if fixes:
            print("Applied Fixes:")
            for fix in fixes:
                print(f"  ✅ {fix}")
        else:
            print("  ℹ️  No automatic fixes available")
            
        print()
        
    # Exit with appropriate code
    sys.exit(0 if report.health_status != 'critical' else 1)


if __name__ == '__main__':
    main()
