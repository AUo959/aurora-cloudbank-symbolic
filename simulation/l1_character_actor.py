#!/usr/bin/env python3
"""Bounded, canon-projected character agency for the governed L1 runtime."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from l1_character_actor_policy import (
    POLICY_VERSION,
    active_commitments,
    classify_intents,
    commitments,
    decision_event,
    duty_drivers,
    knowledge_inputs,
    operational_steps,
    options_considered,
    principle_drivers,
    rationale,
    render_response,
    select_action,
    stable_action_id,
    governed_emergency_state,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = PROJECT_ROOT / "config" / "l1_character_actor_profiles.json"


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
    governed_records: Sequence[Mapping[str, Any]] = ()


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
        intents = classify_intents(str(context.inbound["content"]))
        emergency_state = governed_emergency_state(context.governed_records)
        selected_action = select_action(intents, context.recent_events, emergency_state)
        relevant_event = decision_event(
            selected_action, context.recent_events, emergency_state
        )
        prior_commitments = active_commitments(context.prior_actions)
        action_id = stable_action_id(context, selected_action)
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
            "knowledge_inputs": knowledge_inputs(context),
            "knowledge_gaps": list(context.unresolved_facts),
            "continuity_inputs": [
                item["action_id"] for item in context.prior_actions[-5:]
            ],
            "duty_drivers": self._driver_receipts(
                "duties", duty_drivers(selected_action)
            ),
            "principle_drivers": self._driver_receipts(
                "decision_principles", principle_drivers(selected_action)
            ),
            "options_considered": options_considered(selected_action),
            "selected_action": selected_action,
            "rationale": rationale(selected_action),
            "operational_steps": operational_steps(
                selected_action,
                context.station_records,
                relevant_event,
            ),
            "commitments": commitments(selected_action, relevant_event),
            "prior_active_commitments": prior_commitments,
        }
        decision["response_content"] = render_response(
            decision,
            relevant_event,
            self._opening(),
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
            self._driver_receipts("duties", duty_drivers(action))
            self._driver_receipts(
                "decision_principles", principle_drivers(action)
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
