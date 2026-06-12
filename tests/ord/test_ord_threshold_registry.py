import unittest

import pytest

from modules.ord.ord_inspection_policy import InspectionInput, OrdInspectionPolicy, QuarantineDecision
from modules.ord.ord_policy_engine import MissionBrief, OrdPolicyEngine
from modules.ord.ord_threshold_registry import load_default_registry


pytestmark = pytest.mark.critical

class TestOrdThresholdRegistry(unittest.TestCase):
    def test_dispatch_includes_registry_metadata(self) -> None:
        engine = OrdPolicyEngine()
        order = engine.create_dispatch_order(
            MissionBrief(
                mission_id="tv-201",
                tool_name="fetch_url",
                risk_level=0.41,
                destination="https://example.net/data",
            )
        )
        self.assertEqual("ORD_THRESHOLD_REGISTRY", order.special_instructions["threshold_registry"]["registry_id"])
        self.assertEqual("0.5.0", order.special_instructions["threshold_registry"]["version"])

    def test_default_inspection_uses_registry_threshold(self) -> None:
        policy = OrdInspectionPolicy()
        report = policy.inspect(
            InspectionInput(
                mission_id="tv-202",
                structure_valid=True,
                contamination_detected=False,
                drift_score=load_default_registry().drift_threshold,
                drift_threshold=None,
            )
        )
        self.assertEqual(QuarantineDecision.QUARANTINE, report.decision)
        self.assertTrue(report.human_review_required)


if __name__ == "__main__":
    unittest.main()
