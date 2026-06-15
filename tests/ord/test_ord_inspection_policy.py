import unittest

import pytest

from modules.ord.ord_inspection_policy import (
    InspectionInput,
    OrdInspectionPolicy,
    QuarantineDecision,
    SanitizationAction,
)


pytestmark = pytest.mark.critical

class TestOrdInspectionPolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = OrdInspectionPolicy()

    def test_ethics_violation_sanitize(self) -> None:
        report = self.policy.inspect(
            InspectionInput(
                mission_id="tv-101",
                structure_valid=True,
                contamination_detected=False,
                drift_score=0.001,
                ethics_violations=["potential_secret_exposure"],
            )
        )
        self.assertEqual(QuarantineDecision.SANITIZE, report.decision)
        self.assertIn(SanitizationAction.APPLY_ETHICS_PATCH, report.requires_sanitization)
        self.assertFalse(report.human_review_required)

    def test_drift_exceeded_quarantine(self) -> None:
        report = self.policy.inspect(
            InspectionInput(
                mission_id="tv-102",
                structure_valid=True,
                contamination_detected=False,
                drift_score=0.009,
                ethics_violations=[],
            )
        )
        self.assertEqual(QuarantineDecision.QUARANTINE, report.decision)
        self.assertTrue(report.human_review_required)

    def test_structure_and_contamination_sanitize(self) -> None:
        report = self.policy.inspect(
            InspectionInput(
                mission_id="tv-103",
                structure_valid=False,
                contamination_detected=True,
                contamination_type="script_injection",
                drift_score=0.001,
                ethics_violations=[],
            )
        )
        self.assertEqual(QuarantineDecision.SANITIZE, report.decision)
        self.assertEqual(
            [SanitizationAction.STRIP_MALICIOUS, SanitizationAction.FIX_STRUCTURE],
            report.requires_sanitization,
        )

    def test_combined_drift_and_ethics_requires_review(self) -> None:
        report = self.policy.inspect(
            InspectionInput(
                mission_id="tv-104",
                structure_valid=True,
                contamination_detected=False,
                drift_score=0.009,
                ethics_violations=["potential_key_exposure"],
            )
        )
        self.assertEqual(QuarantineDecision.QUARANTINE, report.decision)
        self.assertTrue(report.human_review_required)

    def test_encoding_anomaly_requests_normalization(self) -> None:
        report = self.policy.inspect(
            InspectionInput(
                mission_id="tv-105",
                structure_valid=True,
                contamination_detected=False,
                drift_score=0.001,
                ethics_violations=[],
                encoding_anomaly=True,
            )
        )
        self.assertEqual(QuarantineDecision.SANITIZE, report.decision)
        self.assertEqual([SanitizationAction.NORMALIZE_ENCODING], report.requires_sanitization)
        self.assertFalse(report.human_review_required)


if __name__ == "__main__":
    unittest.main()
