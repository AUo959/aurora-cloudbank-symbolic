
#!/usr/bin/env python3
"""
Opal2 Staging Dashboard
Interactive dashboard for managing staged components
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .component_staging_system import ComponentStagingSystem, StagingPhase, ComponentHealth

class StagingDashboard:
    """Interactive dashboard for component staging"""
    
    def __init__(self):
        self.staging_system = ComponentStagingSystem()
        
    async def display_dashboard(self):
        """Display the main staging dashboard"""
        dashboard = self.staging_system.get_component_dashboard()
        
        print("\n" + "="*60)
        print("🏗️  OPAL2 COMPONENT STAGING DASHBOARD")
        print("="*60)
        print(f"📊 Overview (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"   Total Components: {dashboard['total_components']}")
        print(f"   Chassis Ready: {dashboard['chassis_ready_count']}")
        print()
        
        # Stage distribution
        print("📈 Stage Distribution:")
        for stage, count in dashboard['stage_distribution'].items():
            if count > 0:
                bar = "█" * min(count * 3, 20)
                print(f"   {stage.replace('_', ' ').title():<20} {count:>2} {bar}")
        
        print()
        
        # Health distribution
        print("🏥 Health Distribution:")
        for health, count in dashboard['health_distribution'].items():
            if count > 0:
                status_icon = {"healthy": "✅", "warning": "⚠️", "critical": "❌", "failing": "💀", "unknown": "❓"}
                print(f"   {status_icon.get(health, '?')} {health.title():<12} {count}")
        
        print()
        
        # Top candidates
        if dashboard['top_candidates']:
            print("🌟 Top Chassis Candidates:")
            for i, candidate in enumerate(dashboard['top_candidates'][:5], 1):
                print(f"   {i}. {candidate['name']} ({candidate['score']:.1f}%)")
        
        print()
        
        # Recent activity
        print("🕒 Components by Stage:")
        for stage_name, components in dashboard['components_by_stage'].items():
            if components:
                print(f"   📂 {stage_name.replace('_', ' ').title()}:")
                for comp in components[:3]:  # Show top 3
                    health_icon = {"healthy": "✅", "warning": "⚠️", "critical": "❌", "failing": "💀", "unknown": "❓"}
                    print(f"      {health_icon.get(comp['health'], '?')} {comp['name']}")
                if len(components) > 3:
                    print(f"      ... and {len(components) - 3} more")
                print()
        
        print("="*60)
    
    async def create_interactive_concept(self):
        """Interactive concept creation"""
        print("\n🌱 CREATE NEW COMPONENT CONCEPT")
        print("-" * 35)
        
        component_id = input("Component ID: ").strip()
        if not component_id:
            print("❌ Component ID required")
            return
        
        name = input("Component Name: ").strip()
        if not name:
            print("❌ Component name required")
            return
        
        description = input("Description: ").strip()
        author = input("Author (press Enter for 'Aurora R&D Team'): ").strip()
        if not author:
            author = "Aurora R&D Team"
        
        concept_notes = input("Concept Notes (optional): ").strip()
        
        try:
            component = await self.staging_system.create_concept(
                component_id, name, description, author, concept_notes
            )
            print(f"✅ Component concept '{component.name}' created successfully!")
            print(f"   ID: {component.component_id}")
            print(f"   Stage: {component.stage.value}")
            print(f"   Version: {component.version}")
        except Exception as e:
            print(f"❌ Failed to create concept: {e}")
    
    async def view_component_details(self, component_id: str = None):
        """View detailed component information"""
        if not component_id:
            component_id = input("Enter component ID: ").strip()
        
        if component_id not in self.staging_system.staged_components:
            print(f"❌ Component '{component_id}' not found")
            return
        
        component = self.staging_system.staged_components[component_id]
        
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
        
        if component.capabilities:
            print("Capabilities:")
            for cap in component.capabilities:
                print(f"  • {cap}")
            print()
        
        if component.dependencies:
            print("Dependencies:")
            for dep in component.dependencies:
                print(f"  • {dep}")
            print()
        
        if component.progression_checklist:
            print("Progression Checklist:")
            for item, completed in component.progression_checklist.items():
                status = "✅" if completed else "❌"
                print(f"  {status} {item.replace('_', ' ').title()}")
            print()
        
        if component.blocking_issues:
            print("⚠️ Blocking Issues:")
            for issue in component.blocking_issues:
                print(f"  • {issue}")
            print()
        
        if component.test_results:
            print("🧪 Latest Test Results:")
            results = component.test_results
            print(f"  Tests: {results.get('tests_passed', 0)}/{results.get('tests_run', 0)} passed")
            print(f"  Coverage: {results.get('coverage', 0):.1f}%")
            if results.get('issues_found'):
                print("  Issues:")
                for issue in results['issues_found']:
                    print(f"    • {issue}")
            print()
        
        if component.validation_metrics:
            print("🔍 Validation Results:")
            validation = component.validation_metrics
            print(f"  Overall Score: {validation.get('overall_score', 0):.1f}%")
            print(f"  Chassis Ready: {validation.get('chassis_ready', False)}")
            if validation.get('recommendations'):
                print("  Recommendations:")
                for rec in validation['recommendations']:
                    print(f"    • {rec}")
    
    async def run_interactive_session(self):
        """Run interactive staging session"""
        while True:
            await self.display_dashboard()
            
            print("\n🎛️  STAGING COMMANDS:")
            print("1. Create new concept")
            print("2. View component details")
            print("3. Test component")
            print("4. Validate component")
            print("5. Generate chassis component")
            print("6. Refresh dashboard")
            print("0. Exit")
            
            choice = input("\nEnter command: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await self.create_interactive_concept()
            elif choice == "2":
                await self.view_component_details()
            elif choice == "3":
                await self.interactive_test_component()
            elif choice == "4":
                await self.interactive_validate_component()
            elif choice == "5":
                await self.interactive_generate_chassis()
            elif choice == "6":
                continue
            else:
                print("❌ Invalid command")
            
            input("\nPress Enter to continue...")
    
    async def interactive_test_component(self):
        """Interactive component testing"""
        component_id = input("Component ID to test: ").strip()
        
        if component_id not in self.staging_system.staged_components:
            print(f"❌ Component '{component_id}' not found")
            return
        
        test_suite = {
            "name": "interactive_test_suite",
            "test_count": 5
        }
        
        print(f"🧪 Running tests for {component_id}...")
        results = await self.staging_system.run_component_tests(component_id, test_suite)
        
        print(f"✅ Test results:")
        print(f"   Passed: {results['tests_passed']}")
        print(f"   Failed: {results['tests_failed']}")
        print(f"   Coverage: {results['coverage']:.1f}%")
        
        if results['issues_found']:
            print("   Issues found:")
            for issue in results['issues_found']:
                print(f"     • {issue}")
    
    async def interactive_validate_component(self):
        """Interactive component validation"""
        component_id = input("Component ID to validate: ").strip()
        
        if component_id not in self.staging_system.staged_components:
            print(f"❌ Component '{component_id}' not found")
            return
        
        print(f"🔍 Validating {component_id}...")
        validation = await self.staging_system.validate_component(component_id)
        
        print(f"✅ Validation results:")
        print(f"   Overall Score: {validation['overall_score']:.1f}%")
        print(f"   Chassis Ready: {validation['chassis_ready']}")
        
        if validation['recommendations']:
            print("   Recommendations:")
            for rec in validation['recommendations']:
                print(f"     • {rec}")
    
    async def interactive_generate_chassis(self):
        """Interactive chassis component generation"""
        # Show chassis candidates
        dashboard = self.staging_system.get_component_dashboard()
        
        if not dashboard['top_candidates']:
            print("❌ No chassis candidates available")
            return
        
        print("🏗️ Available chassis candidates:")
        for i, candidate in enumerate(dashboard['top_candidates'], 1):
            print(f"   {i}. {candidate['name']} ({candidate['score']:.1f}%)")
        
        choice = input("Select candidate (number): ").strip()
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(dashboard['top_candidates']):
                candidate = dashboard['top_candidates'][index]
                component_id = candidate['id']
                
                print(f"🏗️ Generating chassis component for {candidate['name']}...")
                chassis_spec = await self.staging_system.generate_chassis_component(component_id)
                
                if chassis_spec:
                    print("✅ Chassis component generated!")
                    print(f"   Chassis ID: {chassis_spec['component_id']}")
                    print(f"   Type: {chassis_spec['component_type']}")
                    print(f"   Power: {chassis_spec['power_requirement']}")
                    print(f"   Data: {chassis_spec['data_requirement']}")
                    print(f"   Quantum: {chassis_spec['quantum_required']}")
                else:
                    print("❌ Failed to generate chassis component")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")

if __name__ == "__main__":
    dashboard = StagingDashboard()
    asyncio.run(dashboard.run_interactive_session())
