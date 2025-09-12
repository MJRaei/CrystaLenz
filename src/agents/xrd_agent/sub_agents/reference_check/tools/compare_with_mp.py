import math
import numpy as np
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext

from src.data_store.data_store import XRD_DATA_STORE
from src.agents.xrd_agent.sub_agents.reference_check.tools.fetch_mp_xrd import fetch_mp_xrd_lines


def _two_theta_to_d_angstrom(two_theta_deg: float, wavelength_angstrom: float) -> float:
    """Convert 2θ (deg) to d-spacing (Å) via Bragg’s law (n=1)."""
    theta_rad = math.radians(two_theta_deg / 2.0)
    s = math.sin(theta_rad)
    if s <= 0:
        return float("nan")
    return wavelength_angstrom / (2.0 * s)


def compare_with_mp(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Fetch MP reference lines and compare them to experimental peaks.
    Parameters chosen by agent or default:
      - mp_identifier (required),
      - mp_top_n (default=20),
      - mp_min_intensity (default=1.0).
    """
    try:
        path = payload["path"]
        if path not in XRD_DATA_STORE:
            return {"success": False, "path": path, "message": "No data found in store for given path."}

        loop_iter = tool_context.state.get("loop_iteration", 1)

        loop_data = XRD_DATA_STORE[path]["loops"][loop_iter]
        peaks: List[Dict[str, Any]] = loop_data.get("peaks", [])
        meta = loop_data["meta"]

        mp_identifier: Optional[str] = payload.get("mp_identifier") or meta.get("mp_identifier")
        if not mp_identifier:
            return {"success": True, "path": path, "sample_name": meta.get("sample_name"),
                    "message": "No mp_identifier provided, skipping reference check.",
                    "matches": [], "params": {}}

        two_theta_min = float(meta.get("two_theta_min", 5.0))
        two_theta_max = float(meta.get("two_theta_max", 90.0))
        mp_top_n = int(payload.get("mp_top_n", meta.get("mp_top_n", 20)))
        mp_min_intensity = float(payload.get("mp_min_intensity", meta.get("mp_min_intensity", 1.0)))
        lam = float(meta.get("wavelength_angstrom", 1.5406))

        ref = fetch_mp_xrd_lines(
            identifier=mp_identifier,
            wavelength_angstrom=lam,
            two_theta_min=two_theta_min,
            two_theta_max=two_theta_max,
            top_n=mp_top_n,
            min_intensity=mp_min_intensity,
        )

        if "_error" in ref:
            return {"success": False, "path": path, "sample_name": meta.get("sample_name"),
                    "message": ref["_error"]}

        if not peaks:
            return {"success": True, "path": path, "sample_name": meta.get("sample_name"),
                    "params": {"mp_identifier": mp_identifier,
                               "two_theta_range": [two_theta_min, two_theta_max],
                               "mp_top_n": mp_top_n,
                               "mp_min_intensity": mp_min_intensity},
                    "matches": [],
                    "message": "No experimental peaks to compare."}

        exp_d = []
        for p in peaks:
            tt = float(p["two_theta"])
            d = _two_theta_to_d_angstrom(tt, lam)
            if math.isfinite(d):
                exp_d.append({"two_theta": tt, "d_angstrom": d})

        ref_peaks: List[Dict[str, Any]] = ref.get("peaks", [])
        matches: List[Dict[str, Any]] = []
        matched_count = 0

        for rp in ref_peaks:
            d_ref = float(rp.get("d_angstrom"))
            tol = max(0.02, 0.005 * d_ref)
            best = None
            best_delta = None
            for ed in exp_d:
                delta = abs(ed["d_angstrom"] - d_ref)
                if delta <= tol and (best_delta is None or delta < best_delta):
                    best = ed
                    best_delta = delta
            if best is not None:
                matched_count += 1
                matches.append({
                    "ref_d": d_ref,
                    "ref_two_theta": float(rp.get("two_theta")),
                    "exp_two_theta": float(best["two_theta"]),
                    "exp_d": float(best["d_angstrom"]),
                    "delta_d": float(best_delta),
                    "tol_d": tol,
                    "ref_intensity": float(rp.get("intensity", 0.0)),
                    "hkls": rp.get("hkls"),
                })

        comp = {
            "material_id": ref.get("material_id"),
            "formula": ref.get("formula"),
            "wavelength_angstrom": ref.get("wavelength_angstrom"),
            "two_theta_range": [two_theta_min, two_theta_max],
            "total_ref_peaks": len(ref_peaks),
            "matched_count": matched_count,
            "matches": matches,
        }

        # Store in global store
        loop_data["mp_comparison"] = comp

        return {
            "success": True,
            "path": path,
            "sample_name": meta.get("sample_name"),
            "params": {"mp_identifier": mp_identifier,
                       "two_theta_range": [two_theta_min, two_theta_max],
                       "mp_top_n": mp_top_n,
                       "mp_min_intensity": mp_min_intensity},
            "matches": matches,
            "message": f"Reference check complete: {matched_count}/{len(ref_peaks)} matches found for loop {loop_iter}."
        }

    except Exception as e:
        return {"success": False, "path": payload.get("path"), "message": f"Failed: {str(e)}"}
