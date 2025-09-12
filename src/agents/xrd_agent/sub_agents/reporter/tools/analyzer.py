import os
import numpy as np
import json
from typing import Dict, Any
from google.adk.tools import ToolContext
from src.data_store.data_store import XRD_DATA_STORE

def get_results(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieve results (excluding raw/smooth/corrected arrays).
    """
    path = os.path.abspath(payload["path"])
    loop_iter = tool_context.state.get("loop_iteration", 1)
    store = XRD_DATA_STORE[path]["loops"][loop_iter]
    if not store:
        return {"success": False, "message": f"No data found in XRD store for {path}"}

    return {
        "success": True,
        "path": path,
        "meta": store.get("meta", {}),
        "peaks": store.get("peaks", []),
        "scherrer": store.get("scherrer", []),
        "williamson_hall": store.get("williamson_hall"),
        "williamson_hall_diagnostics": store.get("williamson_hall_diagnostics"),
        "mp_comparison": store.get("mp_comparison"),
        "lattice_params": store.get("lattice_params"),
        "analysis": store.get("analysis"),
        "message": "Results retrieved successfully."
    }


def save_analysis(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Save agent-generated analysis into XRD_DATA_STORE.
    """
    path = os.path.abspath(payload["path"])
    loop_iter = tool_context.state.get("loop_iteration", 1)
    store = XRD_DATA_STORE[path]["loops"][loop_iter]
    if not store:
        return {"success": False, "message": f"No data found in XRD store for {path}"}

    analysis = payload.get("analysis")
    if not analysis:
        return {"success": False, "message": "No analysis text provided."}

    store["analysis"] = analysis
    return {
        "success": True,
        "path": path,
        "analysis": analysis,
        "message": f"Analysis saved to XRD data store for loop {loop_iter}."
    }

def save_results(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Save the entire XRD data store for this path into a JSON file.
    """
    path = os.path.abspath(payload["path"])
    loop_iter = tool_context.state.get("loop_iteration", 1)
    store = XRD_DATA_STORE[path]["loops"][loop_iter]
    if not store:
        return {"success": False, "message": f"No data found in XRD store for {path}"}

    outdir = os.path.join(os.getcwd(), "xrd_outputs")
    os.makedirs(outdir, exist_ok=True)
    base = store["meta"].get("sample_name", "sample")
    jpath = os.path.join(outdir, f"{base}_report_{loop_iter}.json")

    clean_store = _safe_convert(store)

    with open(jpath, "w") as f:
        json.dump(clean_store, f, indent=2, default=str)

    return {"success": True, "json_path": jpath, "message": f"Results saved to JSON for loop {loop_iter}."}

def _safe_convert(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _safe_convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe_convert(v) for v in obj]
    return obj