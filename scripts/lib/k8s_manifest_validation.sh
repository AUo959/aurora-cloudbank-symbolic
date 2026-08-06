#!/bin/bash
# This file is sourced by the Kubernetes deployment scripts.

# Validate Kubernetes YAML without contacting a cluster. `kubectl apply
# --dry-run=client` still performs API discovery, so it is not an offline
# validation boundary when no kubeconfig is present.
validate_k8s_manifest_offline() {
    local manifest="$1"

    python3 - "$manifest" <<'PY'
import sys
from pathlib import Path

import yaml


manifest = Path(sys.argv[1])
try:
    documents = list(yaml.safe_load_all(manifest.read_text(encoding="utf-8")))
except (OSError, yaml.YAMLError) as exc:
    raise SystemExit(f"invalid Kubernetes manifest {manifest}: {exc}") from exc

resources = [document for document in documents if document is not None]
if not resources:
    raise SystemExit(f"invalid Kubernetes manifest {manifest}: no resources found")

for index, resource in enumerate(resources, start=1):
    if not isinstance(resource, dict):
        raise SystemExit(
            f"invalid Kubernetes manifest {manifest}: document {index} is not an object"
        )
    missing = [key for key in ("apiVersion", "kind") if not resource.get(key)]
    if missing:
        raise SystemExit(
            f"invalid Kubernetes manifest {manifest}: document {index} missing "
            + ", ".join(missing)
        )

print(f"validated {len(resources)} Kubernetes resource(s): {manifest}")
PY
    return 0
}
