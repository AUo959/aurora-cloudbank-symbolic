"""QGIA Forecast Simulation Engine — Scenario Data Model and Templates.

Provides a helper for creating scenarios and four canonical example
templates with varying evidence fragment compositions.
"""

from .schemas import ScenarioInput

__all__ = [
    "create_scenario",
    "iran_nuclear_escalation",
    "south_china_sea_confrontation",
    "european_energy_crisis",
    "subsaharan_instability",
    "EXAMPLE_SCENARIOS",
]


def create_scenario(
    scenario_id: str,
    title: str,
    description: str,
    region: str,
    domain: str,
    evidence_fragments: list[dict],
    requesting_node: str = "L1_QGIA",
) -> ScenarioInput:
    """Create a validated ScenarioInput."""
    return ScenarioInput(
        scenario_id=scenario_id,
        title=title,
        description=description,
        region=region,
        domain=domain,
        evidence_fragments=evidence_fragments,
        requesting_node=requesting_node,
    )


def iran_nuclear_escalation() -> ScenarioInput:
    """Iran nuclear escalation scenario template."""
    return create_scenario(
        scenario_id="QGIA-SCN-2026-0041",
        title="Iran Nuclear Threshold Escalation",
        description=(
            "Intelligence indicators suggest Iran has accelerated uranium enrichment "
            "to 90%+ purity at the Fordow facility, with IAEA inspectors reporting "
            "access denials at two previously monitored sites. Satellite imagery shows "
            "new construction at Parchin consistent with weaponization research. Regional "
            "diplomatic channels have gone quiet. Israel has moved Iron Dome battery "
            "deployments to forward positions."
        ),
        region="Middle East",
        domain="military",
        evidence_fragments=[
            {
                "source": "IAEA Safeguards Report (Q1 2026)",
                "content": "Enrichment levels at Fordow detected at 89.7% U-235, up from 60% in Dec 2025",
                "reliability": 0.92,
                "recency": "2026-03-01",
            },
            {
                "source": "Commercial satellite imagery (Planet Labs)",
                "content": "New underground construction at Parchin, 3 new ventilation shafts identified",
                "reliability": 0.78,
                "recency": "2026-03-08",
            },
            {
                "source": "OSINT — Farsi-language social media analysis",
                "content": "IRGC-affiliated accounts increasing rhetoric about 'strategic deterrence capability'",
                "reliability": 0.61,
                "recency": "2026-03-10",
            },
            {
                "source": "Diplomatic cable (allied service)",
                "content": "Swiss back-channel reports Tehran rebuffed latest P5+1 outreach",
                "reliability": 0.85,
                "recency": "2026-03-05",
            },
            {
                "source": "IDF force posture tracking (open source)",
                "content": "Iron Dome redeployments to northern border consistent with preemptive strike prep",
                "reliability": 0.72,
                "recency": "2026-03-09",
            },
        ],
    )


def south_china_sea_confrontation() -> ScenarioInput:
    """South China Sea military confrontation scenario template."""
    return create_scenario(
        scenario_id="QGIA-SCN-2026-0042",
        title="South China Sea — Scarborough Shoal Confrontation",
        description=(
            "PLA Navy has established a persistent surface action group within 12nm of "
            "Scarborough Shoal, with coast guard vessels interdicting Philippine resupply "
            "missions. The Philippines has invoked the US Mutual Defense Treaty, and "
            "USS Ronald Reagan CSG has repositioned to the Philippine Sea. ASEAN emergency "
            "session convened but no joint statement issued."
        ),
        region="Indo-Pacific",
        domain="military",
        evidence_fragments=[
            {
                "source": "US INDOPACOM public statement",
                "content": "Reagan CSG conducting 'freedom of navigation' operations in Philippine Sea",
                "reliability": 0.95,
                "recency": "2026-03-11",
            },
            {
                "source": "AIS maritime tracking (open source)",
                "content": "14 PLA Navy vessels maintaining station within 20nm of Scarborough Shoal",
                "reliability": 0.82,
                "recency": "2026-03-10",
            },
            {
                "source": "Philippine DFA press release",
                "content": "Manila formally invokes Article IV of the Mutual Defense Treaty",
                "reliability": 0.98,
                "recency": "2026-03-09",
            },
            {
                "source": "Xinhua state media analysis",
                "content": "PRC framing operations as 'routine sovereignty enforcement'",
                "reliability": 0.55,
                "recency": "2026-03-10",
            },
            {
                "source": "Commercial satellite (Maxar)",
                "content": "New military construction on Mischief Reef — possible ASM battery emplacement",
                "reliability": 0.76,
                "recency": "2026-03-07",
            },
            {
                "source": "ASEAN diplomatic source",
                "content": "Vietnam and Malaysia privately supporting PH position but unwilling to sign joint statement",
                "reliability": 0.68,
                "recency": "2026-03-11",
            },
        ],
    )


