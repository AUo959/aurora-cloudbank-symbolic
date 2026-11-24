"""Profile loading, chronology-driven derivation, orthography and generation.

The central mechanism is relative chronology. A compound has a formation
date. Its elements evolve as independent words under every sound law dated
before that date, are joined, and then evolve together under every later law.
So the shape of a compound records when it was coined:

* elder (formed early): junction syncope fuses it, e.g. *wela+kuna > Velkonn
* middle: the linking vowel survives syncope, e.g. Vela-kynn
* scribal (after the scribal reform): the parts were already worn-down words,
  and the junction is written with an apostrophe, e.g. Vel'Rynn, Tal'Varen

After the common laws, speech may split into dialects; each branch adds its
own later laws (``chronology.json`` -> ``dialects``).
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import syllables
from .phonaesthetics import SoundModel
from .lexicon import Lineage, Root, load_lexicon
from .rules import Boundary, Morph, SoundLaw, Word
from .segments import Inventory

ENGINE_VERSION = "GUMAS_PHONOLOGY_ENGINE_v0.4"
PROFILES_DIR = Path(__file__).resolve().parent / "profiles"
COMMON = "common"

__all__ = ["COMMON", "ENGINE_VERSION", "Derivation", "Engine", "Lineage", "Profile", "Root", "load_profile",
           "shared_roots"]  # fmt: skip


@dataclass(frozen=True)
class Profile:
    name: str
    inventory: Inventory
    tactics: syllables.Phonotactics
    laws: tuple[SoundLaw, ...]
    dialects: Mapping[str, tuple[SoundLaw, ...]]
    split_at: int | None
    sporadic_laws: tuple[SoundLaw, ...]
    sporadic_rate: float
    loan_map: Mapping[str, str]
    eras: Mapping[str, int]
    reform_date: int
    lexicon: Mapping[str, Root]
    lineages: Mapping[str, Lineage]
    content_roots: tuple[str, ...]
    personal_suffixes: tuple[str, ...]
    attested: tuple[Mapping[str, Any], ...]
    fixtures: tuple[Mapping[str, Any], ...]
    unexplained: tuple[Mapping[str, Any], ...]
    digest: str

    @classmethod
    def load(cls, directory: str | Path) -> "Profile":
        directory = Path(directory)
        raw = _read_profile_files(directory)
        inventory = Inventory(raw["inventory"]["phonemes"])
        chronology = raw["chronology"]
        laws = _load_laws(chronology["laws"])
        lexicon = load_lexicon(raw["lexicon"], inventory)
        canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"))
        return cls(
            name=directory.name,
            inventory=inventory,
            tactics=_load_tactics(raw["inventory"], inventory),
            laws=laws,
            dialects=_load_dialects(chronology.get("dialects"), laws),
            split_at=chronology.get("dialects", {}).get("split_at"),
            sporadic_laws=_load_laws(chronology.get("sporadic", {}).get("laws", [])),
            sporadic_rate=float(chronology.get("sporadic", {}).get("rate", 0.0)),
            loan_map=_public(raw["inventory"].get("loan_map", {})),
            eras={name: spec["formed_at"] for name, spec in chronology["eras"].items()},
            reform_date=chronology["orthographic_events"]["scribal_reform"]["date"],
            lexicon=lexicon.roots,
            lineages=lexicon.lineages,
            content_roots=lexicon.content_roots,
            personal_suffixes=lexicon.personal_suffixes,
            attested=tuple(raw["attested"]["names"]),
            fixtures=tuple(raw["attested"].get("fixtures", [])),
            unexplained=tuple(r for r in raw["attested"].get("unexplained", []) if "formal" in r),
            digest=hashlib.sha256(canonical.encode()).hexdigest()[:16],
        )


_PROFILE_FILES = ("inventory", "chronology", "lexicon", "attested")


def _public(mapping: Mapping[str, Any]) -> dict[str, Any]:
    """Drop ``_note``-style keys from a data mapping."""
    return {k: v for k, v in mapping.items() if not k.startswith("_")}


def _read_profile_files(directory: Path) -> dict[str, Any]:
    return {part: json.loads((directory / f"{part}.json").read_text(encoding="utf-8")) for part in _PROFILE_FILES}


def _load_tactics(raw_inventory: Mapping[str, Any], inventory: Inventory) -> syllables.Phonotactics:
    consonants = [s for s in inventory.symbols() if not inventory[s].feature("syllabic")]
    return syllables.Phonotactics.from_profile(raw_inventory.get("phonotactics", {}), consonants)


def _load_laws(raw_laws: Iterable[Mapping[str, Any]]) -> tuple[SoundLaw, ...]:
    laws = tuple(sorted((SoundLaw.from_dict(d) for d in raw_laws), key=lambda law: law.date))
    if len({law.date for law in laws}) != len(laws):
        raise ValueError("two sound laws share a date; relative order would be ambiguous")
    return laws


def _load_dialects(raw: Mapping[str, Any] | None, common: Sequence[SoundLaw]) -> dict[str, tuple[SoundLaw, ...]]:
    """Branch laws per dialect. Every branch law must postdate the split and the last common law."""
    if not raw:
        return {}
    dialects = {name: _load_laws(spec["laws"]) for name, spec in raw["branches"].items()}
    if COMMON in dialects:
        raise ValueError(f"{COMMON!r} is reserved for the undivided language")
    _check_branch_dates(dialects, max([raw["split_at"]] + [law.date for law in common]))
    return dialects


def _check_branch_dates(dialects: Mapping[str, Sequence[SoundLaw]], floor: int) -> None:
    early = sorted(law.law_id for laws in dialects.values() for law in laws if law.date <= floor)
    if early:
        raise ValueError(f"dialect laws must postdate the split and the common laws: {early}")


@lru_cache(maxsize=None)
def load_profile(name: str) -> Profile:
    return Profile.load(PROFILES_DIR / name)


@dataclass
class Derivation:
    roots: tuple[str, ...]
    radicals: tuple[str, ...]
    era: str | None
    formed_at: int
    dialect: str
    proto: str
    phonemic: str
    formal: str
    informal: str
    gloss: str
    gloss_status: list[str]
    lineage: str | None
    trace: list[dict[str, Any]]
    phonotactic_problems: list[str]
    profile: str
    profile_digest: str
    euphony: float = 0.0
    sporadic: list[str] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)

    @property
    def legal(self) -> bool:
        return not self.phonotactic_problems

    def receipt(self) -> dict[str, Any]:
        """Derivation block for a naming receipt (provenance, not player-facing text)."""
        return {
            "engine": ENGINE_VERSION,
            "profile": self.profile,
            "profile_digest": self.profile_digest,
            "roots": list(self.roots),
            "radicals": list(self.radicals),
            "era": self.era,
            "formed_at": self.formed_at,
            "dialect": self.dialect,
            "proto": "*" + self.proto,
            "phonemic": "/" + self.phonemic + "/",
            "formal": self.formal,
            "informal": self.informal,
            "gloss": self.gloss,
            "gloss_status": self.gloss_status,
            "lineage": self.lineage,
            "sporadic": self.sporadic,
            "trace": self.trace,
        }


class Engine:
    def __init__(self, profile: Profile | str):
        self.profile = load_profile(profile) if isinstance(profile, str) else profile
        self._sound_model: SoundModel | None = None

    @property
    def sound_model(self) -> SoundModel:
        """Bigram model of canon Velari spellings (corpus forms and unexplained canon given names)."""
        if self._sound_model is None:
            rows = self.profile.attested + self.profile.unexplained
            words = [r["formal"] for r in rows] + [r["informal"] for r in rows if "informal" in r]
            graphemes = [self.profile.inventory[s].grapheme for s in self.profile.inventory.symbols()]
            self._sound_model = SoundModel(words, graphemes)
        return self._sound_model

    # ------------------------------------------------------------------ derivation

    def _formation(self, era: str | None, formed_at: int | None) -> tuple[str | None, int]:
        if formed_at is not None:
            return era, int(formed_at)
        era = era or "elder"
        if era not in self.profile.eras:
            raise KeyError(f"unknown era {era!r}; known: {sorted(self.profile.eras)}")
        return era, self.profile.eras[era]

    def laws_for(self, dialect: str | None) -> tuple[SoundLaw, ...]:
        """The common laws, followed by a dialect's own laws when one is named."""
        if dialect in (None, COMMON):
            return self.profile.laws
        if dialect not in self.profile.dialects:
            raise KeyError(f"unknown dialect {dialect!r}; known: {[COMMON, *sorted(self.profile.dialects)]}")
        return self.profile.laws + self.profile.dialects[dialect]

    def _proto(self, roots: Sequence[Root], formed_at: int) -> str:
        joiner = "+" if formed_at < self.profile.reform_date else "~"
        out = ""
        for index, root in enumerate(roots):
            if index:
                out += "-" if root.kind == "suffix" else joiner
            out += root.proto
        return out

    def _lookup(self, roots: Sequence[str]) -> list[Root]:
        missing = [key for key in roots if key not in self.profile.lexicon]
        if missing:
            raise KeyError(f"unknown {self.profile.name} roots: {missing}")
        return [self.profile.lexicon[key] for key in roots]

    def _evolve(
        self, used: Sequence[Root], formed_at: int, laws: Sequence[SoundLaw]
    ) -> tuple[Word, list[dict[str, Any]]]:
        """Run the chronology: separate words before ``formed_at``, one word from then on."""
        inventory = self.profile.inventory
        pieces = [Word.from_morph(Morph(r.key, r.kind, r.lineage), inventory.parse(r.proto)) for r in used]
        early, late = _partition(laws, formed_at)
        trace: list[dict[str, Any]] = []
        pieces = self._run_laws(early, pieces, trace)
        word = Word.join(pieces, formed_at)
        if len(pieces) > 1:
            trace.append({"event": "compounded", "date": formed_at, "form": word.phonemic()})
        (word,) = self._run_laws(late, [word], trace)
        return word, trace

    def _run_laws(self, laws: Sequence[SoundLaw], words: list[Word], trace: list[dict[str, Any]]) -> list[Word]:
        """Apply laws in order to each word independently, recording every change."""
        for law in laws:
            before = _show(words)
            words = [law.apply(w, self.profile.inventory) for w in words]
            _record(trace, law, before, _show(words))
        return words

    def derive(
        self,
        roots: Sequence[str],
        era: str | None = None,
        *,
        formed_at: int | None = None,
        dialect: str | None = None,
        sporadic: bool = False,
    ) -> Derivation:
        """Derive a name. ``sporadic`` also applies the profile's irregular laws, recorded in the trace."""
        used = self._lookup(roots)
        era, formed_at = self._formation(era, formed_at)
        joined, trace = self._evolve(used, formed_at, self.laws_for(dialect))
        joined, applied = self._apply_sporadic(joined, trace, sporadic)
        formal, informal = self._render(joined)
        return Derivation(
            roots=tuple(roots),
            radicals=tuple(r.radical for r in used),
            era=era,
            formed_at=formed_at,
            dialect=dialect or COMMON,
            proto=self._proto(used, formed_at),
            phonemic=joined.phonemic(),
            formal=formal,
            informal=informal,
            gloss=" + ".join(r.gloss for r in used),
            gloss_status=[r.gloss_status for r in used],
            lineage=_first_lineage(used),
            trace=trace,
            phonotactic_problems=syllables.check(joined.segments(), self.profile.tactics),
            profile=self.profile.name,
            profile_digest=self.profile.digest,
            euphony=self.sound_model.score(formal),
            sporadic=applied,
        )

    def _apply_sporadic(self, word: Word, trace: list[dict[str, Any]], enabled: bool) -> tuple[Word, list[str]]:
        """Apply the profile's irregular laws when ``enabled``, recording each one that changes the word."""
        applied: list[str] = []
        for law in self.profile.sporadic_laws if enabled else ():
            before = word.phonemic()
            word = law.apply(word, self.profile.inventory)
            if word.phonemic() != before:
                trace.append({"sporadic": law.law_id, "name": law.name, "before": before, "after": word.phonemic()})
                applied.append(law.law_id)
        return word, applied

    # ------------------------------------------------------------------ orthography

    def _render(self, word: Word) -> tuple[str, str]:
        """Return (formal, informal) spellings.

        Formal: scribal-era compound junctions are written with an apostrophe,
        and an element after one is capitalized when it is itself a lineage
        name (Vel'Rynn) but not when it is a common noun (T'karas).
        Informal: the apostrophe is dropped and the word written solid.
        """
        chunks = self._written_chunks(word)
        formal_parts = [chunks[0][0].capitalize()]
        formal_parts += [text.capitalize() if morph.lineage else text for text, morph in chunks[1:]]
        return "'".join(formal_parts), "".join(text for text, _ in chunks).capitalize()

    def _written_chunks(self, word: Word) -> list[tuple[str, Morph]]:
        """Split a word at its apostrophe junctions: (spelling, morph that opens the chunk)."""
        texts: list[list[str]] = []
        openers: list[Morph] = []
        start_new = True
        for token in word.tokens:
            if isinstance(token, Boundary):
                start_new = start_new or self._written_junction(token)
                continue
            if start_new:
                texts.append([])
                openers.append(word.morphs[token.morph])
                start_new = False
            texts[-1].append(token.phoneme.grapheme)
        return [("".join(text), morph) for text, morph in zip(texts, openers)]

    def _written_junction(self, boundary: Boundary) -> bool:
        """Compound junctions formed on or after the scribal reform are written with an apostrophe."""
        return boundary.kind == "compound" and boundary.formed_at >= self.profile.reform_date

    # ------------------------------------------------------------------ corpus fit

    def fit_attested(self, *, include_fixtures: bool = False) -> list[dict[str, Any]]:
        """Derive every corpus row and compare spelling, informal form and legality.

        Rows from ``names`` are canon evidence (tier ``canon``). With
        ``include_fixtures``, non-canon regression targets follow (tier ``fixture``).
        """
        rows = [("canon", row) for row in self.profile.attested]
        if include_fixtures:
            rows += [("fixture", row) for row in self.profile.fixtures]
        return [self._fit_row(tier, row) for tier, row in rows]

    def _fit_row(self, tier: str, row: Mapping[str, Any]) -> dict[str, Any]:
        derived = self.derive(row["roots"], row["era"], dialect=row.get("dialect"))
        spelled = derived.formal == row["formal"] and row.get("informal", derived.informal) == derived.informal
        return {
            "tier": tier,
            "attested": row["formal"],
            "attested_informal": row.get("informal"),
            "derived": derived.formal,
            "derived_informal": derived.informal,
            "proto": "*" + derived.proto,
            "era": row["era"],
            "dialect": derived.dialect,
            "legal": derived.legal,
            "match": spelled and derived.legal,
            "evidence": row.get("evidence"),
            "source": row.get("source") or row.get("reason"),
        }

    # ------------------------------------------------------------------ generation

    def generate(
        self,
        lineage: str,
        *,
        seed: int,
        count: int = 6,
        eras: Sequence[str] | None = None,
        dialect: str | None = None,
        registry: Any | None = None,
        weighted: bool = False,
        sporadic: bool = True,
    ) -> list[Derivation]:
        """Deterministically propose house names for a lineage class.

        ``dialect`` defaults to the lineage's own (``lexicon.json``); pass
        ``"common"`` for the undivided language. With ``registry`` (a
        ``naming.NameRegistry``), BLOCK-level collisions are dropped. ``weighted``
        ranks a wider pool by how Velari each name sounds; ``sporadic`` lets the
        profile's irregular laws strike a seeded share of candidates.
        """
        spec = self._lineage(lineage)
        pool = [(p, c, e) for p in spec.roots for c in self.profile.content_roots for e in (eras or spec.eras)]
        opts = GenerationOptions(dialect or spec.dialect, registry, weighted, sporadic)
        return self._pick(pool, f"house|{lineage}|{seed}", count, opts)

    def generate_given_names(
        self,
        *,
        seed: int,
        count: int = 6,
        eras: Sequence[str] | None = None,
        dialect: str | None = None,
        registry: Any | None = None,
        weighted: bool = False,
        sporadic: bool = True,
    ) -> list[Derivation]:
        """Deterministically propose given names: a content root plus a personal suffix."""
        allowed = eras or tuple(self.profile.eras)
        pool = [(c, s, e) for c in self.profile.content_roots for s in self.profile.personal_suffixes for e in allowed]
        opts = GenerationOptions(dialect, registry, weighted, sporadic)
        return self._pick(pool, f"given|{seed}", count, opts)

    def _lineage(self, lineage: str) -> Lineage:
        if lineage not in self.profile.lineages:
            raise KeyError(f"unknown lineage {lineage!r}; known: {sorted(self.profile.lineages)}")
        return self.profile.lineages[lineage]

    def _pick(
        self, pool: list[tuple[str, str, str]], tag: str, count: int, opts: "GenerationOptions"
    ) -> list[Derivation]:
        """Shuffle the pool by seed, keep the first admissible names, optionally ranked by sound."""
        # Deterministic, seeded shuffle for reproducible naming; not used for security.
        random.Random(int(self._hash(tag)[:16], 16)).shuffle(pool)  # nosec B311
        want = count * WEIGHTED_POOL_FACTOR if opts.weighted else count
        out = self._first_admissible(pool, tag, want, opts)
        if opts.weighted:
            out = sorted(out, key=lambda d: -d.euphony)[:count]
        return out

    def _first_admissible(
        self, pool: list[tuple[str, str, str]], tag: str, want: int, opts: "GenerationOptions"
    ) -> list[Derivation]:
        out: list[Derivation] = []
        seen: set[str] = set()
        for first, second, era in pool:
            hit = opts.sporadic and self._sporadic_hit(tag, first, second, era)
            derived = self.derive((first, second), era, dialect=opts.dialect, sporadic=hit)
            key = derived.informal.lower()
            if key in seen or not _admissible(derived, opts.registry):
                continue
            seen.add(key)
            out.append(derived)
            if len(out) >= want:
                break
        return out

    def _hash(self, *parts: str) -> str:
        return hashlib.sha256("|".join((ENGINE_VERSION, self.profile.digest, *parts)).encode()).hexdigest()

    def _sporadic_hit(self, *parts: str) -> bool:
        """A seeded, reproducible draw: does an irregular change strike this candidate?"""
        if not self.profile.sporadic_laws:
            return False
        return int(self._hash("sporadic", *parts)[:8], 16) / 0xFFFFFFFF < self.profile.sporadic_rate


