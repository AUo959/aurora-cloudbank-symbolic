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
- canonical Lagrange-point siting is active while exact-point uncertainty is
  quarantined from causal use;
- communications use an approximate nonzero latency and require advancement;
- actionable state changes fail closed without an explicit Triplex receipt;
- normal runtime persistence is outside the repository and never promotes run
  state into primary canon automatically.
"""

from __future__ import annotations

import copy
import os
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from l1_runtime_support import (
    GovernanceError,
    PreflightError,
    evaluate_preflight,
    event_for_roll,
    export_run_state,
    persist_run_state,
    read_json,
    required_int,
    resolve_cloudbank_revision,
    resolve_run_root,
    utcnow,
    validate_revision,
)
from l1_runtime_types import (
    DeterministicReplayRNG,
    EpistemicRecord,
    GovernanceReceipt,
    L1RunState,
    PopulationSnapshot,
    RunManifest,
    l1_run_state_from_payload,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = PROJECT_ROOT / "config" / "l1_runtime_baseline.json"
CANON_PROVENANCE_PATH = PROJECT_ROOT / "config" / "canon_provenance.json"
DEFAULT_RUN_ROOT = Path(
    os.environ.get("AURORA_L1_RUN_ROOT", Path.home() / ".aurora" / "l1-runs")
)


class OrionL1Runtime:
    """Minimal governed L1 runtime sufficient for safe INIT and advancement."""

    def __init__(self, baseline_path: Path = BASELINE_PATH) -> None:
        self.baseline_path = baseline_path
        self.baseline = read_json(baseline_path)
        self.population = PopulationSnapshot.from_baseline(self.baseline)
        self.state: Optional[L1RunState] = None
        self._rng: Optional[DeterministicReplayRNG] = None
        self._run_root: Optional[Path] = None

    def preflight(self) -> Dict[str, Any]:
        """Validate bootstrap invariants without creating or advancing a run."""
        return evaluate_preflight(
            self.baseline,
            self.population,
            CANON_PROVENANCE_PATH,
            run_created=self.state is not None,
        )

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
        seed = required_int(seed, "seed")
        canonrec_revision = self._resolve_canonrec_revision(canonrec_revision)
        resolved_run_root = self._prepare_run_root(run_root, persist)
        manifest = self._build_manifest(
            cloudbank_revision,
            canonrec_revision,
            seed,
        )
        new_state = self._build_initial_state(manifest)
        self.state = new_state
        self._rng = DeterministicReplayRNG(seed)
        self._run_root = resolved_run_root
        if persist:
            self._persist()
        return new_state

    def load_run(
        self,
        run_id: str,
        *,
        run_root: Optional[Path] = None,
    ) -> L1RunState:
        """Restore a persisted run and its deterministic replay position."""
        normalized_run_id = self._validated_run_id(run_id)
        resolved_run_root = self._resolve_run_root(run_root or DEFAULT_RUN_ROOT)
        state_path = resolved_run_root / normalized_run_id / "state.json"
        try:
            payload = read_json(state_path)
            restored = l1_run_state_from_payload(payload)
        except (OSError, ValueError, TypeError) as exc:
            raise PreflightError(
                "persisted L1 run state is unavailable or invalid"
            ) from exc
        self._validate_loaded_state(restored, normalized_run_id)
        self.state = restored
        self._run_root = resolved_run_root
        self._restore_replay_generator(restored)
        return restored

    def _resolve_canonrec_revision(self, override: Optional[str]) -> str:
        expected = self.baseline["authority"]["canonrec"]["revision"]
        if override is not None and override != expected:
            raise PreflightError(
                "CanonRec revision override does not match the preflight authority receipt"
            )
        self._validate_revision(expected, "canonrec_revision")
        return expected

    def _prepare_run_root(
        self,
        run_root: Optional[Path],
        persist: bool,
    ) -> Optional[Path]:
        if not persist:
            return None
        return self._resolve_run_root(run_root or DEFAULT_RUN_ROOT)

    def _build_manifest(
        self,
        cloudbank_revision: str,
        canonrec_revision: str,
        seed: int,
    ) -> RunManifest:
        defaults = self.baseline["run_defaults"]
        return RunManifest(
            schema_version=1,
            runtime_contract_version=self.baseline["runtime_contract_version"],
            run_id=str(uuid.uuid4()),
            created_at=utcnow(),
            cloudbank_revision=cloudbank_revision,
            canonrec_revision=canonrec_revision,
            seed=seed,
            station_cycle_length_minutes=int(defaults["station_cycle_length_minutes"]),
            station_cycle_minute=int(defaults["station_cycle_start_minute"]),
            tick=0,
            status="INITIALIZED",
            canon_status="run_state",
            active_quarantines=[
                "orion_exact_lagrange_point",
                "current_crew_81",
            ],
            population=self.population,
        )

    def _build_initial_state(self, manifest: RunManifest) -> L1RunState:
        return L1RunState(
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
                    "certainty": self.baseline["orbital_locus"]["certainty"],
                    "siting_class": self.baseline["orbital_locus"]["siting_class"],
                    "description": self.baseline["orbital_locus"][
                        "safe_runtime_description"
                    ],
                    "unresolved_parameters": copy.deepcopy(
                        self.baseline["orbital_locus"]["unresolved_parameters"]
                    ),
                },
                "communications": {
                    "latency": copy.deepcopy(
                        self.baseline["orbital_locus"]["communications_latency"]
                    )
                },
                "population": asdict(self.population),
            },
        )

    def advance(self, elapsed_minutes: int = 15) -> Dict[str, Any]:
        """Advance autonomous station state; observation focus is not consulted."""
        state = self._require_state()
        if elapsed_minutes <= 0 or elapsed_minutes > 1440:
            raise ValueError("elapsed_minutes must be between 1 and 1440")
        if state.manifest.status not in {"INITIALIZED", "ACTIVE"}:
            raise RuntimeError("run is not advancement-capable")
        if self._rng is None:
            raise RuntimeError("runtime replay generator is unavailable")

        state.manifest.status = "ACTIVE"
        state.manifest.tick += 1
        state.manifest.station_cycle_minute = (
            state.manifest.station_cycle_minute + elapsed_minutes
        ) % state.manifest.station_cycle_length_minutes

        roll = self._rng.random()
        kind, summary = event_for_roll(roll)
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
        self._deliver_queued_communications()
        self._queue_due_station_responses()
        self._persist_if_configured()
        return event

    def _deliver_queued_communications(self) -> None:
        """Deliver prior-tick Earth traffic after a positive time advance."""
        state = self._require_state()
        latency = self.baseline["orbital_locus"]["communications_latency"]
        for message in state.communications:
            if not self._communication_is_due(message, state.manifest.tick):
                continue
            message["delivered_tick"] = state.manifest.tick
            message["latency"] = copy.deepcopy(latency)
            direction = self._communication_direction(message)
            if direction == "earth_to_orion":
                self._record_station_delivery(message)
            elif direction == "station_to_earth":
                self._record_earth_delivery(message)

    @staticmethod
    def _communication_is_due(message: Dict[str, Any], tick: int) -> bool:
        queued_tick = message.get("tick")
        return (
            message.get("status") == "queued"
            and isinstance(queued_tick, int)
            and not isinstance(queued_tick, bool)
            and queued_tick < tick
        )

    @staticmethod
    def _communication_direction(message: Dict[str, Any]) -> Optional[str]:
        direction = message.get("direction")
        if direction in {"earth_to_orion", "station_to_earth"}:
            return direction
        if message.get("origin") == "Earth":
            return "earth_to_orion"
        return None

    def _record_station_delivery(self, message: Dict[str, Any]) -> None:
        state = self._require_state()
        message["status"] = "delivered_to_station"
        state.station_records.append(
            EpistemicRecord(
                record_id=str(uuid.uuid4()),
                subject=f"communication:{message['message_id']}",
                value=self._communication_record_value(message),
                epistemic_class="station_record",
                provenance="earth_to_orion_communications_ledger",
                confidence=1.0,
                tick=state.manifest.tick,
            )
        )

    def _record_earth_delivery(self, message: Dict[str, Any]) -> None:
        state = self._require_state()
        message["status"] = "delivered_to_earth"
        state.pilot_knowledge.append(
            EpistemicRecord(
                record_id=str(uuid.uuid4()),
                subject=f"communication:{message['message_id']}",
                value=self._communication_record_value(message),
                epistemic_class="testimony",
                provenance="station_to_earth_communications_ledger",
                confidence=1.0,
                tick=state.manifest.tick,
            )
        )

    @staticmethod
    def _communication_record_value(message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "message_id": message["message_id"],
            "origin": message["origin"],
            "sender_id": message["sender_id"],
            "target": message.get("target"),
            "content": message["content"],
            "status": message["status"],
        }

    def _queue_due_station_responses(self) -> None:
        state = self._require_state()
        replied_to = {
            item.get("reply_to_message_id")
            for item in state.communications
            if item.get("direction") == "station_to_earth"
        }
        for message in list(state.communications):
            if not self._commander_response_is_due(message, replied_to):
                continue
            response = self._build_commander_status_response(message)
            state.communications.append(response)
            state.character_knowledge.setdefault("CMD_001", []).append(
                EpistemicRecord(
                    record_id=str(uuid.uuid4()),
                    subject=f"communication:{response['message_id']}",
                    value=response["content"],
                    epistemic_class="testimony",
                    provenance="deterministic_status_report_v1",
                    confidence=1.0,
                    tick=state.manifest.tick,
                )
            )

    def _commander_response_is_due(
        self,
        message: Dict[str, Any],
        replied_to: set[Any],
    ) -> bool:
        return (
            self._communication_direction(message) == "earth_to_orion"
            and message.get("status") == "delivered_to_station"
            and message.get("target") == "CMD_001"
            and message.get("message_id") not in replied_to
        )

    def _build_commander_status_response(
        self,
        inbound: Dict[str, Any],
    ) -> Dict[str, Any]:
        state = self._require_state()
        latest_summary = self._latest_autonomous_event_summary()
        content = (
            "Pilot, this is Commander Thorne. Your transmission is received. "
            f"Current run ledger: Orion is active at tick {state.manifest.tick}. "
            f"{latest_summary} No emergency event is recorded in the current run "
            "ledger. The exact Lagrange point and exact current crew complement "
            "remain unresolved. Station operations continue under standing authority."
        )
        latency = self.baseline["orbital_locus"]["communications_latency"]
        return {
            "message_id": str(uuid.uuid4()),
            "reply_to_message_id": inbound["message_id"],
            "tick": state.manifest.tick,
            "direction": "station_to_earth",
            "sender_id": "CMD_001",
            "sender_name": "Commander Alex Thorne",
            "origin": "Orion Station",
            "target": "pilot",
            "content": content,
            "status": "queued",
            "delivery_resolution": latency["delivery_resolution"],
            "modeled_one_way_light_time_seconds": latency[
                "modeled_one_way_light_time_seconds"
            ],
            "latency_certainty": latency["certainty"],
            "automatic_l1_action": False,
            "pilot_directed_content": False,
            "response_policy": "deterministic_status_report_v1",
            "canon_status": "run_state",
        }

    def _latest_autonomous_event_summary(self) -> str:
        state = self._require_state()
        for event in reversed(state.events):
            if event.get("cause") == "autonomous_world_process":
                return str(
                    event.get("summary", "Autonomous event summary unavailable.")
                )
        return "No autonomous station event is recorded."

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
            value=copy.deepcopy(payload),
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
                value=copy.deepcopy(payload),
                epistemic_class="pilot_knowledge",
                provenance=f"runtime_observation:{observation.record_id}",
                confidence=1.0,
                tick=state.manifest.tick,
            )
        )
        self._persist_if_configured()
        return copy.deepcopy(payload)

    def route_operator_input(
        self,
        text: str,
        explicit_kind: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route operator input; only explicit communications cross into L1."""
        normalized = text.strip()
        if explicit_kind == "communication":
            return self.send_communication(normalized)
        self._validate_operator_input_kind(explicit_kind)
        routed = self._route_control_input(normalized)
        if routed is not None:
            return routed
        return {
            "kind": "control",
            "action": "no_op",
            "transmitted": False,
            "reason": "ambiguous operator input defaults to control-plane handling",
        }

    @staticmethod
    def _validate_operator_input_kind(explicit_kind: Optional[str]) -> None:
        if explicit_kind in {None, "control"}:
            return
        raise ValueError("explicit_kind must be 'control', 'communication', or None")

    def _route_control_input(self, normalized: str) -> Optional[Dict[str, Any]]:
        lowered = normalized.lower()
        if lowered in {"continue", "advance", "next"}:
            return {
                "kind": "control",
                "action": "advance",
                "event": self.advance(),
            }
        for prefix in ("observe ", "show "):
            if lowered.startswith(prefix):
                focus = normalized[len(prefix) :].strip() or "station"
                return {
                    "kind": "control",
                    "action": "observe",
                    "observation": self.observe(focus),
                }
        if lowered.startswith("stay with"):
            focus = normalized[len("stay with") :].strip() or "current aperture"
            return {
                "kind": "control",
                "action": "observe",
                "observation": self.observe(focus),
            }
        return None

    def send_communication(
        self,
        content: str,
        target: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Queue explicit Earth→Orion communication without auto-executing it."""
        state = self._require_state()
        if not content:
            raise ValueError("communication content cannot be empty")
        latency = self.baseline["orbital_locus"]["communications_latency"]
        message = {
            "message_id": str(uuid.uuid4()),
            "tick": state.manifest.tick,
            "direction": "earth_to_orion",
            "sender_id": "pilot",
            "sender_name": "Pilot",
            "origin": "Earth",
            "target": target,
            "content": content,
            "status": "queued",
            "delivery_resolution": latency["delivery_resolution"],
            "modeled_one_way_light_time_seconds": latency[
                "modeled_one_way_light_time_seconds"
            ],
            "latency_certainty": latency["certainty"],
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
        """Apply an exceptional fact only after complete Triplex authorization."""
        state = self._require_state()
        if not receipt.complete:
            raise GovernanceError(
                "Triplex authorization incomplete; actionable event rejected"
            )
        record = EpistemicRecord(
            record_id=str(uuid.uuid4()),
            subject=subject,
            value=value,
            epistemic_class="world_fact",
            provenance=f"triplex:{receipt.receipt_id}:{receipt.provenance}",
            confidence=1.0,
            tick=state.manifest.tick,
        )
        state.governance_receipts.append(receipt)
        state.governed_records.append(record)
        state.world_state[subject] = value
        state.events.append(
            {
                "event_id": str(uuid.uuid4()),
                "tick": state.manifest.tick,
                "kind": "governed_action",
                "subject": subject,
                "record_id": record.record_id,
                "receipt_id": receipt.receipt_id,
                "canon_status": "run_state",
            }
        )
        self._persist_if_configured()
        return record

    def nominate_for_canon_review(
        self,
        record_id: str,
        rationale: str,
    ) -> Dict[str, Any]:
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
        return export_run_state(state)

    @staticmethod
    def resolve_cloudbank_revision(project_root: Path = PROJECT_ROOT) -> str:
        """Resolve a checked-out git SHA without executing a subprocess."""
        return resolve_cloudbank_revision(project_root)

    def _persist_if_configured(self) -> None:
        if self._run_root is not None:
            self._persist()

    def _persist(self) -> None:
        state = self._require_state()
        if self._run_root is None:
            raise RuntimeError("run persistence root is not configured")
        persist_run_state(state, self._run_root)

    def _validate_loaded_state(self, state: L1RunState, run_id: str) -> None:
        manifest = state.manifest
        if manifest.run_id != run_id:
            raise PreflightError("persisted run ID does not match its persistence path")
        if manifest.schema_version != 1:
            raise PreflightError("persisted run schema version is unsupported")
        if (
            manifest.runtime_contract_version
            != self.baseline["runtime_contract_version"]
        ):
            raise PreflightError("persisted run contract does not match this runtime")
        if (
            manifest.canonrec_revision
            != self.baseline["authority"]["canonrec"]["revision"]
        ):
            raise PreflightError(
                "persisted run CanonRec revision does not match preflight"
            )
        self._validate_revision(manifest.cloudbank_revision, "cloudbank_revision")
        self._validate_revision(manifest.canonrec_revision, "canonrec_revision")
        if manifest.tick < 0:
            raise PreflightError("persisted run tick cannot be negative")
        if (
            not 0
            <= manifest.station_cycle_minute
            < manifest.station_cycle_length_minutes
        ):
            raise PreflightError("persisted station cycle minute is out of range")
        manifest.population.validate()
        self._validate_loaded_communications(state)

    def _validate_loaded_communications(self, state: L1RunState) -> None:
        message_ids = set()
        for index, message in enumerate(state.communications):
            self._validate_loaded_communication(message, index)
            message_id = message["message_id"]
            if message_id in message_ids:
                raise PreflightError("persisted communications contain duplicate IDs")
            message_ids.add(message_id)

    def _validate_loaded_communication(
        self,
        message: Dict[str, Any],
        index: int,
    ) -> None:
        prefix = f"persisted communication {index}"
        self._require_message_string(message, "message_id", prefix)
        self._require_message_string(message, "content", prefix)
        self._require_message_string(message, "sender_id", prefix)
        self._require_message_string(message, "origin", prefix)
        if type(message.get("tick")) is not int:
            raise PreflightError(f"{prefix} tick must be an integer")
        if message.get("status") not in {
            "queued",
            "delivered_to_station",
            "delivered_to_earth",
        }:
            raise PreflightError(f"{prefix} status is unsupported")
        if self._communication_direction(message) is None:
            raise PreflightError(f"{prefix} direction is unsupported")

    @staticmethod
    def _require_message_string(
        message: Dict[str, Any],
        field: str,
        prefix: str,
    ) -> None:
        value = message.get(field)
        if not isinstance(value, str) or not value:
            raise PreflightError(f"{prefix} {field} must be a non-empty string")

    def _restore_replay_generator(self, state: L1RunState) -> None:
        self._rng = DeterministicReplayRNG(state.manifest.seed)
        autonomous_event_count = sum(
            event.get("cause") == "autonomous_world_process" for event in state.events
        )
        for _ in range(autonomous_event_count):
            self._rng.random()

    @staticmethod
    def _validated_run_id(run_id: str) -> str:
        try:
            normalized = str(uuid.UUID(run_id))
        except (AttributeError, TypeError, ValueError) as exc:
            raise PreflightError("run_id must be a canonical UUID") from exc
        if normalized != run_id:
            raise PreflightError("run_id must be a canonical UUID")
        return normalized

    @staticmethod
    def _resolve_run_root(path: Path) -> Path:
        return resolve_run_root(path, PROJECT_ROOT)

    @staticmethod
    def _validate_revision(value: str, field_name: str) -> None:
        validate_revision(value, field_name)

    def _require_state(self) -> L1RunState:
        if self.state is None:
            raise RuntimeError("INIT has not created an L1 run")
        return self.state
