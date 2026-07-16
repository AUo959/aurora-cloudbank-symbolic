"""Contract tests for the evidence-backed ``src/`` structure audit."""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
AUDIT_PATH = SRC_ROOT / "AUDIT.md"
AUDIT_ROW = re.compile(
    r"^\| `(?P<directory>[^`]+?)/` \| " r"(?P<status>active|deprecated|unknown) \|",
    re.MULTILINE,
)


def _audit_rows() -> dict[str, str]:
    return {
        match.group("directory"): match.group("status")
        for match in AUDIT_ROW.finditer(AUDIT_PATH.read_text(encoding="utf-8"))
    }


class TestSrcStructureContract(unittest.TestCase):
    """Verify the source audit and relocation compatibility contract."""

    def test_audit_classifies_every_top_level_src_directory(self) -> None:
        rows = _audit_rows()
        actual = {path.name for path in SRC_ROOT.iterdir() if path.is_dir() and not path.name.startswith("__")}

        self.assertEqual(43, len(rows))
        self.assertSetEqual(set(rows), actual)
        self.assertTrue(set(rows.values()) <= {"active", "deprecated", "unknown"})

    def test_duplicate_looking_families_are_independent(self) -> None:
        audit = AUDIT_PATH.read_text(encoding="utf-8")
        families = (
            ("bridge", "bridges"),
            ("collab", "collaboration"),
            ("interface", "interfaces"),
            ("visual", "visualization"),
        )

        for left, right in families:
            self.assertIn(f"`{left}/` / `{right}/`", audit)
            for directory in (left, right):
                row = next(line for line in audit.splitlines() if line.startswith(f"| `{directory}/`"))
                self.assertIn("| independent |", row)

    def test_root_python_modules_are_compatibility_imports(self) -> None:
        from modules.code_generation import (
            ClassSpec,
            FunctionSpec,
            UltraHighFidelityCodeGenerator,
        )
        from modules.quantum_decision_oracle import QuantumDecisionOracle
        from src.code_generation_framework import (
            UltraHighFidelityCodeGenerator as LegacyCodeGenerator,
        )
        from src.quantum_decision_oracle import (
            QuantumDecisionOracle as LegacyDecisionOracle,
        )

        self.assertIs(LegacyCodeGenerator, UltraHighFidelityCodeGenerator)
        self.assertIs(LegacyDecisionOracle, QuantumDecisionOracle)

        generator = UltraHighFidelityCodeGenerator(enable_aurora_oversight=False)
        generated = generator.generate_function(
            FunctionSpec(
                name="audit_contract",
                description="Exercise the relocated code generator.",
                parameters=[],
                return_type="None",
                return_description="No return value.",
            )
        )
        self.assertIn("def audit_contract() -> None:", generated.code)
        function_tree = ast.parse(generated.code)
        self.assertIn(
            "audit_contract",
            {node.name for node in function_tree.body if isinstance(node, ast.FunctionDef)},
        )
        self.assertIn("logger = logging.getLogger(__name__)", generated.code)
        self.assertNotIn("self.aurora", generated.code)

        generated_class = generator.generate_class(
            ClassSpec(
                name="AuditContract",
                description="Exercise standalone generated class initialization.",
            )
        )
        self.assertIn('"""Test suite for AuditContract"""', generated_class.tests)
        class_tree = ast.parse(generated_class.code)
        self.assertIn(
            "AuditContract",
            {node.name for node in class_tree.body if isinstance(node, ast.ClassDef)},
        )
        self.assertIn(
            "self.logger = logging.getLogger(__name__)",
            generated_class.code,
        )

        self.assertLess(
            len((SRC_ROOT / "code_generation_framework.py").read_text().splitlines()),
            60,
        )
        self.assertLess(
            len((SRC_ROOT / "quantum_decision_oracle.py").read_text().splitlines()),
            60,
        )
        self.assertGreater(
            len((REPO_ROOT / "modules/code_generation/framework.py").read_text().splitlines()),
            600,
        )
        self.assertGreater(
            len((REPO_ROOT / "modules/quantum_decision_oracle/oracle.py").read_text().splitlines()),
            600,
        )

    def test_constellation_and_pqn_entrypoints_are_documented_and_resolvable(
        self,
    ) -> None:
        audit = AUDIT_PATH.read_text(encoding="utf-8")
        constellation_start = (SRC_ROOT / "constellation/start.ts").read_text(encoding="utf-8")
        pqn_demo = (REPO_ROOT / "demos/demo_entropy_fix.cjs").read_text(encoding="utf-8")

        self.assertIn("`src/index.ts` is active", audit)
        self.assertIn("import '../index.js';", constellation_start)
        self.assertIn("require('../src/pqn/signal_prioritizer.cjs')", pqn_demo)
