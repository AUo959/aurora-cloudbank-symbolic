"""Diachronic phonology prototype for Velari names (velar_imperium).

PROTOTYPE. The current NameService joins syllable chunks from a fixed list.
This module derives Velari names instead: a proto-form is built from roots
that carry meaning, then pushed through an ordered list of deterministic
sound laws. Every output carries its derivation trace.

The canonical spec is the Velar naming convention on
``canon/L2/entities/polities/polity_velar_imperium.json`` (``naming_conventions``):
lineage prefixes Vel- (noble), Varn- (military), Thess- (scholarly),
Rynn- (reformist), Ty- (outworld colonial). The sound laws below are fitted so
that attested canon names come out of the engine unchanged (see ``ATTESTED``),
including two attested informal aliases (``Talvaren``, ``Tkaras``) that the
register rule predicts without being told about them.

Root glosses are prototype hypotheses, not canon. Each root records its
``gloss_status``: ``canon`` (stated in canon), ``inferred`` (implied by canon
context), ``draft`` (invented here), or ``unknown`` (form attested, meaning
not). Generated names still go through the naming gate. This module proposes
forms; it does not admit them.

Orthographic principle: the apostrophe marks one thing, a vowel elided at a
compound junction formed after the Thessari scribal reform. Older ("elder")
compounds fused before the reform and are written solid (Velkonn), while
younger ("scribal") ones keep the mark (Vel'Rynn, Tal'Varen, T'karas).
"""

from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Sequence

ENGINE_VERSION = "VELAR_PHONOLOGY_PROTOTYPE_v0.1"

VOWELS = "aeiouy"
_V = f"[{VOWELS}]"
_C = f"[^{VOWELS}+~'\\-]"

# Internal boundary markers (never rendered as such):
#   "+"  elder compound junction    -> written solid
#   "~"  scribal compound junction  -> written "'" when a vowel was elided there
#   "-"  suffix boundary            -> written solid
_BOUNDARIES = "+~'-"


class Stratum(str, Enum):
    ELDER = "elder"
    SCRIBAL = "scribal"


class Lineage(str, Enum):
    NOBLE = "noble"
    MILITARY = "military"
    SCHOLARLY = "scholarly"
    REFORMIST = "reformist"
    OUTWORLD = "outworld"


@dataclass(frozen=True)
class Root:
    key: str
    proto: str
    gloss: str
    gloss_status: str = "draft"
    lineage: Lineage | None = None
    suffix: bool = False


# fmt: off
LEXICON: dict[str, Root] = {r.key: r for r in (
    # Lineage roots: canonical classes from polity_velar_imperium.naming_conventions.
    Root("wela",   "wela",   "high, elder",          "inferred", Lineage.NOBLE),
    Root("warna",  "warna",  "guard (zero-grade)",   "inferred", Lineage.MILITARY),
    Root("warena", "warena", "guard (full-grade)",   "inferred", Lineage.MILITARY),
    Root("tessa",  "tessa",  "keep, remember",       "inferred", Lineage.SCHOLARLY),
    Root("rina",   "rina",   "voice",                "inferred", Lineage.REFORMIST),
    Root("tu",     "tu",     "outward, far",         "inferred", Lineage.OUTWORLD),
    # Suffixes.
    Root("ari",    "ari",    "people of, ones who",  "draft", suffix=True),
    # Content roots. Attested-only forms are marked unknown.
    Root("kuna",   "kuna",   "flame",                "inferred"),  # House Velkonn; "Sira of Flamewake"
    Root("tala",   "tala",   "stand fast",           "draft"),
    Root("ta",     "ta",     "that, the (demonstrative)", "draft"),
    Root("karasa", "karasa", "hold, fortress",       "draft"),
    Root("karisa", "karisa", "(unknown)",            "unknown"),   # Velkaris
    Root("rena",   "rena",   "(unknown)",            "unknown"),   # Tyren
    Root("mara",   "mara",   "(unknown)",            "unknown"),   # Tymar
    Root("tura",   "tura",   "(unknown)",            "unknown"),   # Tyr
    Root("sela",   "sela",   "star",                 "draft"),
    Root("dura",   "dura",   "stone",                "draft"),
    Root("lira",   "lira",   "song",                 "draft"),
    Root("hesa",   "hesa",   "night",                "draft"),
    Root("mora",   "mora",   "deep",                 "draft"),
    Root("ketha",  "ketha",  "blade",                "draft"),     # cf. legacy chunk 'keth
    Root("drena",  "drena",  "watch",                "draft"),     # cf. legacy chunk 'dren
    Root("syra",   "syra",   "silver",               "draft"),     # cf. legacy chunk 'syr
    Root("vakara", "vakara", "oath",                 "draft"),     # cf. legacy chunk 'vakar
    Root("nima",   "nima",   "river",                "draft"),
    Root("lunda",  "lunda",  "harbor",               "draft"),
)}
# fmt: on

LINEAGE_ROOTS: dict[Lineage, tuple[str, ...]] = {
    Lineage.NOBLE: ("wela",),
    Lineage.MILITARY: ("warna",),
    Lineage.SCHOLARLY: ("tessa",),
    Lineage.REFORMIST: ("rina",),
    Lineage.OUTWORLD: ("tu",),
}

GENERATIVE_CONTENT_ROOTS: tuple[str, ...] = (
    "kuna", "karasa", "sela", "dura", "lira", "hesa", "mora",
    "ketha", "drena", "syra", "vakara", "nima", "lunda",
)  # fmt: skip


# --------------------------------------------------------------------------- sound laws


@dataclass(frozen=True)
class SoundLaw:
    law_id: str
    name: str
    description: str
    apply: Callable[[str], str]


def _sub(pattern: str, repl: str) -> Callable[[str], str]:
    compiled = re.compile(pattern)
    return lambda form: compiled.sub(repl, form)


def _syllables(text: str) -> int:
    return len(re.findall(f"{_V}+", text))


def _apocope(form: str) -> str:
    plain = re.sub(f"[{re.escape(_BOUNDARIES)}]", "", form)
    if _syllables(plain) >= 2 and re.search(f"{_C}a$", form):
        return form[:-1]
    return form


SOUND_LAWS: tuple[SoundLaw, ...] = (
    SoundLaw("VL1", "w-fortition", "*w > v at the start of a morpheme",
             _sub(r"(^|[+~\-])w", r"\1v")),
    SoundLaw("VL2", "t-aspiration", "*t > th at the start of a morpheme before e",
             _sub(r"(^|[+~\-])te", r"\1the")),
    SoundLaw("VL3", "u-fronting", "*u > y in the word's first syllable",
             _sub(r"^([^aeiouy+~\-]*)u", r"\1y")),
    SoundLaw("VL4", "junction elision",
             "stem-final *a is lost at a junction; at a scribal junction the loss is written '",
             lambda f: re.sub(r"a([+\-])", r"\1", re.sub(r"a~", "'", f))),
    SoundLaw("VL5", "apocope", "word-final *a is lost after a consonant in words of 2+ syllables", _apocope),
    SoundLaw("VL6", "high-vowel gemination",
             "n doubles after *i or *u when it ends an element (compensation for the lost vowel)",
             _sub(r"(?<=[iu])n(?=$|[+~'\-])", "nn")),
    SoundLaw("VL7", "u-lowering", "remaining *u > o", _sub("u", "o")),
    SoundLaw("VL8", "i-rounding", "i > y before nn", _sub(r"i(?=nn)", "y")),
)  # fmt: skip


# --------------------------------------------------------------------------- derivation


@dataclass(frozen=True)
class CompoundSpec:
    roots: tuple[str, ...]
    stratum: Stratum = Stratum.ELDER

    def proto(self) -> str:
        joiner = "+" if self.stratum is Stratum.ELDER else "~"
        out = ""
        for index, key in enumerate(self.roots):
            root = LEXICON[key]
            if index:
                out += "-" if root.suffix else joiner
            out += root.proto
        return out


@dataclass
class VelarForm:
    spec: CompoundSpec
    proto: str
    formal: str
    informal: str
    gloss: str
    gloss_status: list[str]
    lineage: Lineage | None
    trace: list[dict[str, str]] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def receipt(self) -> dict[str, Any]:
        """Derivation block suitable for embedding in a naming receipt."""
        return {
            "engine": ENGINE_VERSION,
            "roots": list(self.spec.roots),
            "stratum": self.spec.stratum.value,
            "proto": "*" + self.proto,
            "formal": self.formal,
            "informal": self.informal,
            "gloss": self.gloss,
            "gloss_status": self.gloss_status,
            "lineage": self.lineage.value if self.lineage else None,
            "trace": self.trace,
        }


def _render(form: str, spec: CompoundSpec) -> tuple[str, str]:
    """Return (formal, informal) written forms."""
    # Elements after a written apostrophe are capitalized only when they are
    # themselves lineage names (Vel'Rynn, Tal'Varen) and not common nouns (T'karas).
    parts = form.replace("+", "").replace("~", "").replace("-", "").split("'")
    content = [LEXICON[k] for k in spec.roots if not LEXICON[k].suffix]
    formal_parts = [parts[0].capitalize()]
    for offset, part in enumerate(parts[1:], start=1):
        root = content[offset] if offset < len(content) else None
        formal_parts.append(part.capitalize() if root and root.lineage else part)
    formal = "'".join(formal_parts)
    informal = "".join(parts).capitalize()
    return formal, informal


