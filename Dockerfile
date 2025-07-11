# Aurora CloudBank Docker Container
FROM python:3.11-slim

LABEL maintainer="Aurora CloudBank Team"
LABEL version="3.5.1"
LABEL description="Quantum-Aware Symbolic Processing Framework"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Aurora CloudBank files
COPY aurora_*.py ./
COPY *.json ./
COPY *.html ./
COPY *.md ./

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/exports

# Set environment variables
ENV PYTHONPATH=/app
ENV AURORA_VERSION=3.5.1
ENV AURORA_PHASE=4

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "aurora_api_server.py"]
