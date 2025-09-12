import numpy as np
from google.adk.tools import ToolContext

from src.data_store.data_store import XRD_DATA_STORE

def scherrer_and_wh(payload: dict, tool_context: ToolContext) -> dict:
    """
    Scherrer crystallite size + Williamson-Hall strain/size analysis.
    Uses stored peaks and metadata.
    """
    try:
        path = payload["path"]
        if path not in XRD_DATA_STORE:
            return {"success": False, "path": path, "message": "No data found in store for given path."}

        loop_iter = tool_context.state.get("loop_iteration", 1)
        loop_data = XRD_DATA_STORE[path]["loops"][loop_iter]

        peaks = loop_data.get("peaks", [])
        meta = loop_data["meta"]

        lam = meta.get("wavelength_angstrom", 1.5406) * 1e-10  # convert Å → m
        beta_inst_deg = meta.get("instrument_fwhm_deg")

        sch = []
        X, Y = [], []

        for pk in peaks:
            tt = np.radians(pk["two_theta"])
            theta = tt / 2.0
            beta_fit_deg = float(pk["fwhm_deg"])
            # Correct for instrumental broadening
            if beta_inst_deg is not None and beta_inst_deg > 0:
                beta_corr_deg = max(1e-6, (beta_fit_deg**2 - beta_inst_deg**2)**0.5)
            else:
                beta_corr_deg = beta_fit_deg

            beta = np.radians(beta_corr_deg)
            if beta <= 0 or not np.isfinite(beta):
                continue
            ctheta = np.cos(theta)
            if ctheta <= 0 or not np.isfinite(ctheta):
                continue

            # Scherrer (K=0.9)
            L = 0.9 * lam / (beta * ctheta)
            if L <= 0 or not np.isfinite(L):
                continue

            sch.append({
                "two_theta": pk["two_theta"],
                "L_nm": float(L * 1e9),
                "beta_deg": pk["fwhm_deg"]
            })

            # Williamson–Hall
            X.append(4 * np.sin(theta) / lam)
            Y.append(beta * ctheta)

        wh = None
        wh_diag = None
        if len(X) >= 4:
            X = np.array(X)
            Y = np.array(Y)
            A = np.vstack([X, np.ones_like(X)]).T
            m, c = np.linalg.lstsq(A, Y, rcond=None)[0]
            yhat = A.dot([m, c])
            r2 = 1 - ((Y - yhat)**2).sum() / ((Y - Y.mean())**2).sum()
            if r2 >= 0.9:
                wh = {
                    "slope_strain": float(m),
                    "intercept_size": float(c),
                    "r2": float(r2)
                }
            else:
                wh_diag = {"n_points": int(len(X)), "r2": float(r2), "reason": "R2_below_threshold"}
        else:
            wh_diag = {"n_points": int(len(X)), "reason": "insufficient_points"}

        # store results
        loop_data.update({
            "scherrer": sch,
            "williamson_hall": wh,
            "williamson_hall_diagnostics": wh_diag
        })

        return {
            "success": True,
            "path": path,
            "sample_name": meta.get("sample_name"),
            "params": {
                "wavelength_angstrom": meta.get("wavelength_angstrom", 1.5406),
                "instrument_fwhm_deg": beta_inst_deg,
            },
            "scherrer": sch,
            "williamson_hall": wh,
            "williamson_hall_diagnostics": wh_diag,
            "message": f"Scherrer and Williamson-Hall analysis complete for loop {loop_iter}."
        }

    except Exception as e:
        return {"success": False, "path": payload.get("path"), "message": f"Failed: {str(e)}"}
