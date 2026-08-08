#!/usr/bin/env python3
"""Governed Orion L1 run lifecycle.

This module is the live L1 bootstrap/runtime boundary. It deliberately does not
reuse ``.aurora/SIMULATION_STATE.json`` as genesis state and does not treat the
historical Phase-1 task benchmark as the entire Orion world.

Core invariants:
- preflight never advances L1;
- INIT creates a tick-zero, advancement-capable run;
- Pilot is an Earth-side institutional operator role, never an L1 entity;
- observation is instrumentation and does not alter world causality;
- ambiguous operator input is never silently transmitted into L1;
- epistemic states remain separate;
- disputed population/orbital claims are quarantined from causal use;
- actionable state changes fail closed without an explicit Triplex receipt;
- normal runtime persistence is outside the repository and never promotes run
  state into primary canon automatically.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = PROJECT_ROOT / "config" / "l1_runtime_baseline.json"
CANON_PROVENANCE_PATH = PROJECT_ROOT / "config" / "canon_provenance.json"
DEFAULT_RUN_ROOT = Path(os.environ.get("AURORA_L1_RUN_ROOT", Path.home() / ".aurora" / "l1-runs"))


class PreflightError(RuntimeError):
    """Raised when L1 cannot safely enter INIT."""


class GovernanceError(RuntimeError):
    """Raised when an actionable mutation lacks complete Triplex authorization."""


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
        if self.identified_human_records < 0:
            raise ValueError("identified_human_records cannot be negative")
        if self.persona_resolved_humans is not None:
            if self.persona_resolved_humans < 0:
                raise ValueError("persona_resolved_humans cannot be negative")
            if self.persona_resolved_humans > self.identified_human_records:
                raise ValueError("persona-resolved humans cannot exceed identified human records")
        if self.current_human_crew_complement is not None:
            if self.current_human_crew_complement < self.identified_human_records:
                raise ValueError("human crew complement cannot be smaller than identified human records")
            if self.crew_capacity is not None and self.current_human_crew_complement > self.crew_capacity:
                raise ValueError("human crew complement cannot exceed crew capacity")
        if any(value < 0 for value in self.system_entities.values()):
            raise ValueError("system entity counts cannot be negative")

    @classmethod
    def from_baseline(cls, baseline: Dict[str, Any]) -> "PopulationSnapshot":
        payload = baseline["population"]
        snapshot = cls(
            crew_capacity=payload.get("crew_capacity"),
            current_human_crew_complement=payload.get("current_human_crew_complement"),
            identified_human_records=int(payload["identified_human_records"]),
            persona_resolved_humans=payload.get("persona_resolved_humans"),
            missing_named_human_claim=bool(payload["missing_named_human_claim"]),
            system_entities=dict(payload.get("system_entities", {})),
            historical_aggregate_claims=dict(payload.get("historical_aggregate_claims", {})),
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


class OrionL1Runtime:
    """Minimal governed L1 runtime sufficient for safe INIT and advancement."""

    def __init__(self, baseline_path: Path = BASELINE_PATH) -> None:
        self.baseline_path = baseline_path
        self.baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        self.population = PopulationSnapshot.from_baseline(self.baseline)
        self.state: Optional[L1RunState] = None
        self._rng: Optional[random.Random] = None
        self._run_root: Optional[Path] = None

    def preflight(self) -> Dict[str, Any]:
        """Validate bootstrap invariants without creating or advancing a run."""
        blockers: List[str] = []
        warnings: List[str] = []

        authority = self.baseline.get("authority", {})
        staff = authority.get("staff_registry", {})
        if staff.get("status") != "resolved_authority_boundary":
            blockers.append("staff registry authority boundary is unresolved")
        if staff.get("authority_repository") != "AUo959/CanonRec":
            blockers.append("CanonRec is not configured as staff canon authority")

        pilot = self.baseline.get("pilot_boundary", {})
        if pilot.get("residency") != "Earth" or pilot.get("l1_entity") is not False:
            blockers.append("Pilot boundary would permit L1 embodiment")
        if pilot.get("implicit_station_command_authority") is not False:
            blockers.append("Pilot role incorrectly implies station command authority")

        if self.population.missing_named_human_claim:
            blockers.append("false missing-human claim is active")
        if self.population.current_human_crew_complement is None:
            warnings.append("exact current human crew complement is unresolved and quarantined")

        locus = self.baseline.get("orbital_locus", {})
        if locus.get("status") != "quarantined_conflict":
            blockers.append("orbital locus conflict is not safely quarantined")
        if not locus.get("prohibited_causal_derivations"):
            blockers.append("orbital locus quarantine lacks causal-use restrictions")

        legacy = self.baseline.get("legacy_state", {})
        if legacy.get("genesis_authority") is not False:
            blockers.append("legacy SIMULATION_STATE is still eligible as genesis authority")

        benchmark = self.baseline.get("benchmark", {})
        if benchmark.get("canonical_component") != "simulation/orion_station_simulation_v2.py":
            blockers.append("canonical benchmark is not wired to Orion simulation v2")
        if "not the live L1 world runtime" not in benchmark.get("role", ""):
            blockers.append("historical benchmark is being conflated with the live L1 runtime")

        governance = self.baseline.get("governance", {})
        if governance.get("ethics_protocol") != "Picard_Delta_3":
            blockers.append("Picard_Delta_3 governance is not active in the runtime contract")
        if governance.get("actionable_event_policy") != "explicit_triplex_receipt_required":
            blockers.append("actionable events do not fail closed on Triplex authorization")

        return {
            "ready": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "tick": 0,
            "run_created": self.state is not None,
            "runtime_contract_version": self.baseline["runtime_contract_version"],
        }

    def init_run(
        self,
        *,
        cloudbank_revision: str,
        seed: int,
        canonrec_revision: Optional[str] = None,
        run_root: Optional[Path] = None,
        persist: bool = True,
    ) -> L1RunState:
        """Create a tick-zero L1 run without advancing world state."""
        report = self.preflight()
        if not report["ready"]:
            raise PreflightError("; ".join(report["blockers"]))
        self._validate_revision(cloudbank_revision, "cloudbank_revision")

        canonrec_revision = canonrec_revision or self.baseline["authority"]["canonrec"]["revision"]
        self._validate_revision(canonrec_revision, "canonrec_revision")

        defaults = self.baseline["run_defaults"]
        manifest = RunManifest(
            schema_version=1,
            runtime_contract_version=self.baseline["runtime_contract_version"],
            run_id=str(uuid.uuid4()),
            created_at=_utcnow(),
            cloudbank_revision=cloudbank_revision,
            canonrec_revision=canonrec_revision,
            seed=int(seed),
            station_cycle_length_minutes=int(defaults["station_cycle_length_minutes"]),
            station_cycle_minute=int(defaults["station_cycle_start_minute"]),
            tick=0,
            status="INITIALIZED",
            canon_status="run_state",
            active_quarantines=["orion_orbital_locus", "historical_current_crew_81"],
            population=self.population,
        )

        self.state = L1RunState(
            manifest=manifest,
            world_state={
                "station": "Orion Station",
                "l1_status": "initialized",
                "pilot": {
                    "role": "Pilot",
                    "residency": "Earth",
                    "l1_entity": False,
                },
                "orbital_locus": {
                    "status": self.baseline["orbital_locus"]["status"],
                    "description": self.baseline["orbital_locus"]["safe_runtime_description"],
                },
                "population": asdict(self.population),
            },
        )
        self._rng = random.Random(seed)

        if persist:
            self._run_root = self._resolve_run_root(run_root or DEFAULT_RUN_ROOT)
            self._persist()
        return self.state

    def advance(self, elapsed_minutes: int = 15) -> Dict[str, Any]:
        """Advance autonomous station state; observation focus is not consulted."""
        state = self._require_state()
        if elapsed_minutes <= 0 or elapsed_minutes > 1440:
            raise ValueError("elapsed_minutes must be between 1 and 1440")
        if state.manifest.status != "INITIALIZED" and state.manifest.status != "ACTIVE":
            raise RuntimeError("run is not advancement-capable")
        assert self._rng is not None

        state.manifest.status = "ACTIVE"
        state.manifest.tick += 1
        state.manifest.station_cycle_minute = (
            state.manifest.station_cycle_minute + elapsed_minutes
        ) % state.manifest.station_cycle_length_minutes

        roll = self._rng.random()
        if roll < 0.30:
            kind = "routine_shift_handoff"
            summary = "Routine station shift handoff completed without material exception."
        elif roll < 0.50:
            kind = "maintenance_queue_progress"
            summary = "A scheduled maintenance queue advanced within standing-authority limits."
        elif roll < 0.65:
            kind = "research_queue_progress"
            summary = "A research work queue advanced; no canon-level conclusion was generated."
        else:
            kind = "no_material_event"
            summary = "No material station event was recorded for this advancement window."

        event = {
            "event_id": str(uuid.uuid4()),
            "tick": state.manifest.tick,
            "elapsed_minutes": elapsed_minutes,
            "kind": kind,
            "summary": summary,
            "cause": "autonomous_world_process",
            "pilot_attention_influenced_probability": False,
            "governance": "standing_authority_routine",
            "canon_status": "run_state",
        }
        state.events.append(event)
        state.station_records.append(
            EpistemicRecord(
                record_id=str(uuid.uuid4()),
                subject=f"event:{event['event_id']}",
                value=summary,
                epistemic_class="station_record",
                provenance="autonomous_runtime_event_ledger",
                confidence=1.0,
                tick=state.manifest.tick,
            )
        )
        self._persist_if_configured()
        return event

    def observe(self, focus: str = "station") -> Dict[str, Any]:
        """Expose instrumentation without advancing or rearranging L1."""
        state = self._require_state()
        recent = [asdict(item) for item in state.station_records[-5:]]
        payload = {
            "observation_id": str(uuid.uuid4()),
            "tick": state.manifest.tick,
            "focus": focus.strip() or "station",
            "instrumentation": True,
            "pilot_embodied": False,
            "generated_world_event": False,
            "records": recent,
        }
        observation = EpistemicRecord(
            record_id=payload["observation_id"],
            subject=f"observation:{payload['focus']}",
            value=payload,
            epistemic_class="runtime_observation",
            provenance="l1_observation_aperture",
            confidence=1.0,
            tick=state.manifest.tick,
        )
        state.runtime_observations.append(observation)
        state.pilot_knowledge.append(
            EpistemicRecord(
                record_id=str(uuid.uuid4()),
                subject=observation.subject,
                value=payload,
                epistemic_class="pilot_knowledge",
                provenance=f"runtime_observation:{observation.record_id}",
                confidence=1.0,
                tick=state.manifest.tick,
            )
        )
        self._persist_if_configured()
        return payload

    def route_operator_input(self, text: str, explicit_kind: Optional[str] = None) -> Dict[str, Any]:
        """Route operator input; only explicit communications cross into L1."""
        normalized = text.strip()
        if explicit_kind == "communication":
            return self.send_communication(normalized)
        if explicit_kind not in {None, "control"}:
            raise ValueError("explicit_kind must be 'control', 'communication', or None")

        lowered = normalized.lower()
        if lowered in {"continue", "advance", "next"}:
            return {"kind": "control", "action": "advance", "event": self.advance()}
        for prefix in ("observe ", "show "):
            if lowered.startswith(prefix):
                focus = normalized[len(prefix):].strip() or "station"
                return {"kind": "control", "action": "observe", "observation": self.observe(focus)}
        if lowered.startswith("stay with"):
            focus = normalized[len("stay with"):].strip() or "current aperture"
            return {"kind": "control", "action": "observe", "observation": self.observe(focus)}

        return {
            "kind": "control",
            "action": "no_op",
            "transmitted": False,
            "reason": "ambiguous operator input defaults to control-plane handling",
        }

    def send_communication(self, content: str, target: Optional[str] = None) -> Dict[str, Any]:
        """Queue an explicit Earth→Orion communication without auto-executing it."""
        state = self._require_state()
        if not content:
            raise ValueError("communication content cannot be empty")
        message = {
            "message_id": str(uuid.uuid4()),
            "tick": state.manifest.tick,
            "sender_id": "pilot",
            "sender_name": "Pilot",
            "origin": "Earth",
            "target": target,
            "content": content,
            "status": "queued",
            "automatic_l1_action": False,
            "canon_status": "run_state",
        }
        state.communications.append(message)
        self._persist_if_configured()
        return {"kind": "communication", "message": message}

    def record_character_belief(
        self,
        character_id: str,
        subject: str,
        value: Any,
        *,
        confidence: float,
        provenance: str,
    ) -> EpistemicRecord:
        state = self._require_state()
        record = EpistemicRecord(
            record_id=str(uuid.uuid4()),
            subject=subject,
            value=value,
            epistemic_class="character_belief",
            provenance=provenance,
            confidence=confidence,
            tick=state.manifest.tick,
        )
        state.character_knowledge.setdefault(character_id, []).append(record)
        self._persist_if_configured()
        return record

    def apply_governed_event(
        self,
        *,
        subject: str,
        value: Any,
        receipt: GovernanceReceipt,
    ) -> EpistemicRecord:
        """Apply an exceptional actionable fact only after complete Triplex authorization."""
        state = self._require_state()
        if not receipt.complete:
            raise GovernanceError("Triplex authorization incomplete; actionable event rejected")
        record = EpistemicRecord(
            record_id=str(uuid.uuid4()),
            subject=subject,
            value=value,
            epistemic_class="world_fact",
            provenance=f"triplex:{receipt.receipt_id}:{receipt.provenance}",
            confidence=1.0,
            tick=state.manifest.tick,
        )
        state.world_state[subject] = value
        state.events.append(
            {
                "event_id": str(uuid.uuid4()),
                "tick": state.manifest.tick,
                "kind": "governed_action",
                "subject": subject,
                "receipt_id": receipt.receipt_id,
                "canon_status": "run_state",
            }
        )
        self._persist_if_configured()
        return record

    def nominate_for_canon_review(self, record_id: str, rationale: str) -> Dict[str, Any]:
        """Mark a run artifact as a candidate only; never mutate repository canon."""
        state = self._require_state()
        candidate = {
            "candidate_id": str(uuid.uuid4()),
            "source_record_id": record_id,
            "rationale": rationale,
            "status": "candidate_promotion",
            "repository_mutated": False,
            "tick": state.manifest.tick,
        }
        state.promotion_candidates.append(candidate)
        self._persist_if_configured()
        return candidate

    def close(self) -> None:
        state = self._require_state()
        state.manifest.status = "CLOSED"
        self._persist_if_configured()

    def export_state(self) -> Dict[str, Any]:
        state = self._require_state()
        return {
            "manifest": {
                **asdict(state.manifest),
                "population": asdict(state.manifest.population),
            },
            "world_state": state.world_state,
            "character_knowledge": {
                key: [asdict(record) for record in records]
                for key, records in state.character_knowledge.items()
            },
            "station_records": [asdict(record) for record in state.station_records],
            "runtime_observations": [asdict(record) for record in state.runtime_observations],
            "pilot_knowledge": [asdict(record) for record in state.pilot_knowledge],
            "communications": state.communications,
            "events": state.events,
            "promotion_candidates": state.promotion_candidates,
        }

    @staticmethod
    def resolve_cloudbank_revision(project_root: Path = PROJECT_ROOT) -> str:
        """Resolve the checked-out revision; fail closed if the checkout is not revision-pinned."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=3,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise PreflightError("unable to pin CloudBank git revision") from exc
        revision = result.stdout.strip()
        OrionL1Runtime._validate_revision(revision, "cloudbank_revision")
        return revision

    def _persist_if_configured(self) -> None:
        if self._run_root is not None:
            self._persist()

    def _persist(self) -> None:
        state = self._require_state()
        assert self._run_root is not None
        run_dir = self._run_root / state.manifest.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        destination = run_dir / "state.json"
        temporary = run_dir / ".state.json.tmp"
        temporary.write_text(json.dumps(self.export_state(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(destination)

    @staticmethod
    def _resolve_run_root(path: Path) -> Path:
        resolved = path.expanduser().resolve()
        project = PROJECT_ROOT.resolve()
        if resolved == project or project in resolved.parents:
            raise PreflightError("run persistence must remain outside the repository")
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    @staticmethod
    def _validate_revision(value: str, field_name: str) -> None:
        if len(value) != 40 or any(char not in "0123456789abcdef" for char in value.lower()):
            raise ValueError(f"{field_name} must be a 40-character git SHA")

    def _require_state(self) -> L1RunState:
        if self.state is None:
            raise RuntimeError("INIT has not created an L1 run")
        return self.state


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
