import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "quick_health_check.py"
MODULE_SPEC = importlib.util.spec_from_file_location("quick_health_check", MODULE_PATH)
quick_health_check = importlib.util.module_from_spec(MODULE_SPEC)
assert MODULE_SPEC.loader is not None
MODULE_SPEC.loader.exec_module(quick_health_check)


def test_parse_branches_filters_origin_head_and_empty_values():
    raw_output = "\norigin/HEAD -> origin/main\norigin/main\norigin/feature-a\norigin\n\n"

    branches = quick_health_check._parse_branches(raw_output)

    assert branches == ["origin/main", "origin/feature-a"]


@patch.object(quick_health_check.subprocess, "run")
def test_get_branch_count_uses_remote_branches_when_available(mock_run):
    mock_run.return_value = Mock(returncode=0, stdout="origin/main\norigin/feature-a\n")

    branch_count = quick_health_check._get_branch_count()

    assert branch_count == 2
    assert mock_run.call_count == 1


@patch.object(quick_health_check.subprocess, "run")
def test_get_branch_count_falls_back_to_local_branches(mock_run):
    mock_run.side_effect = [
        Mock(returncode=0, stdout=""),
        Mock(returncode=0, stdout="main\nwork\nfeature/local\n"),
    ]

    branch_count = quick_health_check._get_branch_count()

    assert branch_count == 3
    assert mock_run.call_count == 2
