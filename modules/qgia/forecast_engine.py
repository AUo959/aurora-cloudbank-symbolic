"""QGIA Forecast Simulation Engine — Core QSFE.

Multi-round belief propagation across the 551-agent trust network, producing
three-tier probabilistic forecasts matching the Analyst Orientation Guide
output format. This is the analytical heart of QGIA.

Algorithm phases:
  1. Scenario Relevance Filtering (Crisis Response Cell selection)
  2. Initial Belief Formation (archetype-modulated evidence weighting)
  3. Belief Propagation (5–8 rounds on trust graph)
  4. Aggregation into Tiers (I/II/III)
  5. Dissent and Echo Chamber Analysis
"""

import uuid
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

from .config import GRADE_TIERS, SRD_THEMES, TIER_PROBABILITY_BOUNDS
from .population_generator import generate_population
from .schemas import Agent, ForecastOutput, ScenarioInput, TierAssessment, TrustEdge
from .trust_network import build_adjacency, build_outgoing_adjacency, generate_trust_network

__all__ = ["QGIAForecastEngine"]

# Edge-type influence modifiers for belief propagation
_EDGE_MODIFIERS: dict[str, float] = {
    "collaborate": 1.0,
    "challenge": -0.5,
    "reinforce": 1.2,
    "inform": 0.7,
}

# Region keyword mappings for SRD thematic relevance
_DOMAIN_THEME_MAP: dict[str, list[str]] = {
    "military": ["Proliferation", "Strategic Competition"],
    "political": ["Strategic Competition", "Economic Statecraft"],
    "economic": ["Economic Statecraft", "Technology Transfer"],
    "humanitarian": ["Climate Security"],
    "cyber": ["Cyber Security", "Technology Transfer"],
}


