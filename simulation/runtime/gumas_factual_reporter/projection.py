"""Deterministic factual projection over validated Phase-9 artifacts."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from .constants import (
    CANONICAL_JSON_PROFILE,
    FACTUAL_EVENT_SCHEMA,
    HISTORICAL_CANON_STATUS,
    NORMALIZED_REPORT_SCHEMA,
    PHASE10_CONTRACT_ID,
    PHASE10_VERSION,
    PUBLIC_FACT_TYPES,
    PUBLIC_SUMMARY_PROFILE,
    SIMULATION_TRUTH_PROFILE,
)
from .identity import hash_without_field, json_pointer_escape


PHASE_CODES = {
    "phase4": "p04",
    "phase5": "p05",
    "phase6": "p06",
    "phase7": "p07",
    "phase8": "p08",
    "phase9": "p09",
}


class EvidenceCollector:
    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._by_key: dict[tuple[Any, ...], str] = {}
        self._counts: dict[int, int] = {}

    def add(
        self,
        *,
        macrostep_index: int,
        artifact_kind: str,
        artifact_sha256: str,
        json_pointers: Sequence[str],
        ledger_entry_sha256: str,
    ) -> str:
        pointers = tuple(sorted(str(pointer) for pointer in json_pointers))
        key = (
            macrostep_index,
            artifact_kind,
            artifact_sha256,
            pointers,
            ledger_entry_sha256,
        )
        prior = self._by_key.get(key)
        if prior is not None:
            return prior
        count = self._counts.get(macrostep_index, 0) + 1
        self._counts[macrostep_index] = count
        ref_id = f"m{macrostep_index:08d}:e{count:04d}:{artifact_kind}"
        record = {
            "evidence_ref_id": ref_id,
            "macrostep_index": macrostep_index,
            "artifact_kind": artifact_kind,
            "artifact_sha256": artifact_sha256,
            "json_pointers": list(pointers),
            "ledger_entry_sha256": ledger_entry_sha256,
        }
        self._records.append(record)
        self._by_key[key] = ref_id
        return ref_id

    def records(self) -> list[dict[str, Any]]:
        return sorted(copy.deepcopy(self._records), key=lambda item: item["evidence_ref_id"])


def _event(
    *,
    macrostep_index: int,
    phase: str,
    sequence: int,
    fact_type: str,
    fact_basis: str,
    subject_id: str | None,
    object_id: str | None,
    fields: Mapping[str, Any],
    evidence_ref_ids: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema": FACTUAL_EVENT_SCHEMA,
        "event_id": (
            f"m{macrostep_index:08d}:{PHASE_CODES[phase]}:{sequence:04d}:{fact_type}"
        ),
        "macrostep_index": macrostep_index,
        "phase": phase,
        "sequence": sequence,
        "fact_type": fact_type,
        "fact_basis": fact_basis,
        "subject_id": subject_id,
        "object_id": object_id,
        "fields": copy.deepcopy(dict(fields)),
        "evidence_ref_ids": sorted(set(str(item) for item in evidence_ref_ids)),
    }


def _artifact_ref(
    collector: EvidenceCollector,
    *,
    macrostep_index: int,
    artifact_kind: str,
    artifact_sha256: str,
    pointers: Sequence[str],
    ledger_sha256: str,
) -> str:
    return collector.add(
        macrostep_index=macrostep_index,
        artifact_kind=artifact_kind,
        artifact_sha256=artifact_sha256,
        json_pointers=pointers,
        ledger_entry_sha256=ledger_sha256,
    )


def _sorted_with_original_index(
    values: Sequence[Mapping[str, Any]],
    key,
) -> list[tuple[int, Mapping[str, Any]]]:
    return sorted(enumerate(values), key=lambda pair: key(pair[1]))


def build_truth_projection(
    validated_input: Mapping[str, Any],
    reporter_source_identity: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context = validated_input["run_context"]
    macrosteps = validated_input["macrosteps"]
    collector = EvidenceCollector()
    events: list[dict[str, Any]] = []

    for step in macrosteps:
        ledger = step["ledger_entry"]
        macrostep_index = int(ledger["macrostep_index"])
        ledger_sha = str(ledger["ledger_entry_sha256"])
        step_events: list[dict[str, Any]] = []

        def add_event(
            phase: str,
            fact_type: str,
            fact_basis: str,
            fields: Mapping[str, Any],
            refs: Sequence[str],
            *,
            subject_id: str | None = None,
            object_id: str | None = None,
        ) -> None:
            step_events.append(
                _event(
                    macrostep_index=macrostep_index,
                    phase=phase,
                    sequence=len(step_events) + 1,
                    fact_type=fact_type,
                    fact_basis=fact_basis,
                    subject_id=subject_id,
                    object_id=object_id,
                    fields=fields,
                    evidence_ref_ids=refs,
                )
            )

        ledger_ref = _artifact_ref(
            collector,
            macrostep_index=macrostep_index,
            artifact_kind="phase9_ledger_entry",
            artifact_sha256=ledger_sha,
            pointers=(
                "/macrostep_index",
                "/start_elapsed_ms",
                "/end_elapsed_ms",
                "/previous_ledger_entry_sha256",
                "/previous_committed_state_sha256",
                "/phase8_next_state_sha256",
            ),
            ledger_sha256=ledger_sha,
        )
        add_event(
            "phase9",
            "macrostep_boundary",
            "committed_field",
            {
                "run_identity_sha256": ledger["run_identity_sha256"],
                "t0_roster_sha256": ledger["t0_roster_sha256"],
                "start_elapsed_ms": ledger["start_elapsed_ms"],
                "end_elapsed_ms": ledger["end_elapsed_ms"],
                "previous_ledger_entry_sha256": ledger["previous_ledger_entry_sha256"],
                "previous_committed_state_sha256": ledger["previous_committed_state_sha256"],
                "committed_state_sha256": ledger["phase8_next_state_sha256"],
                "ledger_entry_sha256": ledger_sha,
                "historical_canon_status": ledger["historical_canon_status"],
                "run0_executed": ledger["run0_executed"],
            },
            (ledger_ref,),
        )

        observations = step["observation_receipts_by_side"]
        for side_id, receipt in sorted(observations.items()):
            observation_ref = _artifact_ref(
                collector,
                macrostep_index=macrostep_index,
                artifact_kind="live_observation_receipt",
                artifact_sha256=str(receipt["live_observation_receipt_sha256"]),
                pointers=("/observation", "/observation_sha256", "/side_id", "/fleet_id"),
                ledger_sha256=ledger_sha,
            )
            add_event(
                "phase4",
                "command_observation",
                "committed_field",
                {
                    "side_id": side_id,
                    "fleet_id": receipt["fleet_id"],
                    "decision_epoch": receipt["decision_epoch"],
                    "observation": receipt["observation"],
                    "observation_sha256": receipt["observation_sha256"],
                    "source_committed_state_sha256": receipt["source_committed_state_sha256"],
                },
                (observation_ref, ledger_ref),
                subject_id=side_id,
            )

        decisions = step["decisions_by_fleet"]
        for fleet_id, receipt in sorted(decisions.items()):
            decision_ref = _artifact_ref(
                collector,
                macrostep_index=macrostep_index,
                artifact_kind="command_decision_receipt",
                artifact_sha256=str(receipt["decision_sha256"]),
                pointers=("/orders", "/side_id", "/fleet_id", "/decision_epoch", "/observation_sha256"),
                ledger_sha256=ledger_sha,
            )
            add_event(
                "phase4",
                "command_order",
                "committed_field",
                {
                    "side_id": receipt["side_id"],
                    "fleet_id": fleet_id,
                    "decision_epoch": receipt["decision_epoch"],
                    "observation_sha256": receipt["observation_sha256"],
                    "orders": receipt["orders"],
                    "decision_sha256": receipt["decision_sha256"],
                },
                (decision_ref, ledger_ref),
                subject_id=str(receipt["side_id"]),
                object_id=fleet_id,
            )

        movement = step["movement_receipt"]
        movement_sha = str(movement["movement_receipt_sha256"])
        movement_values = movement["per_vessel"]
        for original_index, summary in _sorted_with_original_index(
            movement_values,
            lambda item: str(item["ship_id"]),
        ):
            movement_ref = _artifact_ref(
                collector,
                macrostep_index=macrostep_index,
                artifact_kind="movement_receipt",
                artifact_sha256=movement_sha,
                pointers=(f"/per_vessel/{original_index}",),
                ledger_sha256=ledger_sha,
            )
            add_event(
                "phase5",
                "movement_vessel",
                "committed_field",
                summary,
                (movement_ref, ledger_ref),
                subject_id=str(summary["ship_id"]),
            )
        movement_aggregate_ref = _artifact_ref(
            collector,
            macrostep_index=macrostep_index,
            artifact_kind="movement_receipt",
            artifact_sha256=movement_sha,
            pointers=("/per_vessel",),
            ledger_sha256=ledger_sha,
        )
        add_event(
            "phase5",
            "movement_aggregate",
            "deterministic_aggregation",
            {
                "vessel_count": len(movement_values),
                "collision_count": sum(item.get("collision") is not None for item in movement_values),
                "boundary_crossing_count": sum(
                    item.get("boundary_crossing") is not None for item in movement_values
                ),
            },
            (movement_aggregate_ref, ledger_ref),
        )

        phase6 = step["phase6_receipt"]
        phase6_sha = str(phase6["phase6_receipt_sha256"])
        phase6_specs = (
            (
                "sensor_contact",
                "contacts",
                lambda item: (str(item.get("observer_ship_id") or ""), str(item.get("target_ship_id") or "")),
                lambda item: str(item.get("observer_ship_id") or "") or None,
                lambda item: str(item.get("target_ship_id") or "") or None,
            ),
            (
                "target_selection",
                "selections",
                lambda item: str(item.get("shooter_ship_id") or ""),
                lambda item: str(item.get("shooter_ship_id") or "") or None,
                lambda item: str(item.get("target_ship_id") or item.get("selected_target_ship_id") or "") or None,
            ),
            (
                "weapon_attempt",
                "weapon_attempts",
                lambda item: (str(item.get("shooter_ship_id") or ""), str(item.get("target_ship_id") or "")),
                lambda item: str(item.get("shooter_ship_id") or "") or None,
                lambda item: str(item.get("target_ship_id") or "") or None,
            ),
            (
                "delivered_effect",
                "effect_descriptors",
                lambda item: str(item.get("effect_id") or ""),
                lambda item: str(item.get("source_ship_id") or "") or None,
                lambda item: str(item.get("target_ship_id") or "") or None,
            ),
        )
        for fact_type, field, sort_key, subject, target in phase6_specs:
            for original_index, item in _sorted_with_original_index(phase6[field], sort_key):
                phase6_ref = _artifact_ref(
                    collector,
                    macrostep_index=macrostep_index,
                    artifact_kind="phase6_receipt",
                    artifact_sha256=phase6_sha,
                    pointers=(f"/{json_pointer_escape(field)}/{original_index}",),
                    ledger_sha256=ledger_sha,
                )
                add_event(
                    "phase6",
                    fact_type,
                    "committed_field",
                    item,
                    (phase6_ref, ledger_ref),
                    subject_id=subject(item),
                    object_id=target(item),
                )
        phase6_aggregate_ref = _artifact_ref(
            collector,
            macrostep_index=macrostep_index,
            artifact_kind="phase6_receipt",
            artifact_sha256=phase6_sha,
            pointers=("/contacts", "/selections", "/weapon_attempts", "/effect_descriptors"),
            ledger_sha256=ledger_sha,
        )
        add_event(
            "phase6",
            "sensing_fire_aggregate",
            "deterministic_aggregation",
            {
                "contact_count": len(phase6["contacts"]),
                "selection_count": len(phase6["selections"]),
                "weapon_attempt_count": len(phase6["weapon_attempts"]),
                "delivered_effect_count": len(phase6["effect_descriptors"]),
            },
            (phase6_aggregate_ref, ledger_ref),
        )

        phase7 = step["phase7_receipt"]
        phase7_sha = str(phase7["phase7_receipt_sha256"])
        targets = phase7["target_damage_receipts"]
        for original_index, target in _sorted_with_original_index(
            targets,
            lambda item: str(item["target_ship_id"]),
        ):
            target_ref = _artifact_ref(
                collector,
                macrostep_index=macrostep_index,
                artifact_kind="target_damage_receipt",
                artifact_sha256=str(target["target_damage_receipt_sha256"]),
                pointers=("/",),
                ledger_sha256=ledger_sha,
            )
            phase7_ref = _artifact_ref(
                collector,
                macrostep_index=macrostep_index,
                artifact_kind="phase7_receipt",
                artifact_sha256=phase7_sha,
                pointers=(f"/target_damage_receipts/{original_index}",),
                ledger_sha256=ledger_sha,
            )
            add_event(
                "phase7",
                "target_damage",
                "committed_field",
                target,
                (target_ref, phase7_ref, ledger_ref),
                subject_id=str(target["target_ship_id"]),
            )
        phase7_aggregate_ref = _artifact_ref(
            collector,
            macrostep_index=macrostep_index,
            artifact_kind="phase7_receipt",
            artifact_sha256=phase7_sha,
            pointers=("/effect_count", "/affected_target_count", "/target_damage_receipts"),
            ledger_sha256=ledger_sha,
        )
        add_event(
            "phase7",
            "damage_aggregate",
            "deterministic_aggregation",
            {
                "effect_count": phase7["effect_count"],
                "affected_target_count": phase7["affected_target_count"],
            },
            (phase7_aggregate_ref, ledger_ref),
        )

        resolution = step["phase8_resolution_state"]
        resolution_sha = str(resolution["resolution_state_sha256"])
        for side_id in sorted(resolution["side_aggregate"]):
            side_pointer = json_pointer_escape(side_id)
            resolution_ref = _artifact_ref(
                collector,
                macrostep_index=macrostep_index,
                artifact_kind="phase8_resolution_state",
                artifact_sha256=resolution_sha,
                pointers=(
                    f"/side_aggregate/{side_pointer}",
                    f"/shock_by_side/{side_pointer}",
                    f"/dissent_by_side/{side_pointer}",
                    f"/withdrawal_by_side/{side_pointer}",
                    f"/surrender_by_side/{side_pointer}",
                    f"/engagement_status_by_side/{side_pointer}",
                    f"/negotiation_signal_q1000_by_side/{side_pointer}",
                ),
                ledger_sha256=ledger_sha,
            )
            add_event(
                "phase8",
                "side_resolution",
                "committed_field",
                {
                    "side_id": side_id,
                    "aggregate": resolution["side_aggregate"][side_id],
                    "shock": resolution["shock_by_side"][side_id],
                    "dissent": resolution["dissent_by_side"][side_id],
                    "withdrawal": resolution["withdrawal_by_side"][side_id],
                    "surrender": resolution["surrender_by_side"][side_id],
                    "engagement_status": resolution["engagement_status_by_side"][side_id],
                    "negotiation_signal_q1000": resolution[
                        "negotiation_signal_q1000_by_side"
                    ][side_id],
                },
                (resolution_ref, ledger_ref),
                subject_id=side_id,
            )

        phase8 = step["phase8_receipt"]
        phase8_ref = _artifact_ref(
            collector,
            macrostep_index=macrostep_index,
            artifact_kind="phase8_receipt",
            artifact_sha256=str(phase8["phase8_receipt_sha256"]),
            pointers=("/terminal_outcome", "/resolution_state_sha256"),
            ledger_sha256=ledger_sha,
        )
        terminal_ref = _artifact_ref(
            collector,
            macrostep_index=macrostep_index,
            artifact_kind="phase8_resolution_state",
            artifact_sha256=resolution_sha,
            pointers=("/terminal_outcome",),
            ledger_sha256=ledger_sha,
        )
        add_event(
            "phase8",
            "terminal_outcome",
            "verbatim_committed_field",
            resolution["terminal_outcome"],
            (terminal_ref, phase8_ref, ledger_ref),
        )
        events.extend(step_events)

    report = {
        "schema": NORMALIZED_REPORT_SCHEMA,
        "phase10_contract_id": PHASE10_CONTRACT_ID,
        "phase10_version": PHASE10_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "reporter_source_identity": copy.deepcopy(dict(reporter_source_identity)),
        "profile_id": SIMULATION_TRUTH_PROFILE,
        "historical_canon_status": HISTORICAL_CANON_STATUS,
        "run0_executed": False,
        "run_identity_sha256": context["run_identity_sha256"],
        "t0_roster_sha256": context["t0_roster_sha256"],
        "macrostep_count": len(macrosteps),
        "first_elapsed_ms": macrosteps[0]["ledger_entry"]["start_elapsed_ms"],
        "final_elapsed_ms": macrosteps[-1]["ledger_entry"]["end_elapsed_ms"],
        "ledger_head_sha256": macrosteps[-1]["ledger_entry"]["ledger_entry_sha256"],
        "events": events,
    }
    report["normalized_report_sha256"] = hash_without_field(
        report,
        "normalized_report_sha256",
    )
    return report, collector.records()


def select_profile(
    truth_report: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
    profile_id: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if profile_id == SIMULATION_TRUTH_PROFILE:
        return copy.deepcopy(dict(truth_report)), copy.deepcopy(list(evidence_records))
    if profile_id != PUBLIC_SUMMARY_PROFILE:
        raise ValueError(f"unsupported report profile: {profile_id}")

    selected_events: list[dict[str, Any]] = []
    sequence_by_step: dict[int, int] = {}
    for raw_event in truth_report["events"]:
        if raw_event["fact_type"] not in PUBLIC_FACT_TYPES:
            continue
        event = copy.deepcopy(dict(raw_event))
        if event["fact_type"] == "side_resolution":
            fields = event["fields"]
            aggregate = fields["aggregate"]
            event["fields"] = {
                "side_id": fields["side_id"],
                "aggregate": {
                    "surviving_count": len(aggregate["surviving_ship_ids"]),
                    "mobile_count": len(aggregate["mobile_ship_ids"]),
                    "combat_effective_count": len(
                        aggregate["combat_effective_ship_ids"]
                    ),
                    "disabled_count": len(aggregate["disabled_ship_ids"]),
                    "destroyed_count": len(aggregate["destroyed_ship_ids"]),
                    "fleet_morale_q1000": aggregate["fleet_morale_q1000"],
                    "fleet_cohesion_q1000": aggregate["fleet_cohesion_q1000"],
                    "combat_effective_fraction_q1000": aggregate[
                        "combat_effective_fraction_q1000"
                    ],
                    "surviving_hull_fraction_q1000": aggregate[
                        "surviving_hull_fraction_q1000"
                    ],
                },
                "engagement_status": fields["engagement_status"],
                "withdrawal_intent": fields["withdrawal"]["intent"],
                "withdrawal_success": fields["withdrawal"]["success"],
                "withdrawn_mobile_fraction_q1000": fields["withdrawal"][
                    "withdrawn_mobile_fraction_q1000"
                ],
                "surrender_eligible_posture": fields["surrender"][
                    "eligible_posture"
                ],
                "surrender_predicate": fields["surrender"]["predicate"],
                "negotiation_signal_q1000": fields["negotiation_signal_q1000"],
            }
        macrostep = int(event["macrostep_index"])
        sequence = sequence_by_step.get(macrostep, 0) + 1
        sequence_by_step[macrostep] = sequence
        event["sequence"] = sequence
        event["event_id"] = (
            f"m{macrostep:08d}:{PHASE_CODES[event['phase']]}:{sequence:04d}:{event['fact_type']}"
        )
        selected_events.append(event)

    used_refs = {
        ref_id
        for event in selected_events
        for ref_id in event["evidence_ref_ids"]
    }
    selected_refs = [
        copy.deepcopy(dict(record))
        for record in evidence_records
        if record["evidence_ref_id"] in used_refs
    ]
    selected = {
        key: copy.deepcopy(value)
        for key, value in truth_report.items()
        if key not in {"profile_id", "events", "normalized_report_sha256"}
    }
    selected["profile_id"] = PUBLIC_SUMMARY_PROFILE
    selected["events"] = selected_events
    selected["normalized_report_sha256"] = hash_without_field(
        selected,
        "normalized_report_sha256",
    )
    return selected, sorted(selected_refs, key=lambda item: item["evidence_ref_id"])
