"""
Aurora HR Module v3.0 Test Suite
Anchor: T7-HR-TEST
Protocol: Picard_Delta_3
Continuity: CP-HR-V3-TEST
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.hr import (
    AuroraHRModule,
    TeamLayer,
    PsychologicalSafetyLevel,
    OnboardingPhase
)


class TestHRModuleSymbolic(unittest.TestCase):
    """Test suite with symbolic continuity tracking"""
    
    def setUp(self):
        """Initialize with memory seal verification"""
        self.hr_module = AuroraHRModule()
        self.anchor_checkpoint = "TEST-CP-20251111"
    
    def test_module_initialization(self):
        """T7.1: Verify module initialization and anchor creation"""
        self.assertIsNotNone(self.hr_module)
        self.assertEqual(len(self.hr_module.departments), 5)
        self.assertTrue(hasattr(self.hr_module, 'config'))
    
    def test_psychological_safety_assessment(self):
        """T7.2: Test psychological safety with entropy monitoring"""
        assessment = self.hr_module.assess_psychological_safety("Helena Vu")
        self.assertIn('overall_score', assessment)
        self.assertIn('level', assessment)
        # Check entropy bounds
        self.assertGreaterEqual(assessment['overall_score'], 0.0)
        self.assertLessEqual(assessment['overall_score'], 4.0)
    
    def test_safety_level_classification(self):
        """T7.3: Verify safety level classification logic"""
        self.assertEqual(
            self.hr_module._classify_safety_level(3.8),
            PsychologicalSafetyLevel.OPTIMAL
        )
        self.assertEqual(
            self.hr_module._classify_safety_level(2.8),
            PsychologicalSafetyLevel.HEALTHY
        )
    
    def test_conflict_detection(self):
        """T7.4: Test conflict detection from indicators"""
        conflict = self.hr_module.detect_conflict({
            "explicit_report": True,
            "parties": ["Member A", "Member B"],
            "reported_severity": 2,
            "category": "technical"
        })
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.severity.value, 2)
    
    def test_onboarding_initiation(self):
        """T7.5: Test onboarding journey creation"""
        journey = self.hr_module.initiate_onboarding(
            "Test Member",
            "Engineer",
            "Coding & Engineering Division",
            "Test Manager"
        )
        self.assertEqual(journey.current_phase, OnboardingPhase.PRE_ARRIVAL)
        self.assertGreater(len(journey.pending_tasks), 0)
    
    def test_cultural_health_assessment(self):
        """T7.6: Test cultural health reporting"""
        report = self.hr_module.assess_cultural_health(TeamLayer.REAL_WORLD)
        self.assertGreaterEqual(report.overall_score, 0.0)
        self.assertLessEqual(report.overall_score, 1.0)
    
    def test_memory_anchor_creation(self):
        """T7.7: Verify memory anchor creation for continuity"""
        anchor_id = self.hr_module.create_memory_anchor("Helena Vu")
        self.assertIsNotNone(anchor_id)
        self.assertTrue(anchor_id.startswith("MEMBER-"))
    
    def test_comprehensive_report(self):
        """T7.8: Test comprehensive report generation"""
        report = self.hr_module.generate_comprehensive_report()
        self.assertIn('report_id', report)
        self.assertIn('sections', report)
        self.assertIn('team_overview', report['sections'])


if __name__ == '__main__':
    print("=" * 60)
    print("ANCHOR: T7-HR-TEST")
    print("CONTINUITY: CP-HR-V3-TEST")
    print("PROTOCOL: Picard_Delta_3")
    print("=" * 60)
    unittest.main(verbosity=2)