WEIGHTED_POOL_FACTOR = 4


@dataclass(frozen=True)
class GenerationOptions:
    dialect: str | None = None
    registry: Any | None = None
    weighted: bool = False
    sporadic: bool = True


def _admissible(derived: Derivation, registry: Any | None) -> bool:
    """Legal phonotactics and, when a registry is given, no BLOCK-level collision."""
    if not derived.legal:
        return False
    if registry is None:
        return True
    derived.findings = registry.evaluate(derived.formal)
    return not any(f.get("level") == "BLOCK" for f in derived.findings)


def _partition(laws: Sequence[SoundLaw], formed_at: int) -> tuple[list[SoundLaw], list[SoundLaw]]:
    """Laws before a compound's formation date, and laws from that date on."""
    early = [law for law in laws if law.date < formed_at]
    return early, list(laws[len(early) :])  # laws are sorted by date


def _first_lineage(used: Sequence[Root]) -> str | None:
    return next((r.lineage for r in used if r.lineage), None)


def _show(pieces: Sequence[Word]) -> str:
    return " · ".join(p.phonemic() for p in pieces)


def _record(trace: list[dict[str, Any]], law: SoundLaw, before: str, after: str) -> None:
    if after != before:
        trace.append({"law": law.law_id, "name": law.name, "date": law.date, "era": law.era,
                      "before": before, "after": after})  # fmt: skip


def shared_roots(a: Derivation, b: Derivation) -> set[str]:
    """Radicals two derivations share. Non-empty means a resemblance is cognate, not crowding.

    Entries derived from one radical in different ablaut grades (warna, warena)
    share it, so Varn- and -Varen names are recognised as kin.
    """
    return set(a.radicals) & set(b.radicals)
