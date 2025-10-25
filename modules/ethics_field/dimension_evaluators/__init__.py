"""
Dimension Evaluators - Multi-dimensional Ethical Metrics

Each dimension evaluator provides metrics for one aspect of ethical geometry.
All evaluators follow a common interface:

    def evaluate(synapse_context: Dict[str, Any]) -> float:
        '''Returns score 0.0 → 1.0 (or -1.0 → 1.0 for welfare tensor)'''

Dimensions:
    - picard_delta_3: Autonomy & Respect
    - thermax_continuity: Memory & Coherence
    - layer_integrity: Reality Coherence (L1/L2/L3)
    - collective_welfare: Distributed Benefit
    - transparency: Auditability & DLP

Thread: T1→T8→INFINITE
DLP: context_tag=dimension_evaluators_init
"""

from .collective_welfare import CollectiveWelfareEvaluator
from .layer_integrity import LayerIntegrityEvaluator
from .picard_delta_3 import PicardDelta3Evaluator
from .thermax_continuity import ThermaxContinuityEvaluator
from .transparency import TransparencyEvaluator

__all__ = [
    "PicardDelta3Evaluator",
    "ThermaxContinuityEvaluator",
    "LayerIntegrityEvaluator",
    "CollectiveWelfareEvaluator",
    "TransparencyEvaluator",
]
