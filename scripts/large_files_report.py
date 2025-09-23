#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

THRESHOLD_MB = float(os.environ.get("THRESHOLD_MB", "10"))
OUTPUT = Path(os.environ.get("OUTPUT", "LARGE_FILES_REPORT.md"))


def get_tracked_files() -> List[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=False, check=False)
    files = []
    if out.returncode == 0 and out.stdout:
        for chunk in out.stdout.split(b"\x00"):
            if chunk:
                p = Path(chunk.decode("utf-8", errors="ignore"))
                if p.is_file():
                    files.append(p)
    return files


def human_mb(size_bytes: int) -> float:
    return round(size_bytes / 1024 / 1024, 1)


def main():
    files = get_tracked_files()
    threshold_bytes = int(THRESHOLD_MB * 1024 * 1024)
    items: List[Tuple[int, Path]] = []
    for f in files:
        try:
            sz = f.stat().st_size
        except OSError:
            continue
        if sz >= threshold_bytes:
            items.append((sz, f))

    items.sort(reverse=True, key=lambda x: x[0])

    by_ext: Dict[str, List[Tuple[int, Path]]] = {}
    for sz, f in items:
        ext = f.suffix.lower() or "(no-ext)"
        by_ext.setdefault(ext, []).append((sz, f))

    lines: List[str] = []
    lines.append("# Tracked Large Files Report")
    lines.append(f"Threshold: {THRESHOLD_MB} MB")
    lines.append("")
    total_mb = sum(human_mb(sz) for sz, _ in items)
    lines.append(f"- Total tracked files over threshold: {len(items)}")
    lines.append(f"- Aggregate size: {total_mb:.1f} MB")
    lines.append("")

    for ext, lst in sorted(by_ext.items(), key=lambda kv: sum(sz for sz, _ in kv[1]), reverse=True):
        ext_total = sum(human_mb(sz) for sz, _ in lst)
        lines.append(f"## {ext} ({len(lst)} files, {ext_total:.1f} MB)")
        for sz, f in lst[:100]:
            lines.append(f"- {human_mb(sz):6.1f} MB  {f}")
        lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(items)} files >= {THRESHOLD_MB}MB)")


if __name__ == "__main__":
    main()
