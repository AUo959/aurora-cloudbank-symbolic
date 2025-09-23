import tempfile
from pathlib import Path

from tools.symbolic.anchor_tracker import SymbolicAnchorTracker


def write_file(base: Path, rel: str, content: str):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_anchor_tracker_scans_and_generates_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create a small sample repo with a few anchors
        write_file(
            root,
            "README.md",
            """
T71_INFRA_SYMBOLIC_TOOLING_GENESIS
Some text with SRB_SYMBOLIC_BRIDGE and T1_TEMPORAL_ANCHOR
""".strip(),
        )
        write_file(
            root,
            "docs/notes.txt",
            """
Random content
ANCHOR_SEED_ORION
Another line with MEMORY_SEAL_ABC123
""".strip(),
        )

        tracker = SymbolicAnchorTracker(str(root))
        found = tracker.scan_repository(extensions=[".md", ".txt"])  # limit scope
        assert isinstance(found, dict)
        total = sum(len(v) for v in found.values())
        assert total >= 3  # at least a few anchors detected

        lineages = tracker.build_lineage_map()
        assert isinstance(lineages, dict)
        # Every discovered anchor should have a lineage entry
        for anchors in found.values():
            for a in anchors:
                assert a.anchor_id in lineages

        # Repository-wide manifest
        manifest = tracker.generate_export_manifest()
        assert manifest.get("anchor_seed") == "REPOSITORY_SYMBOLIC_STATE"
        assert "memory_seal" in manifest and isinstance(manifest["memory_seal"], str)
        # DLP summary is optional but if present should have expected keys
        dlp = manifest.get("dlp_export_summary")
        if dlp is not None:
            assert "manifest_id" in dlp
            assert "total_tags" in dlp

        # Anchor-specific manifest
        any_anchor = next(iter(tracker.anchors.keys()))
        manifest_one = tracker.generate_export_manifest(any_anchor)
        assert manifest_one.get("anchor_seed") == any_anchor
        assert "memory_seal" in manifest_one
