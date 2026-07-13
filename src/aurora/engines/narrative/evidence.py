from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

CANON_AUTHORITY_TIERS = frozenset(
    {"canon", "canonical", "owner_confirmed", "recovered_canon"}
)
CANDIDATE_AUTHORITY_TIERS = frozenset(
    {"draft", "llm_candidate", "operational", "simulation", "staging"}
)
REJECTED_FACT_STATUSES = frozenset({"blocked", "rejected", "superseded"})
INFERRED_FACT_STATUSES = frozenset({"candidate", "inferred", "proposed"})

DEFAULT_SOURCE_POLICY = {
    "promotion_gate": "deterministic_continuity_check_then_owner_review",
    "llm_role": "state_builder_candidate_extractor_only",
}


@dataclass(frozen=True)
class NarrativeEvidenceSource:
    source_id: str
    authority_tier: str
    source_type: str = "fixture"
    uri: str = ""
    observed_at_utc: str = ""
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _canonicalize(asdict(self))


@dataclass(frozen=True)
class NarrativeFact:
    fact_id: str
    claim_type: str
    payload: Mapping[str, Any]
    source_ids: tuple[str, ...] = field(default_factory=tuple)
    authority_tier: str = "draft"
    status: str = "accepted"
    confidence: float = 1.0
    promotion_eligible: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return _canonicalize(asdict(self))


@dataclass(frozen=True)
class NarrativeEvidenceBundle:
    bundle_id: str
    sources: tuple[NarrativeEvidenceSource, ...]
    facts: tuple[NarrativeFact, ...]
    source_policy: Mapping[str, Any] = field(default_factory=dict)
    generated_at_utc: str = "unspecified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "facts": [fact.to_dict() for fact in self.facts],
            "generated_at_utc": self.generated_at_utc,
            "source_policy": _canonicalize(dict(self.source_policy)),
            "sources": [source.to_dict() for source in self.sources],
        }


@dataclass(frozen=True)
class StateBuildReceipt:
    receipt_id: str
    bundle_id: str
    state_id: str
    accepted_fact_ids: tuple[str, ...] = field(default_factory=tuple)
    rejected_fact_ids: tuple[str, ...] = field(default_factory=tuple)
    inferred_fact_ids: tuple[str, ...] = field(default_factory=tuple)
    active_authority_tiers: tuple[str, ...] = field(default_factory=tuple)
    freshness_summary: Mapping[str, Any] = field(default_factory=dict)
    promotion_safety: Mapping[str, Any] = field(default_factory=dict)
    source_policy: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _canonicalize(asdict(self))


@dataclass(frozen=True)
class ContinuityVerdictReceipt:
    receipt_id: str
    state_build_receipt_id: str
    task_kind: str
    verdict: str
    gate_results: Mapping[str, Any] = field(default_factory=dict)
    promotion_safety: Mapping[str, Any] = field(default_factory=dict)

    @property
    def promotion_gate(self) -> str:
        return str(self.gate_results.get("promotion_gate", ""))

    @property
    def gate(self) -> str:
        return self.promotion_gate

    def to_dict(self) -> dict[str, Any]:
        return _canonicalize(asdict(self))


def build_evidence_bundle(
    sources: Iterable[NarrativeEvidenceSource | Mapping[str, Any]],
    facts: Iterable[NarrativeFact | Mapping[str, Any]],
    *,
    source_policy: Mapping[str, Any] | None = None,
    generated_at_utc: str = "unspecified",
) -> NarrativeEvidenceBundle:
    normalized_sources = tuple(
        sorted(
            (_coerce_source(source) for source in sources),
            key=lambda item: item.source_id,
        )
    )
    normalized_facts = tuple(
        sorted((_coerce_fact(fact) for fact in facts), key=lambda item: item.fact_id)
    )
    policy = _merged_source_policy(source_policy)
    canonical_payload = {
        "facts": [fact.to_dict() for fact in normalized_facts],
        "generated_at_utc": generated_at_utc,
        "source_policy": _canonicalize(policy),
        "sources": [source.to_dict() for source in normalized_sources],
    }
    return NarrativeEvidenceBundle(
        bundle_id=_stable_digest(canonical_payload)[:16],
        sources=normalized_sources,
        facts=normalized_facts,
        source_policy=policy,
        generated_at_utc=generated_at_utc,
    )


