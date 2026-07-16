"""Contract tests for the evidence-backed ``src/`` structure audit."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
AUDIT_PATH = SRC_ROOT / "AUDIT.md"
AUDIT_ROW = re.compile(
    r"^\| `(?P<directory>[^`]+?)/` \| "
    r"(?P<status>active|deprecated|unknown) \|",
    re.MULTILINE,
)


def _audit_rows() -> dict[str, str]:
    return {
        match.group("directory"): match.group("status")
        for match in AUDIT_ROW.finditer(AUDIT_PATH.read_text(encoding="utf-8"))
    }


def test_audit_classifies_every_top_level_src_directory() -> None:
    rows = _audit_rows()
    actual = {
        path.name
        for path in SRC_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("__")
    }

    assert len(rows) == 43
    assert set(rows) == actual
    assert set(rows.values()) <= {"active", "deprecated", "unknown"}


def test_duplicate_looking_families_are_independent() -> None:
    audit = AUDIT_PATH.read_text(encoding="utf-8")
    families = (
        ("bridge", "bridges"),
        ("collab", "collaboration"),
        ("interface", "interfaces"),
        ("visual", "visualization"),
    )

    for left, right in families:
        assert f"`{left}/` / `{right}/`" in audit
        for directory in (left, right):
            row = next(
                line
                for line in audit.splitlines()
                if line.startswith(f"| `{directory}/`")
            )
            assert "| independent |" in row


def test_root_python_modules_are_compatibility_imports() -> None:
    from modules.code_generation import FunctionSpec, UltraHighFidelityCodeGenerator
    from modules.quantum_decision_oracle import QuantumDecisionOracle
    from src.code_generation_framework import (
        UltraHighFidelityCodeGenerator as LegacyCodeGenerator,
    )
    from src.quantum_decision_oracle import (
        QuantumDecisionOracle as LegacyDecisionOracle,
    )

    assert LegacyCodeGenerator is UltraHighFidelityCodeGenerator
    assert LegacyDecisionOracle is QuantumDecisionOracle

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
    assert "def audit_contract() -> None:" in generated.code

    assert len((SRC_ROOT / "code_generation_framework.py").read_text().splitlines()) < 60
    assert len((SRC_ROOT / "quantum_decision_oracle.py").read_text().splitlines()) < 60
    assert len(
        (REPO_ROOT / "modules/code_generation/framework.py").read_text().splitlines()
    ) > 600
    assert len(
        (
            REPO_ROOT / "modules/quantum_decision_oracle/oracle.py"
        ).read_text().splitlines()
    ) > 600


def test_constellation_and_pqn_entrypoints_are_documented_and_resolvable() -> None:
    audit = AUDIT_PATH.read_text(encoding="utf-8")
    constellation_start = (SRC_ROOT / "constellation/start.ts").read_text(
        encoding="utf-8"
    )
    pqn_demo = (REPO_ROOT / "demos/demo_entropy_fix.cjs").read_text(
        encoding="utf-8"
    )

    assert "`src/index.ts` is active" in audit
    assert "import '../index.js';" in constellation_start
    assert "require('../src/pqn/signal_prioritizer.cjs')" in pqn_demo
