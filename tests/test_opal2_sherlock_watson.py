import copy

import pytest

from modules.opal2.tool_contract import ToolExecutionContext, ToolInputError
from modules.opal2.tool_registry import ToolRegistry
from modules.opal2.tools.sherlock_watson import (
    SHERLOCK_TOOL_ID,
    SHERLOCK_WATSON_VERIFY_TOOL_ID,
    WATSON_TOOL_ID,
    SherlockCasefileTool,
    SherlockWatsonVerifyTool,
    WatsonBriefTool,
    bind_watson_brief,
    seal_sherlock_case,
    verify_sherlock_watson_bundle,
)


def _case():
    return {
        "subject": "Which location claim is authoritative?",
        "sources": [
            {
                "source_id": "src-1",
                "locator": "repo://canon/location.md",
                "authority": "owner_ruling",
            },
            {
                "source_id": "src-2",
                "locator": "repo://legacy/state.json",
                "authority": "legacy_runtime",
            },
        ],
        "observations": [
            {"statement": "Owner ruling says Lagrange point", "source_ids": ["src-1"]},
            {"statement": "Legacy state says L4", "source_ids": ["src-2"]},
        ],
        "established_facts": ["Current canon establishes a Lagrange-point siting."],
        "derived_findings": ["The older L4 value is historical evidence, not controlling authority."],
        "contradictions": [
            {
                "claim_a": "Lagrange point",
                "claim_b": "Earth-Moon L4",
                "source_ids": ["src-1", "src-2"],
            }
        ],
        "unresolved": ["Exact Lagrange point remains unresolved."],
    }


def _brief():
    return {
        "summary": "The evidence establishes a Lagrange point but not a numbered point.",
        "correlations": ["Later communication assumptions are compatible with a deeper-space locus."],
        "interpretations": ["Treat the numbered legacy value as a historical candidate."],
        "hypotheses": ["Sun-Earth L2 may best fit the remaining context."],
        "recommendations": ["Do not promote a numbered point without new evidence."],
        "residual_uncertainty": ["Primary-body system and exact stationkeeping orbit are unknown."],
    }


def test_sherlock_case_is_deterministic():
    first = seal_sherlock_case(_case())
    second = seal_sherlock_case(_case())
    assert first == second
    assert first["digest"].startswith("sha256:")
    assert first["case_id"].startswith("sherlock-")


def test_watson_bundle_binds_exact_sherlock_digest():
    casefile = seal_sherlock_case(_case())
    bundle = bind_watson_brief(casefile, _brief())
    assert bundle["watson"]["sherlock_case_digest"] == casefile["digest"]
    assert verify_sherlock_watson_bundle(bundle) == bundle


def test_evidence_mutation_breaks_watson_bundle():
    bundle = bind_watson_brief(seal_sherlock_case(_case()), _brief())
    mutated = copy.deepcopy(bundle)
    mutated["sherlock"]["record"]["established_facts"].append("Invented fact")
    with pytest.raises(ToolInputError, match="SHERLOCK case digest mismatch"):
        verify_sherlock_watson_bundle(mutated)


def test_watson_mutation_breaks_bundle():
    bundle = bind_watson_brief(seal_sherlock_case(_case()), _brief())
    mutated = copy.deepcopy(bundle)
    mutated["watson"]["brief"]["hypotheses"].append("Different hypothesis")
    with pytest.raises(ToolInputError, match="WATSON brief digest mismatch"):
        verify_sherlock_watson_bundle(mutated)


@pytest.mark.asyncio
async def test_tools_run_through_neutral_opal2_registry():
    registry = ToolRegistry(
        (SherlockCasefileTool(), WatsonBriefTool(), SherlockWatsonVerifyTool())
    )

    sherlock = await registry.run(
        SHERLOCK_TOOL_ID, {"case": _case()}, ToolExecutionContext()
    )
    watson = await registry.run(
        WATSON_TOOL_ID,
        {"casefile": sherlock.output["casefile"], "brief": _brief()},
        ToolExecutionContext(),
    )
    verification = await registry.run(
        SHERLOCK_WATSON_VERIFY_TOOL_ID,
        {"bundle": watson.output["bundle"]},
        ToolExecutionContext(),
    )

    assert verification.output["valid"] is True
    assert (
        verification.output["sherlock_case_digest"]
        == sherlock.output["casefile"]["digest"]
    )
