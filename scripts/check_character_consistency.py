#!/usr/bin/env python3
"""
Aurora CloudBank - Character Consistency Checker

Pre-commit hook script to detect character inconsistencies across the codebase.
Validates character names, genders, and roles against the canonical PRIMARY_8_CHARACTERS.

This prevents character drift where AI agents may hallucinate incorrect attributes.

Usage:
    python scripts/check_character_consistency.py [files...]
    python scripts/check_character_consistency.py --all

Exit codes:
    0 - No inconsistencies found
    1 - Inconsistencies detected (blocks commit)

Part of Issue #430: Character Init Standardization Phase 3
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# ============================================================================
# CANONICAL CHARACTER DATA - Must match load_simulation.py
# ============================================================================
PRIMARY_8_CHARACTERS = [
    {
        "name": "Commander Alex Thorne",
        "role": "Station Commander",
        "id": "CMD_001",
        "gender": "Male (he/him)",
        "agent_file": "thorne.py",
        "first_name": "Alex",
        "last_name": "Thorne"
    },
    {
        "name": "Lt. Commander Maya Shepard",
        "role": "Executive Officer",
        "id": "CMD_002",
        "gender": "Female (she/her)",
        "agent_file": "shepard.py",
        "first_name": "Maya",
        "last_name": "Shepard"
    },
    {
        "name": "Varya Lin",
        "role": "Chief Science Officer",
        "id": "CSO_001",
        "gender": "Female (she/her)",
        "agent_file": "lin.py",
        "first_name": "Varya",
        "last_name": "Lin"
    },
    {
        "name": "Dr. Amira Sato",
        "role": "Chief Ethics Officer",
        "id": "CEO_001",
        "gender": "Female (she/her)",
        "agent_file": "sato.py",
        "first_name": "Amira",
        "last_name": "Sato"
    },
    {
        "name": "Dr. Elira Noor",
        "role": "Lead Reflexivity Specialist",
        "id": "ETH_002",
        "gender": "Female (she/her)",
        "agent_file": "noor.py",
        "first_name": "Elira",
        "last_name": "Noor"
    },
    {
        "name": "Prof. Elena Sorensen",
        "role": "Cognitive Ethicist",
        "id": "ETH_003",
        "gender": "Female (she/her)",
        "agent_file": "sorensen.py",
        "first_name": "Elena",
        "last_name": "Sorensen"
    },
    {
        "name": "Helena Vu",
        "role": "Cultural & HR Director",
        "id": "HR_001",
        "gender": "Female (she/her)",
        "agent_file": "vu.py",
        "first_name": "Helena",
        "last_name": "Vu"
    },
    {
        "name": "Julian Markov",
        "role": "Chief Security Officer",
        "id": "CSO_002",
        "gender": "Male (he/him)",
        "agent_file": "markov.py",
        "first_name": "Julian",
        "last_name": "Markov"
    },
]

# Known incorrect variations to detect
# Only check when in context of a character name
KNOWN_TYPOS = {
    "Alec Thorne": "Alex Thorne",
    "Commander Alec": "Commander Alex",
    "Thorne, Alec": "Thorne, Alex",
    "Maya Shepherd": "Maya Shepard",
    "Marya Shepard": "Maya Shepard",
}

# Gender pronoun patterns to validate
GENDER_PATTERNS = {
    "Male (he/him)": {
        "correct": ["he", "him", "his", "himself"],
        "incorrect": ["she", "her", "hers", "herself"]
    },
    "Female (she/her)": {
        "correct": ["she", "her", "hers", "herself"],
        "incorrect": ["he", "him", "his", "himself"]
    }
}


# Pre-compiled regex patterns for performance
_compiled_gender_patterns: Dict[str, Dict[str, List[re.Pattern]]] = {}


def _build_compiled_patterns() -> None:
    """Pre-compile regex patterns for character-pronoun checking."""
    for char in PRIMARY_8_CHARACTERS:
        full_name = char["name"].lower()
        gender = char["gender"]
        if gender in GENDER_PATTERNS:
            incorrect_pronouns = GENDER_PATTERNS[gender]["incorrect"]
            patterns = []
            for pronoun in incorrect_pronouns:
                # Pattern: "Character Name" followed by verb-like word, then pronoun
                pattern = re.compile(rf'\b{re.escape(full_name)}\b\s+\w+\s+\b{pronoun}\b')
                patterns.append((pronoun, pattern))
            _compiled_gender_patterns[full_name] = {
                "gender": gender,
                "patterns": patterns
            }


# Build patterns at module load time
_build_compiled_patterns()


def build_character_lookup() -> Dict[str, Dict[str, Any]]:
    """Build lookup dictionaries for character validation."""
    lookup = {}
    for char in PRIMARY_8_CHARACTERS:
        # Index by various name forms
        lookup[char["name"].lower()] = char
        lookup[char["first_name"].lower()] = char
        lookup[char["last_name"].lower()] = char
        lookup[char["id"].lower()] = char
    return lookup


def check_for_typos(content: str, filename: str) -> List[Tuple[int, str, str, str]]:
    """
    Check content for known character name typos.

    Returns:
        List of (line_number, found_text, correct_text, context)
    """
    issues = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        for typo, correct in KNOWN_TYPOS.items():
            if re.search(rf'\b{re.escape(typo)}\b', line, re.IGNORECASE):
                issues.append((
                    line_num,
                    typo,
                    correct,
                    line.strip()[:80]
                ))

    return issues


def check_gender_consistency(content: str, filename: str) -> List[Tuple[int, str, str, str]]:
    """
    Check for gender pronoun inconsistencies near character names.

    This check is conservative - only flags when pronoun appears in same line
    immediately after the character name (e.g., "Thorne said she" but not
    "Thorne commands the ship, and she responded").

    Uses pre-compiled regex patterns for performance.

    Returns:
        List of (line_number, character_name, issue_description, context)
    """
    issues = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()

        for char in PRIMARY_8_CHARACTERS:
            # Only check full names to reduce false positives
            full_name = char["name"].lower()

            if full_name in line_lower:
                # Use pre-compiled patterns for performance
                if full_name in _compiled_gender_patterns:
                    pattern_info = _compiled_gender_patterns[full_name]
                    gender = pattern_info["gender"]
                    for pronoun, pattern in pattern_info["patterns"]:
                        if pattern.search(line_lower):
                            issues.append((
                                line_num,
                                char["name"],
                                f"Possible wrong pronoun '{pronoun}' (should be {gender})",
                                line.strip()[:80]
                            ))
                break  # Only check once per line per character

    return issues


def check_json_consistency(filepath: Path) -> List[Tuple[int, str, str, str]]:
    """
    Check JSON files for character data consistency.

    Returns:
        List of (line_number, field, issue, value)
    """
    issues = []

    try:
        with open(filepath, 'r') as f:
            content = f.read()
            data = json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return issues

    def check_dict(d: Dict, path: str = "") -> None:
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, str):
                # Check for typos in string values
                for typo, correct in KNOWN_TYPOS.items():
                    if typo.lower() in value.lower():
                        issues.append((
                            0,
                            current_path,
                            f"Contains typo '{typo}' -> should be '{correct}'",
                            value[:50]
                        ))
            elif isinstance(value, dict):
                check_dict(value, current_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        check_dict(item, f"{current_path}[{i}]")

    if isinstance(data, dict):
        check_dict(data)

    return issues


def check_file(filepath: Path) -> List[Tuple[str, int, str, str, str]]:
    """
    Check a single file for character inconsistencies.

    Returns:
        List of (filepath, line_number, issue_type, description, context)
    """
    all_issues = []

    if not filepath.exists():
        return all_issues

    # Skip binary files and certain directories
    # Get this script's name dynamically to avoid hard-coding
    this_script_name = Path(__file__).name
    skip_patterns = [
        '.git', '__pycache__', 'node_modules', '.venv', 'venv',
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
        '.woff', '.woff2', '.ttf', '.eot',
        '.zip', '.tar', '.gz',
        # Skip the consistency checker itself (contains typo dictionary)
        this_script_name,
        # Skip the test file for the checker (contains intentional typos)
        'test_character_init.py'
    ]

    filepath_str = str(filepath)
    if any(skip in filepath_str for skip in skip_patterns):
        return all_issues

    try:
        # Handle JSON files specially
        if filepath.suffix == '.json':
            json_issues = check_json_consistency(filepath)
            for line_num, field, issue, context in json_issues:
                all_issues.append((str(filepath), line_num, "JSON", issue, context))
            return all_issues

        # Read text files
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check for typos
        typo_issues = check_for_typos(content, str(filepath))
        for line_num, found, correct, context in typo_issues:
            all_issues.append((
                str(filepath),
                line_num,
                "TYPO",
                f"Found '{found}' -> should be '{correct}'",
                context
            ))

        # Check gender consistency (only for markdown and documentation)
        if filepath.suffix in ['.md', '.txt', '.rst']:
            gender_issues = check_gender_consistency(content, str(filepath))
            for line_num, char_name, issue, context in gender_issues:
                all_issues.append((
                    str(filepath),
                    line_num,
                    "GENDER",
                    f"{char_name}: {issue}",
                    context
                ))

    except Exception:
        # Silently skip files that can't be read
        pass

    return all_issues


def main() -> int:
    """Main entry point for the character consistency checker."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check for character inconsistencies in Aurora CloudBank"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (if empty, checks staged files)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check all relevant files in the repository"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Determine which files to check
    repo_root = Path(__file__).parent.parent
    files_to_check: Set[Path] = set()

    if args.all:
        # Check all relevant files
        patterns = ['**/*.py', '**/*.md', '**/*.json', '**/*.txt']
        for pattern in patterns:
            for filepath in repo_root.glob(pattern):
                if '.git' not in str(filepath):
                    files_to_check.add(filepath)
    elif args.files:
        # Check specified files
        for f in args.files:
            path = Path(f)
            if path.exists():
                files_to_check.add(path)
    else:
        # Check staged files (for pre-commit hook)
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                cwd=repo_root
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    path = repo_root / line
                    if path.exists():
                        files_to_check.add(path)
        except Exception:
            print("Warning: Could not get staged files, checking all files")
            args.all = True
            return main()

    if not files_to_check:
        if args.verbose:
            print("No files to check")
        return 0

    # Check all files
    all_issues = []
    for filepath in files_to_check:
        issues = check_file(filepath)
        all_issues.extend(issues)

    # Report results
    if all_issues:
        print("🚫 Character Consistency Check FAILED")
        print("=" * 60)
        print()

        for filepath, line_num, issue_type, description, context in all_issues:
            print(f"❌ {filepath}:{line_num}")
            print(f"   Type: {issue_type}")
            print(f"   Issue: {description}")
            if context:
                print(f"   Context: {context}")
            print()

        print("=" * 60)
        print(f"Total issues found: {len(all_issues)}")
        print()
        print("💡 To fix:")
        print("   - Check .github/copilot-instructions.md for canonical character data")
        print("   - Use the correct names and pronouns from PRIMARY_8_CHARACTERS")
        return 1
    else:
        if args.verbose:
            print(f"✅ Character Consistency Check PASSED ({len(files_to_check)} files checked)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
