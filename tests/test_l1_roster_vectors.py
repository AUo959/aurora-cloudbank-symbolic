import json
from pathlib import Path


def test_l1_roster_vsa_vectors_structure():
    path = Path("data/hr/l1_roster_vsa.json")
    assert path.exists(), "VSA roster vector file missing"
    data = json.loads(path.read_text())
    vectors = data.get("vectors", {})
    # Expect 24 entries (remaining characters) + enrichments for existing roles
    assert len(vectors) >= 24, f"Expected >=24 vectors, found {len(vectors)}"
    for k, v in vectors.items():
        assert isinstance(v, list) and len(v) == 5, f"Vector for {k} must be length 5"
        assert all(isinstance(x, (int, float)) for x in v), f"Non-numeric value in vector for {k}"
        # Normalization check (approx) - norm should not be zero
        norm = sum(x * x for x in v) ** 0.5
        assert norm > 0.5, f"Vector norm too small for {k}"  # heuristic
