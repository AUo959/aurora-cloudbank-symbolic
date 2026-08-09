"""Regression coverage for case-insensitive tracked-path collisions."""

from scripts.check_casefold_collisions import (
    find_casefold_collisions,
    tracked_paths,
)


def test_detects_directory_component_collision():
    collisions = find_casefold_collisions(
        [
            "QGIA_Integration/a.md",
            "QGIA_integration/b.json",
        ]
    )

    assert collisions == {"qgia_integration": ["QGIA_Integration", "QGIA_integration"]}


def test_accepts_distinct_casefolded_paths():
    assert find_casefold_collisions(["QGIA_Integration/a.md", "docs/readme.md"]) == {}


def test_repository_has_no_casefolded_tracked_path_collisions():
    assert find_casefold_collisions(tracked_paths()) == {}
