FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .

# Install Aurora package
RUN pip install -e .

# Create Aurora user
RUN useradd -m aurora
USER aurora

# Set environment
ENV PYTHONPATH=/app/src
ENV AURORA_SYSTEM=symbolic-vault

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD python -c "from aurora.core.symbolic_engine import SymbolicEngine; print('Aurora ready')" || exit 1

CMD ["python", "-c", "from aurora.core.symbolic_engine import SymbolicEngine; engine = SymbolicEngine(); print('🔮 Aurora Cloudbank Symbolic ready')"]
