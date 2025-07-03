#!/usr/bin/env python3
"""Utilities for interacting with the CASK reference assets.

This module loads data from ``CASK_Assets.zip`` and provides helper
functions to parse the included CSV files as pandas ``DataFrame``
objects. It can also generate a simplified architecture chart for
quick visualization.
"""

from __future__ import annotations

import os
import zipfile

import pandas as pd

ASSET_ZIP = "CASK_Assets.zip"


def _open_asset(name: str) -> str:
    """Return the contents of ``name`` within ``ASSET_ZIP`` as a string."""
    if not os.path.exists(ASSET_ZIP):
        raise FileNotFoundError(f"{ASSET_ZIP} not found")
    with zipfile.ZipFile(ASSET_ZIP) as zf:
        with zf.open(name) as file:
            return file.read().decode("utf-8")


def load_specifications() -> pd.DataFrame:
    """Load the CASK technical specifications table."""
    data = _open_asset("cask_technical_specifications.csv")
    return pd.read_csv(StringIO(data))


def load_risk_assessment() -> pd.DataFrame:
    """Load the CASK risk assessment table."""
    data = _open_asset("cask_risk_assessment.csv")
    return pd.read_csv(StringIO(data))


def load_vs_sota() -> pd.DataFrame:
    """Load the comparison against state of the art table."""
    data = _open_asset("cask_vs_sota_comparison.csv")
    return pd.read_csv(StringIO(data))


def generate_architecture_chart(output: str = "cask_architecture.png") -> str:
    """Generate a simple architecture diagram and return the output path."""
    import plotly.graph_objects as go

    fig = go.Figure()
    colors = {
        "knowledge": "#1FB8CD",
        "processing": "#FFC185",
        "validation": "#5D878F",
    }
    components = [
        (1, 5, "Global DB", colors["knowledge"]),
        (3, 5, "Ethics Index", colors["knowledge"]),
        (5, 5, "Cultural Framework", colors["knowledge"]),
        (1, 3, "SVCC", colors["processing"]),
        (3, 3, "GPT Layer", colors["processing"]),
        (5, 3, "Agent Sim", colors["processing"]),
        (2, 1, "Ethics Validator", colors["validation"]),
        (4, 1, "ORION Runtime", colors["validation"]),
    ]
    for x, y, text, color in components:
        fig.add_shape(
            type="rect",
            x0=x - RECTANGLE_PADDING,
            y0=y - RECTANGLE_PADDING,
            x1=x + RECTANGLE_PADDING,
            y1=y + RECTANGLE_PADDING,
            fillcolor=color,
            line=dict(color="black", width=2),
        )
        fig.add_annotation(x=x, y=y, text=text, showarrow=False)

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        width=800,
        height=400,
        title="CASK Architecture (simplified)",
    )
    fig.write_image(output)
    return output
