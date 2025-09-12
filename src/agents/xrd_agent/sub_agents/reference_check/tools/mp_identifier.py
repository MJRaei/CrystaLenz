from typing import Dict, Any, List
from google.adk.tools import ToolContext

from src.data_store.data_store import XRD_DATA_STORE
from src.agents.xrd_agent.sub_agents.reference_check.tools.fetch_mp_xrd import fetch_mp_xrd_lines


def mp_identifier(payload: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Resolves the most likely Materials Project identifier given either an mp-id
    or a chemical formula, by comparing simulated patterns to experimental data.
    """
    try:
        path = payload["path"]
        if path not in XRD_DATA_STORE:
            return {"success": False, "message": "No data found in store for given path."}

        loop_iter = tool_context.state.get("loop_iteration", 1)

        loop_data = XRD_DATA_STORE[path]["loops"][loop_iter]
        meta = loop_data["meta"]
        peaks = loop_data.get("peaks", [])

        # If mp_identifier already provided
        if "mp_identifier" in payload or "mp_identifier" in meta:
            chosen_id = payload.get("mp_identifier", meta.get("mp_identifier"))
            loop_data["mp_identifier"] = chosen_id
            return {
                "success": True,
                "chosen_material_id": chosen_id,
                "candidates": [],
                "message": "mp_identifier already provided."
            }

        # Otherwise, look for formula
        formula = payload.get("formula") or meta.get("formula") or meta.get("sample_name")
        if not formula:
            return {"success": False, "message": "No formula or mp_identifier provided."}

        two_theta_min = float(meta.get("two_theta_min", 5.0))
        two_theta_max = float(meta.get("two_theta_max", 90.0))
        lam = float(meta.get("wavelength_angstrom", 1.5406))

        # Fetch candidates from MP
        # NOTE: here we assume fetch_mp_xrd_lines can handle formula identifiers too
        try:
            from mp_api.client import MPRester as MPClient
            import os
            api_key = os.getenv("MP_API_KEY")
            with MPClient(api_key) as mpr:
                results = mpr.summary.search(
                    formula=formula,
                    fields=["material_id", "formula_pretty", "structure", "energy_above_hull"]
                )
            if not results:
                return {"success": False, "message": f"No MP entries found for formula '{formula}'."}
        except Exception as e:
            return {"success": False, "message": f"Failed to query MP: {e}"}

        candidates = []
        best_id = None
        best_score = -1.0
        print("Results:", results)
        for r in results:
            # simulate pattern
            ref = fetch_mp_xrd_lines(
                identifier=r.material_id,
                wavelength_angstrom=lam,
                two_theta_min=two_theta_min,
                two_theta_max=two_theta_max,
                top_n=20,
                min_intensity=1.0,
            )
            if "_error" in ref:
                continue

            score = 0.0
            if peaks:
                exp_tths = [pk["two_theta"] for pk in peaks]
                ref_tths = [rp["two_theta"] for rp in ref.get("peaks", [])]
                # crude score: fraction of exp peaks that have a nearby ref peak
                matches = sum(any(abs(et - rt) < 0.3 for rt in ref_tths) for et in exp_tths)
                score = matches / max(1, len(exp_tths))

            candidates.append({
                "material_id": r.material_id,
                "formula": r.formula_pretty,
                "confidence": float(score),
            })
            if score > best_score:
                best_id = r.material_id
                best_score = score

        # persist in loop_data
        loop_data["mp_identifier"] = best_id
        loop_data["mp_candidates"] = candidates

        return {
            "success": True,
            "chosen_material_id": best_id,
            "candidates": candidates,
            "message": f"Selected {best_id} with confidence {best_score:.2f}"
        }

    except Exception as e:
        return {"success": False, "message": f"Failed: {str(e)}"}
