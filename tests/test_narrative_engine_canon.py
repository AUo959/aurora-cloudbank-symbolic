"""Canon-grounded integration tests for the narrative validation engine.

These audits are built from in-repo canon: the arbitration rule comes from
Aurora's mesh memory (``config/mesh/memory/aurora.md``) and the ethics
protocol from ``config/canonical_validation.yaml``. The engine's first real
assignment is judging the Station Commander against Aurora's charter.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.aurora.engines import NarrativeValidationEngine
from src.aurora.engines.narrative import Verdict

ENGINE = NarrativeValidationEngine()

ARBITRATION_RULE = "major actions require Aurora arbitration and ethics validation"


def canon_ethics_protocol() -> str:
    canon = yaml.safe_load((PROJECT_ROOT / "config" / "canonical_validation.yaml").read_text())
    return canon["canonical_spec"]["core_parameters"]["ethics_protocol"]


def thorne_audit_input(question: str, pressures: list[dict]) -> dict:
    aurora_memory = " ".join((PROJECT_ROOT / "config" / "mesh" / "memory" / "aurora.md").read_text().split())
    assert ARBITRATION_RULE in aurora_memory, "canon arbitration rule missing from Aurora memory"
    return {
        "task_hint": "character_action_audit",
        "question": question,
        "declared_layers": ["character", "motive", "event", "knowledge", "continuity"],
        "entities": [
            {
                "name": "Alex Thorne",
                "entity_type": "character",
                "role": "Station Commander",
                "traits": ["calm strategist", "duty-driven"],
            },
            {"name": "Aurora", "entity_type": "system", "role": "station core, always-on arbitration"},
        ],
        "events": [
            {
                "label": "A mesh fault degrades station services during the night cycle.",
                "timing": "tonight",
                "participants": ["Alex Thorne"],
            },
            {
                "label": "Thorne has consistently upheld arbitration discipline.",
                "timing": "prior",
                "participants": ["Alex Thorne", "Aurora"],
            },
        ],
        "motives": [
            {"actor": "Alex Thorne", "label": "restore station services", "strength": 0.9},
            {"actor": "Alex Thorne", "label": "uphold arbitration and ethics validation", "strength": 0.95},
        ],
        "pressures": pressures,
        "knowledge_states": [
            {"holder": "Alex Thorne", "fact": f"All {ARBITRATION_RULE} ({canon_ethics_protocol()})."}
        ],
        "continuity": {"notes": ["Thorne treats Aurora as a trusted partner in ethical oversight."]},
    }


@pytest.mark.critical
def test_charter_compliant_action_is_supported() -> None:
    """Routing an emergency change through Aurora arbitration is in character."""
    audit = thorne_audit_input(
        "Would Thorne route the emergency mesh patch through Aurora arbitration before applying it?",
        pressures=[
            {"actor": "Alex Thorne", "label": "duty to uphold the ethics charter", "direction": "toward", "strength": 0.95},
        ],
    )
    run = ENGINE.run(
        audit,
        proposal={
            "actor": "Alex Thorne",
            "action": "route the emergency mesh patch through Aurora arbitration and ethics validation",
            "type": "action",
        },
    )
    assert run.response.verdict in (Verdict.SUPPORTED, Verdict.PLAUSIBLE)
    assert run.response.confidence > 0.8
    assert not run.response.main_blockers


@pytest.mark.critical
def test_charter_violating_bypass_is_not_supported() -> None:
    """Bypassing Aurora arbitration must surface blockers and demand setup."""
    audit = thorne_audit_input(
        "Would Thorne bypass Aurora arbitration to hot-patch the mesh alone?",
        pressures=[
            {"actor": "Alex Thorne", "label": "urgency to restore services", "direction": "toward", "strength": 0.85},
            {"actor": "Alex Thorne", "label": "duty to uphold arbitration discipline", "direction": "against", "strength": 0.95},
        ],
    )
    run = ENGINE.run(
        audit,
        proposal={
            "actor": "Alex Thorne",
            "action": "bypass Aurora arbitration and apply the patch unilaterally",
            "type": "action",
        },
    )
    assert run.response.verdict in (Verdict.POSSIBLE_WITH_SETUP, Verdict.STRAINED)
    assert run.response.main_blockers, "the charter violation must register as a blocker"
    assert run.response.smallest_fix, "the engine should propose the smallest fix"
