#!/usr/bin/env python3
"""Bounded, canon-projected character agency for the governed L1 runtime."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = PROJECT_ROOT / "config" / "l1_character_actor_profiles.json"
POLICY_VERSION = "bounded_character_action_v1"


@dataclass(frozen=True)
class CharacterContext:
    """Only the L1 information aperture available to one acting character."""

    run_id: str
    tick: int
    inbound: Mapping[str, Any]
    station_records: Sequence[Mapping[str, Any]]
    character_knowledge: Sequence[Mapping[str, Any]]
    recent_events: Sequence[Mapping[str, Any]]
    prior_actions: Sequence[Mapping[str, Any]]
    unresolved_facts: Sequence[str]


class CharacterProfileError(RuntimeError):
    """Raised when a runtime character projection cannot be canon-validated."""


class BoundedCharacterActor:
    """Select auditable actions from canon identity and actor-local evidence."""

    def __init__(self, profile_path: Path = PROFILE_PATH) -> None:
        self.profile_path = profile_path
        self.profile = self._load_profile("CMD_001")
        self._validate_profile_authority()
        self._validate_behavior_projection()

    def decide(self, context: CharacterContext) -> Dict[str, Any]:
        """Return a deterministic character action and its causal receipt."""
        intents = _classify_intents(str(context.inbound["content"]))
        selected_action = _select_action(intents, context.recent_events)
        decision_event = _decision_event(selected_action, context.recent_events)
        prior_commitments = _active_commitments(context.prior_actions)
        action_id = _stable_action_id(context, selected_action)
        decision = {
            "action_id": action_id,
            "actor_id": "CMD_001",
            "actor_name": self.profile["identity"]["display_name"],
            "tick": context.tick,
            "trigger_message_id": context.inbound["message_id"],
            "policy": POLICY_VERSION,
            "canon_status": "run_state",
            "profile_projection_status": "runtime_projection_non_authoritative",
            "profile_evidence": self._profile_evidence(),
            "perceived_intents": intents,
            "knowledge_inputs": _knowledge_inputs(context),
            "knowledge_gaps": list(context.unresolved_facts),
            "continuity_inputs": [
                item["action_id"] for item in context.prior_actions[-5:]
            ],
            "duty_drivers": self._driver_receipts(
                "duties", _duty_drivers(selected_action)
            ),
            "principle_drivers": self._driver_receipts(
                "decision_principles", _principle_drivers(selected_action)
            ),
            "options_considered": _options_considered(selected_action),
            "selected_action": selected_action,
            "rationale": _rationale(selected_action),
            "operational_steps": _operational_steps(
                selected_action,
                context.station_records,
                decision_event,
            ),
            "commitments": _commitments(selected_action, decision_event),
            "prior_active_commitments": prior_commitments,
        }
        decision["response_content"] = self._render_response(
            decision,
            decision_event,
            context.unresolved_facts,
        )
        return decision

    def _load_profile(self, character_id: str) -> Dict[str, Any]:
        try:
            payload = json.loads(self.profile_path.read_text(encoding="utf-8"))
            profiles = payload["profiles"]
            profile = profiles[character_id]
        except (KeyError, OSError, TypeError, json.JSONDecodeError) as exc:
            raise CharacterProfileError("character actor profile is unavailable") from exc
        if payload.get("projection_status") != "runtime_projection_non_authoritative":
            raise CharacterProfileError("character actor profile lacks its authority boundary")
        return copy.deepcopy(profile)

    def _validate_profile_authority(self) -> None:
        registry_path, roster_path, _ = self._authority_paths()
        registry = _read_json(registry_path)
        matches = [
            item
            for item in registry.get("human_staff", [])
            if item.get("id") == "CMD_001"
        ]
        if len(matches) != 1:
            raise CharacterProfileError("CMD_001 is not unique in the staff projection")
        _validate_identity(self.profile["identity"], matches[0])
        roster = roster_path.read_text(encoding="utf-8")
        missing = [
            anchor for anchor in self.profile["canon_anchors"] if anchor not in roster
        ]
        if missing:
            raise CharacterProfileError("character behavior anchors drifted from the roster")

    def _validate_behavior_projection(self) -> None:
        for action in (
            "review_watch_and_report",
            "assess_and_escalate_if_warranted",
            "review_authority_and_respond",
            "acknowledge_and_open_channel",
        ):
            self._driver_receipts("duties", _duty_drivers(action))
            self._driver_receipts(
                "decision_principles", _principle_drivers(action)
            )
        self._opening()

    def _driver_receipts(
        self,
        group: str,
        driver_ids: Sequence[str],
    ) -> list[Dict[str, str]]:
        values = self.profile.get(group)
        if not isinstance(values, dict):
            raise CharacterProfileError(f"character profile lacks {group}")
        try:
            return [
                {"id": driver_id, "basis": str(values[driver_id])}
                for driver_id in driver_ids
            ]
        except KeyError as exc:
            raise CharacterProfileError(
                f"character profile lacks required {group} driver"
            ) from exc

    def _profile_evidence(self) -> list[Dict[str, str]]:
        paths = [self.profile_path, *self._authority_paths()]
        return [
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in paths
        ]

    def _authority_paths(self) -> list[Path]:
        authority = self.profile.get("authority")
        if not isinstance(authority, dict):
            raise CharacterProfileError("character profile lacks authority sources")
        try:
            values = (
                authority["registry_path"],
                authority["roster_path"],
                authority["canonrec_boundary_path"],
            )
        except KeyError as exc:
            raise CharacterProfileError("character authority source is incomplete") from exc
        return [_bounded_authority_path(str(value)) for value in values]

    def _opening(self) -> str:
        voice = self.profile.get("voice")
        if not isinstance(voice, dict):
            raise CharacterProfileError("character profile lacks voice boundaries")
        address = voice.get("address")
        self_identification = voice.get("self_identification")
        if not all(
            isinstance(value, str) and value
            for value in (address, self_identification)
        ):
            raise CharacterProfileError("character voice opening is incomplete")
        return f"{address}, {self_identification}."

    def _render_response(
        self,
        decision: Mapping[str, Any],
        latest_event: Mapping[str, Any] | None,
        unresolved_facts: Sequence[str],
    ) -> str:
        action = decision["selected_action"]
        opening = self._opening()
        if action == "review_watch_and_report":
            return _render_status_report(
                decision, latest_event, unresolved_facts, opening
            )
        if action == "assess_and_escalate_if_warranted":
            return _render_emergency_assessment(latest_event, opening)
        if action == "review_authority_and_respond":
            return _render_authority_response(opening)
        return _render_general_contact(opening)


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CharacterProfileError(f"character authority source unavailable: {path}") from exc
    if not isinstance(payload, dict):
        raise CharacterProfileError(f"character authority source is not an object: {path}")
    return payload


def _bounded_authority_path(value: str) -> Path:
    root = PROJECT_ROOT.resolve()
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise CharacterProfileError(
            "character authority source escapes the repository"
        ) from exc
    return path


def _validate_identity(identity: Mapping[str, str], registry: Mapping[str, Any]) -> None:
    authority_matches = (
        identity.get("name") == registry.get("name")
        and identity.get("division") == registry.get("division")
        and identity.get("role") == "Station Commander"
        and identity.get("clearance") == "L4_COMMAND"
        and registry.get("role") == "Commander, Orion Station"
    )
    if not authority_matches:
        raise CharacterProfileError("character actor identity conflicts with staff authority")


def _classify_intents(content: str) -> list[str]:
    normalized = " ".join(re.findall(r"[a-z0-9']+", content.casefold()))
    intents = []
    if _contains_any(normalized, ("status", "report", "station operations")):
        intents.append("station_operations_status")
    if _contains_any(normalized, ("how is everything", "how are you", "up there")):
        intents.append("welfare_check")
    if _contains_any(normalized, ("emergency", "danger", "crisis", "incident")):
        intents.append("emergency_inquiry")
    if _contains_any(normalized, ("authorize", "authority", "approve", "ethics")):
        intents.append("authority_or_governance_request")
    return intents or ["general_contact"]


def _contains_any(content: str, phrases: Sequence[str]) -> bool:
    return any(phrase in content for phrase in phrases)


def _select_action(
    intents: Sequence[str],
    recent_events: Sequence[Mapping[str, Any]],
) -> str:
    if "emergency_inquiry" in intents or _has_emergency_event(recent_events):
        return "assess_and_escalate_if_warranted"
    if "station_operations_status" in intents or "welfare_check" in intents:
        return "review_watch_and_report"
    if "authority_or_governance_request" in intents:
        return "review_authority_and_respond"
    return "acknowledge_and_open_channel"


def _has_emergency_event(events: Sequence[Mapping[str, Any]]) -> bool:
    return any("emergency" in str(item.get("kind", "")) for item in events)


def _decision_event(
    selected_action: str,
    events: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    if selected_action == "assess_and_escalate_if_warranted":
        emergency = next(
            (
                item
                for item in reversed(events)
                if "emergency" in str(item.get("kind", ""))
            ),
            None,
        )
        if emergency is not None:
            return emergency
    return events[-1] if events else None


def _stable_action_id(context: CharacterContext, selected_action: str) -> str:
    source = (
        f"aurora:l1:{context.run_id}:CMD_001:{context.inbound['message_id']}:"
        f"{context.tick}:{selected_action}:{POLICY_VERSION}"
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, source))


def _knowledge_inputs(context: CharacterContext) -> list[Dict[str, Any]]:
    station = [
        {
            "record_id": item["record_id"],
            "subject": item["subject"],
            "provenance": item["provenance"],
            "tick": item["tick"],
            "scope": "station_record",
        }
        for item in context.station_records[-8:]
    ]
    known = [
        {
            "record_id": item["record_id"],
            "subject": item["subject"],
            "provenance": item["provenance"],
            "tick": item["tick"],
            "scope": "character_knowledge",
        }
        for item in context.character_knowledge[-8:]
    ]
    return station + known


def _duty_drivers(selected_action: str) -> list[str]:
    mapping = {
        "review_watch_and_report": [
            "station_operations",
            "strategic_coordination",
            "crew_welfare",
        ],
        "assess_and_escalate_if_warranted": [
            "station_operations",
            "crisis_command",
            "ethical_transparency",
        ],
        "review_authority_and_respond": [
            "ethical_transparency",
            "strategic_coordination",
        ],
        "acknowledge_and_open_channel": ["strategic_coordination"],
    }
    return mapping[selected_action]


def _principle_drivers(selected_action: str) -> list[str]:
    drivers = ["quiet_authority", "bounded_claims"]
    if selected_action != "acknowledge_and_open_channel":
        drivers.append("operational_follow_through")
    if selected_action in {
        "assess_and_escalate_if_warranted",
        "review_authority_and_respond",
    }:
        drivers.append("principle_led_consensus")
    return drivers


def _options_considered(selected_action: str) -> list[Dict[str, str]]:
    candidates = (
        "acknowledge_and_open_channel",
        "defer_response",
        "review_watch_and_report",
        "assess_and_escalate_if_warranted",
        "review_authority_and_respond",
    )
    return [
        {
            "action": candidate,
            "disposition": "selected" if candidate == selected_action else "not_selected",
            "reason": _option_reason(candidate, selected_action),
        }
        for candidate in candidates
    ]


def _option_reason(candidate: str, selected_action: str) -> str:
    if candidate == selected_action:
        return "best fit for the message intent, current records, and command duties"
    if candidate == "defer_response":
        return "no competing crisis or unavailable record requires deferral"
    if candidate == "acknowledge_and_open_channel":
        return "available operational evidence supports a more useful bounded response"
    return "the current message and ledger do not activate this command path"


def _rationale(selected_action: str) -> str:
    if selected_action == "review_watch_and_report":
        return (
            "Station-operations duty and quiet authority favor inspecting the "
            "available watch record before giving a concise external report."
        )
    if selected_action == "assess_and_escalate_if_warranted":
        return (
            "Crisis-command duty requires checking recorded evidence before any "
            "escalation or reassurance."
        )
    if selected_action == "review_authority_and_respond":
        return (
            "A governance request must be separated from Pilot role assumptions "
            "and routed through established authority."
        )
    return "The message establishes contact but does not support a broader action."


def _operational_steps(
    selected_action: str,
    station_records: Sequence[Mapping[str, Any]],
    latest_event: Mapping[str, Any] | None,
) -> list[Dict[str, Any]]:
    steps = [
        {
            "kind": "review_station_records",
            "status": "completed",
            "records_reviewed": len(station_records),
        }
    ]
    if selected_action == "assess_and_escalate_if_warranted":
        steps.append(_emergency_assessment_step(latest_event))
    if selected_action == "review_watch_and_report":
        steps.extend(_status_report_steps(latest_event))
    steps.append({"kind": "transmit_response", "status": "queued"})
    return steps


def _emergency_assessment_step(
    latest_event: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    emergency = bool(latest_event and "emergency" in str(latest_event.get("kind", "")))
    return {
        "kind": "assess_command_exception",
        "status": "completed",
        "result": "recorded_emergency" if emergency else "no_recorded_emergency",
    }


def _status_report_steps(
    latest_event: Mapping[str, Any] | None,
) -> list[Dict[str, Any]]:
    steps = [_emergency_assessment_step(latest_event)]
    if latest_event and latest_event.get("kind") == "maintenance_queue_progress":
        steps.append(
            {
                "kind": "maintain_command_watch",
                "status": "active",
                "subject": "maintenance_queue",
            }
        )
    return steps


def _commitments(
    selected_action: str,
    latest_event: Mapping[str, Any] | None,
) -> list[Dict[str, str]]:
    if (
        selected_action == "review_watch_and_report"
        and latest_event
        and latest_event.get("kind") == "maintenance_queue_progress"
    ):
        return [
            {
                "commitment": "monitor_maintenance_queue",
                "status": "active",
                "owner": "CMD_001",
            }
        ]
    return []


def _active_commitments(
    actions: Sequence[Mapping[str, Any]],
) -> list[Dict[str, str]]:
    active = []
    for action in actions:
        commitments = action.get("commitments", [])
        active.extend(item for item in commitments if item.get("status") == "active")
    return active[-5:]


def _render_status_report(
    decision: Mapping[str, Any],
    latest_event: Mapping[str, Any] | None,
    unresolved_facts: Sequence[str],
    opening: str,
) -> str:
    event_sentence = _event_sentence(latest_event)
    limits = _limits_sentence(unresolved_facts)
    commitment = _commitment_sentence(decision)
    return " ".join(
        part
        for part in (
            f"{opening} I reviewed the current watch record before answering.",
            event_sentence,
            "No emergency is recorded on the current watch.",
            limits,
            commitment,
        )
        if part
    )


def _event_sentence(latest_event: Mapping[str, Any] | None) -> str:
    if latest_event is None:
        return "The watch contains no autonomous station event yet."
    kind = latest_event.get("kind")
    mapping = {
        "maintenance_queue_progress": (
            "The scheduled maintenance queue advanced under standing authority."
        ),
        "routine_shift_handoff": (
            "The station shift handoff closed without a material exception."
        ),
        "research_queue_progress": (
            "A research queue advanced without producing a canon-level conclusion."
        ),
        "no_material_event": (
            "This window contains no recorded material station event."
        ),
    }
    return mapping.get(kind, "The latest station event remains on command review.")


def _limits_sentence(unresolved_facts: Sequence[str]) -> str:
    if not unresolved_facts:
        return ""
    return (
        "The exact crew complement and exact Lagrange point remain unresolved in "
        "this run, so I will not turn either into an estimate."
    )


def _commitment_sentence(decision: Mapping[str, Any]) -> str:
    current = decision.get("commitments", [])
    prior = decision.get("prior_active_commitments", [])
    if current and prior:
        return (
            "The maintenance queue remains on command watch; I will report if it "
            "leaves standing authority."
        )
    if current:
        return (
            "I have placed the maintenance queue on command watch and will report "
            "if it leaves standing authority."
        )
    return "Station operations remain under standing authority."


def _render_emergency_assessment(
    latest_event: Mapping[str, Any] | None,
    opening: str,
) -> str:
    if latest_event and "emergency" in str(latest_event.get("kind", "")):
        return (
            f"{opening} I reviewed the command record. An emergency is recorded; "
            "I am holding action to the station's command and ethics process and will "
            "report the verified disposition."
        )
    return (
        f"{opening} I checked the current command record. No emergency is "
        "recorded. I will not manufacture reassurance beyond the evidence available."
    )


def _render_authority_response(opening: str) -> str:
    return (
        f"{opening} I reviewed the authority boundary. Your transmission is a "
        "request, not an automatic station order. I will route any actionable proposal "
        "through the established command and ethics process."
    )


def _render_general_contact(opening: str) -> str:
    return (
        f"{opening} I have your transmission. It does not yet identify an "
        "operational question or requested decision; clarify the matter and I will "
        "take it through the proper station channel."
    )