def derive(roots: Sequence[str], stratum: Stratum | str = Stratum.ELDER) -> VelarForm:
    stratum = Stratum(stratum)
    for key in roots:
        if key not in LEXICON:
            raise KeyError(f"unknown Velari root: {key}")
    spec = CompoundSpec(tuple(roots), stratum)
    form = spec.proto()
    trace: list[dict[str, str]] = []
    for law in SOUND_LAWS:
        after = law.apply(form)
        if after != form:
            trace.append({"law": law.law_id, "name": law.name, "before": form, "after": after})
            form = after
    formal, informal = _render(form, spec)
    used = [LEXICON[k] for k in roots]
    lineage = next((r.lineage for r in used if r.lineage), None)
    return VelarForm(
        spec=spec,
        proto=spec.proto(),
        formal=formal,
        informal=informal,
        gloss=" + ".join(r.gloss for r in used),
        gloss_status=[r.gloss_status for r in used],
        lineage=lineage,
        trace=trace,
    )


# --------------------------------------------------------------------------- phonotactics

_ALLOWED_FINAL_CLUSTERS = {"nn", "rn", "th", "rr"}


def phonotactic_ok(written: str) -> bool:
    """Reject forms whose final consonant cluster Velari does not allow."""
    plain = written.lower().replace("'", "")
    tail = re.search(f"[^{VOWELS}]+$", plain)
    if not tail or len(tail.group()) == 1:
        return True
    return tail.group() in _ALLOWED_FINAL_CLUSTERS


# --------------------------------------------------------------------------- attested fit

# Canon names the engine must reproduce. (expected formal, expected informal or None, spec)
ATTESTED: tuple[tuple[str, str | None, CompoundSpec], ...] = (
    ("Velari", None, CompoundSpec(("wela", "ari"))),
    ("Thessari", None, CompoundSpec(("tessa", "ari"))),
    ("Velkonn", None, CompoundSpec(("wela", "kuna"))),
    ("Vel'Rynn", None, CompoundSpec(("wela", "rina"), Stratum.SCRIBAL)),
    ("Tal'Varen", "Talvaren", CompoundSpec(("tala", "warena"), Stratum.SCRIBAL)),
    ("T'karas", "Tkaras", CompoundSpec(("ta", "karasa"), Stratum.SCRIBAL)),
    ("Velkaris", None, CompoundSpec(("wela", "karisa"))),
    ("Rynn", None, CompoundSpec(("rina",))),
    ("Varn", None, CompoundSpec(("warna",))),
    ("Tyren", None, CompoundSpec(("tu", "rena"))),
    ("Tymar", None, CompoundSpec(("tu", "mara"))),
    ("Tyr", None, CompoundSpec(("tura",))),
)


def fit_attested() -> list[dict[str, Any]]:
    report = []
    for expected, expected_informal, spec in ATTESTED:
        form = derive(spec.roots, spec.stratum)
        ok = form.formal == expected and (expected_informal is None or form.informal == expected_informal)
        report.append(
            {
                "attested": expected,
                "attested_informal": expected_informal,
                "derived": form.formal,
                "derived_informal": form.informal,
                "proto": "*" + form.proto,
                "match": ok,
            }
        )
    return report


# --------------------------------------------------------------------------- generation & cognates


def shared_roots(a: VelarForm, b: VelarForm) -> set[str]:
    """Roots two forms share. Non-empty means similar-sounding names are cognates, not crowding."""
    return set(a.spec.roots) & set(b.spec.roots)


def _rng(lineage: Lineage, seed: int) -> random.Random:
    digest = hashlib.sha256(f"{ENGINE_VERSION}|{lineage.value}|{seed}".encode()).hexdigest()
    return random.Random(int(digest[:16], 16))  # nosec B311 - deterministic naming, not security


def generate_house_names(
    lineage: Lineage | str,
    *,
    seed: int,
    count: int = 6,
    stratum: Stratum | str | None = None,
    registry: Any | None = None,
) -> list[VelarForm]:
    """Deterministically propose house names for a canonical lineage class.

    If ``registry`` (a ``naming.NameRegistry``) is given, each candidate carries
    its collision findings and BLOCK-level candidates are dropped.
    """
    lineage = Lineage(lineage)
    rng = _rng(lineage, seed)
    pool = [
        (prefix, content, strat)
        for prefix in LINEAGE_ROOTS[lineage]
        for content in GENERATIVE_CONTENT_ROOTS
        for strat in ((Stratum(stratum),) if stratum else (Stratum.ELDER, Stratum.SCRIBAL))
    ]
    rng.shuffle(pool)
    out: list[VelarForm] = []
    seen: set[str] = set()
    for prefix, content, strat in pool:
        form = derive((prefix, content), strat)
        key = form.informal.lower()
        if key in seen or not phonotactic_ok(form.formal):
            continue
        if registry is not None:
            form.findings = registry.evaluate(form.formal)
            if any(f.get("level") == "BLOCK" for f in form.findings):
                continue
        seen.add(key)
        out.append(form)
        if len(out) >= count:
            break
    return out


def describe(forms: Iterable[VelarForm]) -> list[dict[str, Any]]:
    return [f.receipt() for f in forms]
