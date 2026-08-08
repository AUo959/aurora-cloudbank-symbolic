"""Minimal neutral SHERLOCK -> WATSON protocol-core example."""

import asyncio
import json

from modules.opal2.tool_contract import ToolExecutionContext
from modules.opal2.tool_registry import ToolRegistry
from modules.opal2.tools import (
    SHERLOCK_TOOL_ID,
    WATSON_TOOL_ID,
    SherlockCasefileTool,
    WatsonBriefTool,
)


async def main() -> None:
    registry = ToolRegistry((SherlockCasefileTool(), WatsonBriefTool()))

    case = {
        "subject": "Which specification controls the deployment target?",
        "sources": [
            {"source_id": "current", "locator": "repo://docs/current-spec.md"},
            {"source_id": "legacy", "locator": "repo://archive/old-spec.md"},
        ],
        "observations": [],
        "established_facts": ["The current specification is explicitly authoritative."],
        "derived_findings": ["The legacy specification is historical context."],
        "contradictions": [],
        "unresolved": [],
    }

    sherlock = await registry.run(
        SHERLOCK_TOOL_ID, {"case": case}, ToolExecutionContext()
    )

    brief = {
        "summary": "Use the current specification and preserve the legacy source for provenance.",
        "correlations": [],
        "interpretations": ["The documents represent supersession, not two active truths."],
        "hypotheses": [],
        "recommendations": ["Route deployment logic to the current specification."],
        "residual_uncertainty": [],
    }

    watson = await registry.run(
        WATSON_TOOL_ID,
        {"casefile": sherlock.output["casefile"], "brief": brief},
        ToolExecutionContext(),
    )
    print(json.dumps(watson.output["bundle"], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
