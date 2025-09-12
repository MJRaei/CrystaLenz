import os
import re
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any
from google.adk.tools import ToolContext
from src.data_store.data_store import XRD_DATA_STORE

def plot_results(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Generate interactive + static plots with Plotly.
    """
    path = os.path.abspath(payload["path"])
    loop_iter = tool_context.state.get("loop_iteration", 1)
    base_store = XRD_DATA_STORE[path]
    store = base_store["loops"][loop_iter]
    if not store:
        return {"success": False, "message": f"No data found in XRD store for {path}"}

    theta = np.array(base_store["two_theta_deg"])
    raw = np.array(base_store["intensity"])
    smooth = np.array(store.get("intensity_smooth", raw))
    corr = np.array(store.get("intensity_corr", smooth))
    peaks = store.get("peaks", [])
    tmin, tmax = float(theta.min()), float(theta.max())
    peaks_in_range = [p for p in peaks if tmin <= float(p["two_theta"]) <= tmax]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=theta, y=raw, mode="lines", name="Raw"))
    fig.add_trace(go.Scatter(x=theta, y=smooth, mode="lines", name="Smoothed"))
    fig.add_trace(go.Scatter(x=theta, y=corr, mode="lines", name="Corrected"))
    if peaks_in_range:
        fig.add_trace(go.Scatter(
            x=[p["two_theta"] for p in peaks_in_range],
            y=[corr[np.argmin(np.abs(theta - p["two_theta"]))] for p in peaks_in_range],
            mode="markers", marker=dict(color="red", size=8, symbol="x"),
            name="Peaks"
        ))
    fig.update_layout(
        title=f"XRD Pattern - {store['meta'].get('sample_name','Sample')}",
        xaxis_title="2θ (°)",
        yaxis_title="Intensity (a.u.)",
        template="plotly_white"
    )

    outdir = os.path.join(os.getcwd(), "xrd_outputs")
    os.makedirs(outdir, exist_ok=True)
    base = store["meta"].get("sample_name", "sample")
    html_path = os.path.join(outdir, f"{base}_pattern_{loop_iter}.html")
    png_path = os.path.join(outdir, f"{base}_pattern_{loop_iter}.png")
    fig.write_html(html_path)
    fig.write_image(png_path, scale=2)

    loop_iter += 1
    tool_context.state["loop_iteration"] = loop_iter

    return {"success": True, "figures": [html_path, png_path], "message": f"Plots generated for loop {loop_iter}."}