def promotion_safety_for_bundle(bundle: NarrativeEvidenceBundle) -> dict[str, Any]:
    sources_by_id = {source.source_id: source for source in bundle.sources}
    blocked_fact_ids: list[str] = []
    candidate_fact_ids: list[str] = []
    promotable_fact_ids: list[str] = []
    blocking_tiers: set[str] = set()

    for fact in bundle.facts:
        safety = _promotion_safety_for_fact(fact, sources_by_id)
        if safety is None:
            continue
        if safety["candidate"]:
            candidate_fact_ids.append(fact.fact_id)
        if safety["promotable"]:
            promotable_fact_ids.append(fact.fact_id)
            continue
        if safety["blocked"]:
            blocked_fact_ids.append(fact.fact_id)
            blocking_tiers.update(safety["blocking_tiers"])

    decision = "deterministic_gate_only"
    if blocked_fact_ids:
        decision = "requires_owner_review"

    return {
        "blocked_fact_ids": tuple(sorted(blocked_fact_ids)),
        "blocking_tiers": tuple(sorted(blocking_tiers)),
        "candidate_fact_ids": tuple(sorted(candidate_fact_ids)),
        "canon_promotion_allowed": not blocked_fact_ids,
        "decision": decision,
        "promotable_fact_ids": tuple(sorted(promotable_fact_ids)),
    }


def _promotion_safety_for_fact(
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> dict[str, Any] | None:
    status = fact.status.lower()
    if status in REJECTED_FACT_STATUSES:
        return None

    tiers = _authority_tiers_for_fact(fact, sources_by_id)
    has_candidate_tier = bool(tiers.intersection(CANDIDATE_AUTHORITY_TIERS))
    promotable = fact.promotion_eligible and tiers.issubset(CANON_AUTHORITY_TIERS)
    return {
        "blocked": not promotable and (fact.promotion_eligible or has_candidate_tier),
        "blocking_tiers": {tier for tier in tiers if tier not in CANON_AUTHORITY_TIERS},
        "candidate": status in INFERRED_FACT_STATUSES or has_candidate_tier,
        "promotable": promotable,
    }


def stable_receipt_id(payload: Mapping[str, Any]) -> str:
    return _stable_digest(payload)[:16]


def _coerce_source(
    source: NarrativeEvidenceSource | Mapping[str, Any],
) -> NarrativeEvidenceSource:
    if isinstance(source, NarrativeEvidenceSource):
        return source
    return NarrativeEvidenceSource(
        source_id=str(source["source_id"]),
        authority_tier=str(source.get("authority_tier", "draft")),
        source_type=str(source.get("source_type", "fixture")),
        uri=str(source.get("uri", "")),
        observed_at_utc=str(source.get("observed_at_utc", "")),
        description=str(source.get("description", "")),
        metadata=dict(source.get("metadata", {})),
    )


def _coerce_fact(fact: NarrativeFact | Mapping[str, Any]) -> NarrativeFact:
    if isinstance(fact, NarrativeFact):
        return fact
    return NarrativeFact(
        fact_id=str(fact["fact_id"]),
        claim_type=str(fact["claim_type"]),
        payload=dict(fact.get("payload", {})),
        source_ids=tuple(str(source_id) for source_id in fact.get("source_ids", ())),
        authority_tier=str(fact.get("authority_tier", "draft")),
        status=str(fact.get("status", "accepted")),
        confidence=float(fact.get("confidence", 1.0)),
        promotion_eligible=bool(fact.get("promotion_eligible", False)),
        notes=tuple(str(note) for note in fact.get("notes", ())),
    )


def _merged_source_policy(source_policy: Mapping[str, Any] | None) -> dict[str, Any]:
    policy = dict(DEFAULT_SOURCE_POLICY)
    if source_policy:
        policy.update(dict(source_policy))
    return policy


def _authority_tiers_for_fact(
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> set[str]:
    tiers = {fact.authority_tier}
    tiers.update(
        sources_by_id[source_id].authority_tier
        for source_id in fact.source_ids
        if source_id in sources_by_id
    )
    return tiers


def _stable_digest(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        _canonicalize(payload), sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _canonicalize_mapping(value)
    if isinstance(value, (tuple, list)):
        return _canonicalize_sequence(value)
    if isinstance(value, (frozenset, set)):
        return _canonicalize_set(value)
    return value


def _canonicalize_mapping(value: Mapping[Any, Any]) -> dict[str, Any]:
    return {
        str(key): _canonicalize(value[key])
        for key in sorted(value, key=_canonical_mapping_key)
    }


def _canonicalize_sequence(value: Iterable[Any]) -> list[Any]:
    return [_canonicalize(item) for item in value]


def _canonicalize_set(value: Iterable[Any]) -> list[Any]:
    return sorted(
        (_canonicalize(item) for item in value),
        key=_canonical_sequence_key,
    )


def _canonical_mapping_key(key: Any) -> tuple[str, str, str]:
    return (str(key), type(key).__module__ + "." + type(key).__qualname__, repr(key))


def _canonical_sequence_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
