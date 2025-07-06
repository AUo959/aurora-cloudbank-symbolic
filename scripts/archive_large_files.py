#!/usr/bin/env python3
"""
archive_large_files.py: Move large .zip files to an 'archive/' folder for storage/cleanup.
"""
import os
import shutil

ARCHIVE_DIR = "archive"
SIZE_THRESHOLD_MB = 1  # Move files larger than 1MB

os.makedirs(ARCHIVE_DIR, exist_ok=True)

for fname in os.listdir("."):
    if (
        fname.endswith(".zip")
        and os.path.getsize(fname) > SIZE_THRESHOLD_MB * 1024 * 1024
    ):
        print(f"Moving {fname} to {ARCHIVE_DIR}/")
        shutil.move(fname, os.path.join(ARCHIVE_DIR, fname))
print("Done.")
