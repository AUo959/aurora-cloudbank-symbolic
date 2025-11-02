# Aurora CloudBank Symbolic - Multi-Stage Production Dockerfile
# Ethics Protocol: Picard_Delta_3
# Chain Notation: #K8S//DOCKER//BUILD//AURORA_GUI_CLOUDHUB//
# SRB: DOCKER_IMAGE_v1

# ==============================================================================
# Stage 1: Builder (Install dependencies and compile)
# ==============================================================================
FROM python:3.12-slim AS builder

# Metadata labels for ethics and symbolic continuity
LABEL maintainer="AUo959 <admin@aurora.example.com>"
LABEL aurora.chain-notation="#K8S//DOCKER//BUILDER//"
LABEL aurora.ethics-protocol="Picard_Delta_3"
LABEL aurora.module-id="AURORA_GUI_CLOUDHUB_BUILDER"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements file
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements.txt

# ==============================================================================
# Stage 2: Runtime (Minimal production image)
# ==============================================================================
FROM python:3.12-slim

# Metadata labels
LABEL maintainer="AUo959 <admin@aurora.example.com>"
LABEL aurora.chain-notation="#K8S//DOCKER//RUNTIME//AURORA_GUI_CLOUDHUB//"
LABEL aurora.ethics-protocol="Picard_Delta_3"
LABEL aurora.module-id="AURORA_GUI_CLOUDHUB"
LABEL aurora.srb="DOCKER_RUNTIME_v1"
LABEL version="1.0.0"
LABEL description="Aurora CloudBank Symbolic GUI CloudHub - Quantum VSA Playground with MCP Bridge"

# Security labels
LABEL security.non-root="true"
LABEL security.read-only-root-filesystem="true"
LABEL security.no-new-privileges="true"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    AURORA_MODULE_ID="AURORA_GUI_CLOUDHUB_K8S" \
    AURORA_CHAIN_NOTATION="#K8S//DOCKER//RUNTIME//" \
    AURORA_ETHICS_PROTOCOL="Picard_Delta_3"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user (UID 1000)
# This matches the security context in Kubernetes deployment
RUN groupadd -r aurora -g 1000 && \
    useradd -r -u 1000 -g aurora -m -s /sbin/nologin aurora

# Create application directories
RUN mkdir -p /app /app/uploads /app/logs && \
    chown -R aurora:aurora /app

# Set working directory
WORKDIR /app

# Copy application code
# NOTE: .dockerignore should exclude .git, __pycache__, *.pyc, .env, etc.
COPY --chown=aurora:aurora . /app/

# Copy MCP Bridge Core configuration (default)
# This will be overridden by ConfigMap in Kubernetes
COPY --chown=aurora:aurora modules/symbolic_core/mcp_bridge_core.json /app/config/mcp_bridge_core.json

# Create empty __init__.py files if missing (for Python imports)
RUN find /app -type d -name "src" -o -name "modules" -o -name "tools" | \
    while read dir; do \
        [ ! -f "$dir/__init__.py" ] && touch "$dir/__init__.py" || true; \
    done

# Switch to non-root user
USER aurora

# Expose ports
# 8000: FastAPI application (HTTP)
# 8080: WebSocket connections (optional)
EXPOSE 8000 8080

# Health check
# This endpoint is validated by Kubernetes liveness/readiness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/mcp_bridge/health || exit 1

# Default command: Run uvicorn with 4 workers
# Can be overridden in Kubernetes deployment
CMD ["uvicorn", "aurora_gui_cloudhub_fastapi:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--access-log"]

# ==============================================================================
# Build Instructions:
# ==============================================================================
# Build the image:
#   docker build -t aurora-cloudbank-symbolic:v1.0.0 -f k8s/Dockerfile .
#
# Tag for registry:
#   docker tag aurora-cloudbank-symbolic:v1.0.0 your-registry.io/aurora-cloudbank-symbolic:v1.0.0
#
# Push to registry:
#   docker push your-registry.io/aurora-cloudbank-symbolic:v1.0.0
#
# Test locally:
#   docker run -p 8000:8000 aurora-cloudbank-symbolic:v1.0.0
#
# Verify health:
#   curl http://localhost:8000/mcp_bridge/health
#
# ==============================================================================
# Security Scanning:
# ==============================================================================
# Scan with Trivy:
#   trivy image aurora-cloudbank-symbolic:v1.0.0
#
# Scan with Grype:
#   grype aurora-cloudbank-symbolic:v1.0.0
#
# Scan with Docker Scout:
#   docker scout cves aurora-cloudbank-symbolic:v1.0.0
#
# ==============================================================================
# Multi-Platform Build:
# ==============================================================================
# Build for multiple platforms (ARM64, AMD64):
#   docker buildx build --platform linux/amd64,linux/arm64 \
#     -t your-registry.io/aurora-cloudbank-symbolic:v1.0.0 \
#     -f k8s/Dockerfile . --push
#
# ==============================================================================
# Aurora Metadata:
# ==============================================================================
# Chain Notation: #K8S//DOCKER//BUILD//COMPLETE//
# SRB: DOCKER_IMAGE_v1
# T1: 2025-10-31
# Ethics Protocol: Picard_Delta_3
# Module ID: AURORA_GUI_CLOUDHUB
# Governance: Aurora_Command_Node_CPU
# ==============================================================================
