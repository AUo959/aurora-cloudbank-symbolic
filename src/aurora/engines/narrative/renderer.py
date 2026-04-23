from __future__ import annotations

from .types import EvaluationPacket, ResponsePayload


def finalize_evaluation(packet: EvaluationPacket) -> EvaluationPacket:
    packet.blocks = packet.hard_blocks + packet.soft_blocks
    packet.supports = _dedupe(packet.supports)
    packet.blocks = _dedupe(packet.blocks)
    packet.missing_bridges = _dedupe(packet.missing_bridges)
    packet.confidence_notes = _dedupe(packet.confidence_notes)
    return packet


def compact_response(response: ResponsePayload) -> ResponsePayload:
    return ResponsePayload(
        summary=response.summary.strip(),
        verdict=response.verdict,
        main_supports=_dedupe(response.main_supports),
        main_blockers=_dedupe(response.main_blockers),
        missing_bridges=_dedupe(response.missing_bridges),
        smallest_fix=_dedupe(response.smallest_fix),
        confidence=response.confidence,
        supported_in_phase_one=response.supported_in_phase_one,
        unsupported_reason=response.unsupported_reason,
    )


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered
