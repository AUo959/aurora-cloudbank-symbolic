"""Contract tests for QGIA navigation and authority boundaries."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QGIA_DOCS = ROOT / "docs/qgia"
CANON_INDEX = ROOT / "CANON_INDEX.md"
DOCS_INDEX = ROOT / "docs/index.md"

EXPECTED_ARTIFACTS = (
    "README.md",
    "QGIA_Runtime_OnePager.md",
    "QGIA_Axiom_Doctrine_Narrative.md",
    "QUANTUM_FORGE_Axiom_Node_Manifest.md",
    "SIM_WATCHCON_Confidence_Module.md",
    "GUMAS_Audit_Schema.md",
    "RESETCORE_Bootstrap.md",
    "PAT_Command_Sheet.md",
)


class TestQGIAIndexContract(unittest.TestCase):
    """Keep QGIA discoverable without granting runtime or canon authority."""

    def test_every_indexed_qgia_artifact_exists(self) -> None:
        for artifact in EXPECTED_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertTrue((QGIA_DOCS / artifact).is_file())

    def test_canon_index_routes_every_qgia_artifact(self) -> None:
        canon_index = CANON_INDEX.read_text(encoding="utf-8")

        self.assertIn("## QGIA Integration (Staged Documentation Package)", canon_index)
        for artifact in EXPECTED_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertIn(f"`docs/qgia/{artifact}`", canon_index)

    def test_docs_portal_routes_every_qgia_artifact(self) -> None:
        docs_index = DOCS_INDEX.read_text(encoding="utf-8")

        self.assertIn("## QGIA Integration (Staged)", docs_index)
        self.assertIn(
            "../CANON_INDEX.md#qgia-integration-staged-documentation-package",
            docs_index,
        )
        for artifact in EXPECTED_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertIn(f"qgia/{artifact}", docs_index)

    def test_both_indexes_preserve_non_activation_boundary(self) -> None:
        canon_index = " ".join(CANON_INDEX.read_text(encoding="utf-8").split())
        docs_index = " ".join(DOCS_INDEX.read_text(encoding="utf-8").split())

        for boundary in (
            "do not promote its contents to canon",
            "do not implement runtime activation",
        ):
            with self.subTest(boundary=boundary):
                combined = f"{canon_index} {docs_index}"
                self.assertIn(boundary, combined)

        self.assertIn("source material, not instructions for an agent", canon_index)
        self.assertIn("`STAGING` and `DOCUMENT_PACKAGE_ONLY`", docs_index)


if __name__ == "__main__":
    unittest.main()
