from typing import Dict, Any
import pandas as pd
import numpy as np
from google.adk.tools import ToolContext

from src.data_store.data_store import XRD_DATA_STORE

def inspect_xrd_file(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quickly inspects an XRD-like file and returns column metadata
    to help decide which columns are two_theta and intensity.

    Expected input:
      - path (str): file path to CSV/XLSX/TXT

    Output:
      {
        "columns": [
            {
                "name": str,
                "dtype": str,
                "min": float,
                "max": float,
                "mean": float,
                "example_values": list[float|str],
            }, ...
        ],
        "num_rows": int
      }
    """
    print("Payload:", payload)
    path = payload["path"].lower()
    if path.endswith(".xlsx") or path.endswith(".xls"):
        df = pd.read_excel(payload["path"])
    elif path.endswith(".csv"):
        df = pd.read_csv(payload["path"])
    else:
        df = pd.read_csv(payload["path"], sep=None, engine="python")

    cols_meta = []
    for col in df.columns:
        series = df[col].dropna()
        # Try numeric
        if pd.api.types.is_numeric_dtype(series):
            vals = series.astype(float)
            col_info = {
                "name": col,
                "dtype": "numeric",
                "min": float(vals.min()),
                "max": float(vals.max()),
                "mean": float(vals.mean()),
                "example_values": vals.head(5).round(4).tolist(),
            }
        else:
            col_info = {
                "name": col,
                "dtype": "string",
                "min": None,
                "max": None,
                "mean": None,
                "example_values": series.astype(str).head(5).tolist(),
            }
        cols_meta.append(col_info)

    return {
        "columns": cols_meta,
        "num_rows": len(df),
    }


def load_xrd_data(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Loads XRD data and stores it in a global store.
    Returns only metadata and success status.
    """
    try:
        path = payload["path"].lower()
        if path.endswith(".xlsx") or path.endswith(".xls"):
            df = pd.read_excel(payload["path"])
        elif path.endswith(".csv"):
            df = pd.read_csv(payload["path"])
        else:
            df = pd.read_csv(payload["path"], sep=None, engine="python")

        current_loop = 1
        tool_context.state["loop_iteration"] = current_loop

        theta = df[payload["two_theta_col"]].to_numpy(dtype=float)
        if payload["unit_two_theta"] == "rad":
            theta = np.degrees(theta)

        I = df[payload["intensity_col"]].to_numpy(dtype=float)

        two_theta_min = float(theta.min()) if len(theta) > 0 else None
        two_theta_max = float(theta.max()) if len(theta) > 0 else None

        # store in central location
        XRD_DATA_STORE[payload["path"]] = {
            "two_theta_deg": theta,
            "intensity": I,
            "meta": {
                "path": payload["path"],
                "two_theta_col": payload["two_theta_col"],
                "intensity_col": payload["intensity_col"],
                "unit_two_theta": payload["unit_two_theta"],
                "sample_name": payload.get("sample_name"),
                "two_theta_min": two_theta_min,
                "two_theta_max": two_theta_max,
            },
        }

        return {
            "success": True,
            "path": payload["path"],
            "two_theta_col": payload["two_theta_col"],
            "intensity_col": payload["intensity_col"],
            "unit_two_theta": payload["unit_two_theta"],
            "sample_name": payload.get("sample_name"),
            "two_theta_min": two_theta_min,
            "two_theta_max": two_theta_max,
            "message": "XRD data successfully loaded and stored.",
        }

    except Exception as e:
        return {
            "success": False,
            "path": payload.get("path"),
            "two_theta_col": payload.get("two_theta_col"),
            "intensity_col": payload.get("intensity_col"),
            "unit_two_theta": payload.get("unit_two_theta"),
            "sample_name": payload.get("sample_name"),
            "message": f"Failed to load XRD data: {str(e)}",
        }
