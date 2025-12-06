#!/usr/bin/env python3
"""
Aurora CloudBank Onboarding Wizard
Part of T71 Symbolic Infrastructure Genesis

Guides new developers through initial setup and best practices for the
Aurora CloudBank Symbolic platform.

Features:
- Environment health check via make health-check
- Automated setup via make setup
- Makefile command discovery and explanation
- Symbolic anchor tracking demonstrations
- Memory sealing operations
- Quicksave workflow tutorials
- API server and demo launch options

Thread: T71→ONBOARDING→GENESIS
DLP: context_tag=onboarding_wizard, symbolic_hash=DEVELOPER_EXPERIENCE_v1
"""

import sys
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Add workspace root to Python path
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE_ROOT))

logger = logging.getLogger(__name__)


class OnboardingWizard:
    """Interactive onboarding wizard for new Aurora CloudBank developers"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.version = "1.0.0"
        self.has_completed_steps = set()

    def print_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║            🌟 AURORA CLOUDBANK ONBOARDING WIZARD 🌟                   ║
║                                                                       ║
║        Welcome to the Quantum-Symbolic Computing Platform!           ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

👋 Welcome, Developer!

This wizard will guide you through setting up your Aurora CloudBank
development environment and introduce you to the key tools and workflows.

Let's get started! 🚀
"""
        print(banner)

    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Ask user for confirmation"""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"\n{prompt} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")

    def run_command(self, cmd: List[str], description: str, check: bool = True) -> Tuple[bool, str]:
        """Execute a command and return success status and output"""
        try:
            print(f"\n🔧 {description}...")
            print(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if check and result.returncode != 0:
                logger.error("Command failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"Error output:\n{result.stderr[:500]}")
                return False, result.stderr

            logger.info("{description} completed")
            return True, result.stdout

        except subprocess.TimeoutExpired:
            print("⏰ Command timed out after 300 seconds")
            return False, "Timeout"
        except Exception as e:
            logger.error("Error running command: {e}")
            return False, str(e)

    def step_health_check(self):
        """Step 1: Check environment health"""
        print("\n" + "=" * 70)
        print("STEP 1: ENVIRONMENT HEALTH CHECK")
        print("=" * 70)
        print("""
The health check verifies that your development environment is properly
configured. It checks:
  - Python version and dependencies
  - Git configuration
  - Required tools and utilities
  - Repository integrity
""")

        if self.confirm("Would you like to run the health check?"):
            success, output = self.run_command(
                ["make", "health-check"],
                "Running health check",
                check=False
            )

            if success:
                print("\n📊 Health Check Results:")
                print(output[:1000] if len(output) > 1000 else output)
                self.has_completed_steps.add("health_check")
            else:
                print("\n⚠️  Health check encountered issues. Let's try the setup step.")
        else:
            print("⏭️  Skipping health check")

    def step_environment_setup(self):
        """Step 2: Run make setup"""
        print("\n" + "=" * 70)
        print("STEP 2: ENVIRONMENT SETUP")
        print("=" * 70)
        print("""
The setup process will:
  - Install Python dependencies
  - Configure the virtual environment
  - Set up pre-commit hooks
  - Validate the development environment
  - Initialize necessary directories and configurations

This may take a few minutes on first run.
""")

        if self.confirm("Would you like to run the setup process?"):
            success, output = self.run_command(
                ["make", "setup"],
                "Setting up development environment",
                check=False
            )

            if success:
                print("\n✅ Environment setup completed successfully!")
                self.has_completed_steps.add("setup")
            else:
                print("\n⚠️  Setup encountered some issues. You may need to:")
                print("   - Check Python version (3.11+ required)")
                print("   - Ensure you have pip installed")
                print("   - Check for permission issues")
                print("\n   You can run 'make setup' manually later.")
        else:
            print("⏭️  Skipping setup - you can run 'make setup' later")

    def step_makefile_commands(self):
        """Step 3: Show and explain Makefile commands"""
        print("\n" + "=" * 70)
        print("STEP 3: AVAILABLE MAKEFILE COMMANDS")
        print("=" * 70)
        print("""
Aurora CloudBank uses a Makefile to provide convenient commands for
common development tasks. Let's explore what's available.
""")

        if self.confirm("Would you like to see available commands?"):
            success, output = self.run_command(
                ["make", "help"],
                "Fetching available commands",
                check=False
            )

            if success:
                print("\n📚 Available Make Commands:")
                print(output)

                # Explain key commands
                print("\n💡 KEY COMMANDS EXPLAINED:")
                key_commands = {
                    "make setup": "Set up development environment with dependencies",
                    "make health-check": "Quick repository health status check",
                    "make check": "Fast stability check: linting + tests",
                    "make test": "Run the full test suite",
                    "make lint-tools": "Lint modernized tools (matches CI scope)",
                    "make quicksave DESC='...'": "Create a quicksave snapshot of your work",
                    "make quickload": "Load and display current quicksave",
                    "make quicklist": "List all available quicksaves",
                    "make run": "Start the Aurora system",
                    "make security": "Run comprehensive security scans",
                    "make status": "Show environment status"
                }

                for cmd, desc in key_commands.items():
                    print(f"\n  📌 {cmd}")
                    print(f"     {desc}")

                self.has_completed_steps.add("makefile")
            else:
                logger.warning("Could not fetch commands. Try running 'make help' manually.")
        else:
            print("⏭️  Skipping - you can run 'make help' anytime")

    def step_symbolic_anchors(self):
        """Step 4: Demonstrate symbolic anchor tracking"""
        print("\n" + "=" * 70)
        print("STEP 4: SYMBOLIC ANCHOR TRACKING")
        print("=" * 70)
        print("""
