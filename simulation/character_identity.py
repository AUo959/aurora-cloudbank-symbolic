#!/usr/bin/env python3
"""Provenance-bound character identity and historical identifier resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "config" / "l1_character_identity_registry.json"
CANON_PROVENANCE_PATH = PROJECT_ROOT / "config" / "canon_provenance.json"


class CharacterIdentityError(ValueError):
    """Raised when the identity registry violates continuity invariants."""


class QuarantinedIdentityReference(CharacterIdentityError):
    """Raised when a disputed name must not resolve or instantiate a person."""

    def __init__(self, reference: str, possible_referent: Optional[str]) -> None:
        self.reference = reference
        self.possible_referent = possible_referent
        super().__init__(
            f"character reference {reference!r} is quarantined and must not "
            "instantiate a person"
        )


@dataclass(frozen=True)
class IdentifierAssignment:
    identifier: str
    status: str
    sequence: int
    effective_date: str
    roster_version: str
    role: str
    division: str
    clearance: str
    sources: Tuple[Dict[str, str], ...]
    superseded_by: Optional[str]


@dataclass(frozen=True)
class CharacterIdentity:
    entity_key: str
    preferred_name: str
    name_aliases: Tuple[str, ...]
    current_identifier: str
    identity_confidence: str
    identity_authority: Dict[str, str]
    identifiers: Tuple[IdentifierAssignment, ...]

    @property
    def current_assignment(self) -> IdentifierAssignment:
        return next(item for item in self.identifiers if item.status == "current")

    @property
    def historical_identifiers(self) -> Tuple[str, ...]:
        return tuple(
            item.identifier for item in self.identifiers if item.status == "historical"
        )


@dataclass(frozen=True)
class QuarantinedReference:
    reference: str
    normalized_reference: str
    reason: str
    possible_referent: Optional[str]
    sources: Tuple[Dict[str, str], ...]


class CharacterIdentityRegistry:
    """Resolve names and assignment IDs to a stable CanonRec entity key."""

    def __init__(self, registry_path: Optional[Path] = None) -> None:
        self.registry_path = registry_path or DEFAULT_REGISTRY_PATH
        payload = _read_mapping(self.registry_path, "character identity registry")
        self._validate_metadata(payload)
        self.entities = tuple(
            _identity_from_payload(item, index)
            for index, item in enumerate(_list(payload.get("entities"), "entities"))
        )
        self.quarantined_references = tuple(
            _quarantine_from_payload(item, index)
            for index, item in enumerate(
                _list(payload.get("quarantined_references"), "quarantined_references")
            )
        )
        self._validate_entities()
        self._resolved_index = self._build_resolved_index()
        self._quarantine_index = self._build_quarantine_index()
        self._validate_reference_domains()

    def resolve(self, reference: str) -> Optional[CharacterIdentity]:
        """Resolve a stable key, current/historical ID, or known name alias."""
        normalized = normalize_reference(reference)
        quarantine = self._quarantine_index.get(normalized)
        if quarantine is not None:
            raise QuarantinedIdentityReference(
                quarantine.reference,
                quarantine.possible_referent,
            )
        return self._resolved_index.get(normalized)

    def require(self, reference: str) -> CharacterIdentity:
        identity = self.resolve(reference)
        if identity is None:
            raise CharacterIdentityError(f"unknown character identity: {reference!r}")
        return identity

    def history(self, reference: str) -> Tuple[IdentifierAssignment, ...]:
        return self.require(reference).identifiers

    @staticmethod
    def _validate_metadata(payload: Dict[str, Any]) -> None:
        if payload.get("schema_version") != 1:
            raise CharacterIdentityError("unsupported identity registry schema")
        if payload.get("registry_status") != "runtime_projection_non_authoritative":
            raise CharacterIdentityError(
                "identity registry exceeds CloudBank authority"
            )
        authority = _mapping(payload.get("authority_boundary"), "authority_boundary")
        if authority.get("authority_repository") != "AUo959/CanonRec":
            raise CharacterIdentityError(
                "identity authority repository must be CanonRec"
            )
        _validate_authority_revision(authority.get("authority_revision"))

    def _validate_entities(self) -> None:
        entity_keys = [identity.entity_key for identity in self.entities]
        _require_unique(entity_keys, "duplicate stable character entity key")
        preferred = [
            normalize_reference(identity.preferred_name) for identity in self.entities
        ]
        _require_unique(preferred, "duplicate preferred character identity")
        identifiers = [
            assignment.identifier
            for identity in self.entities
            for assignment in identity.identifiers
        ]
        _require_unique(identifiers, "assignment identifier maps to multiple people")
        for identity in self.entities:
            _validate_identity_history(identity)

    def _build_resolved_index(self) -> Dict[str, CharacterIdentity]:
        index: Dict[str, CharacterIdentity] = {}
        for identity in self.entities:
            references = (
                identity.entity_key,
                identity.preferred_name,
                *identity.name_aliases,
                *(item.identifier for item in identity.identifiers),
            )
            for reference in references:
                normalized = normalize_reference(reference)
                existing = index.get(normalized)
                if existing is not None and existing.entity_key != identity.entity_key:
                    raise CharacterIdentityError(
                        f"identity alias {reference!r} maps to multiple people"
                    )
                index[normalized] = identity
        return index

    def _build_quarantine_index(self) -> Dict[str, QuarantinedReference]:
        index: Dict[str, QuarantinedReference] = {}
        for item in self.quarantined_references:
            if item.normalized_reference != normalize_reference(item.reference):
                raise CharacterIdentityError("quarantine normalization is inconsistent")
            if item.normalized_reference in index:
                raise CharacterIdentityError(
                    "duplicate quarantined character reference"
                )
            index[item.normalized_reference] = item
        return index

    def _validate_reference_domains(self) -> None:
        overlap = set(self._resolved_index).intersection(self._quarantine_index)
        if overlap:
            raise CharacterIdentityError(
                "character reference cannot be both resolved and quarantined"
            )


def normalize_reference(reference: str) -> str:
    if not isinstance(reference, str) or not reference.strip():
        raise CharacterIdentityError("character reference must be a non-empty string")
    return " ".join(reference.strip().casefold().split())


def _validate_authority_revision(value: Any) -> None:
    if not isinstance(value, str) or len(value) != 40:
        raise CharacterIdentityError("identity authority revision must be a git SHA")
    provenance = _read_mapping(CANON_PROVENANCE_PATH, "canon provenance")
    surfaces = _list(provenance.get("resolved_surfaces"), "resolved_surfaces")
    staff = next(
        (
            _mapping(item, "resolved_surfaces item")
            for item in surfaces
            if isinstance(item, dict)
            and item.get("name") == "orion_station_staff_registry"
        ),
        None,
    )
    if staff is None or staff.get("authority_revision") != value:
        raise CharacterIdentityError(
            "identity authority revision does not match staff provenance"
        )


def _validate_identity_history(identity: CharacterIdentity) -> None:
    _validate_current_identifier(identity)
    _validate_identifier_sequence(identity)
    identifiers = {item.identifier: item for item in identity.identifiers}
    for item in identity.identifiers:
        _validate_supersession(identity, item, identifiers)


def _validate_current_identifier(identity: CharacterIdentity) -> None:
    current = [item for item in identity.identifiers if item.status == "current"]
    if len(current) != 1 or current[0].identifier != identity.current_identifier:
        raise CharacterIdentityError(
            f"{identity.entity_key} must have exactly one matching current identifier"
        )


def _validate_identifier_sequence(identity: CharacterIdentity) -> None:
    sequences = [item.sequence for item in identity.identifiers]
    if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
        raise CharacterIdentityError(
            f"{identity.entity_key} identifier sequence must be unique and ordered"
        )


def _validate_supersession(
    identity: CharacterIdentity,
    item: IdentifierAssignment,
    identifiers: Dict[str, IdentifierAssignment],
) -> None:
    if item.status == "current" and item.superseded_by is not None:
        raise CharacterIdentityError("current identifier cannot be superseded")
    if item.status == "historical" and item.superseded_by is None:
        raise CharacterIdentityError("historical identifier requires a successor")
    if item.superseded_by is None:
        return
    successor = identifiers.get(item.superseded_by)
    if successor is None or successor.sequence <= item.sequence:
        raise CharacterIdentityError(
            f"{identity.entity_key} identifier supersession is invalid"
        )


def _identity_from_payload(value: Any, index: int) -> CharacterIdentity:
    payload = _mapping(value, f"entities[{index}]")
    return CharacterIdentity(
        entity_key=_string(payload.get("entity_key"), "entity_key"),
        preferred_name=_string(payload.get("preferred_name"), "preferred_name"),
        name_aliases=tuple(
            _string(item, "name_alias")
            for item in _list(payload.get("name_aliases"), "name_aliases")
        ),
        current_identifier=_string(
            payload.get("current_identifier"), "current_identifier"
        ),
        identity_confidence=_string(
            payload.get("identity_confidence"), "identity_confidence"
        ),
        identity_authority=_source(
            payload.get("identity_authority"), "identity_authority"
        ),
        identifiers=tuple(
            _assignment_from_payload(item, assignment_index)
            for assignment_index, item in enumerate(
                _list(payload.get("identifiers"), "identifiers")
            )
        ),
    )


def _assignment_from_payload(value: Any, index: int) -> IdentifierAssignment:
    payload = _mapping(value, f"identifiers[{index}]")
    return IdentifierAssignment(
        identifier=_string(payload.get("identifier"), "identifier"),
        status=_choice(payload.get("status"), {"historical", "current"}, "status"),
        sequence=_positive_integer(payload.get("sequence"), "sequence"),
        effective_date=_string(payload.get("effective_date"), "effective_date"),
        roster_version=_string(payload.get("roster_version"), "roster_version"),
        role=_string(payload.get("role"), "role"),
        division=_string(payload.get("division"), "division"),
        clearance=_string(payload.get("clearance"), "clearance"),
        sources=tuple(
            _source(item, "assignment source")
            for item in _list(payload.get("sources"), "sources")
        ),
        superseded_by=_optional_string(payload.get("superseded_by"), "superseded_by"),
    )


def _quarantine_from_payload(value: Any, index: int) -> QuarantinedReference:
    payload = _mapping(value, f"quarantined_references[{index}]")
    if payload.get("status") != "quarantined_unresolved_reference":
        raise CharacterIdentityError("unsupported character quarantine status")
    if payload.get("must_not_instantiate") is not True:
        raise CharacterIdentityError("quarantined reference must fail closed")
    return QuarantinedReference(
        reference=_string(payload.get("reference"), "reference"),
        normalized_reference=_string(
            payload.get("normalized_reference"), "normalized_reference"
        ),
        reason=_string(payload.get("reason"), "reason"),
        possible_referent=_optional_string(
            payload.get("possible_referent"), "possible_referent"
        ),
        sources=tuple(
            _source(item, "quarantine source")
            for item in _list(payload.get("sources"), "sources")
        ),
    )


def _source(value: Any, name: str) -> Dict[str, str]:
    payload = _mapping(value, name)
    source = {
        field: _string(payload.get(field), f"{name}.{field}")
        for field in ("repository", "path", "claim", "confidence")
    }
    if source["repository"] == "AUo959/aurora-cloudbank-symbolic":
        path = (PROJECT_ROOT / source["path"]).resolve()
        if PROJECT_ROOT not in path.parents or not path.is_file():
            raise CharacterIdentityError(
                f"CloudBank identity source is missing: {path}"
            )
    return source


def _read_mapping(path: Path, name: str) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CharacterIdentityError(f"unable to read {name}: {path}") from exc
    return _mapping(payload, name)


def _mapping(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise CharacterIdentityError(f"{name} must be a JSON object")
    return value


def _list(value: Any, name: str) -> List[Any]:
    if not isinstance(value, list):
        raise CharacterIdentityError(f"{name} must be a JSON array")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CharacterIdentityError(f"{name} must be a non-empty string")
    return value.strip()


def _optional_string(value: Any, name: str) -> Optional[str]:
    if value is None:
        return None
    return _string(value, name)


def _choice(value: Any, choices: set[str], name: str) -> str:
    string = _string(value, name)
    if string not in choices:
        raise CharacterIdentityError(f"unsupported {name}: {string}")
    return string


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise CharacterIdentityError(f"{name} must be a positive integer")
    return value


def _require_unique(values: List[str], message: str) -> None:
    if len(values) != len(set(values)):
        raise CharacterIdentityError(message)


__all__ = [
    "CharacterIdentity",
    "CharacterIdentityError",
    "CharacterIdentityRegistry",
    "IdentifierAssignment",
    "QuarantinedIdentityReference",
    "QuarantinedReference",
    "normalize_reference",
]
