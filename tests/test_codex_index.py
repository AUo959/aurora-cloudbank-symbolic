"""The CODEX phase index must stay in step with the registers (#1133).

`simulation/CODEX_INDEX.md` is generated from the phase technical registers. A
generated file that nobody regenerates is worse than none, because it looks
authoritative while being stale — so staleness is a test failure, and every link
it emits is checked to actually resolve.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate_codex_index.py"
INDEX = REPO_ROOT / "simulation" / "CODEX_INDEX.md"

sys.path.insert(0, str(SCRIPT.parent))
from generate_codex_index import load_phases, render  # noqa: E402


def test_index_exists() -> None:
    assert INDEX.exists(), "simulation/CODEX_INDEX.md is missing; run the generator"


def test_index_is_not_stale() -> None:
    """Regenerating must be a no-op.

    If this fails: run `python scripts/generate_codex_index.py`.
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_every_phase_register_is_indexed() -> None:
    """A new phase must not be able to appear without reaching the index."""
    registers = sorted(
        p.name for p in (REPO_ROOT / "simulation").glob("CODEX_PHASE*_TECHNICAL_REGISTER.json")
    )
    assert registers, "no phase registers found — this test would be vacuous"
    text = INDEX.read_text()
    missing = [name for name in registers if name not in text]
    assert not missing, f"phase registers absent from the index: {missing}"


def test_all_relative_links_resolve() -> None:
    """Every link in the index must point at something that exists."""
    text = INDEX.read_text()
    targets = re.findall(r"\]\((?!https?://)([^)]+)\)", text)
    assert targets, "no relative links found — this test would be vacuous"
    broken = [t for t in targets if not (INDEX.parent / t).resolve().exists()]
    assert not broken, f"broken links in CODEX_INDEX.md: {broken}"


def test_roster_span_handles_every_register_shape() -> None:
    """The registers spell roster movement three different ways.

    Phases 1-2 use integration_status.roster_version_from/to, phase 3 uses
    roster_version_change, phases 4-5 use roster_version.before/after. A span of
    "—" means a shape was missed.
    """
    spans = {p["number"]: p["roster"] for p in load_phases()}
    assert spans, "no phases loaded"
    unresolved = [n for n, s in spans.items() if s in ("—", "None", "")]
    assert not unresolved, f"roster span unresolved for phases {unresolved}: {spans}"


def test_render_is_deterministic() -> None:
    """Two renders of the same input must match, or --check would flap."""
    phases = load_phases()
    assert render(phases) == render(phases)
