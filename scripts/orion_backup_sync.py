#!/usr/bin/env python3
"""
orion_backup_sync.py

Backup and synchronize the staff registry and Orion Station blueprint
between Command Node and PL branch.

Summary:
    - Exports and archives registry and blueprint states
    - Validates EOS_SEED_ORION anchor to enforce zero drift
    - Supports rollback from timestamped backups
    - Designed for the ORION Constellation symbolic mesh

Integration Notes:
    - Requires `pyyaml` for YAML parsing
    - Stores backups in `backups/` relative to this script

// ANCHOR: EOS_SEED_ORION
// ETHICS: Picard_Delta_3
"""

import argparse
import os
import shutil
from datetime import datetime

import yaml

from modules.telemetry_logger import get_logger

ANCHOR_SEED = "EOS_SEED_ORION"
BACKUP_DIR = "backups"
logger = get_logger("orion_backup_sync")


def load_yaml(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_anchor(data: dict, path: str) -> None:
    anchor = data.get("anchor_seed")
    if anchor != ANCHOR_SEED:
        raise ValueError(f"Anchor mismatch in {path}: {anchor} != {ANCHOR_SEED}")


def backup_file(src: str) -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_name = f"{os.path.basename(src)}.{timestamp}.bak"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(src, backup_path)
    logger.info("Backup created for %s -> %s", src, backup_path)
    return backup_path


def sync_file(src: str, dest: str) -> None:
    shutil.copy2(src, dest)
    logger.info("Synchronized %s -> %s", src, dest)


def rollback_file(dest: str) -> str:
    if not os.path.isdir(BACKUP_DIR):
        raise FileNotFoundError("No backups directory found")
    prefix = os.path.basename(dest)
    matches = [f for f in os.listdir(BACKUP_DIR) if f.startswith(prefix)]
    if not matches:
        raise FileNotFoundError(f"No backups found for {dest}")
    latest = sorted(matches)[-1]
    backup_path = os.path.join(BACKUP_DIR, latest)
    shutil.copy2(backup_path, dest)
    logger.info("Rolled back %s from %s", dest, backup_path)
    return backup_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive and synchronize Orion staff registry and blueprint")
    parser.add_argument("--command-node", default="command_node_data", help="Command node data directory")
    parser.add_argument("--pl-branch", default="pl_branch_data", help="PL branch data directory")
    parser.add_argument("--rollback", choices=["staff", "blueprint", "all"], help="Rollback target")
    args = parser.parse_args()

    staff_cmd = os.path.join(args.command_node, "staff_registry.yaml")
    bp_cmd = os.path.join(args.command_node, "orion_station_blueprint.yaml")
    staff_pl = os.path.join(args.pl_branch, "staff_registry.yaml")
    bp_pl = os.path.join(args.pl_branch, "orion_station_blueprint.yaml")

    resources = [
        (staff_cmd, staff_pl),
        (bp_cmd, bp_pl),
    ]

    if args.rollback:
        targets = resources
        if args.rollback != "all":
            mapping = {"staff": resources[0], "blueprint": resources[1]}
            targets = [mapping[args.rollback]]

        for _, dest in targets:
            try:
                restore_path = rollback_file(dest)
                print(f"Rolled back {dest} from {restore_path}")
            except Exception as e:
                print(f"Rollback failed for {dest}: {e}")
        return

    confirm = input("Proceed with backup and synchronization? [y/N] ")
    if confirm.lower() != "y":
        print("Operation cancelled")
        return

    for src, dest in resources:
        try:
            data = load_yaml(src)
            validate_anchor(data, src)
        except Exception as e:
            print(f"Validation failed for {src}: {e}")
            continue

        if os.path.exists(dest):
            try:
                bpath = backup_file(dest)
                print(f"Backup created: {bpath}")
            except Exception as e:
                print(f"Could not backup {dest}: {e}")
                continue
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)

        try:
            sync_file(src, dest)
            dest_data = load_yaml(dest)
            validate_anchor(dest_data, dest)
            print(f"Synced {src} -> {dest}")
        except Exception as e:
            print(f"Error syncing {src} to {dest}: {e}")

    print("Backup and synchronization complete")


if __name__ == "__main__":
    main()
