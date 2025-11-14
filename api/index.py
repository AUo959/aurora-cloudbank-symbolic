"""
Vercel Deployment Entrypoint for Aurora CloudBank Symbolic

This file serves as the Vercel-compatible entrypoint that imports the main FastAPI app.
Vercel expects to find 'app' exported from api/index.py or api/main.py
"""

from api.aurora_api import app

# Export the FastAPI app instance for Vercel
__all__ = ["app"]
