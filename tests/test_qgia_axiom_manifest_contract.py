"""Contract tests for the staged QGIA axiom manifest reconciliation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "QGIA_integration/QUANTUM_FORGE_Axiom_Manifest.json"
HUMAN_MANIFEST_PATH = ROOT / "QGIA_Integration/01_QUANTUM_FORGE_AxiomManifest.md"

REQUIRED_NODE_FIELDS = {
    "id",
    "name",
    "category",
    "category_label",
    "gumas_tier",
    "ethics_lock",
    "status",
    "rule_summary",
    "violation_signal",
    "gumas_audit_event",
    "pat_command",
    "aurora_hook",
}


class TestQGIAAxiomManifestContract(unittest.TestCase):
    """Keep the machine registry, human mirror, and staging boundary aligned."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.nodes = cls.manifest["axiom_nodes"]
        cls.human_manifest = HUMAN_MANIFEST_PATH.read_text(encoding="utf-8")

    def test_machine_registry_has_exact_stable_ids(self) -> None:
        expected_ids = [f"AN-{index:03d}" for index in range(1, 24)]
        actual_ids = [node["id"] for node in self.nodes]

        self.assertEqual(actual_ids, expected_ids)
        self.assertEqual(len(set(actual_ids)), 23)

    def test_machine_registry_has_unique_complete_nodes(self) -> None:
        names = [node["name"] for node in self.nodes]

        self.assertEqual(len(names), 23)
        self.assertEqual(len(set(names)), 23)
        for node in self.nodes:
            with self.subTest(node=node["id"]):
                self.assertTrue(REQUIRED_NODE_FIELDS.issubset(node))

    def test_reconciliation_metadata_keeps_activation_staged(self) -> None:
        reconciliation = self.manifest["reconciliation"]

        self.assertEqual(reconciliation["certainty"], "STAGING")
        self.assertEqual(reconciliation["runtime_activation"], "NOT_IMPLEMENTED")
        self.assertEqual(reconciliation["layer_scope"], "L1_ANALYTICAL_ADVISORY")
        self.assertEqual(reconciliation["export_semantics"], "DOCUMENT_PACKAGE_ONLY")
        self.assertIsNone(
            reconciliation["binding_crosswalk"]["engine"]["verified_runtime_target"]
        )

    def test_human_registry_mirrors_machine_registry(self) -> None:
        human_rows = {}
        for line in self.human_manifest.splitlines():
            if not line.startswith("| AN-"):
                continue
            columns = [column.strip().strip("`") for column in line.strip("|").split("|")]
            node_id, name, category, tier, ethics_lock, status, hook = columns
            human_rows[node_id] = {
                "name": name,
                "category": category,
                "gumas_tier": tier,
                "ethics_lock": ethics_lock == "true",
                "status": status,
                "aurora_hook": hook,
            }

        machine_rows = {
            node["id"]: {
                "name": node["name"],
                "category": node["category"],
                "gumas_tier": node["gumas_tier"],
                "ethics_lock": node["ethics_lock"],
                "status": node["status"],
                "aurora_hook": node["aurora_hook"],
            }
            for node in self.nodes
        }

        self.assertEqual(human_rows, machine_rows)

    def test_external_agent_dependency_remains_preserved_as_corollary(self) -> None:
        first_node = self.nodes[0]

        self.assertEqual(first_node["id"], "AN-001")
        self.assertIn("1.2 External-Agent Dependency", first_node["corollaries"])
        self.assertIn("not a removed axiom node", self.human_manifest)


if __name__ == "__main__":
    unittest.main()
