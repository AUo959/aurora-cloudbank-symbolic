#!/bin/bash
# NEXUS Recursion Snapshot & Recovery Tool
# Anchor: T9-SNAPSHOT-2025
# Seed: EOS_SEED_ORION
# Ethics: Picard_Delta_3
set -euo pipefail

NEXUS_ROOT="${NEXUS_RECURSION_ROOT:-.nexus}"
SNAPSHOT_DIR="${NEXUS_ROOT}/snapshots"
TIMESTAMP="$(date -u +"%Y%m%d_%H%M%S")"
SNAPSHOT_NAME="recursion_snapshot_${TIMESTAMP}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

create_snapshot() {
    echo -e "${GREEN}Creating snapshot: ${SNAPSHOT_NAME}${NC}"
    mkdir -p "${SNAPSHOT_DIR}/${SNAPSHOT_NAME}"
    if [ -d "${NEXUS_ROOT}/recursion" ]; then
        cp -R "${NEXUS_ROOT}/recursion" "${SNAPSHOT_DIR}/${SNAPSHOT_NAME}/"
        echo "  ✓ Recursion data copied"
    fi
    cat > "${SNAPSHOT_DIR}/${SNAPSHOT_NAME}/manifest.json" <<EOF
{
  "snapshot_id": "${SNAPSHOT_NAME}",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "anchor": "T9-SNAPSHOT-2025",
  "seed": "EOS_SEED_ORION",
  "ethics": "Picard_Delta_3",
  "contents": [
    "recursion/checkpoints",
    "recursion/arbitration",
    "recursion/manifests",
    "recursion/index",
    "recursion/paradoxes"
  ],
  "dlp_classification": "SNAPSHOT_CRITICAL"
}
EOF
    echo "  ✓ Manifest created"
    (cd "${SNAPSHOT_DIR}/${SNAPSHOT_NAME}" && find . -type f -print0 | sort -z | xargs -0 sha256sum > checksums.sha256)
    echo "  ✓ Checksums calculated"
    (cd "${SNAPSHOT_DIR}" && tar -czf "${SNAPSHOT_NAME}.tar.gz" "${SNAPSHOT_NAME}")
    echo "  ✓ Archive created: ${SNAPSHOT_NAME}.tar.gz"
    rm -rf "${SNAPSHOT_DIR:?}/${SNAPSHOT_NAME}"
    echo -e "${GREEN}Snapshot complete: ${SNAPSHOT_DIR}/${SNAPSHOT_NAME}.tar.gz${NC}"
}

validate_snapshot() {
    local snapshot_file="$1"
    if [ -z "${snapshot_file}" ]; then
        echo -e "${RED}Error: Snapshot file required${NC}"
        echo "Usage: $0 validate <snapshot.tar.gz>"
        exit 1
    fi
    echo -e "${YELLOW}Validating snapshot: ${snapshot_file}${NC}"
    local temp_dir
    temp_dir="$(mktemp -d)"
    tar -xzf "${snapshot_file}" -C "${temp_dir}"
    local extracted
    extracted="$(find "${temp_dir}" -mindepth 1 -maxdepth 1 -type d | head -n1)"
    local result=0
    if (cd "${extracted}" && sha256sum -c checksums.sha256 >/dev/null 2>&1); then
        echo -e "${GREEN}  ✓ Checksum validation: PASSED${NC}"
    else
        echo -e "${RED}  ✗ Checksum validation: FAILED${NC}"
        result=1
    fi
    if [ -f "${extracted}/manifest.json" ]; then
        echo -e "${GREEN}  ✓ Manifest found${NC}"
    else
        echo -e "${RED}  ✗ Manifest missing${NC}"
        result=1
    fi
    rm -rf "${temp_dir}"
    if [ "${result}" -eq 0 ]; then
        echo -e "${GREEN}Snapshot validation: PASSED${NC}"
    else
        echo -e "${RED}Snapshot validation: FAILED${NC}"
    fi
    return "${result}"
}

restore_snapshot() {
    local snapshot_file="$1"
    if [ -z "${snapshot_file}" ]; then
        echo -e "${RED}Error: Snapshot file required${NC}"
        echo "Usage: $0 restore <snapshot.tar.gz>"
        exit 1
    fi
    echo -e "${YELLOW}Restoring from snapshot: ${snapshot_file}${NC}"
    if ! validate_snapshot "${snapshot_file}"; then
        echo -e "${RED}Snapshot validation failed. Aborting restore.${NC}"
        exit 1
    fi
    if [ -d "${NEXUS_ROOT}/recursion" ]; then
        mv "${NEXUS_ROOT}/recursion" "${NEXUS_ROOT}/recursion.backup.${TIMESTAMP}"
        echo "  ✓ Existing recursion directory backed up"
    fi
    local temp_dir
    temp_dir="$(mktemp -d)"
    tar -xzf "${snapshot_file}" -C "${temp_dir}"
    local extracted
    extracted="$(find "${temp_dir}" -mindepth 1 -maxdepth 1 -type d | head -n1)"
    mv "${extracted}/recursion" "${NEXUS_ROOT}/"
    echo -e "${GREEN}  ✓ Recursion data restored${NC}"
    rm -rf "${temp_dir}"
    echo -e "${GREEN}Restore complete${NC}"
}

list_snapshots() {
    echo -e "${GREEN}Available snapshots:${NC}"
    if [ -d "${SNAPSHOT_DIR}" ]; then
        ls -lh "${SNAPSHOT_DIR}"/*.tar.gz 2>/dev/null || echo "  No snapshots found"
    else
        echo "  Snapshot directory does not exist"
    fi
}

case "${1:-}" in
    create)
        create_snapshot
        ;;
    validate)
        validate_snapshot "${2:-}"
        ;;
    restore)
        restore_snapshot "${2:-}"
        ;;
    list)
        list_snapshots
        ;;
    *)
        cat <<USAGE
NEXUS Recursion Snapshot Tool
=============================
Usage: $0 {create|validate|restore|list} [options]

Commands:
  create           Create new snapshot
  validate <file>  Validate snapshot integrity
  restore <file>   Restore from snapshot
  list             List available snapshots

Examples:
  $0 create
  $0 validate snapshots/recursion_snapshot_20250927_170607.tar.gz
  $0 restore snapshots/recursion_snapshot_20250927_170607.tar.gz

Anchor: T9-SNAPSHOT-2025
Ethics: Picard_Delta_3
USAGE
        ;;
esac
