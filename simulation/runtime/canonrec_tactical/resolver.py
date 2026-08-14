"""Deterministic CanonRec tactical input resolution for GUMAS.

A resolver instance reads only a clean local CanonRec checkout pinned to an exact
commit. No network or language-model judgment is part of runtime resolution.
Qualitative canon is translated through explicit, versioned integer tables.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

RESOLVER_VERSION = "1.0.1"
DERIVATION_VERSION = "canonrec-tactical-derivation-v1.1"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"

CAPABILITY_KEYS: Tuple[str, ...] = (
    "firepower", "defense", "mobility", "sensors", "stealth",
    "electronic_warfare", "carrier_projection", "support", "boarding",
    "command", "range", "endurance",
)
DOCTRINE_KEYS: Tuple[str, ...] = (
    "coordination", "centralization", "ai_integration", "aggression",
    "defensive_bias", "diplomatic_restraint", "boarding_preference",
    "risk_tolerance",
)

ROLE_PROFILES: Mapping[str, Mapping[str, int]] = {
    "flagship": {"firepower": 720, "defense": 760, "mobility": 430, "sensors": 720, "stealth": 220, "electronic_warfare": 620, "carrier_projection": 420, "support": 520, "boarding": 440, "command": 920, "range": 720, "endurance": 820},
    "fortress": {"firepower": 790, "defense": 940, "mobility": 180, "sensors": 600, "stealth": 120, "electronic_warfare": 470, "carrier_projection": 260, "support": 520, "boarding": 300, "command": 560, "range": 700, "endurance": 900},
    "dreadnought": {"firepower": 920, "defense": 900, "mobility": 240, "sensors": 620, "stealth": 110, "electronic_warfare": 460, "carrier_projection": 300, "support": 300, "boarding": 430, "command": 650, "range": 760, "endurance": 900},
    "carrier": {"firepower": 560, "defense": 670, "mobility": 380, "sensors": 690, "stealth": 180, "electronic_warfare": 560, "carrier_projection": 930, "support": 700, "boarding": 350, "command": 680, "range": 730, "endurance": 820},
    "heavy_combatant": {"firepower": 760, "defense": 760, "mobility": 430, "sensors": 550, "stealth": 220, "electronic_warfare": 420, "carrier_projection": 220, "support": 300, "boarding": 390, "command": 480, "range": 650, "endurance": 700},
    "frigate_escort": {"firepower": 520, "defense": 560, "mobility": 690, "sensors": 650, "stealth": 360, "electronic_warfare": 500, "carrier_projection": 180, "support": 370, "boarding": 300, "command": 390, "range": 520, "endurance": 560},
    "interceptor_patrol": {"firepower": 440, "defense": 410, "mobility": 900, "sensors": 720, "stealth": 500, "electronic_warfare": 430, "carrier_projection": 100, "support": 220, "boarding": 240, "command": 330, "range": 430, "endurance": 430},
    "stealth_combatant": {"firepower": 610, "defense": 470, "mobility": 730, "sensors": 740, "stealth": 930, "electronic_warfare": 760, "carrier_projection": 120, "support": 220, "boarding": 620, "command": 430, "range": 590, "endurance": 590},
    "special_operations": {"firepower": 500, "defense": 450, "mobility": 760, "sensors": 800, "stealth": 880, "electronic_warfare": 820, "carrier_projection": 180, "support": 500, "boarding": 860, "command": 520, "range": 610, "endurance": 650},
    "logistics_support": {"firepower": 230, "defense": 520, "mobility": 430, "sensors": 520, "stealth": 200, "electronic_warfare": 380, "carrier_projection": 180, "support": 950, "boarding": 120, "command": 420, "range": 590, "endurance": 950},
}

ROLE_RULES: Tuple[Tuple[Tuple[str, ...], str], ...] = (
    (("flagship", "command ship"), "flagship"),
    (("fortress", "bastion"), "fortress"),
    (("dreadnought",), "dreadnought"),
    (("carrier",), "carrier"),
    (("special operations", "marshal", "operative"), "special_operations"),
    (("stealth", "infiltration", "recon", "reconnaissance"), "stealth_combatant"),
    (("interceptor", "patrol", "pursuit", "skirmishing"), "interceptor_patrol"),
    (("frigate", "escort"), "frigate_escort"),
    (("logistics", "support", "repair", "medical"), "logistics_support"),
    (("cruiser", "battlecruiser", "destroyer", "combatant", "battleship"), "heavy_combatant"),
)

FEATURE_RULES: Tuple[Tuple[Tuple[str, ...], Mapping[str, int]], ...] = (
    (("rail", "railgun", "railguns", "rail cannon", "rail cannons", "heavy weapon", "plasma", "heavy cannon"), {"firepower": 90, "range": 55}),
    (("missile", "missiles", "torpedo", "torpedoes"), {"firepower": 65, "range": 75}),
    (("point defense", "point defenses"), {"defense": 75, "sensors": 30}),
    (("adaptive shield", "adaptive shielding"), {"defense": 105, "endurance": 35}),
    (("shield", "shields", "shielding"), {"defense": 55}),
    (("armor", "armour", "armored", "armoured"), {"defense": 60, "endurance": 35, "mobility": -20}),
    (("stealth", "cloak", "cloaking", "signature suppression"), {"stealth": 120, "sensors": 25}),
    (("sensor", "sensors", "recon", "reconnaissance", "surveillance", "tracking"), {"sensors": 90, "range": 25}),
    (("ai resistant",), {"command": 55, "electronic_warfare": 60}),
    (("ai assisted", "artificial intelligence"), {"sensors": 35, "command": 35}),
    (("fighter", "fighters", "drone bay", "drone bays", "hangar", "hangars", "carrier capacity"), {"carrier_projection": 110, "range": 35}),
    (("repair", "medical", "logistics", "resupply"), {"support": 115, "endurance": 75}),
    (("boarding", "marine", "marines", "sabotage"), {"boarding": 130, "stealth": 20}),
    (("gravitic", "high speed", "pursuit", "maneuver", "maneuverability", "manoeuvre", "manoeuvrability"), {"mobility": 85}),
    (("hyperdrive", "hyperdrives", "long range"), {"range": 90, "endurance": 35}),
    (("command", "coordination"), {"command": 80, "sensors": 20}),
    (("electronic warfare", "jamming", "interdiction", "cyber", "cyberwarfare"), {"electronic_warfare": 110, "sensors": 30}),
    (("reactor linked",), {"defense": 45, "endurance": 50}),
)

DOCTRINE_RULES: Tuple[Tuple[Tuple[str, ...], Mapping[str, int]], ...] = (
    (("federal", "union", "coalition", "council"), {"coordination": 70, "centralization": 20, "diplomatic_restraint": 60}),
    (("consensus", "collective"), {"coordination": 90, "centralization": 70}),
    (("central", "centralized", "command"), {"centralization": 90, "coordination": 45}),
    (("ai", "machine", "algorithm"), {"ai_integration": 180, "coordination": 45}),
    (("precision", "disciplined", "professional"), {"coordination": 75, "risk_tolerance": -25}),
    (("aggressive", "expansion", "offensive", "dominance"), {"aggression": 110, "risk_tolerance": 75, "diplomatic_restraint": -50}),
    (("defense", "defensive", "protection", "stability"), {"defensive_bias": 110, "risk_tolerance": -35}),
    (("diplomacy", "diplomatic", "treaty", "peace"), {"diplomatic_restraint": 110, "aggression": -45}),
    (("boarding", "capture", "infiltration", "sabotage"), {"boarding_preference": 120}),
    (("autonomy", "decentralized"), {"centralization": -90, "risk_tolerance": 40}),
)


class CanonRecResolutionError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    """Encode the v1 Aurora canonical JSON profile used for deterministic hashes."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def normalize_seed64(value: int | str) -> str:
    """Return an unsigned 64-bit seed as a lossless fixed-width hexadecimal string."""
    if isinstance(value, bool):
        raise CanonRecResolutionError("Boolean values are not valid seeds")
    if isinstance(value, int):
        seed = value
    elif isinstance(value, str):
        raw = value.strip().lower()
        try:
            seed = int(raw, 16) if raw.startswith("0x") else int(raw, 10)
        except ValueError as exc:
            raise CanonRecResolutionError(f"Invalid 64-bit seed: {value!r}") from exc
    else:
        raise CanonRecResolutionError(f"Invalid seed type: {type(value).__name__}")
    if not 0 <= seed <= 0xFFFFFFFFFFFFFFFF:
        raise CanonRecResolutionError(f"Seed outside unsigned 64-bit range: {seed}")
    return f"0x{seed:016x}"


