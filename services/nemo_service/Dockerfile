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
# Stage 1 — Builder
# Base: NVIDIA NGC NeMo 24.07 (includes CUDA, cuDNN, PyTorch, NeMo toolkit)
# ══════════════════════════════════════════════════════════════════════════
FROM nvcr.io/nvidia/nemo:24.07 AS builder

LABEL stage="builder"
LABEL aurora.module-id="AURORA_NEMO_SERVICE"
LABEL aurora.ethics-protocol="Picard_Delta_3"

WORKDIR /build

# Copy service-specific requirements first for layer caching
COPY services/nemo_service/requirements.txt /build/requirements.txt

# Install Python dependencies on top of the NeMo base environment
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /build/requirements.txt

# Copy the full service source
COPY services/nemo_service/ /build/nemo_service/

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

# ── Copy installed Python packages from builder ───────────────────────────
COPY --from=builder /build/nemo_service/ /app/services/nemo_service/

# Install runtime dependencies (pip packages from builder stage)
COPY services/nemo_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

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

# ── Ownership ─────────────────────────────────────────────────────────────
RUN chown -R aurora:aurora /app /models /snapshots || true

# ── Switch to non-root user ───────────────────────────────────────────────
USER aurora

# ── Health check ──────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8090/nemo/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────
CMD ["uvicorn", "services.nemo_service.server:app", \
     "--host", "0.0.0.0", \
     "--port", "8090", \
     "--log-level", "info"]
