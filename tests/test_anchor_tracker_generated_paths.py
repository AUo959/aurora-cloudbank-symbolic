"""Generated frontend bundles should not enter source-anchor indexing."""
from pathlib import Path

from tools.symbolic.anchor_tracker import SymbolicAnchorTracker


def test_repository_scan_keeps_source_but_skips_generated_dist(tmp_path, monkeypatch):
    source = tmp_path / 'frontend' / 'src' / 'editor.js'
    generated = tmp_path / 'frontend' / 'dist' / 'assets' / 'editor.js'
    source.parent.mkdir(parents=True)
    generated.parent.mkdir(parents=True)
    source.write_text('// authored editor source')
    generated.write_text('// generated minified editor bundle')
    tracker = SymbolicAnchorTracker(str(tmp_path))
    scanned = []

    def scan(path: Path):
        scanned.append(path)
        return []

    monkeypatch.setattr(tracker, '_scan_file', scan)
    tracker.scan_repository(extensions=['.js'])
    assert source in scanned
    assert generated not in scanned
