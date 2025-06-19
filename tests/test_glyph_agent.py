from modules.reflective_autonomy.glyph_agent import GlyphAgent


def test_sentari_reinforcement():
    agent = GlyphAgent("Sentari", "resonance")
    classification = {"priority": "medium", "all_hits": {
        "RitualUX": 2}, "reason": "Matched"}
    result = agent.advise_classification(classification)
    assert result["priority"] == "high"
    assert "Sentari reinforcement" in result["reason"]


def test_other_agent_no_reinforcement():
    agent = GlyphAgent("Axiomera", "observer")
    classification = {"priority": "medium", "all_hits": {
        "RitualUX": 2}, "reason": "Matched"}
    result = agent.advise_classification(classification)
    assert result["priority"] == "medium"
