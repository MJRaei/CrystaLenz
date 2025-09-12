from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional


# Convenient declaration for controlled generation.
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json"
)

class DataInjesterOutput(BaseModel):
    """Schema for the ingestion agent deciding columns and unit."""
    two_theta_col: str = Field(description="Name of the column for 2θ values")
    intensity_col: str = Field(description="Name of the column for intensity values")
    unit_two_theta: str = Field(description="Unit of the 2θ column, either 'deg' or 'rad'")

class DataLoaderOutput(BaseModel):
    """Schema for confirming that XRD data was successfully loaded and stored."""
    success: bool = Field(description="Whether the data was successfully loaded and stored.")
    path: str = Field(description="Path of the file that was ingested.")
    two_theta_col: str = Field(description="Column name for 2θ values used.")
    intensity_col: str = Field(description="Column name for intensity values used.")
    unit_two_theta: str = Field(description="Unit of the 2θ values ('deg' or 'rad').")
    sample_name: Optional[str] = Field(default=None, description="Optional identifier for the sample.")
    message: Optional[str] = Field(default=None, description="Additional info about the operation.")

class DataPreprocessorOutput(BaseModel):
    """Schema for confirming preprocessing results."""
    success: bool = Field(description="Whether preprocessing was successful.")
    path: str = Field(description="Path of the dataset that was preprocessed.")
    sample_name: Optional[str] = Field(default=None, description="Optional name/identifier of the sample.")
    message: Optional[str] = Field(default=None, description="Additional info or error message.")

class Peak(BaseModel):
    two_theta: float = Field(description="Fitted peak center in degrees.")
    intensity: float = Field(description="Peak intensity from Voigt fit.")
    fwhm_deg: float = Field(description="Full Width at Half Maximum in degrees.")
    area: float = Field(description="Area under the fitted peak curve.")
    model: str = Field(description="Model used for fitting (e.g. 'voigt').")

class PeakFinderOutput(BaseModel):
    success: bool = Field(description="Whether peak finding and fitting succeeded.")
    path: str = Field(description="Path of the dataset processed.")
    sample_name: Optional[str] = Field(default=None, description="Optional name/identifier of the sample.")
    params: dict = Field(description="Parameters used for peak detection/fitting.")
    peaks: List[Peak] = Field(description="List of fitted peaks with parameters.")
    message: Optional[str] = Field(default=None, description="Additional information about the process.")

class ScherrerResult(BaseModel):
    two_theta: float = Field(description="Peak center in degrees (2θ).")
    L_nm: float = Field(description="Crystallite size from Scherrer equation in nanometers.")
    beta_deg: float = Field(description="FWHM of the peak in degrees used for calculation.")

class WHResult(BaseModel):
    slope_strain: float = Field(description="Microstrain from Williamson-Hall (slope).")
    intercept_size: float = Field(description="Intercept (K/L term) from Williamson-Hall.")
    r2: float = Field(description="Coefficient of determination for the linear fit.")

class ScherrerAndWHOutput(BaseModel):
    success: bool = Field(description="Whether the calculation succeeded.")
    path: str = Field(description="Path of the dataset processed.")
    sample_name: Optional[str] = Field(default=None, description="Optional name/identifier of the sample.")
    params: dict = Field(description="Parameters used for calculations (e.g., wavelength, instrument FWHM).")
    scherrer: List[ScherrerResult] = Field(description="List of Scherrer results per peak.")
    williamson_hall: Optional[WHResult] = Field(default=None, description="Williamson-Hall results if reliable.")
    williamson_hall_diagnostics: Optional[dict] = Field(default=None, description="Diagnostics if WH fit fails.")
    message: Optional[str] = Field(default=None, description="Additional info about the process.")


class MPIdentifierCandidate(BaseModel):
    material_id: str = Field(description="Candidate MP material id.")
    formula: Optional[str] = Field(default=None, description="Chemical formula of the candidate.")
    confidence: float = Field(description="Confidence (0-1) that this candidate matches the data.")

class MPIdentifierOutput(BaseModel):
    success: bool = Field(description="Whether identifier resolution succeeded.")
    chosen_material_id: Optional[str] = Field(default=None, description="Selected mp-id.")
    candidates: List[MPIdentifierCandidate] = Field(default_factory=list, description="List of evaluated candidates.")
    message: Optional[str] = Field(default=None, description="Info or error message.")


class ReferenceMatch(BaseModel):
    ref_d: float = Field(description="Reference d-spacing in Å.")
    ref_two_theta: float = Field(description="Reference peak position (2θ, deg).")
    exp_two_theta: float = Field(description="Experimental peak position (2θ, deg).")
    exp_d: float = Field(description="Experimental d-spacing in Å.")
    delta_d: float = Field(description="Difference between experimental and reference d-spacing (Å).")
    tol_d: float = Field(description="Tolerance used for matching in Å.")
    ref_intensity: float = Field(description="Relative intensity of the reference peak (%).")
    hkls: Optional[List[dict]] = Field(default=None, description="Miller indices for the reference peak.")

class ReferenceCheckOutput(BaseModel):
    success: bool = Field(description="Whether the reference check succeeded.")
    path: str = Field(description="Path of the dataset processed.")
    sample_name: Optional[str] = Field(default=None, description="Optional sample identifier.")
    mp_identifier: Optional[str] = Field(default=None, description="Materials project identifier.")
    params: dict = Field(description="Parameters used for the comparison (identifier, range, top_n, intensity threshold).")
    matches: List[ReferenceMatch] = Field(description="List of matched peaks.")
    message: Optional[str] = Field(default=None, description="Additional info about the process.")

class AnalyzerOutput(BaseModel):
    success: bool = Field(..., description="Whether the analysis succeeded")
    path: str = Field(..., description="File path of the analyzed XRD dataset")
    analysis: str = Field(..., description="Detailed analysis text generated by the analyzer agent")
    message: str = Field(..., description="Diagnostic or explanatory message about the analysis process")


class ReporterOutput(BaseModel):
    success: bool = Field(..., description="Whether report generation was successful")
    path: str = Field(..., description="File path of the XRD dataset")
    sample_name: Optional[str] = Field(None, description="Sample name if available from metadata")
    figures: List[str] = Field(default_factory=list, description="Paths to generated plots (PNG, HTML, etc.)")
    report_path: Optional[str] = Field(None, description="Path to the saved JSON report")
    message: str = Field(..., description="Status or diagnostic message about the report generation")

class HyperparameterOptimizerOutput(BaseModel):
    success: bool = Field(..., description="Whether hyperparameter optimization succeeded")
    path: str = Field(..., description="Path of the dataset being optimized")
    loop_iteration: int = Field(..., description="Current iteration number in the optimization loop")
    smoothing_window: int = Field(..., description="Window size for Savitzky-Golay smoothing")
    smoothing_polyorder: int = Field(..., description="Polynomial order for Savitzky-Golay smoothing")
    baseline_lambda: float = Field(..., description="Lambda parameter for ALS baseline correction")
    baseline_p: float = Field(..., description="Asymmetry parameter for ALS baseline correction")
    peak_min_prominence: float = Field(..., description="Minimum prominence for peak detection")
    peak_min_distance_pts: int = Field(..., description="Minimum distance between detected peaks (points)")
    peak_min_height_rel: float = Field(..., description="Relative minimum height (0-1) for peak detection")
    fit_window_deg: float = Field(..., description="Fitting window width around each peak (degrees)")
    message: str = Field(..., description="Explanation of how and why these parameters were chosen")
