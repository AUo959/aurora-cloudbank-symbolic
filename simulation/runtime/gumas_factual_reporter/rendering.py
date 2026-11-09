"""Fixed-template deterministic rendering for Phase-10 factual reports."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .constants import (
    CANONICAL_JSON_PROFILE,
    PHASE10_CONTRACT_ID,
    PHASE10_VERSION,
    RENDERED_REPORT_SCHEMA,
)
from .identity import canonical_json_bytes, sha256_bytes


def _canonical_inline(value: Any) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def render_report(report: Mapping[str, Any]) -> dict[str, Any]:
    lines: list[str] = []
    structural_line_numbers: list[int] = []
    statements: list[dict[str, Any]] = []

    def structural(text: str) -> None:
        lines.append(text)
        structural_line_numbers.append(len(lines))

    def statement(text: str, event_ids: Sequence[str]) -> None:
        lines.append(text)
        statements.append(
            {
                "statement_id": f"s{len(statements) + 1:06d}",
                "line_number": len(lines),
                "event_ids": sorted(set(event_ids)),
                "text": text,
            }
        )

    events = list(report["events"])
    boundaries = [item for item in events if item["fact_type"] == "macrostep_boundary"]
    boundary_ids = [item["event_id"] for item in boundaries]

    structural("GUMAS FACTUAL REPORT v1")
    statement(
        (
            f"profile={report['profile_id']} "
            f"canon_status={report['historical_canon_status']} "
            f"run0_executed={str(report['run0_executed']).lower()}"
        ),
        boundary_ids,
    )
    statement(
        (
            f"run={report['run_identity_sha256']} "
            f"roster={report['t0_roster_sha256']} "
            f"ledger_head={report['ledger_head_sha256']}"
        ),
        boundary_ids,
    )
    statement(
        (
            f"macrosteps={report['macrostep_count']} "
            f"elapsed_ms={report['first_elapsed_ms']}..{report['final_elapsed_ms']}"
        ),
        boundary_ids,
    )

    by_step: dict[int, list[Mapping[str, Any]]] = {}
    for event in events:
        by_step.setdefault(int(event["macrostep_index"]), []).append(event)

    for step_position, macrostep_index in enumerate(sorted(by_step)):
        structural("")
        step_events = by_step[macrostep_index]
        by_type: dict[str, list[Mapping[str, Any]]] = {}
        for event in step_events:
            by_type.setdefault(str(event["fact_type"]), []).append(event)

        boundary = by_type["macrostep_boundary"][0]
        boundary_fields = boundary["fields"]
        statement(
            (
                f"STEP {macrostep_index} "
                f"elapsed_ms={boundary_fields['start_elapsed_ms']}..{boundary_fields['end_elapsed_ms']} "
                f"ledger={boundary_fields['ledger_entry_sha256']}"
            ),
            (boundary["event_id"],),
        )

        for command in by_type.get("command_order", []):
            fields = command["fields"]
            orders = fields["orders"]
            intents = ",".join(
                f"{role}={value}"
                for role, value in sorted(orders["specialist_intents"].items())
            )
            statement(
                (
                    f"COMMAND side={fields['side_id']} fleet={fields['fleet_id']} "
                    f"posture={orders['strategic_posture']} intents={intents}"
                ),
                (command["event_id"],),
            )

        movement = by_type["movement_aggregate"][0]
        fields = movement["fields"]
        statement(
            (
                f"MOVEMENT vessels={fields['vessel_count']} "
                f"collisions={fields['collision_count']} "
                f"boundary_crossings={fields['boundary_crossing_count']}"
            ),
            (movement["event_id"],),
        )

        sensing = by_type["sensing_fire_aggregate"][0]
        fields = sensing["fields"]
        statement(
            (
                f"SENSING contacts={fields['contact_count']} "
                f"selections={fields['selection_count']} "
                f"attempts={fields['weapon_attempt_count']} "
                f"effects={fields['delivered_effect_count']}"
            ),
            (sensing["event_id"],),
        )

        damage = by_type["damage_aggregate"][0]
        fields = damage["fields"]
        statement(
            (
                f"DAMAGE effects={fields['effect_count']} "
                f"targets={fields['affected_target_count']}"
            ),
            (damage["event_id"],),
        )

        for resolution in by_type["side_resolution"]:
            fields = resolution["fields"]
            aggregate = fields["aggregate"]
            if "surviving_ship_ids" in aggregate:
                counts = {
                    "surviving": len(aggregate["surviving_ship_ids"]),
                    "mobile": len(aggregate["mobile_ship_ids"]),
                    "combat_effective": len(aggregate["combat_effective_ship_ids"]),
                    "disabled": len(aggregate["disabled_ship_ids"]),
                    "destroyed": len(aggregate["destroyed_ship_ids"]),
                }
            else:
                counts = {
                    "surviving": aggregate["surviving_count"],
                    "mobile": aggregate["mobile_count"],
                    "combat_effective": aggregate["combat_effective_count"],
                    "disabled": aggregate["disabled_count"],
                    "destroyed": aggregate["destroyed_count"],
                }
            statement(
                (
                    f"RESOLUTION side={fields['side_id']} "
                    f"surviving={counts['surviving']} "
                    f"mobile={counts['mobile']} "
                    f"combat_effective={counts['combat_effective']} "
                    f"disabled={counts['disabled']} "
                    f"destroyed={counts['destroyed']} "
                    f"morale_q1000={aggregate['fleet_morale_q1000']} "
                    f"cohesion_q1000={aggregate['fleet_cohesion_q1000']}"
                ),
                (resolution["event_id"],),
            )

        terminal = by_type["terminal_outcome"][0]
        fields = terminal["fields"]
        statement(
            (
                f"TERMINAL terminated={str(fields['terminated']).lower()} "
                f"mode={fields['termination_mode']} fields={_canonical_inline(fields)}"
            ),
            (terminal["event_id"],),
        )

        if step_position == len(by_step) - 1:
            continue

    text = "\n".join(lines) + "\n"
    return {
        "schema": RENDERED_REPORT_SCHEMA,
        "phase10_contract_id": PHASE10_CONTRACT_ID,
        "phase10_version": PHASE10_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "profile_id": report["profile_id"],
        "structural_line_numbers": structural_line_numbers,
        "statements": statements,
        "text": text,
        "rendered_report_sha256": sha256_bytes(text.encode("utf-8")),
    }
