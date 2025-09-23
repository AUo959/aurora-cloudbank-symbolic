#!/usr/bin/env python3
import re
from pathlib import Path


REPORT = Path("BRANCH_CLEANUP_REPORT.md")
SUGGESTIONS_MD = Path("REBASE_SUGGESTIONS.md")
REBASE_SH = Path("scripts/rebase_review_branches.sh")


def parse_review_needed(report_text: str):
    branches = []
    in_section = False
    for line in report_text.splitlines():
        if line.startswith("## "):
            in_section = line.strip().startswith("## Review Needed")
            continue
        if not in_section:
            continue
        m = re.match(r"^\s*- \*\*origin/(.+?)\*\*", line)
        if m:
            branches.append(m.group(1).strip())
    return branches


def write_markdown(branches):
    lines = []
    lines.append("# Rebase Suggestions for Review Branches")
    lines.append("")
    lines.append("Generated from BRANCH_CLEANUP_REPORT.md (Review Needed category).")
    lines.append("")
    lines.append("General approach:")
    lines.append("- Prefer rebase onto `origin/main` when feasible.")
    lines.append("- Use `--force-with-lease` when pushing rebased history.")
    lines.append("- If rebase conflicts are non-trivial, abort and consider a merge update.")
    lines.append("")
    for br in branches:
        lines.append(f"## origin/{br}")
        lines.append("")
        lines.append("Rebase path:")
        lines.append("```")
        lines.append("git fetch origin --prune")
        lines.append(f"git checkout -B {br} origin/{br}")
        lines.append("git rebase --rebase-merges --autostash origin/main")
        lines.append("# If successful:")
        lines.append(f"git push --force-with-lease origin {br}")
        lines.append("")
        lines.append("# If conflicts are hard to resolve, abort and consider merge:")
        lines.append("git rebase --abort")
        lines.append(f"git checkout -B {br} origin/{br}")
        lines.append("git merge --no-ff origin/main")
        lines.append(f"git push origin {br}")
        lines.append("```")
        lines.append("")
    SUGGESTIONS_MD.write_text("\n".join(lines), encoding="utf-8")


def write_shell(branches):
    REBASE_SH.parent.mkdir(parents=True, exist_ok=True)
    sh = []
    sh.append("#!/usr/bin/env bash")
    sh.append("set -euo pipefail")
    sh.append("")
    sh.append("# Guarded rebase helper for 'Review Needed' branches.")
    sh.append("# Usage:")
    sh.append("#   bash scripts/rebase_review_branches.sh                # dry-run (prints)")
    sh.append("#   CONFIRM=YES bash scripts/rebase_review_branches.sh --execute  # execute")
    sh.append("")
    sh.append("DRY_RUN=1")
    sh.append('if [[ "${1:-}" == "--execute" ]]; then')
    sh.append('  if [[ "${CONFIRM:-NO}" != "YES" ]]; then')
    sh.append("    echo 'Refusing to execute without CONFIRM=YES' >&2; exit 2")
    sh.append('  fi')
    sh.append('  DRY_RUN=0')
    sh.append('fi')
    sh.append("")
    sh.append("branches=(")
    for br in branches:
        sh.append(f'  "{br}"')
    sh.append(")")
    sh.append("")
    sh.append("echo 'Fetching remotes...' >&2")
    sh.append("git fetch origin --prune")
    sh.append("")
    sh.append("for br in \"${branches[@]}\"; do")
    sh.append("  echo '---' >&2")
    sh.append("  echo \"[INFO] Processing origin/$br\" >&2")
    sh.append("  echo \"git checkout -B $br origin/$br\"")
    sh.append("  echo \"git rebase --rebase-merges --autostash origin/main\"")
    sh.append("  echo \"git push --force-with-lease origin $br\"")
    sh.append("  if [[ $DRY_RUN -eq 0 ]]; then")
    sh.append("    git checkout -B \"$br\" \"origin/$br\"")
    sh.append("    if git rebase --rebase-merges --autostash origin/main; then")
    sh.append("      git push --force-with-lease origin \"$br\"")
    sh.append("      echo \"[OK] Rebased and pushed origin/$br\" >&2")
    sh.append("    else")
    sh.append("      echo \"[WARN] Conflicts on origin/$br; aborting rebase. Consider manual merge.\" >&2")
    sh.append("      git rebase --abort || true")
    sh.append("    fi")
    sh.append("  fi")
    sh.append("done")
    sh.append("")
    sh.append("git checkout main >/dev/null 2>&1 || true")
    REBASE_SH.write_text("\n".join(sh) + "\n", encoding="utf-8")
    REBASE_SH.chmod(0o755)


def main():
    if not REPORT.exists():
        raise SystemExit("BRANCH_CLEANUP_REPORT.md not found. Run the cleanup automation first.")
    text = REPORT.read_text(encoding="utf-8")
    branches = parse_review_needed(text)
    write_markdown(branches)
    write_shell(branches)
    print(f"Generated {SUGGESTIONS_MD} and {REBASE_SH} for {len(branches)} branches.")


if __name__ == "__main__":
    main()
