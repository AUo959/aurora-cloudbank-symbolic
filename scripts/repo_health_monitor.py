#!/usr/bin/env python3
"""
Repository Health Monitoring Script
- Tracks repo size, file count, ZIP count, and branch count
- Outputs a health report to repo_health_status.json
"""
import json
import os
import subprocess


def get_repo_size():
    out = subprocess.check_output(["du", "-sm", "."]).decode().split()[0]
    return int(out)


def get_file_count():
    out = subprocess.check_output(["find", ".", "-type", ""]).decode().splitlines()
    return len(out)


def get_zip_count():
    out = subprocess.check_output(["ls", "-1", "*.zip"]).decode().splitlines()
    return len(out)


def get_branch_count():
    out = subprocess.check_output(["git", "branch", "-r"]).decode().splitlines()
    return len(out)


def main():
    report = {
        "repo_size_mb": get_repo_size(),
        "file_count": get_file_count(),
        "zip_count": get_zip_count(),
        "branch_count": get_branch_count(),
    }
    with open("repo_health_status.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
