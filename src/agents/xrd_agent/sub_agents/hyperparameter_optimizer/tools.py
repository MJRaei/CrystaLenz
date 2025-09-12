from typing import Dict, Any
import os
from src.data_store.data_store import XRD_DATA_STORE

def get_analysis_results(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns the current XRD_DATA_STORE content for analysis.
    Excludes raw diffraction arrays to keep the payload compact.
    """
    path = os.path.abspath(payload.get("path", ""))
    store = XRD_DATA_STORE[path]["loops"]
    if not store:
        return {"success": False, "message": f"No XRD data found for {path}"}

    results = {}
    for loop_idx, loop_data in store.items():
        # keep everything except intensity arrays
        results[loop_idx] = {
            k: v for k, v in loop_data.items()
            if k not in ("intensity_smooth", "intensity_corr")
        }

    return {
        "success": True,
        "path": path,
        "results": results,
        "message": "Retrieved XRD analysis results for hyperparameter optimization."
    }
