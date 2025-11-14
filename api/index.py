"""
Vercel Deployment Entrypoint for Aurora CloudBank Symbolic

This file serves as the Vercel-compatible entrypoint that imports the main FastAPI app.
Vercel expects to find 'app' exported from api/index.py or api/main.py

IMPORTANT: Environment variables must be configured in Vercel before deployment.
The app initialization will fail gracefully if required secrets are missing.
"""

import os
import sys

# Ensure the project root is in the Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set default environment variables for build phase if not present
# These will be overridden by actual Vercel environment variables at runtime
if not os.getenv("CSRF_SECRET_KEY"):
    os.environ["CSRF_SECRET_KEY"] = "BUILD_PHASE_PLACEHOLDER_" + "0" * 48  # 64 chars
if not os.getenv("AURORA_SECRET_KEY"):
    os.environ["AURORA_SECRET_KEY"] = "BUILD_PHASE_PLACEHOLDER_" + "0" * 48
if not os.getenv("WS_AUTH_SECRET"):
    os.environ["WS_AUTH_SECRET"] = "BUILD_PHASE_PLACEHOLDER_" + "0" * 48
if not os.getenv("AES_KEY_256_HEX"):
    os.environ["AES_KEY_256_HEX"] = "BUILD_PHASE_PLACEHOLDER_" + "0" * 48

# Now import the app (will use placeholders during build, real values at runtime)
# Import directly from aurora_api since Vercel runs from the api/ directory context
from aurora_api import app

# Export the FastAPI app instance for Vercel
__all__ = ["app"]
