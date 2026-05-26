import json

import pytest

from modules.reflective_autonomy.thread_transfer.v2.cross_repo_bridge import (
    CrossRepoBridge,
    CrossRepositoryBridge,
)


@pytest.mark.asyncio
async def test_stage5_transfers_thread_context_payload(tmp_path):
    target_repo = tmp_path / "target"
    target_repo.mkdir()
    bridge = CrossRepoBridge(
        bridge_id="bridge-001",
        source_repo_id="source-repo",
        target_repo_id="target-repo",
        thread_id="thread/context:001",
        anchor_hash="anchor-001",
        metadata={
            "target_repo_path": str(target_repo),
            "thread_context": {
                "messages": [{"role": "system", "content": "preserve continuity"}],
                "glyph_chain": ["EOS_SEED_ORION_v2"],
            },
            "source_anchor": {"anchor_hash": "anchor-001", "metadata": {"source": "test"}},
        },
    )
    manager = CrossRepositoryBridge()

    result = await manager._stage5_thread_transfer(bridge)

    assert result["success"] is True
    assert result["bytes_transferred"] > 0
    assert bridge.metadata["thread_context_transferred"] is True
    receipt = bridge.metadata["thread_context_transfer"]
    assert receipt["sha256"] == result["sha256"]

    transfer_path = target_repo / ".aurora" / "thread_context" / "thread_context_001.json"
    assert transfer_path.exists()
    transferred = json.loads(transfer_path.read_text(encoding="utf-8"))
    assert transferred["thread_id"] == "thread/context:001"
    assert transferred["context"]["glyph_chain"] == ["EOS_SEED_ORION_v2"]
    assert manager._verify_thread_context_transfer(bridge)["success"] is True

    transfer_path.write_text("tampered", encoding="utf-8")
    verification = manager._verify_thread_context_transfer(bridge)
    assert verification["success"] is False
    assert "hash mismatch" in verification["error"]


@pytest.mark.asyncio
async def test_stage5_fails_without_thread_context_payload(tmp_path):
    bridge = CrossRepoBridge(
        bridge_id="bridge-002",
        source_repo_id="source-repo",
        target_repo_id="target-repo",
        thread_id="thread-002",
        anchor_hash="anchor-002",
        metadata={"target_repo_path": str(tmp_path / "target")},
    )
    manager = CrossRepositoryBridge()

    result = await manager._stage5_thread_transfer(bridge)

    assert result["success"] is False
    assert result["stage"] == "thread_transfer"
    assert "No thread context payload" in result["error"]
    assert bridge.metadata["thread_context_transferred"] is False
