import numpy as np
from scipy.signal import find_peaks
import lmfit
from lmfit.lineshapes import voigt
from google.adk.tools import ToolContext

from src.data_store.data_store import XRD_DATA_STORE

def _voigt(x, amp, center, sigma, gamma, offset):
    return amp * voigt(x - center, sigma, gamma) + offset

def find_and_fit_peaks(payload: dict, tool_context: ToolContext) -> dict:
    """
    Finds and fits peaks in preprocessed XRD data using Voigt profiles.
    Expects payload to include:
      - path
      - peak_min_prominence (float)
      - peak_min_distance_pts (int)
      - peak_min_height_rel (float)
      - fit_window_deg (float)
    """
    try:
        path = payload["path"]
        if path not in XRD_DATA_STORE:
            return {"success": False, "path": path, "message": "No data found in store for given path."}

        loop_iter = tool_context.state.get("loop_iteration", 1)

        stored = XRD_DATA_STORE[path]
        loop_data = stored.get("loops", {}).get(loop_iter)
        if not loop_data:
            return {
                "success": False,
                "path": path,
                "message": f"No preprocessed data found for loop {loop_iter}."
            }
        
        theta = np.array(stored["two_theta_deg"])
        I = np.array(loop_data.get("intensity_corr"))
        meta = loop_data.get("meta", {})

        # Parameters (payload > meta > defaults)
        prom = float(payload.get("peak_min_prominence", meta.get("peak_min_prominence", 0.1)))
        dist = int(payload.get("peak_min_distance_pts", meta.get("peak_min_distance_pts", 25)))
        h_rel = float(payload.get("peak_min_height_rel", meta.get("peak_min_height_rel", 0.15)))
        fit_win = float(payload.get("fit_window_deg", meta.get("fit_window_deg", 0.8)))

        # height threshold
        h = h_rel * (I.max() if np.ptp(I) > 0 else 1.0)
        peaks, _ = find_peaks(I, height=h, distance=dist, prominence=prom)

        results = []
        for p in peaks:
            theta_p = float(theta[p])
            halfwin = fit_win / 2.0
            mask = np.abs(theta - theta_p) <= halfwin
            if not np.any(mask):
                left = max(0, p - 10); right = min(len(theta) - 1, p + 10)
                x = theta[left:right+1]; y = I[left:right+1]
            else:
                x = theta[mask]; y = I[mask]

            model = lmfit.Model(_voigt)
            center0 = float(x[np.argmax(y)])
            height0 = float(y.max() - np.median(y))
            params = model.make_params(
                amp=max(height0, 1.0),
                center=center0,
                sigma=0.05,
                gamma=0.05,
                offset=float(np.percentile(y, 5.0))
            )

            # bounds
            x_min, x_max = float(x.min()), float(x.max())
            window_width = max(1e-3, x_max - x_min)
            params["center"].min = max(x_min, center0 - 0.12)
            params["center"].max = min(x_max, center0 + 0.12)
            params["sigma"].min, params["sigma"].max = 0.01, min(window_width, 0.20)
            params["gamma"].min, params["gamma"].max = 0.01, min(window_width, 0.20)
            params["amp"].min, params["amp"].max = 0, max(1.0, float(y.max()) * 10.0)
            params["offset"].min = 0

            out = model.fit(y, params, x=x)

            # calculate FWHM (Olivero–Longbothum)
            sigma = out.best_values["sigma"]
            gamma = out.best_values["gamma"]
            fwhm_val = 0.5346 * (2*gamma) + np.sqrt(0.2166*(2*gamma)**2 + (2.3548*sigma)**2)

            area = np.trapz(out.best_fit, x)

            results.append({
                "two_theta": float(out.best_values["center"]),
                "intensity": float(out.best_values["amp"]),
                "fwhm_deg": float(fwhm_val),
                "area": float(area),
                "model": "voigt"
            })

        # update store
        loop_data.update({
            "peaks": results,
            "meta": {
                **meta,
                "peak_min_prominence": prom,
                "peak_min_distance_pts": dist,
                "peak_min_height_rel": h_rel,
                "fit_window_deg": fit_win
            }
        })

        return {
            "success": True,
            "path": path,
            "sample_name": meta.get("sample_name"),
            "params": {
                "peak_min_prominence": prom,
                "peak_min_distance_pts": dist,
                "peak_min_height_rel": h_rel,
                "fit_window_deg": fit_win
            },
            "peaks": results,
            "message": f"Found and fitted {len(results)} peaks in loop {loop_iter}."
        }

    except Exception as e:
        return {"success": False, "path": payload.get("path"), "message": f"Failed: {str(e)}"}
