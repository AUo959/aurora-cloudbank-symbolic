"""CASK data generation utilities."""

from typing import List

_COMPONENTS: List[str] = [
    "Global Cross-Linguistic Database",
    "Ethics & Value Systems Index",
    "Cultural Cognition Framework",
    "Historical Institutional Systems",
    "Language-to-Symbolic Fusion Layer",
    "Symbolic Vector Chain Compressor (SVCC)",
    "GPT Native Encoding Layer",
    "Agent Simulation Generation Module",
    "Recursive Ethics Validator",
    "ORION Simulation Runtime",
]

_TECHNICAL_SPECIFICATIONS: List[str] = [
    "Multi-language family coverage: phonology, morphology, syntax, semantics, pragmatics",
    "Comparative religion, philosophy, governance, cultural norms with conflict arbitration",
    "Collective vs individualistic reasoning, context communication models, negotiation patterns",
    "Academic, scientific, military, religious, trade, diplomatic systems (present to near-future)",
    "Natural language ↔ programming code ↔ symbolic notation translation with GPT optimization",
    "Delta-diff lightweight schema for compressed vector storage",
    "Sub-100ms GPT lookup response time with native semantic embedding",
    "L1 staff builder for agent generation with cultural parameter integration",
    "Picard_Delta_3 compliant ethics validation with full logic chain traceability",
    "Multi-layer simulation runtime supporting L1-L2-L3 recursive AI environments",
]

_KEY_INNOVATIONS: List[str] = [
    "Universal real-time translation devices (PUTI) with cultural context preservation",
    "Non-flattening ethical cognitive architectures maintaining value plurality",
    "Adaptive agent training pipelines for cross-cultural behavior plausibility",
    "Speculative institutional modeling for near-future governance scenarios",
    "Direct ethics chain traceability on GPT outputs with symbolic validation",
    "Scalable vector compression for massive cultural dataset storage",
    "GPT-native optimization for sub-100ms agent generation response times",
    "Cultural parameter-aware agent instantiation with realistic diversity modeling",
    "Recursive ethics validation ensuring coherent multi-layer simulation ethics",
    "High-fidelity recursive AI research environment with emergent behavior modeling",
]

_INTEGRATION_CHALLENGES: List[str] = [
    "Maintaining linguistic nuance across 7000+ world languages",
    "Resolving ethical conflicts without cultural hegemony",
    "Balancing individual and collective decision-making models",
    "Predicting institutional evolution in uncertain futures",
    "Ensuring symbolic-semantic consistency across translation layers",
    "Managing storage and retrieval performance at global scale",
    "Maintaining cultural sensitivity while optimizing for speed",
    "Preventing cultural bias in agent generation algorithms",
    "Avoiding recursive validation loops while ensuring ethical compliance",
    "Managing computational complexity of multi-layer recursive simulations",
]

_TECHNICAL_DOMAINS: List[str] = [
    "Cultural AI Systems",
    "Multi-Agent Simulations",
    "Cross-Cultural Translation",
    "Ethical AI Frameworks",
    "Symbolic Reasoning",
    "Large-Scale Knowledge Graphs",
    "Real-Time Language Processing",
    "Agent-Based Modeling",
    "Simulation Governance",
    "AI Safety Auditing",
]

_CURRENT_SOTA: List[str] = [
    "Cultural Awareness Score (CAS) metrics, SituAnnotate ontology, GPT-4V cultural recognition",
    "SMART (GPT-style), Multi-Agent Systems with SPADE3, Unity3D simulation architectures",
    "Context-aware multi-agent translation (CrewAI), GPT-4o cultural embeddings",
    "Responsible AI frameworks, Four pillars approach (ethics/control/viability/desirability)",
    "Neuro-symbolic AI, TractOR probabilistic databases, Vector Symbolic Architectures",
    "Distributed knowledge graphs, TGraph systems, pgvector integration",
    "Neural machine translation, sub-300ms speech-to-text, Wordly real-time platforms",
    "Mesa/NetLogo frameworks, GAMA platform, AnyLogic enterprise solutions",
    "Standards-based governance, validation protocols, documentation frameworks",
    "Independent audit models, risk assessment frameworks, forensic analysis trails",
]

_CASK_INNOVATIONS: List[str] = [
    "Non-flattening cultural cognition preserving value plurality across 7000+ languages",
    "Recursive L1-L2-L3 AI environments with cultural parameter integration",
    "PUTI devices with symbolic-semantic consistency and cultural context preservation",
    "Picard_Delta_3 compliant recursive ethics with full traceability chains",
    "Language-to-symbolic fusion with direct GPT optimization and ethics validation",
    "SVCC compression enabling global-scale cultural dataset storage and retrieval",
    "Sub-100ms culturally-aware agent generation with GPT-native semantic embedding",
    "Cultural diversity modeling with institutional evolution prediction capabilities",
    "Multi-layer simulation governance with speculative near-future scenario modeling",
    "Recursive ethics validation preventing cultural bias while ensuring safety compliance",
]