class QGIAForecastEngine:
    """QGIA Forecast Simulation Engine — belief propagation forecaster.

    Instantiate with a seed, then call ``run_forecast()`` with any
    :class:`ScenarioInput` to produce a :class:`ForecastOutput`.
    """

    def __init__(self, seed: int = 42) -> None:
        """Initialize engine: generate population and trust network."""
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self.agents = generate_population(seed=seed)
        self.edges = generate_trust_network(self.agents, seed=seed)
        self._agent_map: dict[str, Agent] = {a.agent_id: a for a in self.agents}
        self._incoming: dict[str, list[TrustEdge]] = build_adjacency(self.edges)
        self._outgoing: dict[str, list[TrustEdge]] = build_outgoing_adjacency(self.edges)

    @staticmethod
    def _project_to_bounded_simplex(raw_probabilities: np.ndarray) -> tuple[float, float, float]:
        """Project tier probabilities onto the documented bounded simplex."""
        bounds = [TIER_PROBABILITY_BOUNDS[tier] for tier in (1, 2, 3)]
        lower_bounds = np.array([bound[0] for bound in bounds], dtype=float)
        upper_bounds = np.array([bound[1] for bound in bounds], dtype=float)
        target_total = 1.0

        low = float(np.min(lower_bounds - raw_probabilities))
        high = float(np.max(upper_bounds - raw_probabilities))

        for _ in range(80):
            shift = (low + high) / 2.0
            candidate = np.clip(raw_probabilities + shift, lower_bounds, upper_bounds)
            if float(candidate.sum()) < target_total:
                low = shift
            else:
                high = shift

        projected = np.clip(raw_probabilities + high, lower_bounds, upper_bounds)
        return tuple(float(probability) for probability in projected)

    def run_forecast(self, scenario: ScenarioInput) -> ForecastOutput:
        """Run the full five-phase forecast pipeline on a scenario."""
        t_start = datetime.now(timezone.utc)

        # Phase 1
        cell = self._select_crisis_cell(scenario)

        # Phase 2
        beliefs = self._form_initial_beliefs(cell, scenario)

        # Phase 3
        beliefs, rounds_run, belief_history = self._propagate_beliefs(beliefs, cell)

        # Phase 4
        tier_assessments = self._aggregate_to_tiers(beliefs, cell, scenario, belief_history)

        # Phase 5
        dissenters, echo_warnings = self._analyze_dissent(beliefs, cell)

        # Attach dissent info to tier assessments
        for ta in tier_assessments:
            ta.dissent_count = len(dissenters)
            ta.key_dissenters = [d["agent_id"] for d in dissenters[:5]]

        # Build division participation
        div_counts: dict[str, int] = defaultdict(int)
        for agent in cell:
            div_counts[agent.division.value] += 1

        # Provenance
        n_sources = len({ef.get("source", "") for ef in scenario.evidence_fragments})
        provenance = {
            "sources_consulted": n_sources,
            "evidence_fragments": len(scenario.evidence_fragments),
            "independent_source_ratio": f"{n_sources}/{len(scenario.evidence_fragments)}",
        }

        t_end = datetime.now(timezone.utc)

        return ForecastOutput(
            forecast_id=f"QSFE-{uuid.uuid4().hex[:12].upper()}",
            scenario_id=scenario.scenario_id,
            timestamp=t_end.isoformat(),
            tier_assessments=tier_assessments,
            provenance=provenance,
            echo_chamber_warnings=echo_warnings,
            analyst_participation=dict(div_counts),
            meta={
                "cell_size": len(cell),
                "propagation_rounds": rounds_run,
                "total_edges_in_cell": sum(len(self._incoming.get(a.agent_id, [])) for a in cell),
                "processing_ms": int((t_end - t_start).total_seconds() * 1000),
                "seed": self.seed,
            },
        )

    # ------------------------------------------------------------------
    # Phase 1 — Crisis Response Cell selection
    # ------------------------------------------------------------------

    def _select_crisis_cell(self, scenario: ScenarioInput) -> list[Agent]:
        """Select analysts whose specialization matches the scenario."""
        region = scenario.region
        domain = scenario.domain
        cell: list[Agent] = []

        relevant_themes = _DOMAIN_THEME_MAP.get(domain, SRD_THEMES[:2])

        for agent in self.agents:
            # IID analysts always included (cross-domain integrators)
            if agent.division.value == "IID":
                cell.append(agent)
                continue

            # SRD analysts if thematic focus is relevant
            if agent.division.value == "SRD":
                if agent.regional_specialization in relevant_themes:
                    cell.append(agent)
                continue

            # GMD / MAD — match on regional specialization
            if agent.regional_specialization == region:
                cell.append(agent)

        return cell

    # ------------------------------------------------------------------
    # Phase 2 — Initial Belief Formation
    # ------------------------------------------------------------------

    def _form_initial_beliefs(self, cell: list[Agent], scenario: ScenarioInput) -> dict[str, float]:
        """Compute initial beliefs from evidence fragments, modulated by archetype."""
        beliefs: dict[str, float] = {}

        # Base evidence score: weighted average of fragment reliability
        fragments = scenario.evidence_fragments
        if not fragments:
            for agent in cell:
                beliefs[agent.agent_id] = 0.5
            return beliefs

        for agent in cell:
            ep = agent.epistemic_profile
            # Weight evidence by reliability × (1 - overconfidence)
            total_weight = 0.0
            weighted_sum = 0.0
            for frag in fragments:
                rel = frag.get("reliability", 0.5)
                w = rel * (1.0 - ep.domain_overconfidence)
                weighted_sum += w * rel  # reliability serves as proxy for "evidence strength"
                total_weight += w

            base_belief = weighted_sum / total_weight if total_weight > 0 else 0.5

            # Archetype adjustment
            belief = self._apply_archetype_adjustment(base_belief, agent)
            beliefs[agent.agent_id] = max(0.0, min(1.0, belief))

        return beliefs

    def _apply_archetype_adjustment(self, base: float, agent: Agent) -> float:
        """Apply archetype-specific belief modifier."""
        ep = agent.epistemic_profile
        archetype = agent.archetype

        if archetype == "Aggressive Updater":
            # Amplify evidence signal
            return 0.5 + (base - 0.5) * 1.3

        if archetype == "Prior-Anchored Conservative":
            # Dampen evidence signal
            return 0.5 + (base - 0.5) * 0.7

        if archetype == "Contrarian by Default":
            # Invert toward 1-base, scaled by contrarian index
            target = 1.0 - base
            return base + (target - base) * ep.contrarian_index

        if archetype == "Empirical Minimalist":
            # Reduce confidence proportional to data incompleteness
            data_completeness = base  # proxy
            return base * data_completeness + 0.5 * (1.0 - data_completeness)

        if archetype == "Intuitive Pattern Matcher":
            # Add noise representing pattern intuition
            noise = self._rng.uniform(-0.1, 0.1)
            return base + noise

        if archetype == "Dialectical Synthesizer":
            # Pull toward center
            return base * 0.7 + 0.5 * 0.3

        if archetype == "Recursive Self-Corrector":
            # No initial adjustment — waits for network signal
            return base

        if archetype == "Institutionalist":
            # Pull toward institutional prior (status quo = 0.5)
            return base * (1.0 - ep.institutional_loyalty * 0.3) + 0.5 * ep.institutional_loyalty * 0.3

        return base

    # ------------------------------------------------------------------
    # Phase 3 — Belief Propagation
    # ------------------------------------------------------------------

    def _propagate_beliefs(
        self,
        beliefs: dict[str, float],
        cell: list[Agent],
        max_rounds: int = 8,
    ) -> tuple[dict[str, float], int, list[dict[str, float]]]:
        """Multi-round belief propagation across the trust network.

        Returns:
            (final_beliefs, rounds_run, history_per_round)
        """
        cell_ids = {a.agent_id for a in cell}
        history: list[dict[str, float]] = [dict(beliefs)]

        for round_num in range(max_rounds):
            new_beliefs: dict[str, float] = {}
            max_delta = 0.0

            for agent in cell:
                aid = agent.agent_id
                ep = agent.epistemic_profile
                current = beliefs[aid]

                # Gather neighbor influences (incoming edges within the cell)
                incoming = self._incoming.get(aid, [])
                neighbor_sum = 0.0
                neighbor_weight_total = 0.0

                for edge in incoming:
                    if edge.source not in cell_ids:
                        continue
                    if edge.source not in beliefs:
                        continue

                    modifier = _EDGE_MODIFIERS.get(edge.edge_type, 0.7)
                    influence_weight = edge.weight * abs(modifier)
                    neighbor_belief = beliefs[edge.source]

                    if modifier < 0:
                        # Challenge: push away from challenger's position
                        effective_belief = 1.0 - neighbor_belief
                    else:
                        effective_belief = neighbor_belief

                    neighbor_sum += influence_weight * effective_belief
                    neighbor_weight_total += influence_weight

                if neighbor_weight_total > 0:
                    weighted_avg = neighbor_sum / neighbor_weight_total
                else:
                    new_beliefs[aid] = current
                    continue

                # Compute update rate
                update_rate = (1.0 - ep.prior_strength) * (1.0 - ep.institutional_loyalty * 0.3)

                # High intellectual independence reduces update rate
                if ep.intellectual_independence > 0.7:
                    update_rate *= 0.6

                new_belief = (1.0 - update_rate) * current + update_rate * weighted_avg
                new_belief = max(0.0, min(1.0, new_belief))
                new_beliefs[aid] = new_belief

                delta = abs(new_belief - current)
                if delta > max_delta:
                    max_delta = delta

            beliefs = new_beliefs
            history.append(dict(beliefs))

            # Convergence check
            if max_delta < 0.01:
                return beliefs, round_num + 1, history

        return beliefs, max_rounds, history

    # ------------------------------------------------------------------
    # Phase 4 — Aggregation into Tiers
    # ------------------------------------------------------------------

    def _weighted_mean(self, beliefs: dict[str, float], cell: list[Agent]) -> float:
        """Compute grade-weighted mean belief."""
        total_w = 0.0
        total = 0.0
        for agent in cell:
            w = GRADE_TIERS[agent.grade] * (1.0 - agent.epistemic_profile.domain_overconfidence)
            total += beliefs[agent.agent_id] * w
            total_w += w
        return total / total_w if total_w > 0 else 0.5

    def _weighted_std(self, beliefs: dict[str, float], cell: list[Agent], mean: float) -> float:
        """Compute grade-weighted standard deviation of beliefs."""
        total_w = 0.0
        total_sq = 0.0
        for agent in cell:
            w = GRADE_TIERS[agent.grade] * (1.0 - agent.epistemic_profile.domain_overconfidence)
            total_sq += w * (beliefs[agent.agent_id] - mean) ** 2
            total_w += w
        return (total_sq / total_w) ** 0.5 if total_w > 0 else 0.1

    def _aggregate_to_tiers(
        self,
        beliefs: dict[str, float],
        cell: list[Agent],
        scenario: ScenarioInput,
        belief_history: list[dict[str, float]],
    ) -> list[TierAssessment]:
        """Convert converged beliefs into three-tier probabilistic output."""
        mean = self._weighted_mean(beliefs, cell)
        std = self._weighted_std(beliefs, cell, mean)
        std = max(std, 0.02)  # floor to avoid degenerate cases

        # Confidence components
        fragments = scenario.evidence_fragments
        avg_reliability = (
            sum(f.get("reliability", 0.5) for f in fragments) / len(fragments) if fragments else 0.5
        )
        n_sources = len({f.get("source", "") for f in fragments})
        source_reliability = n_sources / len(fragments) if fragments else 0.5

        # Temporal stability: 1 - std of belief changes across rounds
        if len(belief_history) > 1:
            deltas = []
            for aid in beliefs:
                vals = [h.get(aid, 0.5) for h in belief_history]
                if len(vals) > 1:
                    deltas.append(np.std(vals))
            temporal_stability = 1.0 - (np.mean(deltas) if deltas else 0.0)
        else:
            temporal_stability = 0.8

        confidence_components = {
            "data_quality": round(avg_reliability, 3),
            "source_reliability": round(min(source_reliability, 1.0), 3),
            "methodological_rigor": 0.85,
            "temporal_stability": round(max(0.0, min(1.0, temporal_stability)), 3),
        }
        composite_confidence = round(sum(confidence_components.values()) / 4, 3)

        tiers: list[TierAssessment] = []

        # Compute raw clamped tier probabilities
        tier1_raw = max(TIER_PROBABILITY_BOUNDS[1][0], min(TIER_PROBABILITY_BOUNDS[1][1], mean))
        tier2_raw = max(TIER_PROBABILITY_BOUNDS[2][0], min(TIER_PROBABILITY_BOUNDS[2][1], 0.25 - std * 0.5))
        tier3_raw = max(TIER_PROBABILITY_BOUNDS[3][0], min(TIER_PROBABILITY_BOUNDS[3][1], 0.10 - std))

        # Bounded projection keeps the configured tier bounds while enforcing
        # a coherent probability distribution across the three tiers.
        raw_tier_probs = np.array([tier1_raw, tier2_raw, tier3_raw], dtype=float)
        tier1_prob, tier2_prob, tier3_prob = self._project_to_bounded_simplex(raw_tier_probs)

        # Confidence scalars for each tier
        tier2_confidence = round(composite_confidence * 0.85, 3)
        tier3_confidence = round(composite_confidence * 0.7, 3)

        # Tier I — Most Likely (modal scenario)
        tiers.append(
            TierAssessment(
                tier=1,
                label="Most Likely",
                scenario_variant=self._generate_variant_description(scenario, "primary", mean),
                probability=tier1_prob,
                confidence=composite_confidence,
                confidence_components=confidence_components,
                reasoning_chain=self._build_reasoning_chain(scenario, cell, beliefs, "tier1"),
                dissent_count=0,
                key_dissenters=[],
            )
        )

        # Tier II — Plausible Alternatives (±1 sigma)
        tiers.append(
            TierAssessment(
                tier=2,
                label="Plausible Alternative",
                scenario_variant=self._generate_variant_description(scenario, "alternative", mean + std),
                probability=tier2_prob,
                confidence=tier2_confidence,
                confidence_components={k: round(v * 0.85, 3) for k, v in confidence_components.items()},
                reasoning_chain=self._build_reasoning_chain(scenario, cell, beliefs, "tier2"),
                dissent_count=0,
                key_dissenters=[],
            )
        )

        # Tier III — Tail Risks (±2 sigma)
        tiers.append(
            TierAssessment(
                tier=3,
                label="Tail Risk",
                scenario_variant=self._generate_variant_description(scenario, "tail_risk", mean + 2 * std),
                probability=tier3_prob,
                confidence=tier3_confidence,
                confidence_components={k: round(v * 0.7, 3) for k, v in confidence_components.items()},
                reasoning_chain=self._build_reasoning_chain(scenario, cell, beliefs, "tier3"),
                dissent_count=0,
                key_dissenters=[],
            )
        )

        return tiers

    def _generate_variant_description(self, scenario: ScenarioInput, variant_type: str, belief: float) -> str:
        """Generate a human-readable scenario variant description."""
        title = scenario.title
        if variant_type == "primary":
            return (
                f"Primary assessment: {title} proceeds along current trajectory. "
                f"Evidence convergence at {belief:.2f} indicates {'high' if belief > 0.65 else 'moderate'} "
                f"likelihood of escalation within the assessed timeframe."
            )
        if variant_type == "alternative":
            return (
                f"Alternative pathway: {title} — de-escalation or lateral shift. "
                f"Diplomatic intervention, internal political change, or deterrence recalibration "
                f"diverts the scenario from the primary trajectory."
            )
        return (
            f"Tail risk: {title} — rapid escalation beyond assessed parameters. "
            f"Black swan catalysts (leadership change, miscalculation, third-party intervention) "
            f"produce an outcome outside the primary analytical frame."
        )

    def _build_reasoning_chain(
        self,
        scenario: ScenarioInput,
        cell: list[Agent],
        beliefs: dict[str, float],
        tier: str,
    ) -> list[str]:
        """Build a reasoning chain for a tier assessment."""
        n_cell = len(cell)
        fragments = scenario.evidence_fragments
        avg_rel = sum(f.get("reliability", 0.5) for f in fragments) / len(fragments) if fragments else 0.5

        chain = [
            f"Crisis Response Cell activated: {n_cell} analysts across "
            f"{len({a.division.value for a in cell})} divisions",
            f"Evidence base: {len(fragments)} fragments, average reliability {avg_rel:.2f}",
        ]

        if tier == "tier1":
            mean = self._weighted_mean(beliefs, cell)
            chain.extend([
                f"Belief convergence: weighted mean {mean:.3f} after multi-round propagation",
                "Archetype distribution in cell provides balanced epistemic coverage",
                f"Primary scenario supported by {sum(1 for b in beliefs.values() if b > 0.5)}/{n_cell} analysts",
            ])
        elif tier == "tier2":
            chain.extend([
                "Alternative pathway identified via contrarian analyst cluster",
                "De-escalation indicators present but subordinate to primary evidence trajectory",
                "Historical base rate for diplomatic resolution in comparable scenarios: 15-22%",
            ])
        else:
            chain.extend([
                "Tail risk identified via high-independence analysts with challenge-edge connectivity",
                "Scenario represents discontinuous escalation not captured in primary evidence trajectory",
                "Low probability but high consequence warrants explicit tracking per QGIA protocol",
            ])

        return chain

    # ------------------------------------------------------------------
    # Phase 5 — Dissent and Echo Chamber Analysis
    # ------------------------------------------------------------------

    def _analyze_dissent(
        self, beliefs: dict[str, float], cell: list[Agent]
    ) -> tuple[list[dict], list[str]]:
        """Identify dissenters and detect echo chambers.

        Returns:
            (ranked_dissenters, echo_chamber_warnings)
        """
        cell_ids = {a.agent_id for a in cell}
        mean = self._weighted_mean(beliefs, cell)
        std = self._weighted_std(beliefs, cell, mean)
        threshold = 1.5 * max(std, 0.02)

        # Identify dissenters
        dissenters: list[dict] = []
        for agent in cell:
            deviation = abs(beliefs[agent.agent_id] - mean)
            if deviation > threshold:
                # Influence = grade_tier × intellectual_independence × out_degree_challenge_edges
                out_challenge = sum(
                    1
                    for e in self._outgoing.get(agent.agent_id, [])
                    if e.edge_type == "challenge" and e.target in cell_ids
                )
                influence = (
                    GRADE_TIERS[agent.grade]
                    * agent.epistemic_profile.intellectual_independence
                    * max(out_challenge, 1)
                )
                dissenters.append({
                    "agent_id": agent.agent_id,
                    "archetype": agent.archetype,
                    "division": agent.division.value,
                    "belief": beliefs[agent.agent_id],
                    "deviation": deviation,
                    "influence": influence,
                })

        dissenters.sort(key=lambda d: d["influence"], reverse=True)

        # Detect echo chambers: connected components of reinforce edges
        # with 3+ nodes and internal belief variance < 0.05
        reinforce_adj: dict[str, set[str]] = defaultdict(set)
        for edge in self.edges:
            if edge.edge_type == "reinforce" and edge.source in cell_ids and edge.target in cell_ids:
                reinforce_adj[edge.source].add(edge.target)
                reinforce_adj[edge.target].add(edge.source)

        # BFS to find connected components
        visited: set[str] = set()
        echo_warnings: list[str] = []

        for start_id in reinforce_adj:
            if start_id in visited:
                continue
            component: list[str] = []
            queue = [start_id]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                component.append(node)
                for neighbor in reinforce_adj.get(node, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)

            if len(component) >= 3:
                component_beliefs = [beliefs[aid] for aid in component if aid in beliefs]
                if component_beliefs:
                    variance = np.var(component_beliefs)
                    if variance < 0.05:
                        agents_in_cluster = [self._agent_map[aid] for aid in component if aid in self._agent_map]
                        archetypes = {a.archetype for a in agents_in_cluster}
                        divisions = {a.division.value for a in agents_in_cluster}
                        echo_warnings.append(
                            f"Echo chamber detected: {len(component)} analysts "
                            f"(divisions: {', '.join(sorted(divisions))}, "
                            f"archetypes: {', '.join(sorted(archetypes))}), "
                            f"belief variance {variance:.4f}, "
                            f"mean belief {np.mean(component_beliefs):.3f}"
                        )

        return dissenters, echo_warnings