Symbolic anchors are key markers in the codebase that track important
references, T-series threads, and DLP (Data Lineage Protocol) tags.

The Aurora Developer CLI helps you:
  - Track anchors across the repository
  - Resolve anchor lineage and relationships
  - Seal anchor threads for memory protection
""")

        if self.confirm("Would you like to see how anchor tracking works?"):
            print("\n🔍 Let's track some anchors in the repository...")

            # Example: track anchors
            success, output = self.run_command(
                ["python", "tools/cli/aurora_dev_cli.py", "anchor", "track", "--pattern", "T71"],
                "Tracking T71 anchors",
                check=False
            )

            if success:
                print("\n📊 Anchor Tracking Results:")
                print(output[:800] if len(output) > 800 else output)

                print("\n💡 Try these commands:")
                print("  python tools/cli/aurora_dev_cli.py anchor track")
                print("  python tools/cli/aurora_dev_cli.py anchor track --pattern T70")
                print("  python tools/cli/aurora_dev_cli.py anchor resolve <anchor_id>")
                print("  python tools/cli/aurora_dev_cli.py status")

                self.has_completed_steps.add("anchors")
            else:
                logger.warning("Anchor tracking demo encountered an issue.")
        else:
            print("⏭️  Skipping anchor tracking demo")

    def step_memory_sealing(self):
        """Step 5: Demonstrate memory sealing"""
        print("\n" + "=" * 70)
        print("STEP 5: MEMORY SEALING")
        print("=" * 70)
        print("""
Memory sealing provides cryptographic verification for files, directories,
and symbolic threads. It's used to:
  - Protect important code snapshots
  - Create verifiable checkpoints
  - Enable state restoration
  - Maintain data integrity
""")

        if self.confirm("Would you like to learn about memory sealing?"):
            print("\n🔐 Memory Sealing Capabilities:")
            print("""
You can seal:
  1. Individual files: python tools/cli/aurora_dev_cli.py seal file.py
  2. Directories: python tools/cli/aurora_dev_cli.py seal path/to/dir
  3. Anchor threads: python tools/cli/aurora_dev_cli.py anchor seal <anchor_id>

To verify a seal:
  python tools/cli/aurora_dev_cli.py seal <target> --verify --seal-id <id>

To restore a sealed state:
  python tools/cli/aurora_dev_cli.py restore <seal_id>
""")

            print("\n💡 Example Usage:")
            print("  # Seal the tools/cli directory")
            print("  python tools/cli/aurora_dev_cli.py seal tools/cli")
            print("\n  # Verify the seal")
            print("  python tools/cli/aurora_dev_cli.py seal tools/cli --verify --seal-id <id>")

            self.has_completed_steps.add("sealing")
        else:
            print("⏭️  Skipping memory sealing tutorial")

    def step_quicksave(self):
        """Step 6: Demonstrate quicksave operations"""
        print("\n" + "=" * 70)
        print("STEP 6: QUICKSAVE WORKFLOW")
        print("=" * 70)
        print("""
Quicksave captures your work context - not just file changes, but also:
  - What you were working on
  - Key breakthroughs and insights
  - Next steps and TODO items
  - Git state and recent activity

Think of it as a save point for your development session!
""")

        if self.confirm("Would you like to explore quicksave features?"):
            print("\n💾 Quicksave Commands:")
            print("""
1. CREATE a quicksave:
   make quicksave DESC="Your description here"

   This captures the current state of your work including:
   - Git status and recent commits
   - Modified files and working tree state
   - Your description and focus areas

2. LIST all quicksaves:
   make quicklist

   Shows all available quicksave snapshots with timestamps

3. LOAD a quicksave:
   make quickload

   Loads the most recent quicksave and displays a reconstitution brief
""")

            if self.confirm("Would you like to see existing quicksaves?"):
                success, output = self.run_command(
                    ["make", "quicklist"],
                    "Listing quicksaves",
                    check=False
                )

                if success:
                    print("\n📋 Available Quicksaves:")
                    print(output)
                    self.has_completed_steps.add("quicksave")
                else:
                    logger.warning("Could not list quicksaves. They may not exist yet.")

            print("\n💡 Tip: Create your first quicksave with:")
            print('   make quicksave DESC="Completed onboarding wizard"')
        else:
            print("⏭️  Skipping quicksave tutorial")

    def step_demos_and_api(self):
        """Step 7: Show demo and API server options"""
        print("\n" + "=" * 70)
        print("STEP 7: DEMOS AND API SERVER")
        print("=" * 70)
        print("""
