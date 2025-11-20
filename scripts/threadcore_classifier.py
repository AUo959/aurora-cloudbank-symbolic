#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Union, Optional

# Configuration stays the same as v2
PRIORITY_THRESHOLDS = {"high": 3, "medium": 1}
DEFAULT_RESULT = {
    "primary_folder": "Unsorted",
    "priority": "low",
    "reason": "No content or keywords matched",
    "all_hits": {},
}

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
        "keywords": [
            "encryption",
            "key",
            "decrypt",
            "auth",
            "secure",
            "session",
        ],
    },
    "DataFlow": {
        "weight": 1,
        "keywords": ["vector index", "dataset", "cloudsync", "memory", "export"],
    },
    "RitualUX": {
        "weight": 2,
        "keywords": [
            "ritual",
            "arch",
            "scroll",
            "map",
            "invocation",
            "resilience",
        ],
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
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def tag_thread_context(content: str) -> Dict[str, Union[str, Dict[str, int]]]:
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

    max_score = max(total_scores.values())
    top_categories = [k for k, v in total_scores.items() if v == max_score]
    primary_folder = sorted(top_categories)[0]

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


def load_threadcore_registry(registry_path: Optional[str] = None) -> Dict:
    """Load the ThreadCore registry for validation."""
    if registry_path is None:
        # Default to registry in repo root
        script_dir = Path(__file__).parent
        registry_path = script_dir.parent / "threadcore_registry.json"
    else:
        registry_path = Path(registry_path)

    if not registry_path.exists():
        raise FileNotFoundError(f"ThreadCore registry not found at {registry_path}")

    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_payload_against_registry(
    payload_data: Dict, registry: Dict
) -> Dict[str, Union[bool, str, List[str]]]:
    """Validate a ThreadCore payload against the registry specification."""
    validation_result = {
        "valid": True,
        "status": "valid",
        "errors": [],
        "warnings": [],
    }

    validation_rules = registry.get("validation_rules", {})

    # Check required fields
    required_fields = validation_rules.get("required_fields", [])
    for field in required_fields:
        if field not in payload_data:
            validation_result["errors"].append(f"Missing required field: {field}")
            validation_result["valid"] = False

    # Validate anchor seed
    required_anchor = validation_rules.get("anchor_seed_required")
    if required_anchor and payload_data.get("anchor_seed") != required_anchor:
        validation_result["errors"].append(
            f"Anchor seed must be '{required_anchor}', found '{payload_data.get('anchor_seed')}'"
        )
        validation_result["valid"] = False

    # Validate ethics protocol
    required_ethics = validation_rules.get("ethics_protocol_required")
    if required_ethics and payload_data.get("ethics_protocol") != required_ethics:
        validation_result["errors"].append(
            f"Ethics protocol must be '{required_ethics}', found '{payload_data.get('ethics_protocol')}'"
        )
        validation_result["valid"] = False

    # Validate drift threshold
    max_drift = validation_rules.get("max_drift_threshold")
    if max_drift is not None:
        drift_str = payload_data.get("symbolic_drift", "0.0")
        if isinstance(drift_str, str):
            drift_str = drift_str.rstrip("%")
        try:
            drift_value = float(drift_str) / 100 if "%" in str(
                payload_data.get("symbolic_drift", "")
            ) else float(drift_str)
            if drift_value > max_drift:
                validation_result["warnings"].append(
                    f"Symbolic drift {drift_value} exceeds threshold {max_drift}"
                )
        except (ValueError, TypeError):
            validation_result["warnings"].append(
                f"Could not parse drift value: {payload_data.get('symbolic_drift')}"
            )

    # Set status based on validation
    if not validation_result["valid"]:
        validation_result["status"] = "invalid"
    elif validation_result["warnings"]:
        validation_result["status"] = "valid_with_warnings"

    return validation_result


def classify_payload_status(
    payload_path: str, registry: Dict
) -> Dict[str, Union[str, bool, List[str]]]:
    """Classify a ThreadCore payload file and determine its status."""
    payload_path_obj = Path(payload_path)

    if not payload_path_obj.exists():
        return {
            "status": "not_found",
            "valid": False,
            "errors": [f"Payload file not found: {payload_path}"],
        }

    # Load payload
    try:
        with open(payload_path_obj, "r", encoding="utf-8") as f:
            payload_data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "status": "invalid_json",
            "valid": False,
            "errors": [f"Invalid JSON: {str(e)}"],
        }

    # Check if payload is in registry
    payload_name = payload_path_obj.stem
    payloads = registry.get("payloads", {})

    if payload_name in payloads:
        registry_entry = payloads[payload_name]
        status = registry_entry.get("status", "unknown")

        result = {
            "payload_name": payload_name,
            "registry_status": status,
            "version": registry_entry.get("version"),
            "variant": registry_entry.get("variant"),
            "is_canonical": status == "canonical",
            "is_deprecated": status == "deprecated",
        }

        # Validate against registry rules
        validation = validate_payload_against_registry(payload_data, registry)
        result.update(validation)

        return result
    else:
        return {
            "payload_name": payload_name,
            "registry_status": "unregistered",
            "valid": False,
            "errors": [f"Payload not found in registry: {payload_name}"],
            "warnings": ["Consider adding this payload to the registry or removing it"],
        }


def main():
    parser = argparse.ArgumentParser(
        description="THREADCORE v3 Tagging Classifier and Registry Validator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Tag command (original functionality)
    tag_parser = subparsers.add_parser("tag", help="Tag and classify thread content")
    tag_parser.add_argument("input_file", help="Path to text file to classify")

    # Validate command (new functionality)
    validate_parser = subparsers.add_parser(
        "validate", help="Validate ThreadCore payload against registry"
    )
    validate_parser.add_argument("payload_file", help="Path to ThreadCore payload JSON")
    validate_parser.add_argument(
        "--registry",
        help="Path to threadcore_registry.json (defaults to repo root)",
        default=None,
    )

    # List command (new functionality)
    list_parser = subparsers.add_parser(
        "list", help="List all payloads in the registry"
    )
    list_parser.add_argument(
        "--registry",
        help="Path to threadcore_registry.json (defaults to repo root)",
        default=None,
    )

    args = parser.parse_args()

    if args.command == "tag":
        with open(args.input_file, "r", encoding="utf-8") as f:
            content = f.read()
        result = tag_thread_context(content)
        print(json.dumps(result, indent=2))

    elif args.command == "validate":
        try:
            registry = load_threadcore_registry(args.registry)
            result = classify_payload_status(args.payload_file, registry)
            print(json.dumps(result, indent=2))
        except FileNotFoundError as e:
            print(json.dumps({"error": str(e)}, indent=2))
            exit(1)

    elif args.command == "list":
        try:
            registry = load_threadcore_registry(args.registry)
            payloads = registry.get("payloads", {})
            canonical = registry.get("canonical_version")
            deprecated = registry.get("deprecated_versions", [])

            output = {
                "canonical_version": canonical,
                "total_payloads": len(payloads),
                "payloads": {},
            }

            for name, info in payloads.items():
                output["payloads"][name] = {
                    "version": info.get("version"),
                    "variant": info.get("variant"),
                    "status": info.get("status"),
                    "description": info.get("description"),
                    "file_path": info.get("file_path"),
                }

            output["deprecated_versions"] = deprecated

            print(json.dumps(output, indent=2))
        except FileNotFoundError as e:
            print(json.dumps({"error": str(e)}, indent=2))
            exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
