import unittest

import pytest

from modules.ord.ord_policy_engine import DroneType, MissionBrief, OrdPolicyEngine, SensitivityClass
from modules.ord.ord_receipts import canonical_json, canonical_sha256


pytestmark = pytest.mark.critical

class TestOrdPolicyEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = OrdPolicyEngine()

    def test_external_write_mission(self) -> None:
        mission = MissionBrief(
            mission_id="tv-001",
            tool_name="create_or_update_file",
            risk_level=0.55,
            destination="https://github.com/example/repo",
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertIn(DroneType.DELTA_SCOUT, order.drones_required)
        self.assertIn(DroneType.SHADOWFAX, order.drones_required)
        self.assertIn(DroneType.WISP, order.drones_required)
        self.assertGreaterEqual(order.priority, 5)

    def test_low_risk_internal_read(self) -> None:
        mission = MissionBrief(
            mission_id="tv-002",
            tool_name="read_file",
            risk_level=0.10,
            destination="orion-station://registry",
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertEqual([], order.drones_required)
        self.assertEqual(1, order.priority)

    def test_untrusted_extraction(self) -> None:
        mission = MissionBrief(
            mission_id="tv-003",
            tool_name="fetch_url",
            risk_level=0.45,
            destination="https://example.net/data",
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertEqual(
            [DroneType.DELTA_SCOUT, DroneType.SHADOWFAX, DroneType.GAMMA_SWARM, DroneType.WISP],
            order.drones_required,
        )

    def test_sensitivity_classification(self) -> None:
        mission = MissionBrief(
            mission_id="tv-004",
            tool_name="fetch_url",
            risk_level=0.20,
            destination="https://github.com/example/repo",
            parameters={"token": "redacted"},
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertIsNotNone(order.transport_requirement)
        self.assertEqual(SensitivityClass.RESTRICTED, order.transport_requirement.sensitivity)

    def test_query_string_does_not_spoof_internal_destination(self) -> None:
        mission = MissionBrief(
            mission_id="tv-004b",
            tool_name="fetch_url",
            risk_level=0.10,
            destination="https://evil.example/?next=localhost",
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertEqual(
            [DroneType.DELTA_SCOUT, DroneType.SHADOWFAX, DroneType.GAMMA_SWARM],
            order.drones_required,
        )

    def test_spoofed_trusted_domain_does_not_bypass_sanitization(self) -> None:
        mission = MissionBrief(
            mission_id="tv-004c",
            tool_name="fetch_url",
            risk_level=0.10,
            destination="https://github.com.evil.example/path",
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertIn(DroneType.GAMMA_SWARM, order.drones_required)

    def test_keyword_boundary_does_not_mark_benign_text_restricted(self) -> None:
        mission = MissionBrief(
            mission_id="tv-004d",
            tool_name="fetch_url",
            risk_level=0.10,
            destination="https://example.net/search",
            parameters={"query": "monkey business"},
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertIsNone(order.transport_requirement)

    def test_nested_sensitive_keys_still_require_secure_transport(self) -> None:
        mission = MissionBrief(
            mission_id="tv-004e",
            tool_name="fetch_url",
            risk_level=0.10,
            destination="https://example.net/data",
            parameters={"metadata": {"api_key": "redacted"}},
        )
        order = self.engine.create_dispatch_order(mission)
        self.assertIsNotNone(order.transport_requirement)
        self.assertEqual(SensitivityClass.RESTRICTED, order.transport_requirement.sensitivity)

    def test_deterministic_receipt(self) -> None:
        mission = MissionBrief(
            mission_id="tv-005",
            tool_name="fetch_url",
            risk_level=0.45,
            destination="https://example.net/data",
        )
        order_a = self.engine.create_dispatch_order(mission)
        order_b = self.engine.create_dispatch_order(mission)
        self.assertEqual(canonical_json(order_a), canonical_json(order_b))
        self.assertEqual(canonical_sha256(order_a), canonical_sha256(order_b))


if __name__ == "__main__":
    unittest.main()
