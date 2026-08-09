"""Regression coverage for case-insensitive tracked-path collisions."""

from scripts.check_casefold_collisions import (
    find_casefold_collisions,
    main,
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


def test_parses_nul_delimited_git_paths():
    assert tracked_paths(b"QGIA_Integration/a.md\0docs/readme.md\0") == [
        "QGIA_Integration/a.md",
        "docs/readme.md",
    ]


def test_main_accepts_collision_free_input():
    assert main(b"QGIA_Integration/a.md\0docs/readme.md\0") == 0


def test_main_rejects_empty_input():
    assert main(b"") == 2
