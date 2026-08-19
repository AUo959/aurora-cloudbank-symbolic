"""Filesystem safety tests for the custody-release adapter CLI helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.salvage.prepare_corpus_from_inventory import CustodyAdapterError, _write_new


@pytest.mark.unit
def test_write_new_rejects_dangling_symlink_output(tmp_path: Path) -> None:
    target = tmp_path / "unexpected-target.json"
    output = tmp_path / "prepared.json"
    output.symlink_to(target)

    with pytest.raises(CustodyAdapterError, match="output path must be new"):
        _write_new(output, "{}\n")

    assert output.is_symlink()
    assert not target.exists()
