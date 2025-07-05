#!/bin/bash
# Setup script for Aurora Reflective Autonomy System
echo "Setting up environment..."
pip install -r requirements.txt || exit 1
mkdir -p logs data
cp .env.example .env 2>/dev/null || true
echo "Setup complete."
