import math

from src.sub_agents.xrd_agent.tools.load_xrd_data import load_xrd_data
from src.sub_agents.xrd_agent.tools.preprocess_xrd import preprocess_xrd
from src.sub_agents.xrd_agent.tools.find_and_fit_peaks import find_and_fit_peaks
from src.sub_agents.xrd_agent.tools.scherrer_williamson import scherrer_and_wh


def test_load_xrd_data_shapes(raw_payload: dict):
    theta = raw_payload["two_theta_deg"]
    intensity = raw_payload["intensity"]

    assert isinstance(theta, list) and isinstance(intensity, list)
    assert len(theta) == len(intensity) > 100
    # Ensure metadata captured
    assert "meta" in raw_payload and raw_payload["meta"]["path"].endswith("sample_xrd.csv")


def test_preprocess_outputs(processed_payload: dict):
    assert "intensity_smooth" in processed_payload
    assert "intensity_corr" in processed_payload
    assert len(processed_payload["intensity_smooth"]) == len(processed_payload["intensity"]) \
        == len(processed_payload["two_theta_deg"]) \
        == len(processed_payload["intensity_corr"]) 
    # Baseline correction should make min >= 0
    assert min(processed_payload["intensity_corr"]) >= 0


def test_find_and_fit_peaks_detects_prominent_peak(peaks_payload: dict):
    peaks = peaks_payload.get("peaks", [])
    assert isinstance(peaks, list)
    # Our sample has a strong synthetic peak around ~28.3 deg
    assert any(27.5 <= p["two_theta"] <= 29.0 for p in peaks), "Expected peak near 28.3° not found"

    for p in peaks:
        assert p["fwhm_deg"] > 0
        assert p["area"] > 0


def test_scherrer_outputs(peaks_payload: dict):
    enriched = scherrer_and_wh(peaks_payload)
    sch = enriched.get("scherrer", [])
    assert len(sch) >= 1
    # L_nm should be positive
    assert all(item["L_nm"] > 0 for item in sch)
    # WH fit present only if enough peaks; we accept None or dict
    wh = enriched.get("williamson_hall")
    assert (wh is None) or all(k in wh for k in ("slope_strain", "intercept_size", "r2"))
