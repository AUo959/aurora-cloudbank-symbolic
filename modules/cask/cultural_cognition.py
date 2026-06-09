"""Cultural Cognition Framework — CASK runtime component.

Provides ``score_cultural_sensitivity(text, context)`` — a lightweight scorer
that estimates how culturally aware a piece of text is without requiring heavy
NLP dependencies.  The scorer uses keyword matching and structural heuristics
drawn from the CASK knowledge base (Global Cross-Linguistic Database, Ethics &
Value Systems Index, etc.).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Marker word sets extracted from CASK's knowledge layer
# ---------------------------------------------------------------------------

# Terms that indicate cultural awareness / sensitivity
_POSITIVE_MARKERS: List[str] = [
    "cultural context",
    "cross-cultural",
    "multicultural",
    "cultural diversity",
    "value system",
    "collective",
    "indigenous",
    "local knowledge",
    "cultural nuance",
    "cultural norm",
    "cultural perspective",
    "cultural practice",
    "intercultural",
    "transcultural",
    "contextual",
    "culturally appropriate",
    "inclusive",
    "equity",
    "pluralism",
    "multilingual",
    "bilingual",
    "localization",
    "localisation",
    "adaptation",
    "respect for",
    "community values",
    "traditional knowledge",
    "heritage",
]

# Terms that may indicate cultural insensitivity or hegemony risk
_NEGATIVE_MARKERS: List[str] = [
    "universal standard",
    "best practice globally",
    "one-size-fits-all",
    "western standard",
    "westernized",
    "default culture",
    "dominant culture",
    "cultural imposition",
    "homogenization",
    "assimilation",
    "inferior culture",
    "primitive",
    "uncivilized",
    "backward",
    "develop to our standard",
]

# Language/region markers that suggest cross-cultural scope
_SCOPE_MARKERS: List[str] = [
    r"\b(english|french|spanish|arabic|mandarin|hindi|swahili|portuguese|russian|"
    r"japanese|korean|bengali|german|turkish)\b",
    r"\b(africa|asia|europe|latin america|middle east|south asia|southeast asia|"
    r"oceania|caribbean)\b",
    r"\b(indigenous|aboriginal|diaspora|minority language)\b",
]


@dataclass
class CulturalSensitivityScore:
    """Structured result from :func:`score_cultural_sensitivity`."""

    score: float
    """Normalised sensitivity score in [0.0, 1.0].  Higher is more sensitive."""

    level: str
    """Human-readable band: ``'low'``, ``'medium'``, ``'high'``."""

    positive_matches: List[str] = field(default_factory=list)
    negative_matches: List[str] = field(default_factory=list)
    scope_indicators: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "level": self.level,
            "positive_matches": self.positive_matches,
            "negative_matches": self.negative_matches,
            "scope_indicators": self.scope_indicators,
            "details": self.details,
        }


def _find_matches(text_lower: str, markers: List[str]) -> List[str]:
    """Return unique marker strings found in *text_lower*."""
    found = []
    for marker in markers:
        if marker in text_lower and marker not in found:
            found.append(marker)
    return found


def _find_scope_indicators(text_lower: str) -> List[str]:
    """Return regex scope-marker phrases found in *text_lower*."""
    found = []
    for pattern in _SCOPE_MARKERS:
        for match in re.finditer(pattern, text_lower, re.IGNORECASE):
            term = match.group(0).lower()
            if term not in found:
                found.append(term)
    return found


def _level_from_score(score: float) -> str:
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


def score_cultural_sensitivity(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> CulturalSensitivityScore:
    """Score the cultural sensitivity of *text*.

    The score is computed as a weighted combination of:

    * **positive_ratio** — fraction of positive markers present (weight 0.5)
    * **scope_ratio** — breadth of geographic/linguistic scope (weight 0.3)
    * **negative_penalty** — deduction for hegemony-risk terms (weight -0.2)

    Context keys that influence scoring:

    * ``"domain"`` — ``"governance"`` or ``"legal"`` add +0.05 base
    * ``"num_languages"`` — integer ≥ 2 adds proportional scope bonus (capped +0.1)
    * ``"target_regions"`` — list; each region adds 0.02 (capped +0.1)

    Args:
        text: The text to score.
        context: Optional metadata dict for domain hints.

    Returns:
        :class:`CulturalSensitivityScore` with score, level, and match details.
    """
    if not text or not text.strip():
        return CulturalSensitivityScore(
            score=0.0,
            level="low",
            details={"reason": "empty_input"},
        )

    ctx = context or {}
    text_lower = text.lower()

    positive_matches = _find_matches(text_lower, _POSITIVE_MARKERS)
    negative_matches = _find_matches(text_lower, _NEGATIVE_MARKERS)
    scope_indicators = _find_scope_indicators(text_lower)

    # --- Base scores --------------------------------------------------
    positive_ratio = min(len(positive_matches) / max(len(_POSITIVE_MARKERS), 1), 1.0)
    scope_ratio = min(len(scope_indicators) / 6.0, 1.0)  # saturates at 6 regions
    negative_penalty = min(len(negative_matches) / max(len(_NEGATIVE_MARKERS), 1), 1.0)

    raw = (
        0.5 * positive_ratio
        + 0.3 * scope_ratio
        - 0.2 * negative_penalty
    )

    # --- Context bonuses ----------------------------------------------
    domain_bonus = 0.05 if ctx.get("domain") in ("governance", "legal", "ethics") else 0.0

    try:
        num_languages = int(ctx.get("num_languages", 1))
    except (TypeError, ValueError):
        num_languages = 1
    language_bonus = min((num_languages - 1) * 0.02, 0.10) if num_languages > 1 else 0.0

    raw_regions = ctx.get("target_regions", [])
    target_regions: List[str] = list(raw_regions) if isinstance(raw_regions, (list, tuple)) else []
    region_bonus = min(len(target_regions) * 0.02, 0.10)

    score = max(0.0, min(1.0, raw + domain_bonus + language_bonus + region_bonus))

    details: Dict[str, Any] = {
        "positive_ratio": round(positive_ratio, 4),
        "scope_ratio": round(scope_ratio, 4),
        "negative_penalty": round(negative_penalty, 4),
        "domain_bonus": domain_bonus,
        "language_bonus": language_bonus,
        "region_bonus": region_bonus,
        "raw_score": round(raw, 4),
        "word_count": len(text.split()),
    }

    rounded_score = round(score, 4)
    return CulturalSensitivityScore(
        score=rounded_score,
        level=_level_from_score(rounded_score),
        positive_matches=positive_matches,
        negative_matches=negative_matches,
        scope_indicators=scope_indicators,
        details=details,
    )