Aurora CloudBank provides several ways to explore the system:

1. CLI DEMOS - Interactive demonstrations:
   python aurora_cli.py --quantum        # Quantum processing demo
   python aurora_cli.py --consciousness  # Consciousness simulation
   python aurora_cli.py --learning       # Adaptive learning demo
   python aurora_cli.py --status         # System status
   python aurora_cli.py --interactive    # Interactive mode

2. API SERVER - FastAPI backend:
   make run                              # Start the system
   python aurora_api.py                  # Direct API launch

3. WEB DEMO:
   Visit: https://auo959.github.io/aurora-cloudbank-symbolic
   Experience quantum computing, AI, and cultural simulation in real-time!
""")

        if self.confirm("Would you like to see the system status?"):
            success, output = self.run_command(
                ["python", "aurora_cli.py", "--status"],
                "Checking system status",
                check=False
            )

            if success:
                print("\n📊 System Status:")
                print(output)
                self.has_completed_steps.add("demos")
            else:
                logger.warning("Could not fetch status. Some dependencies may need setup.")

        print("\n💡 Try these when ready:")
        print("   python aurora_cli.py --quantum")
        print("   python aurora_api.py  # Then visit http://localhost:8000/docs")

    def step_next_steps(self):
        """Final step: Next steps and resources"""
        print("\n" + "=" * 70)
        print("CONGRATULATIONS! 🎉")
        print("=" * 70)
        print("""
You've completed the Aurora CloudBank onboarding wizard!

Here's what you've learned:
""")

        if "health_check" in self.has_completed_steps:
            print("  ✅ Environment health checking")
        if "setup" in self.has_completed_steps:
            print("  ✅ Development environment setup")
        if "makefile" in self.has_completed_steps:
            print("  ✅ Makefile commands and workflows")
        if "anchors" in self.has_completed_steps:
            print("  ✅ Symbolic anchor tracking")
        if "sealing" in self.has_completed_steps:
            print("  ✅ Memory sealing operations")
        if "quicksave" in self.has_completed_steps:
            print("  ✅ Quicksave workflow")
        if "demos" in self.has_completed_steps:
            print("  ✅ System demos and API")

        print("""
📚 NEXT STEPS:

1. READ THE DOCS:
   - README.md - Main project overview
   - CONTRIBUTING.md - Contribution guidelines
   - docs/ - Detailed documentation

2. EXPLORE THE CODE:
   - src/ - Core source code
   - modules/ - Modular components
   - tools/ - Development tools

3. RUN TESTS:
   - make test - Full test suite
   - pytest -m unit - Fast unit tests
   - pytest -m integration - Integration tests

4. GET INVOLVED:
   - Check open issues on GitHub
   - Join discussions
   - Submit pull requests

5. STAY UPDATED:
   - Star the repository
   - Watch for updates
   - Follow the project roadmap

📖 KEY RESOURCES:
   - Live Demo: https://auo959.github.io/aurora-cloudbank-symbolic
   - Repository: https://github.com/AUo959/aurora-cloudbank-symbolic
   - Health Dashboard: AURORA_HEALTH_OPTIMIZATION_COMPLETE.md
   - Security Policy: .security/SECURITY_POLICY.md

💡 QUICK REFERENCE:
   - make help - List all make commands
   - python tools/cli/aurora_dev_cli.py --help - CLI help
   - python aurora_cli.py --help - System CLI help

🌟 You're now ready to start developing with Aurora CloudBank!

Thank you for joining us on this quantum-symbolic journey! 🚀
""")

    def run(self):
        """Run the complete onboarding wizard"""
        try:
            self.print_banner()

            # Run all steps in sequence
            self.step_health_check()
            self.step_environment_setup()
            self.step_makefile_commands()
            self.step_symbolic_anchors()
            self.step_memory_sealing()
            self.step_quicksave()
            self.step_demos_and_api()
            self.step_next_steps()

            # Save onboarding completion
            self._save_completion_record()

            return 0

        except KeyboardInterrupt:
            print("\n\n⚠️  Onboarding interrupted. You can resume anytime by running:")
            print("   python tools/cli/onboarding_wizard.py")
            return 130
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return 1

    def _save_completion_record(self):
        """Save a record of completed onboarding"""
        try:
            onboarding_dir = self.repo_path / ".aurora" / "onboarding"
            onboarding_dir.mkdir(parents=True, exist_ok=True)

            record = {
                "completed_at": datetime.now().isoformat(),
                "version": self.version,
                "completed_steps": list(self.has_completed_steps),
                "wizard_version": "1.0.0"
            }

            record_file = onboarding_dir / "completion_record.json"
            record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

        except Exception:
            # Non-critical, don't fail if we can't save
            pass


def main():
    """Main entry point for onboarding wizard"""
    wizard = OnboardingWizard()
    return wizard.run()


if __name__ == "__main__":
    sys.exit(main())
