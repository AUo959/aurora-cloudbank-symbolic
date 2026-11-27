#!/usr/bin/env python3
"""Read-only audit: run the Velari phonology analyzer over CanonRec L2 names.

Usage (from the repo root, with the repo root on PYTHONPATH):

    python scripts/gumas_phonology_canon_audit.py --canon-root <CanonRec checkout> --out audit.json

Population: every CANON entity record with a name under canon/L2/entities.
A record is Velari-linked when

* a linking field names ``velar_imperium``, a Velar-bound organization or the
  Velari species (``binding``),
* or the Velari species record, or the engine's cited corpus, names it
  (``named-velari``),
* or it sits in the Velar Crescent zone (``velar-crescent``).

Every other record is the control group. Names and aliases are split into
name-words; titles, numbers, Roman numerals, record-id aliases and common
English words (lowercase entries of the system word list) are set aside and
listed in the report. The linking and the English filter are heuristics.
Nothing is written to the canon repository.

A canon file that cannot be read or parsed is never skipped silently: it is
listed under ``unreadable``, the report is marked ``complete: false``, and the
script exits with status 1 after writing the report.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from modules.gumas.phonology import Engine
from modules.gumas.phonology.analysis import Analyzer
from modules.gumas.phonology.engine import PROFILES_DIR

LINK_FIELDS = (
    "faction_bindings", "organization_ids", "origin_polity_id", "controlling_polity_id", "polity_id",
    "member_polities", "faction_id", "dominant_species_id", "founding_species_id", "origin_polity_entity_id",
    "parent_org_id", "organization_binding", "species_id", "species",
)  # fmt: skip
TITLES = frozenset({
    "lord", "marshal", "grand", "duke", "duchess", "dr", "councillor", "warlord", "house", "commander",
    "captain", "admiral", "general", "high", "the", "of", "and", "prime", "station", "sector", "system",
})  # fmt: skip
ROMAN = re.compile(r"^(?=[ivxlc]+$)c{0,3}(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")
DASHES = str.maketrans({"‑": "-", "–": "-", "—": "-", "’": "'"})
WORD_LIST = Path("/usr/share/dict/words")


# ---------------------------------------------------------------------- loading


def load_records(canon_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """CANON entity records with a name, plus every file that could not be read or parsed.

    Each record gets ``_path`` relative to canon/L2/entities. Valid JSON that is not a named CANON record
    (a list, a STAGING entry) is simply out of scope; unreadable files are returned, never dropped.
    """
    base = canon_root / "canon" / "L2" / "entities"
    records: list[dict[str, Any]] = []
    unreadable: list[dict[str, str]] = []
    for path in sorted(base.rglob("*.json")):
        rel = path.relative_to(base).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            unreadable.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        if isinstance(data, dict) and data.get("name") and data.get("certainty") == "CANON":
            data["_path"] = rel
            records.append(data)
    return records, unreadable


def english_words(path: Path = WORD_LIST) -> frozenset[str]:
    """Lowercase entries only, so proper nouns in the list do not hide names."""
    if not path.exists():
        return frozenset()
    return frozenset(w for w in path.read_text(encoding="utf-8").split() if w.islower())


# ---------------------------------------------------------------------- linking


class VelariLinker:
    def __init__(self, records: list[dict[str, Any]], corpus_text: str):
        velar_orgs = {r["entity_id"] for r in records if _is_velar_org(r)}
        self.velar_orgs = sorted(velar_orgs)
        self.markers = {"velar_imperium", "species_velari", "velari"} | velar_orgs
        species = next((r for r in records if r.get("entity_id") == "species_velari"), {})
        species_text = json.dumps(species, ensure_ascii=False)
        self.named = {r.get("entity_id") for r in records if _named_in(r, species_text, corpus_text)}

    def basis(self, record: dict[str, Any]) -> str | None:
        if record.get("entity_id") == "species_velari" or _link_values(record) & self.markers:
            return "binding"
        if record.get("entity_id") in self.named:
            return "named-velari"
        if record.get("region_id") == "loc_zone_velar_crescent":
            return "velar-crescent"
        return None


def _is_velar_org(record: dict[str, Any]) -> bool:
    return record.get("entity_kind") == "organization" and "velar_imperium" in (record.get("faction_bindings") or [])


def _named_in(record: dict[str, Any], species_text: str, corpus_text: str) -> bool:
    entity_id = record.get("entity_id")
    if not entity_id:
        return False
    return entity_id in species_text or record["name"] in species_text or record["_path"] in corpus_text


def _link_values(record: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for field in LINK_FIELDS:
        value = record.get(field)
        items = value if isinstance(value, list) else [value]
        values |= {v for v in items if isinstance(v, str)}
    return values


# ---------------------------------------------------------------------- words


def name_words(text: str) -> list[str]:
    words = []
    for raw in re.split(r"[\s/,()]+", text.translate(DASHES)):
        words += [part for part in raw.strip('.:;"').split("-") if part]
    return words


def set_aside_reason(word: str, english: frozenset[str]) -> str | None:
    """Why a word is not analyzed as a name, or None when it is."""
    low = word.lower().replace("'", "")
    stems = _stems(low)
    checks = (  # first match wins
        ("number", re.search(r"[a-z]", low) is None or re.search(r"\d", low) is not None),
        ("record-id", "_" in word),
        ("title", bool(stems & TITLES)),
        ("roman", ROMAN.match(low) is not None),
        ("english", bool(stems & english) and "'" not in word),
    )
    return next((reason for reason, hit in checks if hit), None)


def _stems(low: str) -> set[str]:
    """The word and its likely singulars, so plurals of titles and English words are caught."""
    return {low, low.removesuffix("s"), low.removesuffix("es")}


def record_texts(record: dict[str, Any]) -> Iterable[str]:
    yield record["name"]
    yield from (a for a in record.get("aliases") or [] if isinstance(a, str))


# ---------------------------------------------------------------------- audit


def collect_words(records, linker: VelariLinker, english: frozenset[str]) -> tuple[dict, dict]:
    words: dict[str, dict[str, Any]] = {}
    tally = {"records": collections.Counter(), "link_basis": collections.Counter(), "set_aside": collections.Counter()}
    for record in records:
        basis = linker.basis(record)
        tier = "velar" if basis else "control"
        tally["records"][tier] += 1
        tally["link_basis"][basis or "control"] += 1
        for text in record_texts(record):
            for word in name_words(text):
                _add_word(words, tally, record, tier, word, english)
    return words, tally


def _add_word(words, tally, record, tier, word, english) -> None:
    reason = set_aside_reason(word, english)
    if reason:
        tally["set_aside"][f"{reason}:{word}"] += 1
        return
    entry = words.setdefault(word.lower().replace("'", ""), {"word": word, "tiers": set(), "records": set()})
    entry["tiers"].add(tier)
    entry["records"].add(record.get("entity_id") or record["_path"])
    if "'" in word:
        entry["word"] = word  # keep the formal spelling: an apostrophe dates the coinage


def analyze_words(words: dict[str, dict[str, Any]], analyzer: Analyzer) -> list[dict[str, Any]]:
    keep = ("status", "etymologies", "nearest", "foreign_letters", "loan_adapted")
    results = []
    for _, entry in sorted(words.items()):
        summary = analyzer.analyze(entry["word"]).summary()
        results.append({
            "word": entry["word"],
            "tier": "velar" if "velar" in entry["tiers"] else "control",
            "records": sorted(entry["records"]),
            **{k: summary[k] for k in keep},
        })  # fmt: skip
    return results


def distance_stats(results: list[dict[str, Any]], tier: str) -> dict[str, Any]:
    """Edits from each native-letter word to its nearest derivable form (0 when it derives)."""
    native = [r for r in results if r["tier"] == tier and r["status"] != "loan"]
    dists = [r["nearest"][0]["distance"] if r["nearest"] else 0 for r in native]
    return {
        "native_words": len(dists),
        "distance_0": dists.count(0),
        "distance_le_1": sum(d <= 1 for d in dists),
        "mean_distance": round(sum(dists) / len(dists), 2) if dists else None,
    }


def audit(canon_root: Path, english: frozenset[str] | None = None) -> dict[str, Any]:
    records, unreadable = load_records(canon_root)
    corpus_text = (PROFILES_DIR / "velari" / "attested.json").read_text(encoding="utf-8")
    linker = VelariLinker(records, corpus_text)
    words, tally = collect_words(records, linker, english_words() if english is None else english)
    results = analyze_words(words, Analyzer.shared(Engine("velari")))
    tiers = ("velar", "control")
    return {
        "complete": not unreadable,
        "unreadable": unreadable,
        "records": dict(tally["records"]),
        "link_basis": dict(tally["link_basis"]),
        "velar_orgs": linker.velar_orgs,
        "name_words": len(results),
        "status_by_tier": {t: dict(collections.Counter(r["status"] for r in results if r["tier"] == t)) for t in tiers},
        "nearest_distance": {t: distance_stats(results, t) for t in tiers},
        "set_aside": sorted(tally["set_aside"]),
        "words": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--canon-root", type=Path, required=True, help="CanonRec checkout (contains canon/L2)")
    parser.add_argument("--out", type=Path, required=True, help="where to write the JSON report")
    args = parser.parse_args()
    if not (args.canon_root / "canon" / "L2" / "entities").is_dir():
        raise SystemExit(f"no canon/L2/entities under {args.canon_root}")
    report = audit(args.canon_root)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    keys = ("complete", "records", "link_basis", "name_words", "status_by_tier", "nearest_distance")
    print(json.dumps({k: report[k] for k in keys}, indent=1))
    if report["unreadable"]:
        paths = ", ".join(item["path"] for item in report["unreadable"])
        print(f"audit incomplete: {len(report['unreadable'])} unreadable canon file(s): {paths}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
