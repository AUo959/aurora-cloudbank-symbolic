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
    digest: str

    @classmethod
    def load(cls, directory: str | Path) -> "Profile":
        directory = Path(directory)
        raw = {part: json.loads((directory / f"{part}.json").read_text(encoding="utf-8"))
               for part in ("inventory", "chronology", "lexicon", "attested")}  # fmt: skip
        inventory = Inventory(raw["inventory"]["phonemes"])
        consonants = [s for s in inventory.symbols() if not inventory[s].feature("syllabic")]
        tactics = syllables.Phonotactics.from_profile(raw["inventory"].get("phonotactics", {}), consonants)
        laws = tuple(sorted((SoundLaw.from_dict(d) for d in raw["chronology"]["laws"]), key=lambda law: law.date))
        if len({law.date for law in laws}) != len(laws):
            raise ValueError("two sound laws share a date; relative order would be ambiguous")
        lexicon = {}
        for key, entry in raw["lexicon"]["roots"].items():
            root = Root(key, entry["proto"], entry["gloss"], entry["gloss_status"], entry.get("kind", "root"),
                        entry.get("lineage"), entry.get("source"))  # fmt: skip
            inventory.parse(root.proto)  # fail fast on symbols outside the inventory
            lexicon[key] = root
        lineages = {
            name: Lineage(name, spec["prefix"], tuple(spec["roots"]), tuple(spec["eras"]))
            for name, spec in raw["lexicon"]["lineages"].items()
            if not name.startswith("_")
        }
        canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"))
        return cls(
            name=directory.name,
            inventory=inventory,
            tactics=tactics,
            laws=laws,
            eras={name: spec["formed_at"] for name, spec in raw["chronology"]["eras"].items()},
            reform_date=raw["chronology"]["orthographic_events"]["scribal_reform"]["date"],
            lexicon=lexicon,
            lineages=lineages,
            content_roots=tuple(raw["lexicon"]["generative_content_roots"]),
            attested=tuple(raw["attested"]["names"]),
            digest=hashlib.sha256(canonical.encode()).hexdigest()[:16],
        )


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

    def derive(self, roots: Sequence[str], era: str | None = None, *, formed_at: int | None = None) -> Derivation:
        missing = [key for key in roots if key not in self.profile.lexicon]
        if missing:
            raise KeyError(f"unknown {self.profile.name} roots: {missing}")
        era, formed_at = self._formation(era, formed_at)
        used = [self.profile.lexicon[key] for key in roots]
        inventory = self.profile.inventory
        pieces = [Word.from_morph(Morph(r.key, r.kind, r.lineage), inventory.parse(r.proto)) for r in used]
        joined: Word | None = Word.join(pieces, formed_at) if len(pieces) == 1 else None
        trace: list[dict[str, Any]] = []

        def show() -> str:
            return joined.phonemic() if joined is not None else " · ".join(p.phonemic() for p in pieces)

        for law in self.profile.laws:
            if joined is None and law.date >= formed_at:
                joined = Word.join(pieces, formed_at)
                trace.append({"event": "compounded", "date": formed_at, "form": joined.phonemic()})
            before = show()
            if joined is not None:
                joined = law.apply(joined, inventory)
            else:
                pieces = [law.apply(p, inventory) for p in pieces]
            after = show()
            if after != before:
                trace.append({"law": law.law_id, "name": law.name, "date": law.date, "era": law.era,
                              "before": before, "after": after})  # fmt: skip
        if joined is None:
            joined = Word.join(pieces, formed_at)
            trace.append({"event": "compounded", "date": formed_at, "form": joined.phonemic()})

        formal, informal = self._render(joined)
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
            lineage=next((r.lineage for r in used if r.lineage), None),
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
        chunks: list[tuple[str, Morph | None]] = []  # (text, morph that opens the chunk)
        current, opener = "", None
        for token in word.tokens:
            if isinstance(token, Boundary):
                if token.kind == "compound" and token.formed_at >= self.profile.reform_date:
                    chunks.append((current, opener))
                    current, opener = "", None
                continue
            if not current and opener is None:
                opener = word.morphs[token.morph]
            current += token.phoneme.grapheme
        chunks.append((current, opener))
        formal_parts = [chunks[0][0].capitalize()]
        for text, morph in chunks[1:]:
            formal_parts.append(text.capitalize() if morph is not None and morph.lineage else text)
        return "'".join(formal_parts), "".join(text for text, _ in chunks).capitalize()

    # ------------------------------------------------------------------ corpus fit

    def fit_attested(self) -> list[dict[str, Any]]:
        report = []
        for row in self.profile.attested:
            derived = self.derive(row["roots"], row["era"])
            ok = derived.formal == row["formal"] and row.get("informal", derived.informal) == derived.informal
            report.append({
                "attested": row["formal"],
                "attested_informal": row.get("informal"),
                "derived": derived.formal,
                "derived_informal": derived.informal,
                "proto": "*" + derived.proto,
                "era": row["era"],
                "match": ok,
                "source": row.get("source"),
            })  # fmt: skip
        return report

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
        if lineage not in self.profile.lineages:
            raise KeyError(f"unknown lineage {lineage!r}; known: {sorted(self.profile.lineages)}")
        spec = self.profile.lineages[lineage]
        allowed_eras = tuple(eras) if eras else spec.eras
        digest = hashlib.sha256(f"{ENGINE_VERSION}|{self.profile.digest}|{lineage}|{seed}".encode()).hexdigest()
        # Deterministic, seeded shuffle for reproducible naming; not used for security.
        rng = random.Random(int(digest[:16], 16))  # nosec B311
        pool = [(p, c, e) for p in spec.roots for c in self.profile.content_roots for e in allowed_eras]
        rng.shuffle(pool)
        out: list[Derivation] = []
        seen: set[str] = set()
        for prefix, content, era in pool:
            derived = self.derive((prefix, content), era)
            key = derived.informal.lower()
            if key in seen or not derived.legal:
                continue
            if registry is not None:
                derived.findings = registry.evaluate(derived.formal)
                if any(f.get("level") == "BLOCK" for f in derived.findings):
                    continue
            seen.add(key)
            out.append(derived)
            if len(out) >= count:
                break
        return out


def shared_roots(a: Derivation, b: Derivation) -> set[str]:
    """Roots two derivations share. Non-empty means a resemblance is cognate, not crowding."""
    return set(a.roots) & set(b.roots)
