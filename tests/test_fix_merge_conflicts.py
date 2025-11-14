"""Tests for fix_merge_conflicts.py script"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_resolve_conflicts_basic():
    """Test basic conflict resolution - keeps HEAD version"""
    from fix_merge_conflicts import resolve_conflicts

    content = """line1
<<<<<<< HEAD
head_content
=======
origin_content
>>>>>>> origin/main
line2"""

    fixed, count = resolve_conflicts(content)
    assert count == 1
    assert "head_content" in fixed
    assert "origin_content" not in fixed
    assert "<<<<<<< HEAD" not in fixed
    assert "=======" not in fixed
    assert ">>>>>>>" not in fixed
    assert "line1" in fixed
    assert "line2" in fixed


def test_resolve_conflicts_multiple():
    """Test multiple conflict blocks"""
    from fix_merge_conflicts import resolve_conflicts

    content = """start
<<<<<<< HEAD
first_head
=======
first_origin
>>>>>>> origin/main
middle
<<<<<<< HEAD
second_head
=======
second_origin
>>>>>>> origin/feature
end"""

    fixed, count = resolve_conflicts(content)
    assert count == 2
    assert "first_head" in fixed
    assert "second_head" in fixed
    assert "first_origin" not in fixed
    assert "second_origin" not in fixed
    assert "start" in fixed
    assert "middle" in fixed
    assert "end" in fixed


def test_resolve_conflicts_no_conflicts():
    """Test content with no conflicts"""
    from fix_merge_conflicts import resolve_conflicts

    content = """line1
line2
line3"""

    fixed, count = resolve_conflicts(content)
    assert count == 0
    assert fixed == content


def test_resolve_conflicts_multiline_head():
    """Test conflict with multiple lines in HEAD section"""
    from fix_merge_conflicts import resolve_conflicts

    content = """before
<<<<<<< HEAD
head_line1
head_line2
head_line3
=======
origin_line1
origin_line2
>>>>>>> origin/main
after"""

    fixed, count = resolve_conflicts(content)
    assert count == 1
    assert "head_line1" in fixed
    assert "head_line2" in fixed
    assert "head_line3" in fixed
    assert "origin_line1" not in fixed
    assert "origin_line2" not in fixed
    assert "before" in fixed
    assert "after" in fixed


def test_resolve_conflicts_empty_head():
    """Test conflict where HEAD section is empty"""
    from fix_merge_conflicts import resolve_conflicts

    content = """before
<<<<<<< HEAD
=======
origin_content
>>>>>>> origin/main
after"""

    fixed, count = resolve_conflicts(content)
    assert count == 1
    assert "origin_content" not in fixed
    assert "before" in fixed
    assert "after" in fixed


def test_resolve_conflicts_empty_origin():
    """Test conflict where origin section is empty"""
    from fix_merge_conflicts import resolve_conflicts

    content = """before
<<<<<<< HEAD
head_content
=======
>>>>>>> origin/main
after"""

    fixed, count = resolve_conflicts(content)
    assert count == 1
    assert "head_content" in fixed
    assert "before" in fixed
    assert "after" in fixed


def test_resolve_conflicts_consecutive():
    """Test consecutive conflict blocks"""
    from fix_merge_conflicts import resolve_conflicts

    content = """<<<<<<< HEAD
first_head
=======
first_origin
>>>>>>> origin/main
<<<<<<< HEAD
second_head
=======
second_origin
>>>>>>> origin/main"""

    fixed, count = resolve_conflicts(content)
    assert count == 2
    assert "first_head" in fixed
    assert "second_head" in fixed
    assert "first_origin" not in fixed
    assert "second_origin" not in fixed


def test_resolve_conflicts_with_code():
    """Test conflict with actual code"""
    from fix_merge_conflicts import resolve_conflicts

    content = """def function():
    x = 1
<<<<<<< HEAD
    return x + 2
=======
    return x + 3
>>>>>>> origin/feature
    # end"""

    fixed, count = resolve_conflicts(content)
    assert count == 1
    assert "return x + 2" in fixed
    assert "return x + 3" not in fixed
    assert "def function():" in fixed


def test_resolve_conflicts_branch_names():
    """Test different branch name formats"""
    from fix_merge_conflicts import resolve_conflicts

    content = """<<<<<<< HEAD
head1
=======
origin1
>>>>>>> refs/remotes/origin/feature-branch
<<<<<<< HEAD
head2
=======
origin2
>>>>>>> abc123def456"""

    fixed, count = resolve_conflicts(content)
    assert count == 2
    assert "head1" in fixed
    assert "head2" in fixed
    assert "origin1" not in fixed
    assert "origin2" not in fixed


def test_resolve_conflicts_preserves_indentation():
    """Test that indentation is preserved"""
    from fix_merge_conflicts import resolve_conflicts

    content = """    def test():
<<<<<<< HEAD
        return True
=======
        return False
>>>>>>> origin/main
        # comment"""

    fixed, count = resolve_conflicts(content)
    assert count == 1
    assert "        return True" in fixed
    assert "return False" not in fixed


def test_resolve_conflicts_dos_prevention():
    """Test that function handles potentially malicious input efficiently

    This test ensures the implementation doesn't use vulnerable regex patterns
    that could cause exponential backtracking (ReDoS vulnerability).
    The function should complete quickly even with pathological input.
    """
    from fix_merge_conflicts import resolve_conflicts
    import time

    # Create input with many equals signs that could trigger backtracking
    # in a vulnerable regex pattern
    malicious_content = """<<<<<<< HEAD
""" + "=" * 1000 + """
=======
""" + "=" * 1000 + """
>>>>>>> origin/main"""

    start_time = time.time()
    fixed, count = resolve_conflicts(malicious_content)
    elapsed_time = time.time() - start_time

    # Should complete in well under 1 second
    assert elapsed_time < 1.0
    assert count == 1
    # Content with equals should be preserved (from HEAD section)
    assert "=" * 1000 in fixed


def test_resolve_conflicts_incomplete_marker():
    """Test that incomplete conflict markers are handled gracefully"""
    from fix_merge_conflicts import resolve_conflicts

    # Missing closing marker
    content = """<<<<<<< HEAD
head_content
=======
origin_content"""

    fixed, count = resolve_conflicts(content)
    # Should not crash, and should not count as resolved
    assert count == 0
    # Original content should be preserved
    assert "head_content" in fixed
    assert "origin_content" in fixed
