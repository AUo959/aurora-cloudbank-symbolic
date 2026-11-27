"""Shadow mode: the phonology engine watches NameService without changing it.

Attach a ``PhonologyShadow`` to ``NameService(shadow=...)``. For every resolved
name whose faction has a phonology profile, the shadow records:

* how the analyzer reads each name-word (derived / near / loan / unexplained),
* advisories (``no_etymology``, ``loan_spelling``), which are notes for review
  and never findings: they do not enter the registry's BLOCK/WARN gate,
* what the engine would have proposed for the same request and seed.

The shadow writes only to its own log. ``NameResolution``, the signature and the
``naming_receipt`` are untouched, so CanonRec admission behaves exactly as it
does without a shadow. If the engine raises, the error is recorded in the log
and the resolution is returned unchanged.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from .phonology.analysis import Analyzer
from .phonology.engine import Engine

if TYPE_CHECKING:
    from .naming import NameRequest, NameResolution

SHADOW_VERSION = "GUMAS_PHONOLOGY_SHADOW_v0.1"

# Factions whose names a phonology profile covers.
FACTION_PROFILES: Mapping[str, str] = {"velar_imperium": "velari"}

# Words in legacy candidates that are English framing, not names ("Sel'or of House Veyr").
FRAMING_WORDS = frozenset({"of", "house", "line", "ward"})


@dataclass
class ShadowObservation:
    entity_id: str
    entity_type: str
    faction: str
    profile: str
    name: str
    seed: int | None
    words: list[dict[str, Any]] = field(default_factory=list)
    advisories: list[dict[str, str]] = field(default_factory=list)
    engine_alternative: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PhonologyShadow:
    """Collects observations; never alters what NameService returns."""

    def __init__(self, engines: Mapping[str, Engine] | None = None):
        self._engines: dict[str, Engine] = dict(engines or {})
        self._analyzers: dict[str, Analyzer] = {}
        self.observations: list[ShadowObservation] = []

    # ------------------------------------------------------------------ hook

    def applies(self, request: "NameRequest") -> bool:
        return faction_key(request.faction_context) in FACTION_PROFILES

    def observe(self, request: "NameRequest", resolution: "NameResolution") -> ShadowObservation | None:
        """Record what the engine thinks of a resolved name. Errors are logged, never raised."""
        if not self.applies(request):
            return None
        faction = faction_key(request.faction_context)
        observation = ShadowObservation(
            entity_id=request.entity_id,
            entity_type=request.entity_type.value,
            faction=faction,
            profile=FACTION_PROFILES[faction],
            name=resolution.canonical_name,
            seed=resolution.signature.get("seed"),
        )
        try:
            self._fill(observation, request)
        except Exception as exc:  # shadow must never change the resolution's outcome
            observation.error = f"{type(exc).__name__}: {exc}"
        self.observations.append(observation)
        return observation

    # ------------------------------------------------------------------ reporting

    def report(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        advisories: dict[str, int] = {}
        for obs in self.observations:
            for word in obs.words:
                statuses[word["status"]] = statuses.get(word["status"], 0) + 1
            for note in obs.advisories:
                advisories[note["code"]] = advisories.get(note["code"], 0) + 1
        return {
            "shadow": SHADOW_VERSION,
            "observed": len(self.observations),
            "errors": sum(1 for obs in self.observations if obs.error),
            "word_status": statuses,
            "advisories": advisories,
            "observations": [obs.to_dict() for obs in self.observations],
        }

    # ------------------------------------------------------------------ internals

    def _engine(self, profile: str) -> Engine:
        if profile not in self._engines:
            self._engines[profile] = Engine(profile)
        return self._engines[profile]

    def _analyzer(self, profile: str) -> Analyzer:
        if profile not in self._analyzers:
            self._analyzers[profile] = Analyzer(self._engine(profile))
        return self._analyzers[profile]

    def _fill(self, observation: ShadowObservation, request: "NameRequest") -> None:
        analyzer = self._analyzer(observation.profile)
        for word in name_words(observation.name):
            summary = analyzer.analyze(word).summary()
            observation.words.append(_word_record(summary))
            note = _advisory(summary)
            if note:
                observation.advisories.append(note)
        if request.entity_type.value == "PERSON":
            observation.engine_alternative = self._alternative(observation, request)

    def _alternative(self, observation: ShadowObservation, request: "NameRequest") -> dict[str, Any]:
        """The engine's own proposal for the same request: a given name and a house name."""
        engine = self._engine(observation.profile)
        seed = observation.seed or 0
        lineage = str(request.constraints.get("lineage", "noble"))
        given = engine.generate_given_names(seed=seed, count=1)[0]
        house = engine.generate(lineage, seed=seed, count=1)[0]
        return {
            "name": f"{given.formal} {house.formal}",
            "lineage": lineage,
            "given": _derivation_record(given),
            "house": _derivation_record(house),
        }


def faction_key(faction_context: str | None) -> str:
    """Normalize a faction exactly as ``NameService._person_candidate`` does ("Velar Imperium" -> velar_imperium)."""
    return (faction_context or "").casefold().replace(" ", "_")


def name_words(name: str) -> list[str]:
    words = re.split(r"[\s\-]+", name.replace("’", "'"))
    return [w for w in words if w and w.casefold() not in FRAMING_WORDS]


def _word_record(summary: Mapping[str, Any]) -> dict[str, Any]:
    nearest = summary["nearest"][0] if summary["nearest"] else None
    etymology = summary["etymologies"][0] if summary["etymologies"] else None
    return {
        "word": summary["written"],
        "status": summary["status"],
        "etymology": etymology,
        "nearest": nearest,
        "loan_adapted": summary["loan_adapted"],
    }


def _advisory(summary: Mapping[str, Any]) -> dict[str, str] | None:
    if summary["status"] == "unexplained":
        return {"code": "no_etymology", "word": summary["written"],
                "note": "No etymology and no loan reading; review before admission."}  # fmt: skip
    if summary["status"] == "loan":
        letters = ", ".join(summary["foreign_letters"])
        return {"code": "loan_spelling", "word": summary["written"],
                "note": f"Uses letters the language lacks ({letters}); a loan reading, not a derivation."}  # fmt: skip
    return None


def _derivation_record(derived: Any) -> dict[str, Any]:
    return {
        "formal": derived.formal,
        "roots": list(derived.roots),
        "era": derived.era,
        "dialect": derived.dialect,
        "gloss": derived.gloss,
        "sporadic": list(derived.sporadic),
    }
