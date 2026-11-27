"""Lexicon: roots, radicals with ablaut grades, suffixes, and lineage classes.

A lexicon entry is either written out (``"proto": "kuna"``) or derived from a
radical plus a stem formant in a given ablaut grade::

    "radicals": {"WAR": {"form": "war", "gloss": "guard", ...}}
    "formants": {"N": {"gloss": "stem", "grades": {"zero": "na", "full": "ena"}}}
    "roots":    {"warna":  {"derive": {"radical": "WAR", "formant": "N", "grade": "zero"}},
                 "warena": {"derive": {"radical": "WAR", "formant": "N", "grade": "full"}}}

Entries derived from one radical are cognates: they share ``Root.radical``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .segments import Inventory


@dataclass(frozen=True)
class Root:
    key: str
    proto: str
    gloss: str
    gloss_status: str
    kind: str = "root"  # root | suffix | proclitic
    lineage: str | None = None
    source: str | None = None
    radical: str = ""  # the radical this entry descends from; its own key when written out
    grade: str | None = None


@dataclass(frozen=True)
class Lineage:
    name: str
    prefix: str
    roots: tuple[str, ...]
    eras: tuple[str, ...]
    dialect: str | None = None


@dataclass(frozen=True)
class Lexicon:
    roots: Mapping[str, Root]
    lineages: Mapping[str, Lineage]
    content_roots: tuple[str, ...]
    personal_suffixes: tuple[str, ...]


def load_lexicon(raw: Mapping[str, Any], inventory: Inventory) -> Lexicon:
    radicals = raw.get("radicals", {})
    formants = raw.get("formants", {})
    roots = {key: _load_root(key, entry, radicals, formants) for key, entry in raw["roots"].items()}
    for root in roots.values():
        inventory.parse(root.proto)  # fail fast on symbols outside the inventory
    lexicon = Lexicon(
        roots=roots,
        lineages=_load_lineages(raw["lineages"]),
        content_roots=tuple(raw["generative_content_roots"]),
        personal_suffixes=tuple(raw.get("personal_suffixes", ())),
    )
    _check_references(lexicon)
    return lexicon


def _load_root(key: str, entry: Mapping[str, Any], radicals: Mapping[str, Any], formants: Mapping[str, Any]) -> Root:
    if "derive" in entry:
        return _derived_root(key, entry, radicals, formants)
    return Root(
        key=key,
        proto=entry["proto"],
        gloss=entry["gloss"],
        gloss_status=entry["gloss_status"],
        kind=entry.get("kind", "root"),
        lineage=entry.get("lineage"),
        source=entry.get("source"),
        radical=key,
    )


def _derived_root(key: str, entry: Mapping[str, Any], radicals: Mapping[str, Any], formants: Mapping[str, Any]) -> Root:
    spec = entry["derive"]
    radical = radicals.get(spec["radical"])
    formant = formants.get(spec["formant"])
    if radical is None or formant is None:
        raise ValueError(f"root {key!r} derives from unknown radical or formant: {spec}")
    grade = spec["grade"]
    if grade not in formant["grades"]:
        raise ValueError(f"root {key!r}: formant {spec['formant']!r} has no {grade!r} grade")
    return Root(
        key=key,
        proto=radical["form"] + formant["grades"][grade],
        gloss=f"{radical['gloss']} ({grade}-grade)",
        gloss_status=radical["gloss_status"],
        lineage=radical.get("lineage"),
        source=radical.get("source"),
        radical=spec["radical"],
        grade=grade,
    )


def _load_lineages(raw_lineages: Mapping[str, Any]) -> dict[str, Lineage]:
    specs = {name: spec for name, spec in raw_lineages.items() if not name.startswith("_")}
    return {
        name: Lineage(name, s["prefix"], tuple(s["roots"]), tuple(s["eras"]), s.get("dialect"))
        for name, s in specs.items()
    }


def _check_references(lexicon: Lexicon) -> None:
    missing = _undefined_references(lexicon)
    if missing:
        raise ValueError(f"lexicon refers to undefined roots: {missing}")
    not_suffixes = [key for key in lexicon.personal_suffixes if lexicon.roots[key].kind != "suffix"]
    if not_suffixes:
        raise ValueError(f"personal_suffixes must be suffix entries: {not_suffixes}")


def _undefined_references(lexicon: Lexicon) -> list[str]:
    """Keys named by lineages, the generation pool or the personal suffixes that have no entry."""
    lineage_keys = [key for spec in lexicon.lineages.values() for key in spec.roots]
    named = set(lineage_keys) | set(lexicon.content_roots) | set(lexicon.personal_suffixes)
    return sorted(named - set(lexicon.roots))
