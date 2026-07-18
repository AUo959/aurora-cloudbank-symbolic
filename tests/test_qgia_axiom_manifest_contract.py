"""Contract tests for the staged QGIA axiom manifest reconciliation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def resolve_qgia_file(filename: str, preferred_directory: str) -> Path:
    """Resolve either historical QGIA directory casing during consolidation."""
    directories = dict.fromkeys(
        (preferred_directory, "QGIA_Integration", "QGIA_integration")
    )
    for directory in directories:
        candidate = ROOT / directory / filename
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Could not locate QGIA file: {filename}")


MANIFEST_PATH = resolve_qgia_file(
    "QUANTUM_FORGE_Axiom_Manifest.json", "QGIA_integration"
)
HUMAN_MANIFEST_PATH = resolve_qgia_file(
    "01_QUANTUM_FORGE_AxiomManifest.md", "QGIA_Integration"
)

EXPECTED_LEGACY_ALIASES = {
    "A01": ("AN-001", "NODE", "TRUMP_REACTIVE_AGENT_MODEL"),
    "A02": ("AN-001", "COROLLARY", "EXTERNAL_AGENT_DEPENDENCY"),
    "A03": ("AN-002", "NODE", "COWARD_BULLY_CONFIG"),
    "B01": ("AN-015", "NODE", "DOMINATION_AXIOM"),
    "B02": ("AN-016", "NODE", "AGENCY_AXIOM"),
    "B03": ("AN-017", "NODE", "THRESHOLD_AXIOM"),
    "B04": ("AN-018", "NODE", "PERCEPTION_AXIOM"),
    "B05": ("AN-019", "NODE", "ALLIANCE_AXIOM"),
    "B06": ("AN-020", "NODE", "RATIONAL_POWER"),
    "C01": ("AN-006", "NODE", "NEUTRALITY_FLUFF"),
    "C02": ("AN-008", "NODE", "4D_CHESS_EXCLUSION"),
    "C03": ("AN-009", "NODE", "MOSAIC_EVIDENCE"),
    "C04": ("AN-011", "NODE", "REVEALED_BELIEF_DISSONANCE"),
    "C05": ("AN-003", "NODE", "PREDICTION_MARKET_WEIGHT"),
    "D01": ("AN-004", "NODE", "RATIONALE_TREADMILL"),
    "D02": ("AN-012", "NODE", "SELF_INFLICTED_BLIND_SPOT"),
    "D03": ("AN-005", "NODE", "WEAPONIZED_DIPLOMACY"),
    "D04": ("AN-013", "NODE", "PHOTO_OP_DURABILITY"),
    "D05": ("AN-014", "NODE", "PERSONAL_ENRICHMENT_VEHICLE"),
    "E01": ("AN-022", "NODE", "MACHIAVELLI_HATRED_THRESHOLD"),
    "E02": ("AN-023", "NODE", "DRAFT_THREAT_ACTIVATION"),
    "S01": ("AN-021", "NODE", "FORECAST_CONSENSUS_SEPARATION"),
}

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

        self.assertEqual(sorted(actual_ids), expected_ids)
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
        nodes_by_id = {node["id"]: node for node in self.nodes}

        self.assertIn("AN-001", nodes_by_id)
        node = nodes_by_id["AN-001"]
        self.assertIn("corollaries", node)
        self.assertIn("1.2 External-Agent Dependency", node["corollaries"])
        self.assertIn("not a removed axiom node", self.human_manifest)

    def test_legacy_bundle_aliases_resolve_to_canonical_registry(self) -> None:
        aliases = {
            alias: (
                entry["target_id"],
                entry["relationship"],
                entry["target_name"],
            )
            for alias, entry in self.manifest["legacy_id_aliases"].items()
        }
        canonical_nodes = {node["id"]: node for node in self.nodes}

        self.assertEqual(aliases, EXPECTED_LEGACY_ALIASES)
        for alias, (target_id, relationship, target_name) in aliases.items():
            with self.subTest(alias=alias):
                self.assertIn(target_id, canonical_nodes)
                if relationship == "NODE":
                    self.assertEqual(canonical_nodes[target_id]["name"], target_name)
                else:
                    self.assertEqual(alias, "A02")
                    self.assertEqual(target_name, "EXTERNAL_AGENT_DEPENDENCY")
                    self.assertIn(
                        "1.2 External-Agent Dependency",
                        canonical_nodes[target_id]["corollaries"],
                    )


if __name__ == "__main__":
    unittest.main()
