# ──────────────────────────────────────────────────────────────────────────
# Aurora NeMo Service — GPU-Capable Multi-Stage Dockerfile
# ──────────────────────────────────────────────────────────────────────────
# Ethics Protocol: Picard_Delta_3
# T1: Build-time anchor
# SRB: NEMO_SERVICE_v1
# Chain Notation: #SERVICES//NEMO//DOCKERFILE//
# DLP: [nemo, docker, gpu, build]
# Anchor Seed: EOS_SEED_ORION
#
# Aurora symbolic labels:
#   aurora.chain-notation  — #SERVICES//NEMO//RUNTIME//
#   aurora.ethics-protocol — Picard_Delta_3
#   aurora.module-id       — AURORA_NEMO_SERVICE
#   aurora.srb             — NEMO_SERVICE_v1
# ──────────────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════
# Stage 1 — (builder stage removed)
# NOTE: A dedicated builder stage previously installed Python dependencies
# and copied the service source. This has been simplified into a single-
# stage image to avoid reinstalling dependencies in multiple stages.
# The runtime stage below now handles copying the source and installing
# the required Python packages directly.














# ══════════════════════════════════════════════════════════════════════════
# Stage 2 — Runtime
# Minimal production image built on the same NeMo base (GPU support)
# ══════════════════════════════════════════════════════════════════════════
FROM nvcr.io/nvidia/nemo:24.07 AS runtime

# ── Aurora symbolic labels ────────────────────────────────────────────────
LABEL aurora.chain-notation="#SERVICES//NEMO//RUNTIME//"
LABEL aurora.ethics-protocol="Picard_Delta_3"
LABEL aurora.module-id="AURORA_NEMO_SERVICE"
LABEL aurora.srb="NEMO_SERVICE_v1"
LABEL aurora.anchor-seed="EOS_SEED_ORION"
LABEL aurora.dlp="nemo,inference,gpu,models"

# ── OCI / security labels matching k8s conventions ────────────────────────
LABEL org.opencontainers.image.title="Aurora NeMo Inference Service"
LABEL org.opencontainers.image.description="NVIDIA NeMo service integrated with Aurora CloudBank Symbolic"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Aurora CloudBank Symbolic"
LABEL security.non-root="true"
LABEL security.read-only-rootfs="false"

WORKDIR /app

# ── Create non-root aurora user (UID 1000) ────────────────────────────────
RUN groupadd -g 1000 aurora \
    && useradd -u 1000 -g aurora -m -s /bin/bash aurora

# ── Copy service source and install Python dependencies ───────────────────
COPY --chown=aurora:aurora services/nemo_service/ /app/services/nemo_service/
COPY --chown=aurora:aurora services/nemo_service/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt \
    && mkdir -p /models /snapshots \
    && chown -R aurora:aurora /app /models /snapshots

# ── Volume mount points ───────────────────────────────────────────────────
# /models    — NeMo model weight checkpoints (persistent PVC in K8s)
# /snapshots — State simulation snapshots (persistent PVC or emptyDir)
VOLUME ["/models", "/snapshots"]

# ── Expose inference port ─────────────────────────────────────────────────
EXPOSE 8090

# ── Environment defaults (overridden at deploy time) ─────────────────────
ENV NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    AURORA_MODULE_ID=AURORA_NEMO_SERVICE \
    AURORA_ETHICS_PROTOCOL=Picard_Delta_3 \
    NEMO_ANCHOR_SEED=EOS_SEED_ORION \
    NEMO_HOST=0.0.0.0 \
    NEMO_PORT=8090 \
    NEMO_MODELS_DIR=/models \
    NEMO_SNAPSHOTS_DIR=/snapshots \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER aurora

# ── Health check (Python-based — no curl dependency required) ─────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + __import__('os').environ.get('NEMO_PORT','8090') + '/nemo/health')" || exit 1

CMD ["uvicorn", "services.nemo_service.server:app", "--host", "0.0.0.0", "--port", "8090", "--log-level", "info"]