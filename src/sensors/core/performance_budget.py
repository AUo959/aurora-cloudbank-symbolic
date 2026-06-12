"""
Performance budget enforcement — spec §Performance Budget.

v0.3.0 additions: ``sii_update`` key and ``per_tick_aggregate`` (≤10% of the
tick wall-clock budget, 15% hard max). On aggregate breach the decimation
factor doubles for non-critical sensors; rupture-class monitoring is never
decimated.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.sensors import constants as C
from src.sensors.core.sensor_base import utcnow

logger = logging.getLogger(__name__)


@dataclass
class BudgetViolation:
    operation_type: str
    elapsed_seconds: float
    budget_seconds: float
    timestamp: object = field(default_factory=utcnow)


class PerformanceBudget:
    """Enforce sensor operation latency budgets (max-latency column)."""

    BUDGETS: Dict[str, float] = {
        "internal_sensor": 0.010,
        "external_sensor": 0.025,
        "observatory_physical": 0.050,
        "observatory_symbolic": 0.100,
        "concept_resonance": 0.200,
        "ethical_signal": 0.100,
        "drift_presig": 0.075,
        "fusion_correlation": 0.200,
        "fusion_prediction": 0.300,
        "coherence_certification": 1.000,
        "sii_update": 0.025,                      # NEW v0.3.0
    }

    def __init__(self, tick_budget_seconds: Optional[float] = None):
        self.violations: List[BudgetViolation] = []
        self.tick_budget_seconds = tick_budget_seconds
        self.decimation_n = C.DECIMATION_DEFAULT_N
        self._tick_elapsed = 0.0

    @contextmanager
    def timed_operation(self, operation_type: str):
        budget = self.BUDGETS.get(operation_type, 1.0)
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self._tick_elapsed += elapsed
            if elapsed > budget:
                logger.warning(
                    "Operation %s exceeded budget: %.3fs > %.3fs",
                    operation_type, elapsed, budget,
                )
                self._record_budget_violation(operation_type, elapsed, budget)

    def _record_budget_violation(
        self, operation_type: str, elapsed: float, budget: float
    ) -> None:
        self.violations.append(BudgetViolation(operation_type, elapsed, budget))

    # -- per-tick aggregate (v0.3.0) ------------------------------------------

    def start_tick(self) -> None:
        self._tick_elapsed = 0.0

    def end_tick(self) -> bool:
        """Check aggregate overhead. Returns True if within budget.

        On breach: decimation factor doubles for non-critical sensors and a
        per_tick_aggregate violation is logged. Caller (phase observer) applies
        the new decimation; critical/rupture-class sensors are exempt.
        """
        if not self.tick_budget_seconds:
            return True
        limit = self.tick_budget_seconds * C.TICK_BUDGET_FRACTION
        if self._tick_elapsed > limit:
            self._record_budget_violation(
                "per_tick_aggregate", self._tick_elapsed, limit
            )
            self.decimation_n *= 2
            logger.warning(
                "Per-tick sensor overhead %.4fs > %.4fs; decimation N -> %d "
                "(rupture-class sensors exempt)",
                self._tick_elapsed, limit, self.decimation_n,
            )
            return False
        return True
