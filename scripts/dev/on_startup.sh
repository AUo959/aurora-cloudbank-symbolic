#!/bin/bash

echo "🚀 Aurora Devcontainer Onboarding Script"
echo "----------------------------------------"

# Basic toolchain check
echo "🔍 Verifying key tools..."
for cmd in node npm python3 git jq zip; do
  if command -v $cmd &>/dev/null; then
    echo "✅ $cmd: $(command -v $cmd)"
  else
    echo "❌ $cmd is missing!"
  fi
done

# Node & NPM
echo "📦 Node.js version: $(node -v)"
echo "📦 NPM version: $(npm -v)"

# Python
echo "🐍 Python version: $(python3 --version)"

# Optional: initialize symbolic metadata (mock placeholder)
echo "🌐 Initializing symbolic loom scaffold (placeholder)"
mkdir -p .aurora/loomfield
touch .aurora/loomfield/halo-anchor.json

# Optional: npm install, build or verify
echo "📦 Running npm install..."
npm install

bash .aurora/system/on_startup.sh && echo "🚀 Aurora Core Initialized"

echo "✅ Onboarding complete!"