def european_energy_crisis() -> ScenarioInput:
    """European energy security crisis scenario template."""
    return create_scenario(
        scenario_id="QGIA-SCN-2026-0043",
        title="European Energy Grid Destabilization",
        description=(
            "Coordinated cyberattacks on Baltic LNG terminal SCADA systems coincide with "
            "a sudden reduction in Norwegian pipeline flows to the EU. Natural gas spot "
            "prices have spiked 340% in 72 hours. Germany has activated its emergency "
            "energy reserve protocol. Attribution indicators point to a state actor with "
            "both cyber capability and motive to disrupt European energy security."
        ),
        region="Europe",
        domain="economic",
        evidence_fragments=[
            {
                "source": "CERT-EU incident report",
                "content": "Coordinated intrusion detected across 3 Baltic LNG terminal SCADA systems",
                "reliability": 0.88,
                "recency": "2026-03-12",
            },
            {
                "source": "TTF gas futures (market data)",
                "content": "Spot price €187/MWh, up from €42/MWh 72 hours prior",
                "reliability": 0.99,
                "recency": "2026-03-12",
            },
            {
                "source": "Equinor operational disclosure",
                "content": "Norwegian pipeline throughput reduced 35% citing 'technical maintenance'",
                "reliability": 0.80,
                "recency": "2026-03-11",
            },
            {
                "source": "Threat intelligence (Mandiant)",
                "content": "TTPs consistent with Sandworm (GRU Unit 74455); C2 infrastructure overlaps with 2023 campaigns",
                "reliability": 0.74,
                "recency": "2026-03-12",
            },
            {
                "source": "German Federal Ministry of Economics",
                "content": "Emergency reserve protocol activated; strategic reserve draw authorized",
                "reliability": 0.96,
                "recency": "2026-03-12",
            },
        ],
    )


def subsaharan_instability() -> ScenarioInput:
    """Sub-Saharan Africa political instability scenario template."""
    return create_scenario(
        scenario_id="QGIA-SCN-2026-0044",
        title="Sahel Belt Cascading Instability",
        description=(
            "Military coup in Niger's neighbor state has triggered refugee flows exceeding "
            "UNHCR capacity. Wagner-successor Africa Corps units observed repositioning "
            "toward the capital. ECOWAS standby force on alert but divided on intervention. "
            "Chinese mining concessions in the region are being renegotiated under duress. "
            "Food insecurity index has crossed the Famine Early Warning threshold."
        ),
        region="Africa",
        domain="political",
        evidence_fragments=[
            {
                "source": "UNHCR Situation Report",
                "content": "450,000 displaced in 96 hours; camp capacity at 280% in Diffa region",
                "reliability": 0.91,
                "recency": "2026-03-10",
            },
            {
                "source": "Commercial satellite (Planet Labs)",
                "content": "Military vehicle convoy (est. 40 vehicles) moving south from Libya border",
                "reliability": 0.73,
                "recency": "2026-03-11",
            },
            {
                "source": "FEWS NET alert",
                "content": "IPC Phase 4 (Emergency) declared across three provinces; Phase 5 projected",
                "reliability": 0.87,
                "recency": "2026-03-09",
            },
            {
                "source": "ECOWAS communiqué",
                "content": "Standby force placed on 48-hour alert; Nigeria and Senegal opposed to intervention",
                "reliability": 0.90,
                "recency": "2026-03-11",
            },
            {
                "source": "Financial Times reporting",
                "content": "CNNC lithium concession contract 'under review' by transitional military council",
                "reliability": 0.70,
                "recency": "2026-03-10",
            },
        ],
    )


EXAMPLE_SCENARIOS: dict[str, callable] = {
    "iran_nuclear": iran_nuclear_escalation,
    "south_china_sea": south_china_sea_confrontation,
    "european_energy": european_energy_crisis,
    "subsaharan_instability": subsaharan_instability,
}