def clamp(value: int) -> int:
    return max(0, min(1000, int(value)))


def flatten_text(value: Any) -> List[str]:
    out: List[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, Mapping):
        for key in sorted(value):
            out.extend(flatten_text(value[key]))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            out.extend(flatten_text(item))
    return out


def record_text(record: Mapping[str, Any]) -> str:
    fields = (
        "name", "role", "division", "description", "key_features", "tags",
        "recovered_profile", "government_type", "governance", "government",
        "military_doctrine", "strategic_doctrine", "principles", "traits",
        "capabilities", "notes", "org_type", "nature", "political_evolution",
        "legal_status",
    )
    return " ".join(flatten_text([record.get(key) for key in fields if key in record]))


def normalize_match_text(value: str) -> str:
    """Normalize punctuation/case so semantic rules match whole token phrases only."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def term_matches(text: str, term: str) -> bool:
    """Match a normalized term on token boundaries, never as an arbitrary substring."""
    haystack = normalize_match_text(text)
    needle = normalize_match_text(term)
    if not haystack or not needle:
        return False
    return f" {needle} " in f" {haystack} "


def choose_role_profile(text: str) -> str:
    for needles, profile in ROLE_RULES:
        if any(term_matches(text, needle) for needle in needles):
            return profile
    raise CanonRecResolutionError(
        f"No deterministic role profile for canonical text: {text[:160]!r}"
    )


def apply_rules(
    base: Mapping[str, int],
    text: str,
    rules: Sequence[Tuple[Tuple[str, ...], Mapping[str, int]]],
) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
    values = dict(base)
    fired: List[Dict[str, Any]] = []
    for needles, deltas in rules:
        matches = sorted({needle for needle in needles if term_matches(text, needle)})
        if not matches:
            continue
        applied: Dict[str, int] = {}
        for key, delta in sorted(deltas.items()):
            if key not in values:
                continue
            values[key] = clamp(values[key] + int(delta))
            applied[key] = int(delta)
        if applied:
            fired.append({"matched": matches, "deltas": applied})
    return values, fired


def derive_capability(
    record: Mapping[str, Any], scoped_doctrine_text: str = ""
) -> Dict[str, Any]:
    text = f"{record_text(record)} {scoped_doctrine_text}".strip()
    role_profile = choose_role_profile(text)
    values, fired = apply_rules(ROLE_PROFILES[role_profile], text, FEATURE_RULES)
    return {
        "values": values,
        "provenance": "DERIVED_FROM_CANON",
        "derivation_version": DERIVATION_VERSION,
        "role_profile": role_profile,
        "rules_fired": fired,
    }


def derive_doctrine(record: Mapping[str, Any]) -> Dict[str, Any]:
    base = {key: 500 for key in DOCTRINE_KEYS}
    values, fired = apply_rules(base, record_text(record), DOCTRINE_RULES)
    return {
        "values": values,
        "provenance": "DERIVED_FROM_CANON",
        "derivation_version": DERIVATION_VERSION,
        "rules_fired": fired,
    }


def canonical_certainty(record: Mapping[str, Any]) -> str:
    """Return canonical certainty without confusing lifecycle status with canon status."""
    for key in ("certainty", "canonical_status"):
        value = str(record.get(key) or "").strip().upper()
        if value:
            return value
    legacy = str(record.get("status") or "").strip().upper()
    if legacy in {"CANON", "STAGING", "NONCANON", "NON_CANON", "REJECTED"}:
        return legacy
    return ""


def canonical_record_id(record: Mapping[str, Any]) -> str:
    return str(record.get("entity_id") or record.get("id") or "").strip()


class CanonRecTacticalResolver:
    """Resolve tactical manifests from a clean, exact CanonRec checkout."""

    def __init__(self, canonrec_root: str | Path, source_set: Mapping[str, Any]):
        self.root = Path(canonrec_root).resolve()
        self.source_set = dict(source_set)
        self.expected_commit = str(self.source_set["canonrec_commit"])
        actual = self._git("rev-parse", "HEAD")
        if actual != self.expected_commit:
            raise CanonRecResolutionError(
                f"CanonRec HEAD {actual} != pinned {self.expected_commit}"
            )
        if self._git("status", "--porcelain", "--untracked-files=no"):
            raise CanonRecResolutionError("CanonRec checkout must be clean")
        self._records: Dict[str, Dict[str, Any]] = {}
        self._source_refs: Dict[str, Dict[str, str]] = {}
        self._doctrine_sources: List[Dict[str, Any]] = []
        self._load_sources()
        self.source_set_sha256 = sha256_json(self._source_refs)

    @classmethod
    def from_files(
        cls, canonrec_root: str | Path, source_set_path: str | Path
    ) -> "CanonRecTacticalResolver":
        return cls(
            canonrec_root,
            json.loads(Path(source_set_path).read_text(encoding="utf-8")),
        )

    def _git(self, *args: str) -> str:
        try:
            return subprocess.check_output(
                ["git", "-C", str(self.root), *args], text=True
            ).strip()
        except subprocess.CalledProcessError as exc:
            raise CanonRecResolutionError(
                f"Git verification failed: {' '.join(args)}"
            ) from exc

    def _load_sources(self) -> None:
        for entry in sorted(
            self.source_set.get("sources", []), key=lambda item: item["path"]
        ):
            rel = str(entry["path"])
            path = self.root / rel
            if not path.is_file():
                raise CanonRecResolutionError(f"Pinned CanonRec source missing: {rel}")
            raw = path.read_bytes()
            ref = {
                "path": rel,
                "git_blob_sha": self._git("rev-parse", f"HEAD:{rel}"),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
            self._source_refs[rel] = ref
            kind = str(entry["kind"])
            if rel.endswith(".json"):
                data: Any = json.loads(raw.decode("utf-8"))
            elif rel.endswith(".csv"):
                data = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
            else:
                raise CanonRecResolutionError(
                    f"Unsupported CanonRec source type: {rel}"
                )
            if kind in {"organization", "polity", "ship_class"}:
                if not isinstance(data, Mapping):
                    raise CanonRecResolutionError(
                        f"Canonical record is not an object: {rel}"
                    )
                record_id = canonical_record_id(data)
                if not record_id:
                    raise CanonRecResolutionError(f"Canonical record has no id: {rel}")
                expected_id = str(entry.get("id") or "").strip()
                if expected_id and record_id != expected_id:
                    raise CanonRecResolutionError(
                        f"Canonical record id mismatch in {rel}: {record_id} != {expected_id}"
                    )
                if record_id in self._records:
                    raise CanonRecResolutionError(
                        f"Duplicate canonical record id in pinned source set: {record_id}"
                    )
                self._records[record_id] = {
                    "record": dict(data),
                    "source": ref,
                    "kind": kind,
                }
            elif kind == "scoped_doctrine":
                self._doctrine_sources.append(
                    {
                        "data": data,
                        "source": ref,
                        "scope": tuple(
                            sorted(
                                normalize_match_text(str(value))
                                for value in entry.get("scope", [])
                                if normalize_match_text(str(value))
                            )
                        ),
                    }
                )

    @staticmethod
    def _status(record: Mapping[str, Any]) -> str:
        return canonical_certainty(record)

    def _record(self, record_id: str) -> Dict[str, Any]:
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise CanonRecResolutionError(
                f"Record not present in pinned source set: {record_id}"
            ) from exc

    @staticmethod
    def _binding_matches(
        class_record: Mapping[str, Any], authority_record: Mapping[str, Any]
    ) -> bool:
        bindings = {
            normalize_match_text(str(value))
            for value in class_record.get("faction_bindings", [])
            if normalize_match_text(str(value))
        }
        if not bindings:
            return True
        authority_tokens = {
            normalize_match_text(str(authority_record.get("entity_id", ""))),
            normalize_match_text(str(authority_record.get("id", ""))),
            normalize_match_text(str(authority_record.get("name", ""))),
            *(
                normalize_match_text(str(value))
                for value in authority_record.get("faction_bindings", [])
            ),
        }
        authority_tokens.discard("")
        for binding in bindings:
            if binding in authority_tokens:
                return True
            if any(
                term_matches(token, binding) or term_matches(binding, token)
                for token in authority_tokens
            ):
                return True
        return False

    def _scoped_doctrine(
        self,
        class_record: Mapping[str, Any],
        authority_record: Mapping[str, Any],
    ) -> Tuple[List[Dict[str, str]], str]:
        scope_text = " ".join(
            (
                str(class_record.get("division", "")),
                str(class_record.get("role", "")),
                str(class_record.get("name", "")),
                str(class_record.get("recovered_profile", "")),
                str(authority_record.get("entity_id", "")),
                str(authority_record.get("id", "")),
                str(authority_record.get("name", "")),
            )
        )
        refs: List[Dict[str, str]] = []
        text: List[str] = []
        for source in self._doctrine_sources:
            if not any(term_matches(scope_text, token) for token in source["scope"]):
                continue
            refs.append(dict(source["source"]))
            text.extend(flatten_text(source["data"]))
        return refs, " ".join(text)

    def resolve_authority(self, authority_id: str) -> Dict[str, Any]:
        holder = self._record(authority_id)
        record = holder["record"]
        status = self._status(record)
        if status and status != "CANON":
            raise CanonRecResolutionError(
                f"Authority {authority_id} is not CANON: {status}"
            )
        direct_numeric = {
            key: value
            for key, value in sorted(record.items())
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }
        payload = {
            "authority_id": authority_id,
            "name": record.get("name"),
            "canonical_status": status or None,
            "source": dict(holder["source"]),
            "identity_provenance": "CANON_DIRECT",
            "direct_numeric_profile": {
                "values": direct_numeric,
                "provenance": "CANON_DIRECT",
            },
            "doctrine_vector": derive_doctrine(record),
        }
        payload["resolution_sha256"] = sha256_json(payload)
        return payload

    def resolve_class(self, class_id: str, authority_id: str) -> Dict[str, Any]:
        holder = self._record(class_id)
        authority_holder = self._record(authority_id)
        record = holder["record"]
        authority = authority_holder["record"]
        status = self._status(record)
        if status and status != "CANON":
            raise CanonRecResolutionError(
                f"Ship class {class_id} is not CANON: {status}"
            )
        if not self._binding_matches(record, authority):
            raise CanonRecResolutionError(
                f"Ship class {class_id} is not bound to authority {authority_id}"
            )
        doctrine_refs, doctrine_text = self._scoped_doctrine(record, authority)
        payload = {
            "class_id": class_id,
            "name": record.get("name"),
            "role": record.get("role"),
            "division": record.get("division"),
            "faction_bindings": sorted(
                str(value) for value in record.get("faction_bindings", [])
            ),
            "canonical_status": status or None,
            "source": dict(holder["source"]),
            "authority_source": dict(authority_holder["source"]),
            "identity_provenance": "CANON_DIRECT",
            "capability_vector": derive_capability(record, doctrine_text),
            "scoped_doctrine_sources": doctrine_refs,
            "scoped_doctrine_provenance": (
                "CANON_SCOPED_DOCTRINE" if doctrine_refs else None
            ),
        }
        payload["resolution_sha256"] = sha256_json(payload)
        return payload

    def resolve_roster(
        self, authority_id: str, roster: Iterable[Mapping[str, Any]]
    ) -> Dict[str, Any]:
        authority = self.resolve_authority(authority_id)
        normalized: List[Dict[str, Any]] = []
        weighted = {key: 0 for key in CAPABILITY_KEYS}
        total = 0
        for entry in sorted(roster, key=lambda item: str(item["class_id"])):
            class_id = str(entry["class_id"])
            count = int(entry["count"])
            if count <= 0:
                raise CanonRecResolutionError(
                    f"Invalid vessel count for {class_id}: {count}"
                )
            resolved = self.resolve_class(class_id, authority_id)
            normalized.append(
                {"class_id": class_id, "count": count, "resolved": resolved}
            )
            total += count
            for key in CAPABILITY_KEYS:
                weighted[key] += count * int(
                    resolved["capability_vector"]["values"][key]
                )
        if total <= 0:
            raise CanonRecResolutionError("Roster is empty")
        aggregate = {key: weighted[key] // total for key in CAPABILITY_KEYS}
        payload = {
            "schema_version": "1.1",
            "resolver_version": RESOLVER_VERSION,
            "derivation_version": DERIVATION_VERSION,
            "canonical_json_profile": CANONICAL_JSON_PROFILE,
            "canonrec_repo": self.source_set["canonrec_repo"],
            "canonrec_commit": self.expected_commit,
            "material_source_set_sha256": self.source_set_sha256,
            "authority": authority,
            "roster": normalized,
            "total_vessels": total,
            "aggregate_capability_vector": {
                "values": aggregate,
                "provenance": "DERIVED_FROM_CANON",
            },
        }
        payload["manifest_sha256"] = sha256_json(payload)
        return payload
