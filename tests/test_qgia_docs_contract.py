"""Contract tests for the staged QGIA documentation package."""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QGIA_DOCS = ROOT / "docs/qgia"

EXPECTED_ARTIFACTS = {
    "GUMAS_Audit_Schema.md",
    "PAT_Command_Sheet.md",
    "QGIA_Axiom_Doctrine_Narrative.md",
    "QGIA_Runtime_OnePager.md",
    "QUANTUM_FORGE_Axiom_Node_Manifest.md",
    "README.md",
    "RESETCORE_Bootstrap.md",
    "SIM_WATCHCON_Confidence_Module.md",
}

MIRRORED_SOURCES = {
    "GUMAS_Audit_Schema.md": ROOT / "QGIA_Integration/04_GUMAS_AuditSchema.md",
    "PAT_Command_Sheet.md": ROOT / "QGIA_Integration/05_PAT_CommandSheet.md",
    "QUANTUM_FORGE_Axiom_Node_Manifest.md": (
        ROOT / "QGIA_Integration/01_QUANTUM_FORGE_AxiomManifest.md"
    ),
    "RESETCORE_Bootstrap.md": (
        ROOT / "QGIA_Integration/03_RESETCORE_Bootstrap.md"
    ),
    "SIM_WATCHCON_Confidence_Module.md": (
        ROOT / "QGIA_Integration/02_SIM_WATCHCON_Confidence_Module.md"
    ),
}

IMPORTED_PACKAGE_HASHES = {
    "QGIA_Axiom_Doctrine_Narrative.md": (
        "f8ddcbfaa8c1e7e0520b9098db3e10eeb674108096c92afad319169ab57debfa"
    ),
    "QGIA_Runtime_OnePager.md": (
        "eb5b336a2c6bd2bd567524cbc89453bfa771f3067c1feb4dc528425fa593d5a2"
    ),
}


def normalize_table_separators(markdown: str) -> str:
    """Apply the repository's Markdown table-separator spacing convention."""
    normalized_lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        cells = stripped.split("|")[1:-1]
        is_separator = cells and all(
            re.fullmatch(r"\s*:?-{3,}:?\s*", cell) for cell in cells
        )
        if is_separator:
            normalized_lines.append("| " + " | ".join(cell.strip() for cell in cells) + " |")
        else:
            normalized_lines.append(line)
    trailing_newline = "\n" if markdown.endswith("\n") else ""
    return "\n".join(normalized_lines) + trailing_newline


class TestQGIADocsContract(unittest.TestCase):
    """Keep the package complete, traceable, and explicitly non-activating."""

    def test_package_contains_exactly_the_eight_requested_artifacts(self) -> None:
        self.assertTrue(QGIA_DOCS.is_dir(), f"missing QGIA docs directory: {QGIA_DOCS}")
        artifacts = {path.name for path in QGIA_DOCS.iterdir() if path.is_file()}

        self.assertEqual(artifacts, EXPECTED_ARTIFACTS)
        for artifact in artifacts:
            with self.subTest(artifact=artifact):
                self.assertTrue((QGIA_DOCS / artifact).read_text(encoding="utf-8"))

    def test_established_bundle_documents_remain_normalized_mirrors(self) -> None:
        for artifact, source in MIRRORED_SOURCES.items():
            with self.subTest(artifact=artifact):
                self.assertEqual(
                    (QGIA_DOCS / artifact).read_text(encoding="utf-8"),
                    normalize_table_separators(source.read_text(encoding="utf-8")),
                )

    def test_imported_source_snapshots_keep_recorded_hashes(self) -> None:
        for artifact, expected_hash in IMPORTED_PACKAGE_HASHES.items():
            with self.subTest(artifact=artifact):
                digest = hashlib.sha256((QGIA_DOCS / artifact).read_bytes()).hexdigest()
                self.assertEqual(digest, expected_hash)

    def test_readme_preserves_staging_and_layer_boundaries(self) -> None:
        readme = (QGIA_DOCS / "README.md").read_text(encoding="utf-8")
        normalized_readme = " ".join(readme.split())

        for boundary in (
            "`STAGING`",
            "`DOCUMENT_PACKAGE_ONLY`",
            "`NOT_IMPLEMENTED`",
            "not instructions for an agent",
            "crew or relay-agent mediation",
            "not Aurora's L1/L2 reality layers",
            "does not make that promotion decision implicitly",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, normalized_readme)

    def test_axiom_mirror_has_stable_ids_and_legacy_alias_context(self) -> None:
        manifest = (QGIA_DOCS / "QUANTUM_FORGE_Axiom_Node_Manifest.md").read_text(
            encoding="utf-8"
        )
        actual_ids = []
        for line in manifest.splitlines():
            if line.startswith("| AN-"):
                actual_ids.append(line.split("|", maxsplit=2)[1].strip())

        expected_ids = [f"AN-{index:03d}" for index in range(1, 24)]
        self.assertEqual(sorted(actual_ids), expected_ids)
        self.assertIn("| A02 | AN-001 | Corollary |", manifest)


if __name__ == "__main__":
    unittest.main()
