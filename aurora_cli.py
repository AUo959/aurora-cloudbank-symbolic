#!/usr/bin/env python3
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

"""
⌨️ Aurora CloudBank Command Line Interface
Interactive CLI for Aurora CloudBank operations
"""


class AuroraCLI:
    """Aurora CloudBank Command Line Interface"""

    def __init__(self):
        self.version = "3.5.1"

    def print_banner(self):
        """Print Aurora CloudBank banner"""
        banner = """

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

    def run_data_guardian_command(self, command: str):
        """Run Data Guardian command (data:scan, data:redact, etc.)"""
        try:
            # Import Data Guardian CLI
            from modules.data_guardian.cli import DataGuardianCLI

            # Parse command (e.g., "data:scan file.txt" or "data:strategies")
            parts = command.split(maxsplit=1)
            if len(parts) < 1:
                print("❓ Usage: data:<subcommand> [args]")
                print("Examples: data:scan file.txt, data:redact file.txt --strategy mask, data:strategies")
                return

            subcommand = parts[0].replace("data:", "")
            args = parts[1].split() if len(parts) > 1 else []

            # Create CLI instance
            cli = DataGuardianCLI()

            # Execute subcommand
            if subcommand == "scan":
                if not args:
                    print("❓ Usage: data:scan <file> [--confidence 0.7] [--region US] [--format text|json]")
                    return

                file_path = args[0]
                confidence = 0.7
                region = "US"
                output_format = "text"

                # Parse simple flags
                i = 1
                while i < len(args):
                    if args[i] == "--confidence" and i + 1 < len(args):
                        confidence = float(args[i + 1])
                        i += 2
                    elif args[i] == "--region" and i + 1 < len(args):
                        region = args[i + 1]
                        i += 2
                    elif args[i] == "--format" and i + 1 < len(args):
                        output_format = args[i + 1]
                        i += 2
                    else:
                        i += 1

                result = cli.scan_file(file_path, confidence, region, output_format)

                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                    return

                import json

                if output_format == "json":
                    print(json.dumps(result, indent=2))
                else:
                    print(f"📄 File: {result.get('file')}")
                    print(f"🔍 Total detections: {result['total_detections']}")
                    if result['total_detections'] > 0:
                        print("\n📊 Detections by type:")
                        print(result['summary'])

            elif subcommand == "redact":
                if not args:
                    print("❓ Usage: data:redact <file> [--output <file>] [--strategy mask] [--in-place]")
                    return

                file_path = args[0]
                output_path = None
                strategy = "mask"
                confidence = 0.7
                region = "US"
                in_place = False

                # Parse flags
                i = 1
                while i < len(args):
                    if args[i] in ["--output", "-o"] and i + 1 < len(args):
                        output_path = args[i + 1]
                        i += 2
                    elif args[i] in ["--strategy", "-s"] and i + 1 < len(args):
                        strategy = args[i + 1]
                        i += 2
                    elif args[i] == "--confidence" and i + 1 < len(args):
                        confidence = float(args[i + 1])
                        i += 2
                    elif args[i] == "--region" and i + 1 < len(args):
                        region = args[i + 1]
                        i += 2
                    elif args[i] == "--in-place":
                        in_place = True
                        i += 1
                    else:
                        i += 1

                result = cli.redact_file(file_path, output_path, strategy, confidence, region, in_place)

                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                    return

                print(f"📄 File: {result['file']}")
                print(f"📝 Output: {result['output_file']}")
                print(f"🔒 Total redactions: {result['total_redactions']}")
                print(f"🛡️ Strategy: {result['strategy']}")
                print(f"📋 Audit entries: {result['audit_entries']}")

            elif subcommand == "strategies":
                result = cli.list_strategies()
                print("🛡️ Available Redaction Strategies:")
                print("=" * 60)
                for strategy in result["strategies"]:
                    print(f"  {strategy['name']:12} - {strategy['description']}")
                print(f"\n✨ Default: {result['default']}")

            elif subcommand == "pii-types":
                result = cli.list_pii_types()
                print("🔍 Detectable PII Types:")
                print("=" * 60)
                for pii_type in result["pii_types"]:
                    print(f"  {pii_type['type']:18} - {pii_type['description']}")
                print(f"\n📊 Total: {result['total']} types")

            else:
                print(f"❓ Unknown Data Guardian command: {subcommand}")
                print("Available: scan, redact, strategies, pii-types")

        except ImportError:
            print("❌ Data Guardian module not available")
            print("Install with: pip install -e .")
        except Exception as e:
            print(f"❌ Error running Data Guardian command: {e}")

    def run_quantum_simulator_command(self, subcommand: str):
        """Run Quantum Simulator command (run, list, stats, etc.)"""
        try:
            import asyncio

            from modules.quantum_simulator import (
                OptimizationMethod,
                QuantumBackend,
                ScenarioRequest,
                ScenarioType,
                get_cache,
                get_orchestrator,
            )
            from modules.quantum_simulator.scenario_engine import ScenarioEngine

            if subcommand.startswith("run "):
                # Parse scenario type
                parts = subcommand.split(" ", 1)
                scenario_type = parts[1] if len(parts) > 1 else "optimization"

                print(f"🔬 Running {scenario_type} quantum simulation...")

                # Create request
                request = ScenarioRequest(
                    scenario_type=ScenarioType(scenario_type),
                    name=f"CLI {scenario_type} simulation",
                    description=f"Command-line initiated {scenario_type} simulation",
                    backend=QuantumBackend.MOCK,
                    optimization_method=OptimizationMethod.QAOA,
                    parameters={"max_iterations": 50},
                    seed=42,
                )

                # Run simulation
                async def run_sim():
                    orchestrator = await get_orchestrator()
                    engine = ScenarioEngine(orchestrator)
                    result = await engine.execute_scenario(request)
                    return result

                result = asyncio.run(run_sim())

                print(f"✅ Simulation completed: {result.simulation_id}")
                print(f"   Status: {result.status}")
                print(f"   Execution time: {result.execution_time_seconds:.2f}s")
                if result.optimization_result:
                    print(f"   Objective value: {result.optimization_result.objective_value:.4f}")

            elif subcommand == "list":
                # List cached scenarios
                cache = get_cache()
                scenarios = cache.list_scenarios(limit=20)

                print(f"\n📋 Cached Simulations ({len(scenarios)}):")
                print("=" * 80)
                for scenario in scenarios:
                    sim_id = scenario.simulation_id[:16]
                    sim_type = scenario.scenario_type.value
                    sim_status = scenario.status
                    print(f"  {sim_id}... | {sim_type:15} | {sim_status:10}")

            elif subcommand == "stats":
                # Show cache stats
                cache = get_cache()
                stats = cache.get_cache_stats()

                print("\n📊 Quantum Simulator Cache Statistics:")
                print("=" * 50)
                print(f"  Total entries:     {stats['total_entries']}")
                print(f"  Active entries:    {stats['active_entries']}")
                print(f"  Expired entries:   {stats['expired_entries']}")
                print(f"  Cache utilization: {stats['cache_utilization']:.1%}")
                print(f"  Total accesses:    {stats['total_accesses']}")
                print(f"  Avg access count:  {stats['avg_access_count']:.1f}")

            elif subcommand == "backends":
                # List available backends
                async def list_backends():
                    orchestrator = await get_orchestrator()
                    return orchestrator.list_available_backends()

                backends = asyncio.run(list_backends())

                print("\n🔧 Available Quantum Backends:")
                print("=" * 40)
                for backend in backends:
                    print(f"  ✓ {backend.value}")

            elif subcommand == "clear":
                # Clear cache
                cache = get_cache()
                count = cache.clear_all()
                print(f"✅ Cleared {count} cached simulations")

            else:
                print(f"❓ Unknown Quantum Simulator command: {subcommand}")
                print("Available: run, list, stats, backends, clear")

        except ImportError as e:
            print("❌ Quantum Simulator module not available")
            print(f"Error: {e}")
        except Exception as e:
            print(f"❌ Error running Quantum Simulator command: {e}")

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
                elif command.startswith("data:"):
                    # Data Guardian commands
                    self.run_data_guardian_command(command)
                elif command.startswith("qsim:"):
                    # Quantum Simulator commands
                    subcommand = command.split(":", 1)[1]
                    self.run_quantum_simulator_command(subcommand)
                elif command == "clear":
                    # SECURITY: Using shell=False for safe subprocess execution
                    subprocess.run(["clear"], shell=False)
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

Data Guardian Commands:
  data:scan <file>       Scan file for PII
  data:redact <file>     Redact PII from file
  data:strategies        List redaction strategies
  data:pii-types         List detectable PII types

Quantum Simulator Commands:
  qsim:run <type>        Run quantum simulation (supply_chain, energy_grid, optimization, etc.)
  qsim:list              List cached simulations
  qsim:stats             Show cache statistics
  qsim:backends          List available quantum backends
  qsim:clear             Clear simulation cache

Utility Commands:
  help           Show this help message
  clear          Clear screen
  exit/quit      Exit CLI

Examples:
  aurora> status
  aurora> quantum
  aurora> test
  aurora> data:scan myfile.txt
  aurora> data:redact myfile.txt --strategy mask
  aurora> data:strategies
  aurora> qsim:run optimization
  aurora> qsim:list
  aurora> qsim:stats
  aurora> qsim:backends

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
