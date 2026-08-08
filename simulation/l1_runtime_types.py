#!/usr/bin/env python3
"""Data contracts for the governed Orion L1 runtime."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from l1_runtime_support import (
    int_mapping,
    optional_int,
    required_bool,
    required_int,
    string_mapping,
)


class DeterministicReplayRNG:
    """Hash/counter replay generator for non-security simulation choices."""

    def __init__(self, seed: int) -> None:
        self._seed = str(seed).encode("ascii")
        self._counter = 0

    def random(self) -> float:
        payload = self._seed + b":" + str(self._counter).encode("ascii")
        digest = hashlib.sha256(payload).digest()
        self._counter += 1
        return int.from_bytes(digest[:8], "big") / float(1 << 64)


@dataclass(frozen=True)
class PopulationSnapshot:
    crew_capacity: Optional[int]
    current_human_crew_complement: Optional[int]
    identified_human_records: int
    persona_resolved_humans: Optional[int]
    missing_named_human_claim: bool
    system_entities: Dict[str, int]
    historical_aggregate_claims: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        self._validate_base_counts()
        self._validate_persona_subset()
        self._validate_human_complement()
        self._validate_system_entities()

    def _validate_base_counts(self) -> None:
        if self.crew_capacity is not None and self.crew_capacity < 0:
            raise ValueError("crew_capacity cannot be negative")
        if self.identified_human_records < 0:
            raise ValueError("identified_human_records cannot be negative")

    def _validate_persona_subset(self) -> None:
        if self.persona_resolved_humans is None:
            return
        if self.persona_resolved_humans < 0:
            raise ValueError("persona_resolved_humans cannot be negative")
        if self.persona_resolved_humans > self.identified_human_records:
            raise ValueError(
                "persona-resolved humans cannot exceed identified human records"
            )

    def _validate_human_complement(self) -> None:
        complement = self.current_human_crew_complement
        if complement is None:
            return
        if complement < self.identified_human_records:
            raise ValueError(
                "human crew complement cannot be smaller than identified human records"
            )
        if self.crew_capacity is not None and complement > self.crew_capacity:
            raise ValueError("human crew complement cannot exceed crew capacity")

    def _validate_system_entities(self) -> None:
        if any(value < 0 for value in self.system_entities.values()):
            raise ValueError("system entity counts cannot be negative")

    @classmethod
    def from_baseline(cls, baseline: Dict[str, Any]) -> "PopulationSnapshot":
        payload = baseline.get("population")
        if not isinstance(payload, dict):
            raise ValueError("population must be a JSON object")

        snapshot = cls(
            crew_capacity=optional_int(payload.get("crew_capacity"), "crew_capacity"),
            current_human_crew_complement=optional_int(
                payload.get("current_human_crew_complement"),
                "current_human_crew_complement",
            ),
            identified_human_records=required_int(
                payload.get("identified_human_records"),
                "identified_human_records",
            ),
            persona_resolved_humans=optional_int(
                payload.get("persona_resolved_humans"),
                "persona_resolved_humans",
            ),
            missing_named_human_claim=required_bool(
                payload.get("missing_named_human_claim"),
                "missing_named_human_claim",
            ),
            system_entities=int_mapping(
                payload.get("system_entities"),
                "system_entities",
            ),
            historical_aggregate_claims=string_mapping(
                payload.get("historical_aggregate_claims", {}),
                "historical_aggregate_claims",
            ),
        )
        snapshot.validate()
        return snapshot


@dataclass(frozen=True)
class EpistemicRecord:
    record_id: str
    subject: str
    value: Any
    epistemic_class: str
    provenance: str
    confidence: float
    tick: int
    canon_status: str = "run_state"

    def __post_init__(self) -> None:
        allowed = {
            "world_fact",
            "character_belief",
            "station_record",
            "runtime_observation",
            "pilot_knowledge",
            "testimony",
            "inference",
        }
        if self.epistemic_class not in allowed:
            raise ValueError(f"unsupported epistemic_class: {self.epistemic_class}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class GovernanceReceipt:
    l3_glyph_arbitration: bool
    continuity_and_relay_verification: bool
    l1_human_consent: bool
    receipt_id: str
    provenance: str

    @property
    def complete(self) -> bool:
        return (
            self.l3_glyph_arbitration
            and self.continuity_and_relay_verification
            and self.l1_human_consent
        )


@dataclass
class RunManifest:
    schema_version: int
    runtime_contract_version: str
    run_id: str
    created_at: str
    cloudbank_revision: str
    canonrec_revision: str
    seed: int
    station_cycle_length_minutes: int
    station_cycle_minute: int
    tick: int
    status: str
    canon_status: str
    active_quarantines: List[str]
    population: PopulationSnapshot


@dataclass
class L1RunState:
    manifest: RunManifest
    world_state: Dict[str, Any]
    character_knowledge: Dict[str, List[EpistemicRecord]] = field(default_factory=dict)
    station_records: List[EpistemicRecord] = field(default_factory=list)
    runtime_observations: List[EpistemicRecord] = field(default_factory=list)
    pilot_knowledge: List[EpistemicRecord] = field(default_factory=list)
    communications: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    promotion_candidates: List[Dict[str, Any]] = field(default_factory=list)