_TECHNICAL_ADVANTAGES: List[str] = [
    "Maintains cultural authenticity without Western hegemony",
    "Enables realistic cultural diversity in high-stakes simulations",
    "Preserves cultural nuance while enabling universal communication",
    "Prevents ethical flattening through recursive validation",
    "Bridges statistical and symbolic AI with cultural awareness",
    "Scales to global cultural knowledge without performance degradation",
    "Combines speed with cultural sensitivity in real-time processing",
    "Models realistic cross-cultural collaboration scenarios",
    "Addresses governance challenges in recursive AI systems",
    "Ensures safety while preserving cultural diversity and ethical plurality",
]

_IMPLEMENTATION_COMPLEXITY: List[str] = [
    "High - requires deep cultural expertise and linguistic resources",
    "Very High - novel recursive architecture with cultural parameters",
    "High - symbolic consistency across cultural and linguistic boundaries",
    "Very High - recursive validation without infinite loops",
    "High - bridging multiple AI paradigms with cultural constraints",
    "Very High - global-scale storage with sub-100ms retrieval requirements",
    "Medium - optimization for cultural awareness adds complexity",
    "High - cultural parameter integration with existing frameworks",
    "High - governance across multiple simulation layers",
    "Very High - auditing recursive systems while preserving cultural authenticity",
]

_RISK_CATEGORIES: List[str] = [
    "Cultural Bias Introduction",
    "Computational Complexity",
    "Linguistic Accuracy",
    "Ethical Validation Loops",
    "Scalability Bottlenecks",
    "Real-time Performance",
    "System Integration",
    "Data Quality",
    "Cultural Representation",
    "Validation Accuracy",
]

_RISK_PROBABILITIES: List[str] = [
    "Medium", "High", "Medium", "High", "High",
    "Medium", "High", "Medium", "High", "Medium",
]

_RISK_IMPACTS: List[str] = [
    "Very High", "High", "High", "Very High", "High",
    "Medium", "High", "High", "Very High", "High",
]

_MITIGATION_STRATEGIES: List[str] = [
    "Multi-cultural expert validation, bias detection algorithms",
    "Distributed computing, optimized vector compression",
    "Native speaker validation, continuous linguistic updates",
    "Circuit breaker patterns, validation depth limits",
    "Horizontal scaling, caching strategies, load balancing",
    "GPT-native optimization, parallel processing pipelines",
    "Modular architecture, API standardization, incremental deployment",
    "Crowdsourced validation, academic partnerships, quality metrics",
    "Global cultural advisory board, representative sampling",
    "Multi-layer validation, expert review protocols",
]

_RISK_PRIORITIES: List[str] = [
    "Critical", "High", "High", "Critical", "High",
    "Medium", "High", "Medium", "Critical", "High",
]


def _write_csv(records: List[dict], output_csv: str) -> None:
    """Write *records* to *output_csv* using pandas (optional dependency)."""
    try:
        import pandas as pd
        pd.DataFrame(records).to_csv(output_csv, index=False)
    except ImportError as exc:
        raise ImportError(
            "pandas is required for CASK analysis features. "
            "Install with: pip install pandas>=2.1.0"
        ) from exc


def generate_technical_specifications(output_csv: str | None = None) -> List[dict]:
    """Return CASK technical specifications as a list of record dicts."""
    records: List[dict] = [
        {
            "Component": component,
            "Technical_Specification": spec,
            "Key_Innovation": innovation,
            "Integration_Challenge": challenge,
        }
        for component, spec, innovation, challenge in zip(
            _COMPONENTS, _TECHNICAL_SPECIFICATIONS, _KEY_INNOVATIONS, _INTEGRATION_CHALLENGES
        )
    ]
    if output_csv is not None:
        _write_csv(records, output_csv)
    return records


def generate_vs_sota_comparison(output_csv: str | None = None) -> List[dict]:
    """Return comparison of CASK against state of the art as a list of record dicts."""
    records: List[dict] = [
        {
            "Technical_Domain": domain,
            "Current_State_of_Art": sota,
            "CASK_Innovation": innovation,
            "Technical_Advantage": advantage,
            "Implementation_Complexity": complexity,
        }
        for domain, sota, innovation, advantage, complexity in zip(
            _TECHNICAL_DOMAINS,
            _CURRENT_SOTA,
            _CASK_INNOVATIONS,
            _TECHNICAL_ADVANTAGES,
            _IMPLEMENTATION_COMPLEXITY,
        )
    ]
    if output_csv is not None:
        _write_csv(records, output_csv)
    return records


def generate_risk_assessment(output_csv: str | None = None) -> List[dict]:
    """Return CASK project risk assessment as a list of record dicts."""
    records: List[dict] = [
        {
            "Risk_Category": category,
            "Probability": probability,
            "Impact": impact,
            "Mitigation_Strategy": mitigation,
            "Priority": priority,
        }
        for category, probability, impact, mitigation, priority in zip(
            _RISK_CATEGORIES,
            _RISK_PROBABILITIES,
            _RISK_IMPACTS,
            _MITIGATION_STRATEGIES,
            _RISK_PRIORITIES,
        )
    ]
    if output_csv is not None:
        _write_csv(records, output_csv)
    return records
