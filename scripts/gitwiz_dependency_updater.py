import subprocess

# !/usr/bin/env python3
"""

    import argparse

GITWiz Dependency Auto-Updater
Comprehensive dependency management and auto-updating system.
"""


import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class DependencyAutoUpdater:
    """Advanced dependency auto-updater for GITWiz."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.backup_branch = f"gitwiz-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def create_safety_backup(self) -> bool:
        """Create safety backup branch."""
        try:
            # Create backup branch
            subprocess.run(
                ["git", "checkout", "-b", self.backup_branch],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )

            # Switch back to main
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )

            print(f"✅ Safety backup created: {self.backup_branch}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create backup: {e}")
            return False

    def scan_python_dependencies(self) -> Dict[str, Any]:
        """Scan Python dependencies for updates."""
        scan_result = {
            "dependencies": [],
            "outdated": [],
            "security_issues": [],
            "scan_successful": False,
        }

        # Check requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                # Use pip list --outdated to check for updates
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "list",
                        "--outdated",
                        "--format=json",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    shell=False,
                    check=False,
                )

                if result.returncode == 0:
                    outdated = json.loads(result.stdout)
                    scan_result["outdated"] = outdated
                    scan_result["scan_successful"] = True

                    print(f"📦 Found {len(outdated)} outdated Python packages")
                    for pkg in outdated[:5]:  # Show first 5
                        print(f"  • {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")

            except (OSError, ValueError, RuntimeError) as e:
                scan_result["error"] = str(e)
                print(f"❌ Python dependency scan failed: {e}")

        return scan_result

    def scan_node_dependencies(self) -> Dict[str, Any]:
        """Scan Node.js dependencies for updates."""
        scan_result = {
            "dependencies": [],
            "outdated": [],
            "security_issues": [],
            "scan_successful": False,
        }

        # Check package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                # Use npm outdated to check for updates
                result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    shell=False,
                    check=False,
                )

                # npm outdated returns non-zero when packages are outdated
                if result.stdout:
                    outdated = json.loads(result.stdout)
                    scan_result["outdated"] = outdated
                    scan_result["scan_successful"] = True

                    print(f"📦 Found {len(outdated)} outdated Node.js packages")
                    for pkg_name, info in list(outdated.items())[:5]:  # Show first 5
                        print(f"  • {pkg_name}: {info['current']} → {info['latest']}")

            except (OSError, ValueError, RuntimeError) as e:
                scan_result["error"] = str(e)
                print(f"❌ Node.js dependency scan failed: {e}")

        return scan_result

    def update_python_dependencies(self, dry_run: bool = True) -> Dict[str, Any]:
        """Update Python dependencies."""
        update_result = {"updated": [], "failed": [], "skipped": [], "success": False}

        if dry_run:
            print("🔍 DRY RUN: Python dependency updates")
            scan_result = self.scan_python_dependencies()
            if scan_result["outdated"]:
                for pkg in scan_result["outdated"]:
                    print(f"  Would update: {pkg['name']} {pkg['version']} → {pkg['latest_version']}")
            update_result["success"] = True
            return update_result

        try:
            # Update all packages
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "-r",
                    "requirements.txt",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                shell=False,
                check=False,
            )

            if result.returncode == 0:
                print("✅ Python dependencies updated successfully")
                update_result["success"] = True
            else:
                print(f"❌ Python dependency update failed: {result.stderr}")

        except (OSError, ValueError, RuntimeError) as e:
            print(f"❌ Python dependency update error: {e}")

        return update_result

    def update_node_dependencies(self, dry_run: bool = True) -> Dict[str, Any]:
        """Update Node.js dependencies."""
        update_result = {"updated": [], "failed": [], "skipped": [], "success": False}

        if dry_run:
            print("🔍 DRY RUN: Node.js dependency updates")
            scan_result = self.scan_node_dependencies()
            if scan_result["outdated"]:
                for pkg_name, info in scan_result["outdated"].items():
                    print(f"  Would update: {pkg_name} {info['current']} → {info['latest']}")
            update_result["success"] = True
            return update_result

        try:
            # Update packages
            result = subprocess.run(
                ["npm", "update"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                shell=False,
                check=False,
            )

            if result.returncode == 0:
                print("✅ Node.js dependencies updated successfully")
                update_result["success"] = True
            else:
                print(f"❌ Node.js dependency update failed: {result.stderr}")

        except (OSError, ValueError, RuntimeError) as e:
            print(f"❌ Node.js dependency update error: {e}")

        return update_result

    def run_security_audit(self) -> Dict[str, Any]:
        """Run security audit on dependencies."""
        audit_result = {
            "python_audit": {},
            "node_audit": {},
            "critical_issues": [],
            "recommendations": [],
        }

        # Python security audit with pip-audit (if available)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pip-audit"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                shell=False,
                check=False,
            )

            if result.returncode == 0:
                audit_cmd = subprocess.run(
                    [sys.executable, "-m", "pip_audit", "--format=json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    shell=False,
                    check=False,
                )

                if audit_cmd.returncode == 0:
                    audit_result["python_audit"] = json.loads(audit_cmd.stdout)
                    print("✅ Python security audit completed")
        except (OSError, ValueError, RuntimeError) as e:
            print(f"ℹ️  Python security audit not available: {e}")

        # Node.js security audit
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    shell=False,
                    check=False,
                )

                if result.stdout:
                    audit_result["node_audit"] = json.loads(result.stdout)
                    print("✅ Node.js security audit completed")

            except (OSError, ValueError, RuntimeError) as e:
                print(f"ℹ️  Node.js security audit failed: {e}")

        return audit_result

    def execute_comprehensive_update(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute comprehensive dependency update workflow."""
        workflow_result = {
            "start_time": datetime.utcnow().isoformat(),
            "backup_created": False,
            "python_scan": {},
            "node_scan": {},
            "security_audit": {},
            "python_update": {},
            "node_update": {},
            "success": False,
            "recommendations": [],
        }

        print("🚀 Starting GITWiz Comprehensive Dependency Update")
        print("=" * 60)

        # Step 1: Create safety backup
        if not dry_run:
            workflow_result["backup_created"] = self.create_safety_backup()
        else:
            print("🔍 DRY RUN: Would create safety backup branch")
            workflow_result["backup_created"] = True

        # Step 2: Scan dependencies
        print("\n📊 Scanning Dependencies...")
        workflow_result["python_scan"] = self.scan_python_dependencies()
        workflow_result["node_scan"] = self.scan_node_dependencies()

        # Step 3: Security audit
        print("\n🔒 Running Security Audit...")
        workflow_result["security_audit"] = self.run_security_audit()

        # Step 4: Update dependencies
        print("\n⬆️  Updating Dependencies...")
        workflow_result["python_update"] = self.update_python_dependencies(dry_run)
        workflow_result["node_update"] = self.update_node_dependencies(dry_run)

        # Step 5: Generate recommendations
        workflow_result["recommendations"] = self._generate_recommendations(workflow_result)

        workflow_result["success"] = (
            workflow_result["python_update"]["success"] and workflow_result["node_update"]["success"]
        )

        workflow_result["end_time"] = datetime.utcnow().isoformat()

        print("\n" + "=" * 60)
        if workflow_result["success"]:
            print("✅ Dependency update workflow completed successfully!")
        else:
            print("⚠️  Dependency update workflow completed with issues")

        return workflow_result

    def _generate_recommendations(self, workflow_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on workflow results."""
        recommendations = []

        # Check for outdated packages
        python_outdated = len(workflow_result["python_scan"].get("outdated", []))
        node_outdated = len(workflow_result["node_scan"].get("outdated", []))

        if python_outdated > 0:
            recommendations.append(f"Update {python_outdated} outdated Python packages")

        if node_outdated > 0:
            recommendations.append(f"Update {node_outdated} outdated Node.js packages")

        # Security recommendations
        if workflow_result["security_audit"].get("critical_issues"):
            recommendations.append("Address critical security vulnerabilities immediately")

        # General recommendations
        recommendations.extend(
            [
                "Schedule regular dependency updates (monthly)",
                "Monitor security advisories for your dependencies",
                "Consider using dependency pinning for production",
                "Run tests after dependency updates",
                "Keep a backup before major updates",
            ]
        )

        return recommendations


def main():
    """Main CLI interface for dependency auto-updater."""

    parser = argparse.ArgumentParser(description="GITWiz Dependency Auto-Updater")
    parser.add_argument("--scan", action="store_true", help="Scan dependencies")
    parser.add_argument("--update", action="store_true", help="Update dependencies")
    parser.add_argument("--security-audit", action="store_true", help="Run security audit")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive workflow")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    args = parser.parse_args()

    updater = DependencyAutoUpdater()

    if args.comprehensive:
        result = updater.execute_comprehensive_update(dry_run=args.dry_run)
        print("\n📊 Workflow Result Summary:")
        print(f"  Python packages scanned: {len(result['python_scan'].get('outdated', []))}")
        print(f"  Node.js packages scanned: {len(result['node_scan'].get('outdated', []))}")
        print(f"  Updates successful: {result['success']}")

    elif args.scan:
        print("📦 Scanning Dependencies...")
        python_result = updater.scan_python_dependencies()
        node_result = updater.scan_node_dependencies()

    elif args.update:
        print("⬆️  Updating Dependencies...")
        python_result = updater.update_python_dependencies(dry_run=args.dry_run)
        node_result = updater.update_node_dependencies(dry_run=args.dry_run)

    elif args.security_audit:
        print("🔒 Running Security Audit...")
        updater.run_security_audit()

    else:
        parser.print_help()
        print("\n🚀 GITWiz Dependency Auto-Updater")
        print("Usage examples:")
        print("  python3 gitwiz_dependency_updater.py --scan")
        print("  python3 gitwiz_dependency_updater.py --comprehensive --dry-run")
        print("  python3 gitwiz_dependency_updater.py --update --dry-run")


if __name__ == "__main__":
    main()
