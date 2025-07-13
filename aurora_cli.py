#!/usr/bin/env python3
"""
⌨️ Aurora CloudBank Command Line Interface
Interactive CLI for Aurora CloudBank operations
"""

import sys
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
import subprocess


class AuroraCLI:
    """Aurora CloudBank Command Line Interface"""

    def __init__(self):
        self.version = "3.5.1"

    def print_banner(self):
        """Print Aurora CloudBank banner"""
        banner = f"""

╔═══════════════════════════════════════╗
║         Aurora CloudBank CLI          ║
║    Quantum-Aware Symbolic Processing  ║
║            Version {self.version}            ║
╚═══════════════════════════════════════╝

"""
        print(banner)

    def run_quantum_demo(self):
        """Run quantum processing demonstration"""
        print("🌀 Running Quantum Processing Demo...")
        try:
            result = subprocess.run(
                [sys.executable, "aurora_quantum_processor.py"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print("✅ Quantum demo completed successfully")
                print(result.stdout)
            else:
                print(f"❌ Quantum demo failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running quantum demo: {e}")

    def run_consciousness_demo(self):
        """Run consciousness simulation demonstration"""
        print("🧠 Running Consciousness Simulation Demo...")
        try:
            result = subprocess.run(
                [sys.executable, "aurora_consciousness_engine.py"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print("✅ Consciousness demo completed successfully")
                print(result.stdout)
            else:
                print(f"❌ Consciousness demo failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running consciousness demo: {e}")

    def run_learning_demo(self):
        """Run adaptive learning demonstration"""
        print("🎯 Running Adaptive Learning Demo...")
        try:
            result = subprocess.run(
                [sys.executable, "aurora_adaptive_learning.py"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print("✅ Learning demo completed successfully")
                print(result.stdout)
            else:
                print(f"❌ Learning demo failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running learning demo: {e}")

    def run_integration_test(self):
        """Run comprehensive integration test"""
        print("🧪 Running Comprehensive Integration Test...")
        try:
            result = subprocess.run(
                [sys.executable, "aurora_master_integration.py"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                print("✅ Integration test completed successfully")
                print(result.stdout)
            else:
                print(f"❌ Integration test failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running integration test: {e}")

    def show_status(self):
        """Show system status"""
        print("📊 Aurora CloudBank System Status")
        print("=" * 40)

        modules = [
            ("Quantum Processor", "aurora_quantum_processor.py"),
            ("Consciousness Engine", "aurora_consciousness_engine.py"),
            ("Adaptive Learning", "aurora_adaptive_learning.py"),
            ("Master Integration", "aurora_master_integration.py"),
        ]

        for name, file in modules:
            if Path(file).exists():
                print(f"✅ {name}: Available")
            else:
                print(f"❌ {name}: Not Found")

        print(f"\n🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔢 Version: {self.version}")

    def interactive_mode(self):
        """Run interactive command mode"""
        print("🎮 Aurora CloudBank Interactive Mode")
        print("Type 'help' for available commands, 'exit' to quit\n")

        while True:
            try:
                command = input("aurora> ").strip().lower()

                if command == "exit" or command == "quit":
                    print("👋 Goodbye!")
                    break
                elif command == "help":
                    self.show_help()
                elif command == "status":
                    self.show_status()
                elif command == "quantum" or command == "q":
                    self.run_quantum_demo()
                elif command == "consciousness" or command == "c":
                    self.run_consciousness_demo()
                elif command == "learning" or command == "l":
                    self.run_learning_demo()
                elif command == "test" or command == "t":
                    self.run_integration_test()
                elif command == "clear":
                    subprocess.run("clear", shell=True)
                elif command == "":
                    continue
                else:
                    print(f"❓ Unknown command: {command}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break

    def show_help(self):
        """Show help information"""
        help_text = """
🎮 Aurora CloudBank CLI Commands:

Core Commands:
  status         Show system status
  quantum   (q)  Run quantum processing demo
  consciousness (c)  Run consciousness simulation demo
  learning  (l)  Run adaptive learning demo
  test      (t)  Run comprehensive integration test

Utility Commands:
  help           Show this help message
  clear          Clear screen
  exit/quit      Exit CLI

Examples:
  aurora> status
  aurora> quantum
  aurora> test

🌟 Aurora CloudBank v3.5.1 - Quantum-Aware Symbolic Processing
"""
        print(help_text)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Aurora CloudBank Command Line Interface")
    parser.add_argument("--quantum", "-q", action="store_true", help="Run quantum processing demo")
    parser.add_argument("--consciousness", "-c", action="store_true", help="Run consciousness simulation demo")
    parser.add_argument("--learning", "-l", action="store_true", help="Run adaptive learning demo")
    parser.add_argument("--test", "-t", action="store_true", help="Run comprehensive integration test")
    parser.add_argument("--status", "-s", action="store_true", help="Show system status")
    parser.add_argument("--interactive", "-i", action="store_true", help="Enter interactive mode")

    args = parser.parse_args()
    cli = AuroraCLI()

    if len(sys.argv) == 1:
        # No arguments, show banner and enter interactive mode
        cli.print_banner()
        cli.interactive_mode()
    else:
        # Process command line arguments
        if args.quantum:
            cli.run_quantum_demo()
        elif args.consciousness:
            cli.run_consciousness_demo()
        elif args.learning:
            cli.run_learning_demo()
        elif args.test:
            cli.run_integration_test()
        elif args.status:
            cli.show_status()
        elif args.interactive:
            cli.print_banner()
            cli.interactive_mode()


if __name__ == "__main__":
    main()
