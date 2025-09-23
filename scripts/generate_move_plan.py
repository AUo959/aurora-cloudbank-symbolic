#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
from typing import List

THRESHOLD_MB = float(os.environ.get("THRESHOLD_MB", "20"))
OUTPUT = Path(os.environ.get("OUTPUT", "BACKUP_MOVE_PLAN.md"))
BACKUPS_DIR = Path("backups")
EXTS = {".zip", ".7z", ".rar", ".tar", ".tar.gz", ".tgz"}


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
    threshold_bytes = int(THRESHOLD_MB * 1024 * 1024)
    files = get_tracked_files()

    candidates = []
    for f in files:
        if f.suffix.lower() in EXTS and not str(f).startswith("backups/"):
            try:
                sz = f.stat().st_size
            except OSError:
                continue
            if sz >= threshold_bytes:
                candidates.append((sz, f))

    candidates.sort(reverse=True, key=lambda x: x[0])

    lines: List[str] = []
    lines.append("# Backup Move Plan (dry-run)")
    lines.append(f"Threshold: {THRESHOLD_MB} MB | backups/: {BACKUPS_DIR}")
    lines.append("")
    if not candidates:
        lines.append("No tracked archive files exceed the threshold.")
    else:
        lines.append("The following tracked archives can be moved to backups/ (retain history, shrink working tree):")
        lines.append("")
        for sz, f in candidates:
            lines.append(f"- {human_mb(sz):6.1f} MB  {f} -> backups/{f.name}")
        lines.append("")
        lines.append("Suggested commands (dry-run preview):")
        lines.append("```")
        lines.append("mkdir -p backups")
        for _, f in candidates:
            lines.append(f"git mv '{f.as_posix()}' 'backups/{f.name}'")
        lines.append("git commit -m 'chore(backups): relocate large tracked archives to backups/'")
        lines.append("```")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(candidates)} candidates)")


if __name__ == "__main__":
    main()
