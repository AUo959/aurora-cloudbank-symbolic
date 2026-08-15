"""Render compact prose-generation constraints from a Narrative River Frame."""

from __future__ import annotations

from collections.abc import Iterable

from .models import NarrativeRiverFrame


def _bullets(values: Iterable[str], *, empty: str = "- None recorded") -> str:
    items = [value.strip() for value in values if value.strip()]
    return "\n".join(f"- {value}" for value in items) if items else empty


def render_prompt_contract(frame: NarrativeRiverFrame, axioms_text: str = "") -> str:
    values = _prompt_values(frame)
    sections = [
        "NARRATIVE RIVER CONSTRAINTS",
        f"Frame: {frame.frame_id}",
        f"Scene: {frame.scene_id}",
    ]
    for title, body in _prompt_sections(frame, values):
        sections.extend(["", title, body])
    sections.extend(
        [
            "",
            "SURFACE-LANGUAGE FIREWALL",
            (
                "Do not use RiverCycle abstractions such as flow, sediment, reservoir, "
                "nutrient, or turbulence unless an in-world speaker would naturally use "
                "that exact language. Translate internal state into concrete action, "
                "institutional behavior, equipment limits, timing, and consequence."
            ),
        ]
    )
    if axioms_text.strip():
        sections.extend(["", "GOVERNING NARRATIVE AXIOMS", axioms_text.strip()])
    return "\n".join(sections).rstrip() + "\n"


def _prompt_values(frame: NarrativeRiverFrame) -> dict[str, list[str]]:
    pressure_lines = [
        f"{name}: {value:.2f}"
        for name, value in sorted(
            frame.active_pressures.items(), key=lambda item: item[0]
        )
    ]
    flow_lines = [
        f"{item.flow_type} from {item.source_id} to {item.target_id} via {item.carrier} "
        f"(confidence {item.confidence:.2f})"
        for item in frame.incoming_flows
    ]
    sediment_lines = [
        f"{item.description} Current effect: {item.current_effect}"
        for item in frame.sediment
    ]
    evidence_lines = [
        f"[{item.status}] {item.claim} (confidence {item.confidence:.2f})"
        for item in frame.evidence_state
    ]
    actor_lines = [
        f"{item.actor_id}: {item.interpretation} Preferred response: {item.preferred_response} "
        f"Blind spot: {item.blind_spot}"
        for item in frame.actor_interpretations
    ]
    scarcity_lines = [
        f"{item.scarce_asset}: {item.current_quantity if item.current_quantity is not None else 'bounded'}; "
        f"{item.consequence}"
        for item in frame.scarcity_state
    ]

    return {
        "pressures": pressure_lines,
        "flows": flow_lines,
        "sediment": sediment_lines,
        "evidence": evidence_lines,
        "actors": actor_lines,
        "scarcity": scarcity_lines,
    }


def _prompt_sections(
    frame: NarrativeRiverFrame,
    values: dict[str, list[str]],
) -> list[tuple[str, str]]:
    return [
        (
            "VIEWPOINT",
            "\n".join(
                [
                    f"Mode: {frame.viewpoint.mode}",
                    (
                        "Focal characters: "
                        + (", ".join(frame.viewpoint.focal_character_ids) or "unspecified")
                    ),
                    "Prohibited omniscience: "
                    + ("yes" if frame.viewpoint.prohibited_omniscience else "no"),
                ]
            ),
        ),
        (
            "SCENE OBJECTIVE",
            "\n".join(
                [
                    f"Operational: {frame.scene_objective.operational_goal}",
                    f"Dramatic: {frame.scene_objective.dramatic_goal}",
                    (
                        "Required state change: "
                        f"{frame.scene_objective.required_state_change}"
                    ),
                ]
            ),
        ),
        ("INCOMING FLOWS", _bullets(values["flows"])),
        ("ACTIVE PRESSURES", _bullets(values["pressures"])),
        ("ACTIVE RESIDUE", _bullets(values["sediment"])),
        ("EVIDENCE BOUNDARIES", _bullets(values["evidence"])),
        ("ACTOR INTERPRETATIONS", _bullets(values["actors"])),
        ("SCARCITY", _bullets(values["scarcity"])),
        ("UNRESOLVED QUESTIONS", _bullets(frame.unresolved_questions)),
        (
            "REQUIRED DOWNSTREAM EFFECTS",
            _bullets(frame.required_downstream_effects),
        ),
        ("PROHIBITED SHORTCUTS", _bullets(frame.prohibited_shortcuts)),
        ("EXIT CONDITIONS", _bullets(frame.exit_conditions)),
    ]
