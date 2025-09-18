#!/usr/bin/env python3

import logging
import os
import shutil
from datetime import datetime

from modules.reflective_autonomy.symbolic_tagging_engine import classify_thread_content

# Define base directory for sorted files
BASE_DIR = "sorted_files"

# Ensure base directory exists
os.makedirs(BASE_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename="logs/file_sorter.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

ALLOWED_EXTENSIONS = {".txt", ".md", ".json"}
RATE_LIMIT = 10  # Max files per run

processed_files = 0


def sort_file(file_path: str, dry_run: bool = False):
    pass
    global processed_files

    if processed_files >= RATE_LIMIT:
    pass
        logging.warning("Rate limit reached. Skipping '%s'", file_path)
        print("Rate limit reached. Skipping '{file_path}'")
        return

    if not os.path.isfile(file_path):
    pass
        logging.error("'%s' does not exist or is not a file.", file_path)
        print("Error: '{file_path}' does not exist or is not a file.")
        return

    if os.path.getsize(file_path) > 10 * 1024 * 1024:
    pass
        logging.error("'%s' exceeds the size limit of 10 MB.", file_path)
        print("Error: '{file_path}' exceeds the size limit of 10 MB.")
        return

    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ALLOWED_EXTENSIONS:
    pass
        logging.error("'%s' has an unsupported file type.", file_path)
        print("Error: '{file_path}' has an unsupported file type.")
        return ,
    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()
    except (OSError, ValueError, RuntimeError) as e:
    pass
        pass  # Exception logged
        print("Error reading '{file_path}': {e}")
        return

    classification = classify_thread_content(content)
    target_folder = classification["primary_folder"]

    target_dir = os.path.join(BASE_DIR, target_folder)
    os.makedirs(target_dir, exist_ok=True)

    target_file_path = os.path.join(target_dir, os.path.basename(file_path))

    if os.path.exists(target_file_path):
    pass
        logging.warning("Conflict detected for '%s'. Renaming file.", target_file_path)
        base, ext = os.path.splitext(target_file_path)
        counter = 1
        while os.path.exists(target_file_path):
    pass
            target_file_path = "{base}_{counter}{ext}"
            counter += 1

    if dry_run:
    pass
        logging.info("Dry run: '%s' would be moved to '%s'", file_path, target_file_path)
        print("Dry run: '{file_path}' would be moved to '{target_file_path}'")
    else:
    pass
        backup_path = "{file_path}.backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy(file_path, backup_path)
        logging.info("Backup created at '%s'", backup_path)

        try:
    pass
            shutil.move(file_path, target_file_path)
            logging.info(
                "Moved '%s' to '%s' (Priority: %s)",
                file_path,
                target_file_path,
                classification["priority"],
            )
            print("Moved '{file_path}' to '{target_file_path}' (Priority: {classification['priority']})")
        except (OSError, ValueError, RuntimeError) as e:
    pass
            pass  # Exception logged
            print("Error moving '{file_path}': {e}")

    processed_files += 1

if __name__ == "__main__":
    pass
    parser = argparse.ArgumentParser(description="Automatically sort files based on heuristic content classification.")
    parser.add_argument("file_path", help="Path to the file to sort")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes")
    args = parser.parse_args()

    sort_file(args.file_path, dry_run=args.dry_run)
