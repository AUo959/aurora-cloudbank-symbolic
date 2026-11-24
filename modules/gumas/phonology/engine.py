"""Profile loading, chronology-driven derivation, orthography and generation.

The central mechanism is relative chronology. A compound has a formation
date. Its elements evolve as independent words under every sound law dated
before that date, are joined, and then evolve together under every later law.
So the shape of a compound records when it was coined:

* elder (formed early): junction syncope fuses it, e.g. *wela+kuna > Velkonn
* middle: the linking vowel survives syncope, e.g. Vela-kynn
* scribal (after the scribal reform): the parts were already worn-down words,
  and the junction is written with an apostrophe, e.g. Vel'Rynn, Tal'Varen
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import syllables
from .rules import Boundary, Morph, SoundLaw, Word
from .segments import Inventory

ENGINE_VERSION = "GUMAS_PHONOLOGY_ENGINE_v0.2"
PROFILES_DIR = Path(__file__).resolve().parent / "profiles"


@dataclass(frozen=True)
class Root:
    key: str
    proto: str
    gloss: str
    gloss_status: str
    kind: str = "root"
    lineage: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class Lineage:
    name: str
    prefix: str
    roots: tuple[str, ...]
    eras: tuple[str, ...]


@dataclass(frozen=True)
class Profile:
    name: str
    inventory: Inventory
    tactics: syllables.Phonotactics
    laws: tuple[SoundLaw, ...]
    eras: Mapping[str, int]
    reform_date: int
    lexicon: Mapping[str, Root]
    lineages: Mapping[str, Lineage]
    content_roots: tuple[str, ...]
    attested: tuple[Mapping[str, Any], ...]
    fixtures: tuple[Mapping[str, Any], ...]
    digest: str

    @classmethod
    def load(cls, directory: str | Path) -> "Profile":
        directory = Path(directory)
        raw = _read_profile_files(directory)
        inventory = Inventory(raw["inventory"]["phonemes"])
        chronology = raw["chronology"]
        canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"))
        return cls(
            name=directory.name,
            inventory=inventory,
            tactics=_load_tactics(raw["inventory"], inventory),
            laws=_load_laws(chronology["laws"]),
            eras={name: spec["formed_at"] for name, spec in chronology["eras"].items()},
            reform_date=chronology["orthographic_events"]["scribal_reform"]["date"],
            lexicon=_load_lexicon(raw["lexicon"]["roots"], inventory),
            lineages=_load_lineages(raw["lexicon"]["lineages"]),
            content_roots=tuple(raw["lexicon"]["generative_content_roots"]),
            attested=tuple(raw["attested"]["names"]),
            fixtures=tuple(raw["attested"].get("fixtures", [])),
            digest=hashlib.sha256(canonical.encode()).hexdigest()[:16],
        )


_PROFILE_FILES = ("inventory", "chronology", "lexicon", "attested")


def _read_profile_files(directory: Path) -> dict[str, Any]:
    return {part: json.loads((directory / f"{part}.json").read_text(encoding="utf-8")) for part in _PROFILE_FILES}


def _load_tactics(raw_inventory: Mapping[str, Any], inventory: Inventory) -> syllables.Phonotactics:
    consonants = [s for s in inventory.symbols() if not inventory[s].feature("syllabic")]
    return syllables.Phonotactics.from_profile(raw_inventory.get("phonotactics", {}), consonants)


def _load_laws(raw_laws: Sequence[Mapping[str, Any]]) -> tuple[SoundLaw, ...]:
    laws = tuple(sorted((SoundLaw.from_dict(d) for d in raw_laws), key=lambda law: law.date))
    if len({law.date for law in laws}) != len(laws):
        raise ValueError("two sound laws share a date; relative order would be ambiguous")
    return laws


def _load_lexicon(raw_roots: Mapping[str, Mapping[str, Any]], inventory: Inventory) -> dict[str, Root]:
    lexicon = {}
    for key, entry in raw_roots.items():
        inventory.parse(entry["proto"])  # fail fast on symbols outside the inventory
        lexicon[key] = Root(
            key=key,
            proto=entry["proto"],
            gloss=entry["gloss"],
            gloss_status=entry["gloss_status"],
            kind=entry.get("kind", "root"),
            lineage=entry.get("lineage"),
            source=entry.get("source"),
        )
    return lexicon


def _load_lineages(raw_lineages: Mapping[str, Any]) -> dict[str, Lineage]:
    specs = {name: spec for name, spec in raw_lineages.items() if not name.startswith("_")}
    return {name: Lineage(name, s["prefix"], tuple(s["roots"]), tuple(s["eras"])) for name, s in specs.items()}


@lru_cache(maxsize=None)
def load_profile(name: str) -> Profile:
    return Profile.load(PROFILES_DIR / name)


@dataclass
class Derivation:
    roots: tuple[str, ...]
    era: str | None
    formed_at: int
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
            "era": self.era,
            "formed_at": self.formed_at,
            "proto": "*" + self.proto,
            "phonemic": "/" + self.phonemic + "/",
            "formal": self.formal,
            "informal": self.informal,
            "gloss": self.gloss,
            "gloss_status": self.gloss_status,
            "lineage": self.lineage,
            "trace": self.trace,
        }


class Engine:
    def __init__(self, profile: Profile | str):
        self.profile = load_profile(profile) if isinstance(profile, str) else profile

    # ------------------------------------------------------------------ derivation

    def _formation(self, era: str | None, formed_at: int | None) -> tuple[str | None, int]:
        if formed_at is not None:
            return era, int(formed_at)
        era = era or "elder"
        if era not in self.profile.eras:
            raise KeyError(f"unknown era {era!r}; known: {sorted(self.profile.eras)}")
        return era, self.profile.eras[era]

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

    def _evolve(self, used: Sequence[Root], formed_at: int) -> tuple[Word, list[dict[str, Any]]]:
        """Run the chronology: separate words before ``formed_at``, one word from then on."""
        inventory = self.profile.inventory
        pieces = [Word.from_morph(Morph(r.key, r.kind, r.lineage), inventory.parse(r.proto)) for r in used]
        early, late = _partition(self.profile.laws, formed_at)
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

    def derive(self, roots: Sequence[str], era: str | None = None, *, formed_at: int | None = None) -> Derivation:
        used = self._lookup(roots)
        era, formed_at = self._formation(era, formed_at)
        joined, trace = self._evolve(used, formed_at)
        formal, informal = self._render(joined)
        lineages = [r.lineage for r in used if r.lineage]
        return Derivation(
            roots=tuple(roots),
            era=era,
            formed_at=formed_at,
            proto=self._proto(used, formed_at),
            phonemic=joined.phonemic(),
            formal=formal,
            informal=informal,
            gloss=" + ".join(r.gloss for r in used),
            gloss_status=[r.gloss_status for r in used],
            lineage=lineages[0] if lineages else None,
            trace=trace,
            phonotactic_problems=syllables.check(joined.segments(), self.profile.tactics),
            profile=self.profile.name,
            profile_digest=self.profile.digest,
        )

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
        derived = self.derive(row["roots"], row["era"])
        spelled = derived.formal == row["formal"] and row.get("informal", derived.informal) == derived.informal
        return {
            "tier": tier,
            "attested": row["formal"],
            "attested_informal": row.get("informal"),
            "derived": derived.formal,
            "derived_informal": derived.informal,
            "proto": "*" + derived.proto,
            "era": row["era"],
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
        registry: Any | None = None,
    ) -> list[Derivation]:
        """Deterministically propose names for a lineage class.

        With ``registry`` (a ``naming.NameRegistry``), candidates carry collision
        findings and BLOCK-level candidates are dropped.
        """
        out: list[Derivation] = []
        seen: set[str] = set()
        for prefix, content, era in self._candidate_pool(lineage, seed, eras):
            derived = self.derive((prefix, content), era)
            key = derived.informal.lower()
            if key in seen or not _admissible(derived, registry):
                continue
            seen.add(key)
            out.append(derived)
            if len(out) >= count:
                break
        return out

    def _candidate_pool(self, lineage: str, seed: int, eras: Sequence[str] | None) -> list[tuple[str, str, str]]:
        """Every (lineage root, content root, era) combination, in a seed-determined order."""
        if lineage not in self.profile.lineages:
            raise KeyError(f"unknown lineage {lineage!r}; known: {sorted(self.profile.lineages)}")
        spec = self.profile.lineages[lineage]
        allowed_eras = tuple(eras) if eras else spec.eras
        pool = [(p, c, e) for p in spec.roots for c in self.profile.content_roots for e in allowed_eras]
        digest = hashlib.sha256(f"{ENGINE_VERSION}|{self.profile.digest}|{lineage}|{seed}".encode()).hexdigest()
        # Deterministic, seeded shuffle for reproducible naming; not used for security.
        random.Random(int(digest[:16], 16)).shuffle(pool)  # nosec B311
        return pool


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


def _show(pieces: Sequence[Word]) -> str:
    return " · ".join(p.phonemic() for p in pieces)


def _record(trace: list[dict[str, Any]], law: SoundLaw, before: str, after: str) -> None:
    if after != before:
        trace.append({"law": law.law_id, "name": law.name, "date": law.date, "era": law.era,
                      "before": before, "after": after})  # fmt: skip


def shared_roots(a: Derivation, b: Derivation) -> set[str]:
    """Roots two derivations share. Non-empty means a resemblance is cognate, not crowding."""
    return set(a.roots) & set(b.roots)
