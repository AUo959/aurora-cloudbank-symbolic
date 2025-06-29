#!/usr/bin/env python3
"""Combine multiple module packages into a single archive."""

import argparse
import os
import shutil
import tempfile
import zipfile


def combine(output: str, packages: list[str]) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        for pkg in packages:
            if not zipfile.is_zipfile(pkg):
                raise ValueError(f"{pkg} is not a valid zip file")
            with zipfile.ZipFile(pkg) as z:
                z.extractall(tmp)
        archive_path = shutil.make_archive(os.path.splitext(output)[0], "zip", tmp)
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge package zip files")
    parser.add_argument("output", help="Output combined zip file")
    parser.add_argument("packages", nargs="+", help="Input package zip files")
    args = parser.parse_args()

    out_path = combine(args.output, args.packages)
    print(f"Combined package created at {out_path}")


if __name__ == "__main__":
    main()
