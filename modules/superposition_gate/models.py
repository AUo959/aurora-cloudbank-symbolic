"""
Superposition Gate - Verdict Schema

Normalizes heterogeneous evaluator outputs (rule engines, geometric hard-veto
scorers, graduated-intervention gates) into one typed shape so they can be
combined by a single deterministic collapse rule, without requiring any of
the source evaluators to know about each other or share an implementation.

DLP: context_tag=superposition_gate_models, symbolic_hash=SUPERPOSITION_GATE_v1
"""

from enum import IntEnum
from typing import Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field


class VerdictSeverity(IntEnum):
    """Ordinal severity, lowest to highest concern.

    The ordering is load-bearing: collapse() and any downstream disagreement
    metric both depend on ALLOW < WARN < THROTTLE < BLOCK < HARD_VETO holding.
    """

    ALLOW = 0
    WARN = 1
    THROTTLE = 2
    BLOCK = 3
    HARD_VETO = 4


class Verdict(BaseModel):
    """One evaluator's independent judgment on a single action.

    `hard_veto` is the only field the collapse invariant depends on;
    `severity` orders everything else; `score` and `reason` are informational
    context for audit. Convention: lower `score` means more concerning (0.0 =
    maximally concerning, 1.0 = fully acceptable), matching the existing
    Picard_Delta_3 evaluator's vector-magnitude convention so that evaluator's
    output can be passed through unchanged if it's ever wired in here.
    """

    model_config = ConfigDict(frozen=True)

    source: str = Field(..., min_length=1, description="Identifier of the evaluator that produced this verdict")
    severity: VerdictSeverity = Field(..., description="Ordinal severity level")
    score: float = Field(..., ge=0.0, le=1.0, description="Evaluator's own 0-1 score; lower is more concerning")
    hard_veto: bool = Field(default=False, description="Unconditional block, independent of severity ordering")
    reason: str = Field(default="", description="Human-readable rationale")
    context_tag: Optional[str] = Field(default=None, description="Caller-supplied DLP context tag, for audit trail")


class CollapsedVerdict(BaseModel):
    """The single decision produced by combining a set of independent Verdicts."""

    model_config = ConfigDict(frozen=True)

    final: VerdictSeverity
    binding_verdict: Verdict = Field(..., description="The Verdict that determined the final outcome")
    all_verdicts: Tuple[Verdict, ...] = Field(..., description="Every verdict considered, in the order received")

    @property
    def blocked(self) -> bool:
        """True if the collapsed decision blocks the action (BLOCK or HARD_VETO)."""
        return self.final >= VerdictSeverity.BLOCK
