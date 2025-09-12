import os
from typing import Any, Dict, List, Optional

import dotenv

dotenv.load_dotenv()


def fetch_mp_xrd_lines(
    identifier: str,
    api_key: Optional[str] = None,
    wavelength_angstrom: float = 1.5406,      # Cu Kα
    two_theta_min: float = 5.0,
    two_theta_max: float = 90.0,
    top_n: int = 20,
    min_intensity: float = 1.0,               # relative intensity threshold (0-100)
) -> Dict[str, Any]:
    """
    Fetch a structure from Materials Project (by material_id or formula),
    simulate its powder XRD pattern with pymatgen, and return top-N peaks.

    Returns a dict with keys: material_id, formula, wavelength_angstrom,
    two_theta_range, and peaks (list of dicts with two_theta, d_angstrom,
    intensity (relative %), hkls).
    """
    api_key = api_key or os.getenv("MP_API_KEY")
    if not api_key:
        return {"_error": "Missing Materials Project API key. Set MP_API_KEY or pass api_key=."}

    # --- 1) Get a pymatgen Structure from MP ---
    structure = None
    material_id: Optional[str] = None
    formula_pretty: Optional[str] = None

    # Prefer mp-api if present (new API)
    try:
        from mp_api.client import MPRester as MPClient  # type: ignore
        with MPClient(api_key) as mpr:
            if identifier.lower().startswith(("mp-", "mvc-", "mat-")):
                material_id = identifier
                try:
                    s = mpr.get_structure_by_material_id(material_id)
                except Exception as e:
                    return {"_error": f"Failed to fetch structure for {material_id}: {e}"}
                structure = s
                try:
                    sm = mpr.summary.get_data_by_id(material_id)
                    if sm:
                        formula_pretty = getattr(sm[0], "formula_pretty", None)
                except Exception:
                    pass
            else:
                results = mpr.summary.search(
                    formula=identifier,
                    fields=["material_id", "formula_pretty", "energy_above_hull", "structure"],
                )
                if not results:
                    return {"_error": f"No MP entries found for formula '{identifier}'."}
                results.sort(key=lambda r: (getattr(r, "energy_above_hull", float("inf")) or float("inf")))
                best = results[0]
                structure = best.structure
                material_id = best.material_id
                formula_pretty = best.formula_pretty
    except Exception:
        # Fallback to legacy pymatgen client
        try:
            from pymatgen.ext.matproj import MPRester  # type: ignore
        except Exception as e:
            return {"_error": f"Cannot import Materials Project client: {e}"}

        with MPRester(api_key) as mpr:
            if identifier.lower().startswith("mp-"):
                material_id = identifier
                try:
                    structure = mpr.get_structure_by_material_id(material_id)
                except Exception as e:
                    return {"_error": f"Failed to fetch structure for {material_id}: {e}"}
                try:
                    doc = mpr.query(material_id=[material_id], properties=["pretty_formula"])
                    if doc:
                        formula_pretty = doc[0].get("pretty_formula")
                except Exception:
                    pass
            else:
                structs = mpr.get_structures(identifier)
                if not structs:
                    return {"_error": f"No structures found for formula '{identifier}'."}
                structure = structs[0]
                try:
                    q = mpr.query(criteria={"formula_pretty": identifier}, properties=["material_id"])
                    material_id = q[0]["material_id"] if q else None
                    formula_pretty = identifier
                except Exception:
                    formula_pretty = identifier

    if structure is None:
        return {"_error": f"Could not obtain a structure for identifier '{identifier}'."}

    # --- 2) Simulate XRD pattern with pymatgen ---
    try:
        from pymatgen.analysis.diffraction.xrd import XRDCalculator  # type: ignore
    except Exception as e:
        return {"_error": f"pymatgen not available or XRDCalculator import failed: {e}"}

    try:
        calc = XRDCalculator(wavelength=wavelength_angstrom)
        patt = calc.get_pattern(structure, two_theta_range=(two_theta_min, two_theta_max))
        rows: List[Dict[str, Any]] = []
        for tth, inten, hkls in zip(patt.x, patt.y, patt.hkls):
            if inten < min_intensity:
                continue
            # Compute d-spacing from 2θ (degrees) using Bragg's law (n=1)
            theta_rad = (tth / 2.0) * 3.141592653589793 / 180.0
            s = __import__("math").sin(theta_rad)
            d = float("nan") if s <= 0 else float(wavelength_angstrom / (2.0 * s))
            hkls_fmt: List[Dict[str, Any]] = []
            try:
                for item in hkls:
                    if isinstance(item, dict) and "hkl" in item:
                        h, k, l = item["hkl"]
                        hkls_fmt.append({"hkl": [int(h), int(k), int(l)], "multiplicity": int(item.get("multiplicity", 1))})
                    else:
                        h, k, l = item
                        hkls_fmt.append({"hkl": [int(h), int(k), int(l)], "multiplicity": None})
            except Exception:
                hkls_fmt = []
            rows.append({
                "two_theta": float(tth),
                "d_angstrom": float(d),
                "intensity": float(inten),
                "hkls": hkls_fmt,
            })

        rows.sort(key=lambda r: r["intensity"], reverse=True)
        if top_n and len(rows) > top_n:
            rows = rows[:top_n]

        return {
            "material_id": material_id,
            "formula": formula_pretty,
            "wavelength_angstrom": float(wavelength_angstrom),
            "two_theta_range": [float(two_theta_min), float(two_theta_max)],
            "peaks": rows,
        }
    except Exception as e:
        return {"_error": f"Failed to generate XRD pattern: {e}"}


# if __name__ == "__main__":
#     api_key = os.getenv("MP_API_KEY")
#     identifier = "V2O5"
#     import time
#     st = time.time()
#     res = fetch_mp_xrd_lines(identifier=identifier, api_key=api_key, wavelength_angstrom=1.5406, two_theta_min=5.0, two_theta_max=90.0, top_n=20, min_intensity=1.0)
#     et = time.time()
#     print(f"Time taken: {et - st} seconds")
#     print(res)
    