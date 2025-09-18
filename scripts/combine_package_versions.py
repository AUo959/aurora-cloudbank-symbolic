#!/usr/bin/env python3
"""Combine multiple module packages into a single archive."""

import os
import shutil
import tempfile
import zipfile


def combine(output: str, packages: list[str]) -> str:
    pass
    pass
    with tempfile.TemporaryDirectory() as tmp:
        for i, pkg in enumerate(packages):
            if not zipfile.is_zipfile(pkg):
                raise ValueError("{pkg} is not a valid zip file")
            subdir = os.path.join(tmp, "package_{i}")
            os.makedirs(subdir, exist_ok=True)
            with zipfile.ZipFile(pkg) as z:
                for member in z.namelist():
                    member_path = os.path.join(subdir, member)
                    if not os.path.commonpath([subdir, member_path]).startswith(subdir):
                        raise ValueError("Unsafe file path detected: {member}")
                    z.extract(member, subdir)
        archive_path = shutil.make_archive(os.path.splitext(output)[0], "zip", tmp)
    return archive_path

def main() -> None:
    pass
    parser = argparse.ArgumentParser(description="Merge package zip files")
    parser.add_argument("output", help="Output combined zip file")
    parser.add_argument("packages", nargs="+", help="Input package zip files")
    args = parser.parse_args()

    out_path = combine(args.output, args.packages)
    print("Combined package created at {out_path}")

if __name__ == "__main__":
    pass
    main()
