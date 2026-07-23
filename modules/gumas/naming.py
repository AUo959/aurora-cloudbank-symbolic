"""Deterministic, collision-aware naming for GUMAS L2 referents.

The service implements the runtime contract documented by
GUMAS_NAMING_PROTOCOL_v0.1. It is deliberately stdlib-only so it can run in
simulation workers, CanonRec tooling, and offline authoring environments.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROTOCOL_VERSION = "GUMAS_NAMING_PROTOCOL_v0.1"
RECEIPT_VERSION = "1.0"


class NameEntityType(str, Enum):
    PERSON = "PERSON"
    FACTION = "FACTION"
    TREATY = "TREATY"
    CONFLICT = "CONFLICT"
    SHIP = "SHIP"
    LOCATION = "LOCATION"
    OPERATION = "OPERATION"
    CUSTOM = "CUSTOM"


class NameRegister(str, Enum):
    FORMAL = "FORMAL"
    INFORMAL = "INFORMAL"
    CALLSIGN = "CALLSIGN"
    BUREAUCRATIC = "BUREAUCRATIC"


@dataclass(frozen=True)
class NameRequest:
    entity_type: NameEntityType
    entity_id: str
    faction_context: str | None = None
    region_context: str | None = None
    register: NameRegister = NameRegister.FORMAL
    constraints: Mapping[str, Any] = field(default_factory=dict)
    seed_hint: int | None = None
    candidate_count: int = 12


@dataclass(frozen=True)
class RegistryEntry:
    canonical_name: str
    entity_id: str
    entity_type: str = "CUSTOM"
    aliases: tuple[str, ...] = ()
    root: str | None = None
    minted_turn: int | None = None


@dataclass
class NameResolution:
    canonical_name: str
    aliases: list[str]
    signature: dict[str, Any]
    rejected_candidates: list[dict[str, Any]]
    collisions_checked: int
    protocol: str = PROTOCOL_VERSION
    receipt_version: str = RECEIPT_VERSION
    request: dict[str, Any] = field(default_factory=dict)
    registry_digest: str = ""
    candidate_set: list[str] = field(default_factory=list)
    selection_mode: str = "generated"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def naming_receipt(self) -> dict[str, Any]:
        """Return the CanonRec-compatible receipt payload."""
        payload = self.to_dict()
        payload["canonical_name"] = self.canonical_name
        return payload


def _strip_marks(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_name(value: str) -> str:
    value = _strip_marks(value).casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def tokenize_name(value: str) -> list[str]:
    value = _strip_marks(value).casefold()
    return [token for token in re.split(r"[^a-z0-9]+", value) if token]


def name_root(value: str) -> str:
    tokens = tokenize_name(value)
    if not tokens:
        return ""
    token = tokens[-1]
    for suffix in ("son", "sen", "ian", "ius", "ara", "orin", "en", "an", "ar"):
        if len(token) - len(suffix) >= 3 and token.endswith(suffix):
            token = token[: -len(suffix)]
            break
    return token[:6]


def phonetic_key(value: str) -> str:
    """Return a conservative cross-faction phonetic crowding key."""
    text = normalize_name(value)
    if not text:
        return ""
    replacements = (
        ("ph", "f"),
        ("th", "t"),
        ("kh", "k"),
        ("q", "k"),
        ("ck", "k"),
        ("c", "k"),
        ("v", "f"),
        ("z", "s"),
        ("ae", "e"),
        ("ai", "e"),
        ("ei", "e"),
        ("y", "i"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    first = text[0]
    tail = re.sub(r"[aeiou]", "", text[1:])
    tail = re.sub(r"(.)\1+", r"\1", tail)
    return (first + tail)[:10]


def cadence_signature(value: str) -> dict[str, Any]:
    tokens = tokenize_name(value)
    return {
        "token_count": len(tokens),
        "token_lengths": [len(token) for token in tokens],
        "vowel_groups": [len(re.findall(r"[aeiouy]+", token)) for token in tokens],
        "initials": "".join(token[0] for token in tokens if token),
        "terminal": tokens[-1][-2:] if tokens else "",
    }


def registry_digest(entries: Iterable[RegistryEntry]) -> str:
    rows = []
    for entry in entries:
        rows.append(
            {
                "canonical_name": entry.canonical_name,
                "entity_id": entry.entity_id,
                "entity_type": entry.entity_type,
                "aliases": sorted(entry.aliases),
            }
        )
    encoded = json.dumps(
        sorted(rows, key=lambda row: (row["canonical_name"].casefold(), row["entity_id"])),
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class NameRegistry:
    """Canonical-name registry with exact, root, phonetic and cadence indexes."""

    def __init__(self, entries: Iterable[RegistryEntry] | None = None):
        self._entries: list[RegistryEntry] = []
        self._by_normalized: dict[str, RegistryEntry] = {}
        self._roots: dict[str, list[RegistryEntry]] = {}
        self._phonetics: dict[str, list[RegistryEntry]] = {}
        self._cadences: dict[str, list[RegistryEntry]] = {}
        self._cooldowns: dict[str, int] = {}
        for entry in entries or ():
            self.reserve_entry(entry)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "NameRegistry":
        raw_entries = data.get("entries", data if isinstance(data, list) else [])
        entries = []
        for raw in raw_entries:
            entries.append(
                RegistryEntry(
                    canonical_name=str(raw["canonical_name"]),
                    entity_id=str(raw.get("entity_id", raw.get("canonical_id", "unknown"))),
                    entity_type=str(raw.get("entity_type", raw.get("entity_kind", "CUSTOM"))).upper(),
                    aliases=tuple(str(alias) for alias in raw.get("aliases", [])),
                    root=raw.get("root"),
                    minted_turn=raw.get("minted_turn"),
                )
            )
        return cls(entries)

    @classmethod
    def from_json(cls, path: str | Path) -> "NameRegistry":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    @property
    def entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(self._entries)

    @property
    def digest(self) -> str:
        return registry_digest(self._entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": PROTOCOL_VERSION,
            "registry_digest": self.digest,
            "entries": [asdict(entry) for entry in self._entries],
        }

    def reserve(self, name: str, entity_ref: Mapping[str, Any] | RegistryEntry) -> None:
        if isinstance(entity_ref, RegistryEntry):
            entry = entity_ref
        else:
            entry = RegistryEntry(
                canonical_name=name,
                entity_id=str(entity_ref.get("entity_id", entity_ref.get("canonical_id", "unknown"))),
                entity_type=str(entity_ref.get("entity_type", entity_ref.get("entity_kind", "CUSTOM"))).upper(),
                aliases=tuple(entity_ref.get("aliases", ())),
            )
        self.reserve_entry(entry)

    def reserve_entry(self, entry: RegistryEntry) -> None:
        normalized = normalize_name(entry.canonical_name)
        if not normalized:
            raise ValueError("Canonical name must contain at least one alphanumeric character")
        existing = self._by_normalized.get(normalized)
        if existing and existing.entity_id != entry.entity_id:
            raise ValueError(f"Name already reserved by {existing.entity_id}: {entry.canonical_name}")
        self._entries.append(entry)
        for name in (entry.canonical_name, *entry.aliases):
            key = normalize_name(name)
            if key:
                self._by_normalized.setdefault(key, entry)
        root = entry.root or name_root(entry.canonical_name)
        if root:
            self._roots.setdefault(root, []).append(entry)
        pkey = phonetic_key(entry.canonical_name)
        if pkey:
            self._phonetics.setdefault(pkey, []).append(entry)
        ckey = json.dumps(cadence_signature(entry.canonical_name), sort_keys=True)
        self._cadences.setdefault(ckey, []).append(entry)

    def cooldown_root(self, root: str, turns: int) -> None:
        self._cooldowns[root.casefold()] = max(0, int(turns))

    def advance_turn(self) -> None:
        expired = []
        for root, turns in self._cooldowns.items():
            remaining = turns - 1
            if remaining <= 0:
                expired.append(root)
            else:
                self._cooldowns[root] = remaining
        for root in expired:
            del self._cooldowns[root]

    def evaluate(self, candidate: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        normalized = normalize_name(candidate)
        if normalized in self._by_normalized:
            entry = self._by_normalized[normalized]
            findings.append(
                {
                    "level": "BLOCK",
                    "kind": "exact",
                    "entity_id": entry.entity_id,
                    "name": entry.canonical_name,
                }
            )

        root = name_root(candidate)
        if root in self._cooldowns:
            findings.append(
                {
                    "level": "BLOCK",
                    "kind": "root_cooldown",
                    "root": root,
                    "turns": self._cooldowns[root],
                }
            )
        for entry in self._roots.get(root, []):
            if normalize_name(entry.canonical_name) != normalized:
                findings.append(
                    {
                        "level": "WARN",
                        "kind": "root",
                        "entity_id": entry.entity_id,
                        "name": entry.canonical_name,
                    }
                )

        pkey = phonetic_key(candidate)
        for entry in self._phonetics.get(pkey, []):
            if normalize_name(entry.canonical_name) != normalized:
                findings.append(
                    {
                        "level": "WARN",
                        "kind": "phonetic",
                        "entity_id": entry.entity_id,
                        "name": entry.canonical_name,
                    }
                )

        ckey = json.dumps(cadence_signature(candidate), sort_keys=True)
        for entry in self._cadences.get(ckey, []):
            if normalize_name(entry.canonical_name) != normalized:
                findings.append(
                    {
                        "level": "WARN",
                        "kind": "cadence",
                        "entity_id": entry.entity_id,
                        "name": entry.canonical_name,
                    }
                )
        return findings


_PERSON_PROFILES: dict[str, dict[str, Sequence[str]]] = {
    "galactic_union": {
        "given_a": ("Ari", "Cael", "Dara", "Eli", "Ilya", "Joren", "Luma", "Neris", "Oren", "Rhea", "Savi", "Tarin", "Vara", "Ysol"),
        "given_b": ("a", "an", "en", "ia", "in", "is", "o", "on", "ra", "us"),
        "surname_a": ("Bren", "Cor", "Dey", "Fenn", "Garan", "Hale", "Iver", "Jast", "Kelm", "Morrow", "Nadir", "Orlan", "Perr", "Quen", "Rusk", "Tal", "Ulan", "Wren"),
        "surname_b": ("", "a", "en", "er", "ik", "in", "or", "us"),
    },
    "velar_imperium": {
        "given_a": ("Tal", "Vey", "Kor", "Rha", "Sel", "Zhar", "Ael", "Dren", "Ith", "Vor"),
        "given_b": ("'varen", "'keth", "'or", "'essa", "'dren", "'kai", "'vakar", "'syr"),
        "surname_a": ("House", "Line", "Ward"),
        "surname_b": (" Veyr", " Khar", " Tal", " Orun", " Sareth"),
    },
    "zyphari_compact": {
        "given_a": ("Zei", "Qira", "Meya", "Tzi", "Ora", "Shaal", "Yae", "Piri"),
        "given_b": ("li", "ra", "ven", "shi", "aya", "orin", "eth"),
        "surname_a": ("Aru", "Bel", "Cira", "Dava", "Eshi", "Fara", "Ilo", "Nemi"),
        "surname_b": ("n", "ra", "vi", "sen", "thel", "yo"),
    },
    "elari_ascendancy": {
        "given_a": ("Ael", "Eli", "Ira", "Lio", "Nae", "Sera", "Thae", "Veli"),
        "given_b": ("rion", "sai", "thiel", "vara", "lune", "mir", "eth"),
        "surname_a": ("Aster", "Celen", "Ilyr", "Lumen", "Oris", "Seren", "Vael"),
        "surname_b": ("", "is", "or", "a", "en", "iel"),
    },
    "vorran_clans": {
        "given_a": ("Brak", "Dorr", "Garn", "Hruk", "Korr", "Marn", "Rukk", "Varr"),
        "given_b": ("", "a", "ek", "or", "un"),
        "surname_a": ("Stone", "Iron", "Ash", "Red", "Deep", "Storm"),
        "surname_b": ("hand", "mark", "scar", "voice", "ward", "born"),
    },
    "shadow_fleet": {
        "given_a": ("Eir", "Nhal", "Oss", "Ruun", "Sey", "Thren", "Va", "Ysil"),
        "given_b": ("a", "en", "ith", "or", "ra", "un"),
        "surname_a": ("",),
        "surname_b": ("",),
    },
}

_SHIP_WORDS = (
    "Arbiter",
    "Continuance",
    "Far Witness",
    "Quiet Measure",
    "Resolute",
    "Second Lantern",
    "Stone Horizon",
    "Unbroken Line",
    "Vigil",
    "Wayfarer",
    "Winter Accord",
    "Last Meridian",
)
_LOCATION_WORDS = (
    "Aster Reach",
    "Cinder Verge",
    "Dawnward",
    "Eidolon Crossing",
    "Far Kharis",
    "Glass Meridian",
    "Harrow Gate",
    "Ilyr Expanse",
    "Nadir Fields",
    "Orison Belt",
    "Pale Concord",
    "Vesper Reach",
)
_OPERATION_WORDS = (
    "Clear Lantern",
    "Far Anchor",
    "Glass Hammer",
    "Long Measure",
    "Open Hand",
    "Quiet Spear",
    "Red Ledger",
    "Second Watch",
    "Stone Thread",
    "Winter Gate",
)
_FACTION_WORDS = (
    "Accord",
    "Assembly",
    "Compact",
    "Concord",
    "Consortium",
    "League",
    "Pact",
    "Synod",
    "Union",
)


class NameService:
    """Resolve stable names against a supplied canonical registry."""

    def __init__(self, registry: NameRegistry | None = None, max_attempts: int = 128):
        self.registry = registry or NameRegistry()
        self.max_attempts = max(8, int(max_attempts))

    def resolve(self, request: NameRequest) -> NameResolution:
        seed = self._seed_for_request(request)
        rng = random.Random(seed)
        candidates: list[str] = []
        rejected: list[dict[str, Any]] = []
        collisions_checked = 0
        warning_budget = int(request.constraints.get("max_warnings", 0))

        for _ in range(self.max_attempts):
            candidate = self._candidate(request, rng)
            if candidate in candidates:
                continue
            candidates.append(candidate)
            findings = self.registry.evaluate(candidate)
            collisions_checked += len(self.registry.entries)
            blocks = [finding for finding in findings if finding["level"] == "BLOCK"]
            warnings = [finding for finding in findings if finding["level"] == "WARN"]
            if blocks or len(warnings) > warning_budget:
                rejected.append({"candidate": candidate, "findings": findings})
                continue

            aliases = self._aliases(candidate, request)
            signature = {
                "normalized": normalize_name(candidate),
                "root": name_root(candidate),
                "phonetic_key": phonetic_key(candidate),
                "cadence": cadence_signature(candidate),
                "seed": seed,
                "warnings": warnings,
            }
            resolution = NameResolution(
                canonical_name=candidate,
                aliases=aliases,
                signature=signature,
                rejected_candidates=rejected[:24],
                collisions_checked=collisions_checked,
                request={
                    "entity_type": request.entity_type.value,
                    "entity_id": request.entity_id,
                    "faction_context": request.faction_context,
                    "region_context": request.region_context,
                    "register": request.register.value,
                    "constraints": dict(request.constraints),
                    "seed_hint": request.seed_hint,
                },
                registry_digest=self.registry.digest,
                candidate_set=candidates[: max(1, request.candidate_count)],
            )
            self.registry.reserve(
                candidate,
                {
                    "entity_id": request.entity_id,
                    "entity_type": request.entity_type.value,
                    "aliases": aliases,
                },
            )
            return resolution

        raise RuntimeError(
            f"Unable to mint a collision-safe name for {request.entity_id} "
            f"after {self.max_attempts} attempts"
        )

    def resolve_candidates(self, request: NameRequest) -> list[NameResolution]:
        """Return a deterministic shortlist without mutating the caller's registry."""
        shortlist: list[NameResolution] = []
        working = NameRegistry(self.registry.entries)
        for index in range(max(1, request.candidate_count)):
            varied = NameRequest(
                entity_type=request.entity_type,
                entity_id=f"{request.entity_id}__candidate_{index}",
                faction_context=request.faction_context,
                region_context=request.region_context,
                register=request.register,
                constraints=request.constraints,
                seed_hint=(request.seed_hint or self._seed_for_request(request)) + index,
                candidate_count=request.candidate_count,
            )
            resolution = NameService(working, self.max_attempts).resolve(varied)
            resolution.request["entity_id"] = request.entity_id
            resolution.selection_mode = "candidate"
            shortlist.append(resolution)
        return shortlist

    @staticmethod
    def select(
        resolutions: Sequence[NameResolution], index: int, entity_id: str
    ) -> NameResolution:
        selected = resolutions[index]
        selected.request["entity_id"] = entity_id
        selected.selection_mode = "owner_selected_from_candidates"
        selected.candidate_set = [resolution.canonical_name for resolution in resolutions]
        return selected

    def _seed_for_request(self, request: NameRequest) -> int:
        if request.seed_hint is not None:
            return int(request.seed_hint)
        material = "|".join(
            [
                PROTOCOL_VERSION,
                request.entity_type.value,
                request.entity_id,
                request.faction_context or "",
                request.region_context or "",
                request.register.value,
                json.dumps(dict(request.constraints), sort_keys=True, default=str),
            ]
        )
        return int(hashlib.sha256(material.encode("utf-8")).hexdigest()[:16], 16)

    def _candidate(self, request: NameRequest, rng: random.Random) -> str:
        forced = request.constraints.get("candidate")
        if forced:
            return str(forced).strip()
        if request.entity_type == NameEntityType.PERSON:
            return self._person_candidate(request, rng)
        if request.entity_type == NameEntityType.SHIP:
            return rng.choice(_SHIP_WORDS)
        if request.entity_type == NameEntityType.LOCATION:
            return rng.choice(_LOCATION_WORDS)
        if request.entity_type == NameEntityType.OPERATION:
            return rng.choice(_OPERATION_WORDS)
        if request.entity_type == NameEntityType.FACTION:
            qualifier = str(
                request.constraints.get(
                    "qualifier", rng.choice(("Free", "Outer", "United", "New", "High"))
                )
            )
            return f"{qualifier} {rng.choice(_FACTION_WORDS)}"
        if request.entity_type == NameEntityType.TREATY:
            place = str(
                request.constraints.get("place", rng.choice(_LOCATION_WORDS).split()[0])
            )
            return f"{place} {rng.choice(('Accord', 'Compact', 'Convention', 'Settlement'))}"
        if request.entity_type == NameEntityType.CONFLICT:
            place = str(
                request.constraints.get("place", rng.choice(_LOCATION_WORDS).split()[0])
            )
            return f"{rng.choice(('War', 'Crisis', 'Rising', 'Interdiction'))} of {place}"
        prefix = str(request.constraints.get("prefix", "Project"))
        return f"{prefix} {rng.choice(_OPERATION_WORDS)}"

    def _person_candidate(self, request: NameRequest, rng: random.Random) -> str:
        profile_key = (request.faction_context or "galactic_union").casefold().replace(
            " ", "_"
        )
        profile = _PERSON_PROFILES.get(
            profile_key, _PERSON_PROFILES["galactic_union"]
        )
        given = rng.choice(profile["given_a"]) + rng.choice(profile["given_b"])
        surname = rng.choice(profile["surname_a"]) + rng.choice(profile["surname_b"])
        if not surname:
            return given
        if profile_key == "velar_imperium" and surname.startswith(
            ("House", "Line", "Ward")
        ):
            return f"{given} of {surname}"
        return f"{given} {surname}"

    @staticmethod
    def _aliases(candidate: str, request: NameRequest) -> list[str]:
        aliases: list[str] = []
        if request.register == NameRegister.BUREAUCRATIC:
            aliases.append(request.entity_id.upper().replace("_", "-"))
        callsign = request.constraints.get("callsign")
        if callsign:
            aliases.append(str(callsign))
        return aliases


def load_registry(path: str | Path | None) -> NameRegistry:
    return NameRegistry.from_json(path) if path else NameRegistry()
