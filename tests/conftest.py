import os
from pathlib import Path
import pytest

from src.sub_agents.xrd_agent.tools.load_xrd_data import load_xrd_data
from src.sub_agents.xrd_agent.tools.preprocess_xrd import preprocess_xrd
from src.sub_agents.xrd_agent.tools.find_and_fit_peaks import find_and_fit_peaks


@pytest.fixture(scope="session")
def sample_path() -> str:
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "sample_data" / "sample_xrd.csv"
    assert csv_path.exists(), f"Sample file not found: {csv_path}"
    # Return absolute path as str
    return str(csv_path)


@pytest.fixture(scope="session")
def raw_payload(sample_path: str) -> dict:
    cfg = {
        "path": sample_path,
        "two_theta_col": "two_theta",
        "intensity_col": "intensity",
        "wavelength_angstrom": 1.5406,
        "unit_two_theta": "deg",
        "smoothing_window": 11,
        "smoothing_polyorder": 3,
        "peak_min_prominence": 0.01,
        "peak_min_distance_pts": 5,
        "peak_min_height_rel": 0.01,
        "assumed_symmetry": None,
        "sample_name": "sample_xrd",
    }
    return load_xrd_data(cfg)


@pytest.fixture(scope="session")
def processed_payload(raw_payload: dict) -> dict:
    return preprocess_xrd(raw_payload)


@pytest.fixture(scope="session")
def peaks_payload(processed_payload: dict) -> dict:
    return find_and_fit_peaks(processed_payload)
