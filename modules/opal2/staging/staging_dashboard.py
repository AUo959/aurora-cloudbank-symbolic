#!/usr/bin/env python3
"""Interactive dashboard for managing OPAL2 staged components."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Mapping, Sequence

from .component_staging_system import ComponentStagingSystem


logger = logging.getLogger(__name__)

COMPONENT_NOT_FOUND = "Component %r not found"
HEALTH_ICONS = {
    "healthy": "✅",
    "warning": "⚠️",
    "critical": "❌",
    "failing": "💀",
    "unknown": "❓",
}


async def _read_input(prompt: str) -> str:
    """Read terminal input without blocking the dashboard event loop."""

    return (await asyncio.to_thread(input, prompt)).strip()


class StagingDashboard:
    """Interactive dashboard for component staging."""

    def __init__(self) -> None:
        self.staging_system = ComponentStagingSystem()

    def display_dashboard(self) -> None:
        """Display the main staging dashboard."""

        dashboard = self.staging_system.get_component_dashboard()
        print("\n" + "=" * 60)
        print("🏗️  OPAL2 COMPONENT STAGING DASHBOARD")
        print("=" * 60)
        print(f"📊 Overview (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"   Total Components: {dashboard['total_components']}")
        print(f"   Chassis Ready: {dashboard['chassis_ready_count']}")
        print()

        self._print_stage_distribution(dashboard["stage_distribution"])
        self._print_health_distribution(dashboard["health_distribution"])
        self._print_top_candidates(dashboard["top_candidates"])
        self._print_components_by_stage(dashboard["components_by_stage"])
        print("=" * 60)

    @staticmethod
    def _print_stage_distribution(distribution: Mapping[str, int]) -> None:
        print("📈 Stage Distribution:")
        for stage, count in distribution.items():
            if count > 0:
                bar = "█" * min(count * 3, 20)
                print(f"   {stage.replace('_', ' ').title():<20} {count:>2} {bar}")
        print()

    @staticmethod
    def _print_health_distribution(distribution: Mapping[str, int]) -> None:
        print("🏥 Health Distribution:")
        for health, count in distribution.items():
            if count > 0:
                icon = HEALTH_ICONS.get(health, "?")
                print(f"   {icon} {health.title():<12} {count}")
        print()

    @staticmethod
    def _print_top_candidates(candidates: Sequence[Mapping[str, Any]]) -> None:
        if candidates:
            print("🌟 Top Chassis Candidates:")
            for index, candidate in enumerate(candidates[:5], 1):
                print(f"   {index}. {candidate['name']} ({candidate['score']:.1f}%)")
        print()

    @staticmethod
    def _print_components_by_stage(
        components_by_stage: Mapping[str, Sequence[Mapping[str, Any]]],
    ) -> None:
        print("🕒 Components by Stage:")
        for stage_name, components in components_by_stage.items():
            if not components:
                continue
            print(f"   📂 {stage_name.replace('_', ' ').title()}:")
            for component in components[:3]:
                icon = HEALTH_ICONS.get(component["health"], "?")
                print(f"      {icon} {component['name']}")
            if len(components) > 3:
                print(f"      ... and {len(components) - 3} more")
            print()

    async def create_interactive_concept(self) -> None:
        """Collect component details and create a staged concept."""

        print("\n🌱 CREATE NEW COMPONENT CONCEPT")
        print("-" * 35)

        component_id = await _read_input("Component ID: ")
        if not component_id:
            logger.error("Component ID required")
            return

        name = await _read_input("Component Name: ")
        if not name:
            logger.error("Component name required")
            return

        description = await _read_input("Description: ")
        author = await _read_input("Author (press Enter for 'Aurora R&D Team'): ")
        author = author or "Aurora R&D Team"
        concept_notes = await _read_input("Concept Notes (optional): ")

        try:
            component = await self.staging_system.create_concept(
                component_id, name, description, author, concept_notes
            )
        except Exception:
            logger.exception("Failed to create concept")
            return

        logger.info("Component concept %r created successfully!", component.name)
        print(f"   ID: {component.component_id}")
        print(f"   Stage: {component.stage.value}")
        print(f"   Version: {component.version}")

    async def view_component_details(self, component_id: str | None = None) -> None:
        """View detailed component information."""

        resolved_id = component_id or await _read_input("Enter component ID: ")
        component = self._component_or_log(resolved_id)
        if component is None:
            return

        self._print_component_summary(component)
        self._print_named_values("Capabilities", component.capabilities)
        self._print_named_values("Dependencies", component.dependencies)
        self._print_progression_checklist(component.progression_checklist)
        self._print_named_values(
            "Blocking Issues", component.blocking_issues, warning=True
        )
        self._print_test_results(component.test_results)
        self._print_validation_metrics(component.validation_metrics)

    def _component_or_log(self, component_id: str) -> Any | None:
        component = self.staging_system.staged_components.get(component_id)
        if component is None:
            logger.error(COMPONENT_NOT_FOUND, component_id)
        return component

    @staticmethod
    def _print_component_summary(component: Any) -> None:
        print(f"\n📋 COMPONENT DETAILS: {component.name}")
        print("-" * 50)
        print(f"ID: {component.component_id}")
        print(f"Stage: {component.stage.value}")
        print(f"Version: {component.version}")
        print(f"Author: {component.author}")
        print(f"Health: {component.health_status.value}")
        print(f"Created: {component.created_at}")
        print(f"Modified: {component.last_modified}")
        print()
        if component.description:
            print(f"Description: {component.description}")
            print()

    @staticmethod
    def _print_named_values(
        title: str, values: Sequence[str], *, warning: bool = False
    ) -> None:
        if not values:
            return
        heading = f"{title}:"
        print(heading)
        if warning:
            logger.warning("%s", heading)
        for value in values:
            print(f"  • {value}")
        print()

    @staticmethod
    def _print_progression_checklist(checklist: Mapping[str, bool]) -> None:
        if not checklist:
            return
        print("Progression Checklist:")
        for item, completed in checklist.items():
            status = "✅" if completed else "❌"
            print(f"  {status} {item.replace('_', ' ').title()}")
        print()

    @staticmethod
    def _print_test_results(results: Mapping[str, Any]) -> None:
        if not results:
            return
        print("🧪 Latest Test Results:")
        print(
            f"  Tests: {results.get('tests_passed', 0)}/"
            f"{results.get('tests_run', 0)} passed"
        )
        print(f"  Coverage: {results.get('coverage', 0):.1f}%")
        StagingDashboard._print_named_values("  Issues", results.get("issues_found", []))

    @staticmethod
    def _print_validation_metrics(validation: Mapping[str, Any]) -> None:
        if not validation:
            return
        print("🔍 Validation Results:")
        print(f"  Overall Score: {validation.get('overall_score', 0):.1f}%")
        print(f"  Chassis Ready: {validation.get('chassis_ready', False)}")
        StagingDashboard._print_named_values(
            "  Recommendations", validation.get("recommendations", [])
        )

    async def run_interactive_session(self) -> None:
        """Run the interactive staging session."""

        commands = {
            "1": self.create_interactive_concept,
            "2": self.view_component_details,
            "3": self.interactive_test_component,
            "4": self.interactive_validate_component,
            "5": self.interactive_generate_chassis,
        }
        while True:
            self.display_dashboard()
            self._print_commands()
            choice = await _read_input("\nEnter command: ")

            if choice == "0":
                return
            if choice == "6":
                continue

            command = commands.get(choice)
            if command is None:
                logger.error("Invalid command")
            else:
                await command()
            await _read_input("\nPress Enter to continue...")

    @staticmethod
    def _print_commands() -> None:
        print("\n🎛️  STAGING COMMANDS:")
        print("1. Create new concept")
        print("2. View component details")
        print("3. Test component")
        print("4. Validate component")
        print("5. Generate chassis component")
        print("6. Refresh dashboard")
        print("0. Exit")

    async def interactive_test_component(self) -> None:
        """Run the staged-component test suite."""

        component_id = await _read_input("Component ID to test: ")
        if self._component_or_log(component_id) is None:
            return

        test_suite = {"name": "interactive_test_suite", "test_count": 5}
        print(f"🧪 Running tests for {component_id}...")
        results = await self.staging_system.run_component_tests(
            component_id, test_suite
        )

        logger.info("Test results:")
        print(f"   Passed: {results['tests_passed']}")
        print(f"   Failed: {results['tests_failed']}")
        print(f"   Coverage: {results['coverage']:.1f}%")
        self._print_named_values("   Issues found", results["issues_found"])

    async def interactive_validate_component(self) -> None:
        """Validate a staged component."""

        component_id = await _read_input("Component ID to validate: ")
        if self._component_or_log(component_id) is None:
            return

        print(f"🔍 Validating {component_id}...")
        validation = await self.staging_system.validate_component(component_id)

        logger.info("Validation results:")
        print(f"   Overall Score: {validation['overall_score']:.1f}%")
        print(f"   Chassis Ready: {validation['chassis_ready']}")
        self._print_named_values(
            "   Recommendations", validation["recommendations"]
        )

    async def interactive_generate_chassis(self) -> None:
        """Generate a chassis component from a staged candidate."""

        candidates = self.staging_system.get_component_dashboard()["top_candidates"]
        if not candidates:
            logger.error("No chassis candidates available")
            return

        self._print_available_candidates(candidates)
        choice = await _read_input("Select candidate (number): ")
        candidate = self._selected_candidate(candidates, choice)
        if candidate is None:
            return

        print(f"🏗️ Generating chassis component for {candidate['name']}...")
        chassis_spec = await self.staging_system.generate_chassis_component(
            candidate["id"]
        )
        if chassis_spec is None:
            logger.error("Failed to generate chassis component")
            return
        self._print_chassis_spec(chassis_spec)

    @staticmethod
    def _print_available_candidates(candidates: Sequence[Mapping[str, Any]]) -> None:
        print("🏗️ Available chassis candidates:")
        for index, candidate in enumerate(candidates, 1):
            print(f"   {index}. {candidate['name']} ({candidate['score']:.1f}%)")

    @staticmethod
    def _selected_candidate(
        candidates: Sequence[Mapping[str, Any]], choice: str
    ) -> Mapping[str, Any] | None:
        try:
            index = int(choice) - 1
        except ValueError:
            logger.error("Invalid input")
            return None
        if not 0 <= index < len(candidates):
            logger.error("Invalid selection")
            return None
        return candidates[index]

    @staticmethod
    def _print_chassis_spec(chassis_spec: Mapping[str, Any]) -> None:
        logger.info("Chassis component generated!")
        print(f"   Chassis ID: {chassis_spec['component_id']}")
        print(f"   Type: {chassis_spec['component_type']}")
        print(f"   Power: {chassis_spec['power_requirement']}")
        print(f"   Data: {chassis_spec['data_requirement']}")
        print(f"   Quantum: {chassis_spec['quantum_required']}")


if __name__ == "__main__":
    dashboard = StagingDashboard()
    asyncio.run(dashboard.run_interactive_session())
