import json
import re
from typing import Dict, List, Union

# ------------------------------------------------------------------
# Configurable constants (priority thresholds, weighting, fallback)
# ------------------------------------------------------------------
# Total weighted score thresholds
PRIORITY_THRESHOLDS = {"high": 3, "medium": 1}
DEFAULT_RESULT = {
    "primary_folder": "Unsorted",
    "priority": "low",
    "reason": "No content or keywords matched",
    "all_hits": {},
}

# ------------------------------------------------------------------
# Symbolic categories with weighted keywords (optional weights added)
# ------------------------------------------------------------------
PROJECT_CATEGORIES: Dict[str, Dict[str, Union[int, List[str]]]] = {
    "SymbolicOps": {
        "weight": 2,
        "keywords": [
            "threadcore",
            "symbolic",
            "anchor",
            "drift",
            "vector",
            "reflect",
            "seal",
        ],
    },
    "GitOps": {
        "weight": 1,
        "keywords": ["github", "commit", "repo", "branch", "merge", "pr"],
    },
    "SiteBuilder": {
        "weight": 1,
        "keywords": ["html", "css", "website", "page", "image", "lafinca"],
    },
    "SecurityCore": {
        "weight": 2,
        "keywords": ["encryption", "key", "decrypt", "auth", "secure", "session"],
    },
    "DataFlow": {
        "weight": 1,
        "keywords": ["vector index", "dataset", "cloudsync", "memory", "export"],
    },
    "RitualUX": {
        "weight": 2,
        "keywords": ["ritual", "arch", "scroll", "map", "invocation", "resilience"],
    },
    "AutomationEngine": {
        "weight": 1,
        "keywords": ["bot", "agent", "automation", "api", "workflow", "routine"],
    },
    "Diagnostics": {
        "weight": 1,
        "keywords": ["error", "bug", "trace", "status", "log", "issue"],
    },
}

def _word_boundary_search(text: str, keyword: str) -> bool:
    """True if keyword appears as a whole word (case-insensitive)."""
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None

def tag_thread_context(content: str) -> Dict[str, Union[str, Dict[str, int]]]:
    """Return folder, priority, and reason based on weighted keyword matches."""
    if not isinstance(content, str) or not content.strip():
        return DEFAULT_RESULT.copy()

    content_lower = content.lower()
    scores: Dict[str, int] = {}

    for category, config in PROJECT_CATEGORIES.items():
        weight = config.get("weight", 1)
        count = 0
        for kw in config["keywords"]:
            if _word_boundary_search(content_lower, kw):
                count += 1
        scores[category] = count * weight

    total_scores = {k: v for k, v in scores.items() if v > 0}

    if not total_scores:
        return DEFAULT_RESULT.copy()

    # Determine primary category
    max_score = max(total_scores.values())
    top_categories = [k for k, v in total_scores.items() if v == max_score]
    primary_folder = sorted(top_categories)[0]

    # Priority calculation
    priority = "low"
    if max_score >= PRIORITY_THRESHOLDS["high"]:
        priority = "high"
    elif max_score >= PRIORITY_THRESHOLDS["medium"]:
        priority = "medium"

    return {
        "primary_folder": primary_folder,
        "priority": priority,
        "reason": f"Matched weighted score {max_score} for '{primary_folder}'",
        "all_hits": total_scores,
    }

# Example interactive use
if __name__ == "__main__":
    sample = "ThreadCORE drift detected; anchor vector misaligned. Commit fixes to GitHub repo."
    result = tag_thread_context(sample)
    print(json.dumps(result, indent=2))
