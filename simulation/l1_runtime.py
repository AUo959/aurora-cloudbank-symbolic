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

from l1_character_actor import BoundedCharacterActor, CharacterContext
from l1_character_actor_policy import POLICY_VERSION
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
        self._commander_actor = BoundedCharacterActor()

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
        report = self.preflight()
        if not report["ready"]:
            raise PreflightError("; ".join(report["blockers"]))
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
            direction = self._communication_direction(message)
            if direction is None:
                raise RuntimeError("queued communication direction is unsupported")
            message["delivered_tick"] = state.manifest.tick
            message["latency"] = copy.deepcopy(latency)
            if direction == "earth_to_orion":
                self._record_station_delivery(message)
            else:
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
        if direction is not None:
            return None
        if message.get("origin") == "Earth":
            return "earth_to_orion"
        if message.get("origin") == "Orion Station":
            return "station_to_earth"
        return None

    def _record_station_delivery(self, message: Dict[str, Any]) -> None:
        state = self._require_state()
        message["status"] = "delivered_to_station"
        station_record = EpistemicRecord(
            record_id=str(uuid.uuid4()),
            subject=f"communication:{message['message_id']}",
            value=self._communication_record_value(message),
            epistemic_class="station_record",
            provenance="earth_to_orion_communications_ledger",
            confidence=1.0,
            tick=state.manifest.tick,
        )
        state.station_records.append(station_record)
        self._record_direct_character_delivery(message, station_record)

    def _record_direct_character_delivery(
        self,
        message: Dict[str, Any],
        station_record: EpistemicRecord,
    ) -> None:
        target = message.get("target")
        if not isinstance(target, str) or not target:
            return
        state = self._require_state()
        state.character_knowledge.setdefault(target, []).append(
            EpistemicRecord(
                record_id=str(uuid.uuid4()),
                subject=station_record.subject,
                value=copy.deepcopy(station_record.value),
                epistemic_class="testimony",
                provenance="direct_communication_delivery",
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
            if self._communication_direction(item) == "station_to_earth"
        }
        for message in tuple(state.communications):
            if not self._commander_response_is_due(message, replied_to):
                continue
            decision = self._commander_actor.decide(
                self._commander_context(message)
            )
            response = self._build_commander_action_response(message, decision)
            decision["response_message_id"] = response["message_id"]
            decision["operational_steps"][-1]["message_id"] = response["message_id"]
            state.character_actions.append(decision)
            state.communications.append(response)
            self._record_character_action_knowledge(decision)

    def _commander_context(self, inbound: Dict[str, Any]) -> CharacterContext:
        state = self._require_state()
        return CharacterContext(
            run_id=state.manifest.run_id,
            tick=state.manifest.tick,
            inbound=copy.deepcopy(inbound),
            station_records=tuple(
                asdict(item) for item in state.station_records[-8:]
            ),
            character_knowledge=tuple(
                asdict(item)
                for item in state.character_knowledge.get("CMD_001", [])[-8:]
            ),
            recent_events=tuple(copy.deepcopy(state.events[-8:])),
            prior_actions=tuple(
                copy.deepcopy(
                    [
                        item
                        for item in state.character_actions
                        if item.get("actor_id") == "CMD_001"
                    ][-8:]
                )
            ),
            unresolved_facts=self._commander_unresolved_facts(),
            governed_records=self._commander_governed_records(),
        )

    def _commander_governed_records(self) -> tuple[Dict[str, Any], ...]:
        """Bound actor context while retaining the current emergency fact."""
        state = self._require_state()
        latest_by_subject = {}
        for record in state.governed_records:
            latest_by_subject.pop(record.subject, None)
            latest_by_subject[record.subject] = record
        emergency = latest_by_subject.pop("emergency_active", None)
        limit = 7 if emergency is not None else 8
        records = list(latest_by_subject.values())[-limit:]
        if emergency is not None:
            records.append(emergency)
        return tuple(asdict(item) for item in records)

    def _commander_unresolved_facts(self) -> tuple[str, ...]:
        state = self._require_state()
        unresolved = list(
            state.world_state["orbital_locus"].get("unresolved_parameters", [])
        )
        if state.manifest.population.current_human_crew_complement is None:
            unresolved.append("exact_current_human_crew_complement")
        return tuple(unresolved)

    def _record_character_action_knowledge(
        self,
        decision: Dict[str, Any],
    ) -> None:
        state = self._require_state()
        knowledge = state.character_knowledge.setdefault("CMD_001", [])
        known_subjects = {item.subject for item in knowledge}
        station_by_id = {item.record_id: item for item in state.station_records}
        for item in decision["knowledge_inputs"]:
            if item.get("scope") != "station_record":
                continue
            source = station_by_id.get(item["record_id"])
            if source is None or source.subject in known_subjects:
                continue
            knowledge.append(self._character_review_record(source, decision))
            known_subjects.add(source.subject)
        knowledge.append(
            EpistemicRecord(
                record_id=str(uuid.uuid4()),
                subject=f"character_action:{decision['action_id']}",
                value={
                    "selected_action": decision["selected_action"],
                    "rationale": decision["rationale"],
                    "commitments": copy.deepcopy(decision["commitments"]),
                    "response_message_id": decision["response_message_id"],
                },
                epistemic_class="inference",
                provenance=decision["policy"],
                confidence=1.0,
                tick=state.manifest.tick,
            )
        )

    def _character_review_record(
        self,
        source: EpistemicRecord,
        decision: Dict[str, Any],
    ) -> EpistemicRecord:
        state = self._require_state()
        return EpistemicRecord(
            record_id=str(uuid.uuid4()),
            subject=source.subject,
            value=copy.deepcopy(source.value),
            epistemic_class="station_record",
            provenance=f"character_review:{decision['action_id']}:{source.provenance}",
            confidence=source.confidence,
            tick=state.manifest.tick,
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

    def _build_commander_action_response(
        self,
        inbound: Dict[str, Any],
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        state = self._require_state()
        response_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"aurora:l1:response:{decision['action_id']}",
            )
        )
        latency = self.baseline["orbital_locus"]["communications_latency"]
        return {
            "message_id": response_id,
            "reply_to_message_id": inbound["message_id"],
            "caused_by_action_id": decision["action_id"],
            "tick": state.manifest.tick,
            "direction": "station_to_earth",
            "sender_id": "CMD_001",
            "sender_name": decision["actor_name"],
            "origin": "Orion Station",
            "target": "pilot",
            "content": decision["response_content"],
            "status": "queued",
            "delivery_resolution": latency["delivery_resolution"],
            "modeled_one_way_light_time_seconds": latency[
                "modeled_one_way_light_time_seconds"
            ],
            "latency_certainty": latency["certainty"],
            "automatic_l1_action": False,
            "pilot_directed_content": False,
            "response_policy": decision["policy"],
            "canon_status": "run_state",
        }

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
        self._validate_loaded_world_state(state)
        self._validate_replay_position(state)
        self._validate_loaded_communications(state)
        self._validate_loaded_character_actions(state)

    @staticmethod
    def _validate_loaded_world_state(state: L1RunState) -> None:
        world_state = state.world_state
        locus = world_state.get("orbital_locus")
        pilot = world_state.get("pilot")
        if not isinstance(world_state.get("station"), str):
            raise PreflightError("persisted world state lacks its station identity")
        if not isinstance(locus, dict) or not isinstance(
            locus.get("unresolved_parameters"), list
        ):
            raise PreflightError("persisted world state lacks its orbital locus")
        if not isinstance(pilot, dict) or (
            pilot.get("residency") != "Earth" or pilot.get("l1_entity") is not False
        ):
            raise PreflightError("persisted world state violates the Pilot boundary")

    @staticmethod
    def _validate_replay_position(state: L1RunState) -> None:
        autonomous_events = sum(
            event.get("cause") == "autonomous_world_process"
            for event in state.events
        )
        if autonomous_events != state.manifest.tick:
            raise PreflightError(
                "persisted autonomous event ledger does not match manifest tick"
            )

    def _validate_loaded_character_actions(self, state: L1RunState) -> None:
        action_ids = set()
        response_ids = set()
        messages = {item["message_id"]: item for item in state.communications}
        for index, action in enumerate(state.character_actions):
            prefix = f"persisted character action {index}"
            action_id = self._require_action_string(action, "action_id", prefix)
            actor_id = self._require_action_string(action, "actor_id", prefix)
            trigger_id = self._require_action_string(
                action, "trigger_message_id", prefix
            )
            response_id = self._require_action_string(
                action, "response_message_id", prefix
            )
            self._require_action_string(action, "selected_action", prefix)
            policy = self._require_action_string(action, "policy", prefix)
            response_content = self._require_action_string(
                action, "response_content", prefix
            )
            if actor_id != "CMD_001" or policy != POLICY_VERSION:
                raise PreflightError(
                    f"{prefix} actor or policy is unsupported"
                )
            if action_id in action_ids:
                raise PreflightError("persisted character actions contain duplicate IDs")
            if response_id in response_ids:
                raise PreflightError(
                    "persisted character actions reuse a response communication"
                )
            self._validate_character_action_references(
                prefix, trigger_id, response_id, messages
            )
            self._validate_character_action_links(
                prefix,
                action_id,
                actor_id,
                policy,
                trigger_id,
                response_id,
                response_content,
                messages,
            )
            self._validate_character_action_tick(
                prefix, action.get("tick"), state.manifest.tick
            )
            action_ids.add(action_id)
            response_ids.add(response_id)
        self._validate_character_response_coverage(messages, response_ids)

    def _validate_character_response_coverage(
        self,
        messages: Dict[str, Dict[str, Any]],
        response_ids: set[str],
    ) -> None:
        unlinked_responses = {
            message_id
            for message_id, message in messages.items()
            if self._communication_direction(message) == "station_to_earth"
            and message_id not in response_ids
        }
        if unlinked_responses:
            raise PreflightError(
                "persisted station-to-Earth communication lacks a character action"
            )

    @staticmethod
    def _validate_character_action_references(
        prefix: str,
        trigger_id: str,
        response_id: str,
        messages: Dict[str, Dict[str, Any]],
    ) -> None:
        if trigger_id not in messages or response_id not in messages:
            raise PreflightError(f"{prefix} references an unavailable communication")

    @staticmethod
    def _validate_character_action_tick(
        prefix: str,
        tick: Any,
        manifest_tick: int,
    ) -> None:
        if type(tick) is not int or not 0 <= tick <= manifest_tick:
            raise PreflightError(f"{prefix} tick is invalid")

    def _validate_character_action_links(
        self,
        prefix: str,
        action_id: str,
        actor_id: str,
        policy: str,
        trigger_id: str,
        response_id: str,
        response_content: str,
        messages: Dict[str, Dict[str, Any]],
    ) -> None:
        trigger = messages[trigger_id]
        response = messages[response_id]
        expected_response_fields = {
            "reply_to_message_id": trigger_id,
            "caused_by_action_id": action_id,
            "sender_id": actor_id,
            "response_policy": policy,
            "content": response_content,
        }
        links_match = (
            self._communication_direction(trigger) == "earth_to_orion"
            and self._communication_direction(response) == "station_to_earth"
            and all(
                response.get(field) == expected
                for field, expected in expected_response_fields.items()
            )
        )
        if not links_match:
            raise PreflightError(f"{prefix} communication causality is inconsistent")

    @staticmethod
    def _require_action_string(
        action: Dict[str, Any],
        field: str,
        prefix: str,
    ) -> str:
        value = action.get(field)
        if not isinstance(value, str) or not value:
            raise PreflightError(f"{prefix} {field} must be a non-empty string")
        return value

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
        status = message.get("status")
        if status not in {
            "queued",
            "delivered_to_station",
            "delivered_to_earth",
        }:
            raise PreflightError(f"{prefix} status is unsupported")
        direction = self._communication_direction(message)
        if direction is None:
            raise PreflightError(f"{prefix} direction is unsupported")
        allowed_statuses = {
            "earth_to_orion": {"queued", "delivered_to_station"},
            "station_to_earth": {"queued", "delivered_to_earth"},
        }[direction]
        if status not in allowed_statuses:
            raise PreflightError(f"{prefix} status contradicts direction")
        expected_origin = {
            "earth_to_orion": "Earth",
            "station_to_earth": "Orion Station",
        }[direction]
        if message["origin"] != expected_origin:
            raise PreflightError(f"{prefix} origin does not match direction")

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
