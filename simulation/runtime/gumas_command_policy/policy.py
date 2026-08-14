"""Deterministic fixed-point GUMAS command-team policy v1.0."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .coefficients import (
    CANONICAL_JSON_PROFILE,
    COMMANDER_FIELDS,
    OBSERVATION_DEFAULTS,
    POLICY_ID,
    POLICY_VERSION,
    ROLE_ORDER,
    SPECIALIST_FIELDS,
    SPECIALIST_RULES,
    STRATEGIC_WEIGHTS,
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _round_half_even_fraction(numerator: int, denominator: int = 1000) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    sign = -1 if numerator < 0 else 1
    value = abs(numerator)
    quotient, remainder = divmod(value, denominator)
    doubled = remainder * 2
    if doubled > denominator or (doubled == denominator and quotient % 2 == 1):
        quotient += 1
    return sign * quotient


def mul_q(value_q1000: int, weight: int) -> int:
    return _round_half_even_fraction(int(value_q1000) * int(weight), 1000)


def decimal_to_q1000(value: Any) -> int:
    parsed = Decimal(str(value))
    result = int(
        (parsed * Decimal(1000)).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
    )
    if not 0 <= result <= 1000:
        raise ValueError(f"normalized officer value outside [0,1]: {value!r}")
    return result


def normalize_observation(observation: Mapping[str, Any]) -> dict[str, int]:
    unknown = sorted(set(observation) - set(OBSERVATION_DEFAULTS))
    if unknown:
        raise ValueError(f"unknown command observation fields: {unknown}")
    result = dict(OBSERVATION_DEFAULTS)
    for key, value in observation.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"observation {key} must be an integer Q1000")
        if not 0 <= value <= 1000:
            raise ValueError(f"observation {key} outside [0,1000]")
        result[key] = value
    return result


def normalize_command_team(
    command_team: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    by_assignment: dict[str, Mapping[str, Any]] = {}
    for raw in command_team:
        assignment = str(raw.get("assignment", "")).strip()
        if not assignment:
            raise ValueError("command-team member missing assignment")
        if assignment in by_assignment:
            raise ValueError(f"duplicate command assignment: {assignment}")
        by_assignment[assignment] = raw

    required = {"commander", *ROLE_ORDER}
    missing = sorted(required - set(by_assignment))
    extra = sorted(set(by_assignment) - required)
    if missing or extra:
        raise ValueError(
            f"invalid command assignments; missing={missing}, extra={extra}"
        )

    commander_raw = by_assignment["commander"]
    commander_attrs = commander_raw.get("attributes") or {}
    commander = {
        "entity_id": str(commander_raw.get("entity_id", "")),
        "assignment": "commander",
        "attributes_q1000": {
            field: decimal_to_q1000(commander_attrs[field])
            for field in COMMANDER_FIELDS
        },
    }
    if not commander["entity_id"]:
        raise ValueError("commander missing entity_id")

    specialists: dict[str, Any] = {}
    for role in ROLE_ORDER:
        raw = by_assignment[role]
        attrs = raw.get("attributes") or {}
        entity_id = str(raw.get("entity_id", ""))
        if not entity_id:
            raise ValueError(f"{role} specialist missing entity_id")
        specialists[role] = {
            "entity_id": entity_id,
            "assignment": role,
            "attributes_q1000": {
                field: decimal_to_q1000(attrs[field])
                for field in SPECIALIST_FIELDS
            },
        }

    return {"commander": commander, "specialists": specialists}


def _derived_observation(obs: Mapping[str, int]) -> dict[str, int]:
    return {
        "parity": 1000 - min(1000, abs(obs["relative_advantage"] - 500) * 2),
        "contact_deficit": 1000 - obs["contact_quality"],
        "repair_deficit": 1000 - obs["repair_need"],
        "mobility_deficit": 1000 - obs["mobility_margin"],
        "logistics_margin": 1000 - obs["logistics_strain"],
    }


def _score_weight_table(
    weights: Mapping[str, int],
    commander: Mapping[str, int],
    specialist: Mapping[str, int] | None,
    obs: Mapping[str, int],
    derived: Mapping[str, int],
) -> tuple[int, list[dict[str, int | str]]]:
    terms: list[dict[str, int | str]] = []
    total = 0
    specialist = specialist or {}
    derived_sp = {
        "risk_aversion": 1000 - specialist.get("risk_tolerance", 500),
    }
    for source, weight in sorted(weights.items()):
        namespace, key = source.split(".", 1)
        if namespace == "cmd":
            value = commander[key]
        elif namespace == "sp":
            value = specialist[key]
        elif namespace == "obs":
            value = obs[key]
        elif namespace == "derived":
            if key in derived_sp:
                value = derived_sp[key]
            else:
                value = derived[key]
        else:
            raise ValueError(f"unknown scoring namespace: {namespace}")
        contribution = mul_q(value, weight)
        total += contribution
        terms.append(
            {
                "source": source,
                "value_q1000": value,
                "weight": weight,
                "contribution": contribution,
            }
        )
    return total, terms


def _choose(score_map: Mapping[str, int]) -> tuple[str, list[str]]:
    best = max(score_map.values())
    tied = sorted(action for action, score in score_map.items() if score == best)
    return tied[0], tied


def score_strategic(
    commander: Mapping[str, int], observation: Mapping[str, int]
) -> dict[str, Any]:
    derived = _derived_observation(observation)
    scores: dict[str, Any] = {}
    raw: dict[str, int] = {}
    for action, weights in sorted(STRATEGIC_WEIGHTS.items()):
        total, terms = _score_weight_table(
            weights,
            commander,
            None,
            observation,
            derived,
        )
        raw[action] = total
        scores[action] = {"score": total, "terms": terms}
    selected, tied = _choose(raw)
    return {
        "scores": scores,
        "selected": selected,
        "tie_break": tied if len(tied) > 1 else [],
    }


def specialist_competence(attrs: Mapping[str, int]) -> int:
    return sum(
        [
            mul_q(attrs["domain_skill"], 350),
            mul_q(attrs["initiative"], 150),
            mul_q(attrs["discipline"], 150),
            mul_q(attrs["stress_tolerance"], 200),
            mul_q(attrs["risk_tolerance"], 150),
        ]
    )


def score_specialist(
    role: str,
    attrs: Mapping[str, int],
    commander: Mapping[str, int],
    observation: Mapping[str, int],
    strategic_posture: str,
) -> dict[str, Any]:
    if role not in SPECIALIST_RULES:
        raise ValueError(f"unknown specialist role: {role}")
    derived = _derived_observation(observation)
    competence = specialist_competence(attrs)
    independence = 1000 - attrs["commander_alignment"]
    effective_voice = (
        mul_q(competence, 700)
        + mul_q(attrs["commander_alignment"], 300)
    )
    safety_pressure = max(
        observation["own_damage"],
        observation["logistics_strain"],
        observation["enemy_closing_pressure"],
        observation["uncertainty"],
        observation["repair_need"],
    )

    independent_scores: dict[str, int] = {}
    final_scores: dict[str, int] = {}
    details: dict[str, Any] = {}

    for action, rule in sorted(SPECIALIST_RULES[role].items()):
        base, terms = _score_weight_table(
            rule["weights"],
            commander,
            attrs,
            observation,
            derived,
        )
        independent_scores[action] = base
        compatibility_weight = int(
            rule.get("compat", {}).get(strategic_posture, 0)
        )
        alignment_term = mul_q(
            attrs["commander_alignment"], compatibility_weight
        )
        safety_term = 0
        if bool(rule.get("safety")):
            independent_safety = mul_q(competence, independence)
            independent_safety = mul_q(independent_safety, safety_pressure)
            safety_term = mul_q(independent_safety, 250)
        final = base + alignment_term + safety_term
        final_scores[action] = final
        details[action] = {
            "score": final,
            "independent_score": base,
            "attribute_observation_terms": terms,
            "strategic_compatibility_weight": compatibility_weight,
            "alignment_term": alignment_term,
            "independent_safety_term": safety_term,
        }

    independent_preferred, _ = _choose(independent_scores)
    selected, tied = _choose(final_scores)
    dissent = 0
    if independent_preferred != selected:
        dissent = mul_q(competence, independence)

    return {
        "role": role,
        "competence_q1000": competence,
        "independence_q1000": independence,
        "effective_voice_q1000": effective_voice,
        "independent_preferred": independent_preferred,
        "scores": details,
        "selected": selected,
        "dissent_q1000": dissent,
        "tie_break": tied if len(tied) > 1 else [],
    }


def _source_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def decide(
    command_team: Sequence[Mapping[str, Any]],
    observation: Mapping[str, Any],
    *,
    side_id: str,
    fleet_id: str,
    decision_epoch: int,
    baseline_identity: Mapping[str, str],
) -> dict[str, Any]:
    if (
        isinstance(decision_epoch, bool)
        or not isinstance(decision_epoch, int)
        or decision_epoch < 0
    ):
        raise ValueError("decision_epoch must be a non-negative integer")
    if not side_id or not fleet_id:
        raise ValueError("side_id and fleet_id are required")

    obs = normalize_observation(observation)
    team = normalize_command_team(command_team)
    commander = team["commander"]["attributes_q1000"]
    strategic = score_strategic(commander, obs)
    specialist_receipts = {}
    for role in ROLE_ORDER:
        specialist_receipts[role] = score_specialist(
            role,
            team["specialists"][role]["attributes_q1000"],
            commander,
            obs,
            strategic["selected"],
        )

    receipt: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/command_decision_receipt/v1.0",
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "policy_source_sha256": _source_sha256(),
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "baseline_identity": dict(sorted(baseline_identity.items())),
        "side_id": side_id,
        "fleet_id": fleet_id,
        "decision_epoch": decision_epoch,
        "observation": obs,
        "observation_sha256": sha256_canonical(obs),
        "command_team_numeric": team,
        "command_team_numeric_sha256": sha256_canonical(team),
        "strategic": strategic,
        "specialists": specialist_receipts,
        "orders": {
            "strategic_posture": strategic["selected"],
            "specialist_intents": {
                role: specialist_receipts[role]["selected"]
                for role in ROLE_ORDER
            },
        },
        "prose_inputs_used": False,
        "rng_used": False,
    }
    receipt["decision_sha256"] = sha256_canonical(receipt)
    return receipt
