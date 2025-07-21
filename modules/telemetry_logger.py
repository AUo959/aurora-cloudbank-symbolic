#!/usr/bin/env python3
"""
telemetry_logger.py

Simple telemetry logging system for Orion Constellation modules.

Summary:
    - Provides logging utilities for integration and backup scripts
    - Outputs logs to `logs/telemetry.log` for operator dashboard

Integration Notes:
    - Uses Python's `logging` module
    - Creates the log directory if missing

// ANCHOR: EOS_SEED_ORION
// ETHICS: Picard_Delta_3
"""

import logging
import os

TELEMETRY_LOG = "logs/telemetry.log"

def get_logger(name: str = "telemetry") -> logging.Logger:
    os.makedirs(os.path.dirname(TELEMETRY_LOG), exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(TELEMETRY_LOG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
