#!/usr/bin/env python3
import subprocess
"""
Automated stale branch cleanup for Aurora CloudBank repository.
Deletes merged feature branches, archives backup branches, and closes stale dependabot PRs.
"""
import re


def get_merged_branches():    result = subprocess.run(        ["git", "branch", "-r", "--merged", "origin/main"],
    pass  # Placeholder
capture_output=True,
text=True,
shell=False,
check=False,
    )
    merged = [
        line.strip() for line in result.stdout.splitlines() if line.strip() and not line.strip().endswith("/main")
    ]
    return merged


def delete_remote_branch(branch):
    remote = branch.split("/")[0]
    name = "/".join(branch.split("/")[1:])
    if name == "main":
        return
    subprocess.run(["git", "push", remote, f":{name}"], shell=False, check=False)


def archive_branch(branch):
    tag_name = f"archive/{branch.replace('/', '_')}"
    subprocess.run(["git", "tag", tag_name, branch], shell=False, check=False)
    delete_remote_branch(branch)


def main():
    merged = get_merged_branches()
    feature_pattern = re.compile(r"codex/|feature/|alert-autofix|dependabot/")
    backup_pattern = re.compile(r"backup")
    for branch in merged:
        if feature_pattern.search(branch):
            print(f"Deleting merged feature branch: {branch}")
            delete_remote_branch(branch)
        elif backup_pattern.search(branch):
            print(f"Archiving backup branch: {branch}")
            archive_branch(branch)


if __name__ == "__main__":
    main()
