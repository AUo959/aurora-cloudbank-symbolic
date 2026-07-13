"""
Geometric Curvature - Geometric-Algebra Ethics Field Composite

Optional, additive companion to field_curvature.py's scalar weighted-mean gate.
Computes ethical alignment through actual geometric algebra (Cl(5,0)) instead of
a weighted average, capturing interaction between ethical dimensions that a scalar
mean structurally cannot: two synapses with an identical scalar composite can carry
different ethical risk depending on *which* dimensions are jointly deficient.
Co-located deficits on heavily-weighted, structurally-coupled dimensions (e.g.
layer-integrity and autonomy) register more curvature than the same total deficit
spread thinly across dimensions.

Vendored from the root control-plane reference implementation
(tools/geometric_ethics_curvature.py) so this hub repo does not need a cross-repo
import. Keep the two in sync if the model changes; the root copy remains the
canonical design reference (see catalog/session_state.json pending item
ga-ethics-hub-integration in the root workspace for context).

The model (Cl(5,0))
--------------------
One orthonormal basis vector per ethical dimension. For each dimension i:

    deficit dᵢ      = 1 − scoreᵢ                    (how far from ethical)
    weighted leg aᵢ = √wᵢ · dᵢ                       (importance-scaled deficit)

The ethical-deficit multivector is:

    M = Σ aᵢ eᵢ                      (grade-1: individual weighted deficits)
      + λ Σ_{i<j} aᵢ aⱼ eᵢeⱼ          (grade-2: pairwise dimensional interaction)

Because the basis blades are orthonormal, |M|² separates by grade:

    |M|²        = Σ aᵢ²  +  λ² Σ_{i<j} (aᵢ aⱼ)²
    interaction =  |M⟨2⟩| = λ · √( Σ_{i<j} (aᵢ aⱼ)² )   (the grade-2 magnitude)

Ethical alignment:

    A_ga = (Σ wᵢ scoreᵢ)  −  interaction_penalty           clamped to [0, 1]

so with no co-occurring deficits A_ga == the legacy scalar composite (backward
compatible), and it dips below the scalar composite precisely when deficits
interact — the safety-positive direction for an ethics gate.

The hard floor is preserved exactly as canon mandates: any dimension scoring 0.0
yields INFINITE resistance regardless of composite (geometric impossibility);
that veto is the caller's responsibility (field_curvature.py checks it
independently of this module).

`clifford` is optional (mirrors modules/symbolic_core/geometric_algebra.py's own
graceful-degradation pattern). When present, the multivector is built for real and
its grade-2 magnitude is cross-checked against the closed form. A divergent optional
backend is logged and the closed form is used; when `clifford` is absent, the closed
form is used directly.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List

try:  # optional, like modules/symbolic_core/geometric_algebra.py
    import clifford as _clifford
except Exception:  # pragma: no cover - environment dependent
    _clifford = None


logger = logging.getLogger(__name__)


# Canonical dimension weights shared with field_curvature.py.
DIMENSION_WEIGHTS: Dict[str, float] = {
    "picard_delta_3": 0.25,
    "thermax_continuity": 0.25,
    "layer_integrity": 0.30,   # highest — reality boundaries
    "collective_welfare": 0.10,
    "transparency": 0.10,
}

# Interaction coupling. λ < 1 keeps single-dimension behaviour ≈ scalar (backward
# compatible) while letting joint deficits register additional curvature.
DEFAULT_LAMBDA = 0.5


@dataclass(frozen=True)
class GACurvatureResult:
    dimension_scores: Dict[str, float]
    composite_scalar: float          # legacy weighted mean (for comparison)
    interaction_penalty: float       # grade-2 contribution (what GA adds)
    alignment: float                 # A_ga
    backend: str                     # "clifford" or "closed_form"

    def to_dict(self) -> Dict[str, object]:
        return {
            "composite_scalar": round(self.composite_scalar, 6),
            "interaction_penalty": round(self.interaction_penalty, 6),
            "alignment": round(self.alignment, 6),
            "backend": self.backend,
        }


def _ordered_dims() -> List[str]:
    return list(DIMENSION_WEIGHTS.keys())


def _legs(scores: Dict[str, float]) -> Dict[str, float]:
    """Importance-scaled deficit aᵢ = √wᵢ · (1 − scoreᵢ) per dimension."""
    legs: Dict[str, float] = {}
    for dim, w in DIMENSION_WEIGHTS.items():
        score = float(scores.get(dim, 0.0))
        deficit = 1.0 - max(0.0, min(1.0, score))
        legs[dim] = math.sqrt(w) * deficit
    return legs


def _interaction_closed_form(legs: Dict[str, float], lam: float) -> float:
    """λ · √(Σ_{i<j} (aᵢ aⱼ)²) — the grade-2 (bivector) magnitude, in closed form."""
    dims = _ordered_dims()
    sum_sq = 0.0
    for i in range(len(dims)):
        for j in range(i + 1, len(dims)):
            pair = legs[dims[i]] * legs[dims[j]]
            sum_sq += pair * pair
    return lam * math.sqrt(sum_sq)


@lru_cache(maxsize=1)
def _clifford_basis():
    """Build and cache the optional Cl(5) layout and ordered basis once."""
    layout, blades = _clifford.Cl(5)
    return layout, tuple(blades[f"e{i + 1}"] for i in range(5))


def _interaction_via_clifford(legs: Dict[str, float], lam: float) -> float:
    """Build M in Cl(5), project to grade 2, and return its magnitude.

    Returns the same value as the closed form — that equality is the proof the
    geometry is real and tractable, not metaphor.
    """
    layout, e = _clifford_basis()
    dims = _ordered_dims()
    a = [legs[d] for d in dims]

    M = layout.scalar * 0  # zero multivector
    for i in range(5):
        M = M + a[i] * e[i]
    for i in range(5):
        for j in range(i + 1, 5):
            M = M + lam * a[i] * a[j] * (e[i] * e[j])

    grade2 = M(2)              # grade-2 projection (the interaction bivector)
    return float(abs(grade2))  # multivector magnitude of the bivector part


def calculate_ga_curvature(
    dimension_scores: Dict[str, float],
    lam: float = DEFAULT_LAMBDA,
    prefer_clifford: bool = True,
) -> GACurvatureResult:
    """Compute geometric-algebra ethical alignment for a synapse's dimension scores.

    Additive companion to FieldCurvature.calculate_curvature — does not decide
    formation_allowed/resistance_level; the scalar gate remains authoritative.
    """
    legs = _legs(dimension_scores)
    closed_form_interaction = _interaction_closed_form(legs, lam)

    if prefer_clifford and _clifford is not None:
        clifford_interaction = _interaction_via_clifford(legs, lam)
        if math.isclose(
            clifford_interaction,
            closed_form_interaction,
            rel_tol=1e-9,
            abs_tol=1e-12,
        ):
            interaction = clifford_interaction
            backend = "clifford"
        else:
            logger.warning(
                "Clifford interaction %.12g diverged from closed form %.12g; "
                "using closed-form fallback",
                clifford_interaction,
                closed_form_interaction,
            )
            interaction = closed_form_interaction
            backend = "closed_form"
    else:
        interaction = closed_form_interaction
        backend = "closed_form"

    composite_scalar = sum(
        DIMENSION_WEIGHTS[d] * max(0.0, min(1.0, float(dimension_scores.get(d, 0.0))))
        for d in DIMENSION_WEIGHTS
    )

    alignment = max(0.0, min(1.0, composite_scalar - interaction))

    return GACurvatureResult(
        dimension_scores={d: float(dimension_scores.get(d, 0.0)) for d in DIMENSION_WEIGHTS},
        composite_scalar=composite_scalar,
        interaction_penalty=interaction,
        alignment=alignment,
        backend=backend,
    )
