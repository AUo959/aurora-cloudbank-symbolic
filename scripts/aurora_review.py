#!/usr/bin/env python3
"""
Senior Officer Review Protocol - CLI Tool
==========================================

Quick activation tool for Aurora CloudBank's Senior Officer Review Protocol.
Enables rapid, multi-stakeholder code review with coordinated officer personas.

Usage:
    aurora-review --pr 123              # Review PR #123
    aurora-review --quick               # Fast track review (30 min)
    aurora-review --thorough            # Deep dive review (4 hours)
    aurora-review --officers "CSO,CTO"  # Limited officer set
    aurora-review --help                # Show help

"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class SeniorOfficerReview:
    """Orchestrates the Senior Officer Review Protocol"""

    OFFICERS = {
        "CMD": {
            "name": "Commander Alex Thorne",
            "role": "Station Commander",
            "code": "CMD_001",
            "expertise": "Strategic decision making, mission planning, risk assessment"
        },
        "CSO": {
            "name": "CSO Commander Aria Chen",
            "role": "Security Director",
            "code": "SEC_001",
            "expertise": "Security vulnerabilities, CVE analysis, threat modeling"
        },
        "CTO": {
            "name": "CTO Dr. Marcus Webb",
            "role": "Technical Director",
            "code": "ENG_001",
            "expertise": "Architecture, scalability, performance, testing"
        },
        "OPS": {
            "name": "OPS Captain Sarah Rodriguez",
            "role": "Operations Director",
            "code": "OPS_001",
            "expertise": "Production operations, monitoring, incident response"
        },
        "CO": {
            "name": "CO Director James Park",
            "role": "Compliance Director",
            "code": "COM_001",
            "expertise": "Policy compliance, audit trails, governance"
        }
    }

    def __init__(self, args):
        self.args = args
        self.workspace = Path.cwd()
        self.start_time = datetime.now()

    def get_git_info(self):
        """Get current git context"""
        try:
            branch = subprocess.check_output(
                ["git", "branch", "--show-current"],
                text=True
            ).strip()

            # Get PR number from branch name if not provided
            if not self.args.pr and "pr" in branch.lower():
                # Extract number from branch name (e.g., pr-123 or PR/123)
                import re
                match = re.search(r'pr[-/]?(\d+)', branch, re.IGNORECASE)
                if match:
                    self.args.pr = match.group(1)

            return {
                "branch": branch,
                "pr_number": self.args.pr,
                "repo": subprocess.check_output(
                    ["git", "config", "--get", "remote.origin.url"],
                    text=True
                ).strip()
            }
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not get git info: {e}")
            return {"branch": "unknown", "pr_number": self.args.pr}

    def print_banner(self):
        """Print protocol activation banner"""
        print("=" * 70)
        print("🎖️  SENIOR OFFICER REVIEW PROTOCOL ACTIVATED")
        print("=" * 70)
        print()
        print(f"📅 Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        git_info = self.get_git_info()
        if git_info.get('pr_number'):
            print(f"📋 PR: #{git_info['pr_number']}")
        print(f"🌿 Branch: {git_info.get('branch', 'unknown')}")
        print(f"⏱️  Mode: {self.get_mode_description()}")
        print()

    def get_mode_description(self):
        """Get review mode description"""
        if self.args.quick:
            return "⚡ FAST TRACK (30 minutes)"
        elif self.args.thorough:
            return "🔬 THOROUGH REVIEW (4 hours)"
        else:
            return "📊 STANDARD REVIEW (90 minutes)"

    def get_active_officers(self):
        """Determine which officers are active for this review"""
        if self.args.officers:
            officer_codes = [o.strip().upper() for o in self.args.officers.split(",")]
            return {code: self.OFFICERS[code] for code in officer_codes if code in self.OFFICERS}
        else:
            # Default: all officers
            return self.OFFICERS

    def print_officer_roster(self):
        """Print active officer roster"""
        officers = self.get_active_officers()

        print("👥 OFFICER ROSTER")
        print("-" * 70)
        for code, officer in officers.items():
            print(f"  [{code}] {officer['name']} - {officer['role']}")
            print(f"       {officer['expertise']}")
            print()

    def run_security_scan(self):
        """Run security scan if available"""
        print("🔒 Running security scan...")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-m", "security", "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("✅ Security tests passing")
            else:
                print("⚠️  Security test failures detected")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Could not run security scan: {e}")
            return None

    def run_quick_tests(self):
        """Run quick test suite"""
        print("🧪 Running quick test suite...")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-x", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("✅ Tests passing")
            else:
                print("⚠️  Test failures detected")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Could not run tests: {e}")
            return None

    def generate_briefing(self):
        """Generate officer briefing document"""
        print("📄 Generating officer briefing...")

        git_info = self.get_git_info()
        briefing_path = self.workspace / "docs" / f"HANDOFF_SENIOR_OFFICERS_PR{git_info.get('pr_number', 'CURRENT')}.md"

        # Get recent commits
        try:
            commits = subprocess.check_output(
                ["git", "log", "--oneline", "-10"],
                text=True
            ).strip()
        except subprocess.CalledProcessError:
            commits = "Unable to retrieve commit history"

        # Get changed files
        try:
            files = subprocess.check_output(
                ["git", "diff", "--name-only", "main...HEAD"],
                text=True
            ).strip().split('\n')
        except subprocess.CalledProcessError:
            files = []

        briefing_content = f"""# Senior Officer Briefing - PR #{git_info.get('pr_number', 'CURRENT')}

**Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Branch:** {git_info.get('branch', 'unknown')}
**Review Mode:** {self.get_mode_description()}

---

## 📋 PR Context

**Repository:** {git_info.get('repo', 'unknown')}
**Files Changed:** {len(files)}
**Recent Commits:** {len(commits.split('\\n'))}

## 📝 Recent Commits

```
{commits}
```

## 📂 Changed Files

{chr(10).join('- ' + f for f in files if f)}

---

## 👥 Officer Assignments

Please review this PR from your respective areas of expertise:

{self._generate_officer_assignments()}

---

## ✅ Review Checklist

- [ ] **CSO Chen:** Security vulnerabilities identified and assessed
- [ ] **CTO Webb:** Technical architecture reviewed and validated
- [ ] **OPS Rodriguez:** Operational readiness confirmed
- [ ] **CO Park:** Compliance requirements verified
- [ ] **Commander Thorne:** Strategic synthesis completed

---

**Protocol:** Senior Officer Review Protocol v1.0
**Generated:** {self.start_time.isoformat()}
"""

        briefing_path.parent.mkdir(parents=True, exist_ok=True)
        briefing_path.write_text(briefing_content)
        print(f"✅ Briefing generated: {briefing_path}")
        return briefing_path

    def _generate_officer_assignments(self):
        """Generate officer assignment section"""
        officers = self.get_active_officers()
        assignments = []

        for code, officer in officers.items():
            assignments.append(f"### [{code}] {officer['name']} - {officer['role']}")
            assignments.append(f"**Focus Areas:** {officer['expertise']}")
            assignments.append("")

        return "\n".join(assignments)

    def activate_protocol(self):
        """Main protocol activation sequence"""
        self.print_banner()
        self.print_officer_roster()

        print("=" * 70)
        print("PHASE 1: ACTIVATION & SETUP")
        print("=" * 70)
        print()

        # Run checks
        self.run_security_scan()
        self.run_quick_tests()

        # Generate briefing
        briefing_path = self.generate_briefing()

        print()
        print("=" * 70)
        print("✅ PROTOCOL ACTIVATED")
        print("=" * 70)
        print()
        print("📋 Next Steps:")
        print()
        print("1. Review officer briefing:")
        print(f"   cat {briefing_path}")
        print()
        print("2. Officers will provide individual assessments")
        print("   (Use GitHub Copilot chat or interactive mode)")
        print()
        print("3. Commander Thorne will synthesize into strategic framework")
        print()
        print("4. Execute sprint if needed to resolve blocking issues")
        print()
        print("5. Merge when all officers approve")
        print()
        print("🎯 To continue in chat:")
        print('   Say: "Senior officers, please review this PR"')
        print()
        print("📚 Protocol Documentation:")
        print("   docs/SENIOR_OFFICER_REVIEW_PROTOCOL.md")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Aurora CloudBank Senior Officer Review Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aurora-review --pr 123              Review PR #123 with all officers
  aurora-review --quick               Fast 30-minute review
  aurora-review --thorough            Deep 4-hour review
  aurora-review --officers "CSO,CTO"  Limited officer set

For full documentation, see: docs/SENIOR_OFFICER_REVIEW_PROTOCOL.md
        """
    )

    parser.add_argument(
        "--pr",
        type=str,
        help="PR number to review"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Fast track review (30 minutes)"
    )

    parser.add_argument(
        "--thorough",
        action="store_true",
        help="Thorough review (4 hours)"
    )

    parser.add_argument(
        "--officers",
        type=str,
        help="Comma-separated officer codes (e.g., 'CSO,CTO,OPS')"
    )

    args = parser.parse_args()

    # Validate officers if specified
    if args.officers:
        officer_codes = [o.strip().upper() for o in args.officers.split(",")]
        valid_codes = set(SeniorOfficerReview.OFFICERS.keys())
        invalid = [code for code in officer_codes if code not in valid_codes]
        if invalid:
            print(f"❌ Invalid officer codes: {', '.join(invalid)}")
            print(f"   Valid codes: {', '.join(valid_codes)}")
            return 1

    # Create and run review
    review = SeniorOfficerReview(args)
    review.activate_protocol()

    return 0


if __name__ == "__main__":
    sys.exit(main())
