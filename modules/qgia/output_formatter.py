"""QGIA Forecast Simulation Engine — Three-Tier Output Formatter.

Formats ForecastOutput into structured text matching the Analyst Orientation
Guide reading protocol: TIMESTAMP -> TIER I -> TIER II -> TIER III ->
CONFIDENCE -> PROVENANCE -> YOUR INTEL.
"""

from .schemas import ForecastOutput, TierAssessment

__all__ = ["format_forecast"]

_TIER_HEADERS = {
    1: "TIER I \u2014 MOST LIKELY (P > 0.25)",
    2: "TIER II \u2014 PLAUSIBLE ALTERNATIVES (P 0.10\u20130.25)",
    3: "TIER III \u2014 TAIL RISKS (P < 0.10)",
}


def _format_tier(assessment: TierAssessment) -> str:
    """Format a single tier assessment block."""
    cc = assessment.confidence_components
    lines = [
        f"\u2501\u2501\u2501 {_TIER_HEADERS.get(assessment.tier, 'UNKNOWN TIER')} \u2501\u2501\u2501",
        assessment.scenario_variant,
        f"Probability: {assessment.probability:.2f} | Confidence: {assessment.confidence:.2f}",
        f"  \u251c\u2500 Data Quality:        {cc.get('data_quality', 0):.3f}",
        f"  \u251c\u2500 Source Reliability:   {cc.get('source_reliability', 0):.3f}",
        f"  \u251c\u2500 Methodological Rigor: {cc.get('methodological_rigor', 0):.3f}",
        f"  \u2514\u2500 Temporal Stability:   {cc.get('temporal_stability', 0):.3f}",
        "",
        "Reasoning Chain:",
    ]
    for i, step in enumerate(assessment.reasoning_chain, 1):
        lines.append(f"  {i}. {step}")

    lines.append(f"\nDissenters: {assessment.dissent_count}")
    if assessment.key_dissenters:
        lines.append(f"Key dissenters: {', '.join(assessment.key_dissenters)}")

    return "\n".join(lines)


def format_forecast(output: ForecastOutput, scenario_title: str = "") -> str:
    """Format a ForecastOutput into the canonical QGIA text report.

    Args:
        output: Forecast output from QGIAForecastEngine.run_forecast().
        scenario_title: Optional human-readable title for the header.

    Returns:
        Formatted multi-line string report.
    """
    sep = "\u2550" * 59
    title = scenario_title or output.scenario_id

    header = "\n".join([
        sep,
        f"QGIA ANALYTICAL PRODUCT \u2014 {output.classification}",
        f"Forecast ID: {output.forecast_id}",
        f"Timestamp: {output.timestamp}",
        f"Scenario: {title}",
        sep,
    ])

    # Tier sections
    tier_sections: list[str] = []
    for ta in sorted(output.tier_assessments, key=lambda t: t.tier):
        tier_sections.append(_format_tier(ta))

    # Dissent report
    all_dissenters = set()
    top_dissenter_info = ""
    for ta in output.tier_assessments:
        all_dissenters.update(ta.key_dissenters)
    cell_size = output.meta.get("cell_size", 0)

    if all_dissenters:
        top_id = output.tier_assessments[0].key_dissenters[0] if output.tier_assessments[0].key_dissenters else "N/A"
        top_dissenter_info = f"Highest-influence dissenter: {top_id}"

    dissent_section = "\n".join([
        "\u2501\u2501\u2501 DISSENT REPORT \u2501\u2501\u2501",
        f"Active dissenters: {len(all_dissenters)} of {cell_size}",
        top_dissenter_info,
    ])

    # Echo chamber warnings
    echo_section_lines = ["\u2501\u2501\u2501 ECHO CHAMBER WARNINGS \u2501\u2501\u2501"]
    if output.echo_chamber_warnings:
        for warning in output.echo_chamber_warnings:
            echo_section_lines.append(f"  \u26a0 {warning}")
    else:
        echo_section_lines.append("  No echo chamber clusters detected in this cell.")
    echo_section = "\n".join(echo_section_lines)

    # Provenance
    prov = output.provenance
    ap = output.analyst_participation
    div_line = " | ".join(f"{d}: {c}" for d, c in sorted(ap.items()))
    provenance_section = "\n".join([
        "\u2501\u2501\u2501 PROVENANCE \u2501\u2501\u2501",
        f"Sources consulted: {prov.get('sources_consulted', 'N/A')}",
        f"Evidence fragments: {prov.get('evidence_fragments', 'N/A')}",
        f"Independent source ratio: {prov.get('independent_source_ratio', 'N/A')}",
        f"Division participation: {div_line}",
    ])

    # Quick reference
    quick_ref = "\n".join([
        "\u2501\u2501\u2501 QUICK REFERENCE \u2501\u2501\u2501",
        "Check: TIMESTAMP \u2192 TIER I \u2192 TIER II \u2192 TIER III \u2192 CONFIDENCE \u2192 PROVENANCE \u2192 YOUR INTEL",
        sep,
    ])

    # Meta
    meta = output.meta
    meta_section = "\n".join([
        "\u2501\u2501\u2501 PROCESSING METADATA \u2501\u2501\u2501",
        f"Cell size: {meta.get('cell_size', 'N/A')} analysts",
        f"Propagation rounds: {meta.get('propagation_rounds', 'N/A')}",
        f"Edges in cell subgraph: {meta.get('total_edges_in_cell', 'N/A')}",
        f"Processing time: {meta.get('processing_ms', 'N/A')} ms",
        f"Seed: {meta.get('seed', 'N/A')}",
    ])

    return "\n\n".join([
        header,
        *tier_sections,
        dissent_section,
        echo_section,
        provenance_section,
        meta_section,
        quick_ref,
    ])
