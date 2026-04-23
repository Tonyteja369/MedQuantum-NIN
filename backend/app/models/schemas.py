from datetime import datetime, timezone
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class LeadData(BaseModel):
    name: str
    signal: list[float]
    unit: str = "mV"


class QualityMetrics(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    noise_level: Literal["low", "medium", "high"]
    baseline_wander: bool
    signal_loss: bool
    details: list[str] = []
    snr_db: Optional[float] = None
    clipping_ratio: Optional[float] = None
    flatline_ratio: Optional[float] = None
    noise_variance: Optional[float] = None
    baseline_wander_power: Optional[float] = None
    non_finite_ratio: Optional[float] = None


class ECGSignal(BaseModel):
    id: str
    filename: str
    sampling_rate: int
    duration: float
    leads: list[LeadData]
    uploaded_at: datetime
    quality: QualityMetrics


class ECGFeatures(BaseModel):
    heart_rate: float
    rr_intervals: list[float]
    pr_interval: Optional[float] = None
    qrs_duration: Optional[float] = None
    qt_interval: Optional[float] = None
    qtc_interval: Optional[float] = None
    rr_mean: float
    rr_std: float
    hr_variability: float
    rr_min: Optional[float] = None
    rr_max: Optional[float] = None
    rr_median: Optional[float] = None
    rr_iqr: Optional[float] = None
    rr_rmssd: Optional[float] = None
    rr_sdsd: Optional[float] = None
    rr_pnn20: Optional[float] = None
    rr_pnn50: Optional[float] = None
    heart_rate_min: Optional[float] = None
    heart_rate_max: Optional[float] = None
    heart_rate_std: Optional[float] = None
    hrv_sdnn: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    hrv_sdsd: Optional[float] = None
    hrv_cvsd: Optional[float] = None
    hrv_cvnn: Optional[float] = None
    hrv_triangular_index: Optional[float] = None
    hrv_tinn: Optional[float] = None
    freq_vlf_power: Optional[float] = None
    freq_lf_power: Optional[float] = None
    freq_hf_power: Optional[float] = None
    freq_total_power: Optional[float] = None
    freq_lf_hf_ratio: Optional[float] = None
    freq_peak_hz: Optional[float] = None
    p_wave_amp: Optional[float] = None
    q_wave_amp: Optional[float] = None
    r_wave_amp: Optional[float] = None
    s_wave_amp: Optional[float] = None
    t_wave_amp: Optional[float] = None
    p_wave_duration: Optional[float] = None
    t_wave_duration: Optional[float] = None
    st_segment_deviation: Optional[float] = None
    st_slope: Optional[float] = None
    qrs_area: Optional[float] = None
    qt_dispersion: Optional[float] = None
    qtc_framingham: Optional[float] = None
    qtc_fridericia: Optional[float] = None
    axis_p: Optional[float] = None
    axis_qrs: Optional[float] = None
    axis_t: Optional[float] = None
    r_peak_count: Optional[int] = None
    beat_count: Optional[int] = None
    ectopy_premature_count: Optional[int] = None
    ectopy_pause_count: Optional[int] = None
    ectopy_irregularity: Optional[float] = None
    signal_duration: Optional[float] = None
    sampling_rate: Optional[int] = None
    lead_count: Optional[int] = None
    lead_mean_amp: Optional[float] = None
    lead_std_amp: Optional[float] = None
    lead_peak_to_peak: Optional[float] = None
    lead_rms: Optional[float] = None
    lead_kurtosis: Optional[float] = None
    lead_skewness: Optional[float] = None
    lead_noise_est: Optional[float] = None
    lead_baseline_wander: Optional[float] = None
    lead_signal_loss_ratio: Optional[float] = None
    quality_score: Optional[float] = None
    quality_snr: Optional[float] = None
    quality_clipping_ratio: Optional[float] = None
    quality_flatline_ratio: Optional[float] = None
    quality_noise_level: Optional[str] = None
    quality_noise_level_score: Optional[float] = None


class ReasoningStep(BaseModel):
    step: int
    description: str
    feature_used: str
    value: Union[float, str]
    threshold: str
    conclusion: str


class FeatureContribution(BaseModel):
    feature: str
    value: Union[float, str, None]
    contribution: float
    direction: Literal["positive", "negative", "neutral"]
    source: Literal["rule", "ml", "probabilistic", "fusion"]


class DiagnosisResult(BaseModel):
    id: str
    condition: str
    confidence: float = Field(ge=0, le=1)
    severity: Literal["normal", "warning", "critical"]
    source: Literal["rule", "ml", "probabilistic", "fusion"] = "rule"
    supporting_features: list[str] = []
    reasoning: list[ReasoningStep] = []
    recommendations: list[str] = []
    feature_contributions: list[FeatureContribution] = []
    probability: Optional[float] = None


class AnalysisResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    ecg_id: str
    features: ECGFeatures
    diagnoses: list[DiagnosisResult]
    overall_risk: Literal["normal", "low-risk", "moderate", "high-risk", "critical"]
    processing_time: float
    timestamp: datetime
    model_version: str
    normalized_features: dict[str, float] = Field(default_factory=dict)
    engine_breakdown: Optional["EngineBreakdown"] = None
    explainability_summary: Optional["ExplainabilitySummary"] = None
    pipeline_metrics: Optional["PipelineMetrics"] = None


class SOAPNote(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: str


class EngineBreakdown(BaseModel):
    rule_based: list[DiagnosisResult] = Field(default_factory=list)
    ml_based: list[DiagnosisResult] = Field(default_factory=list)
    probabilistic: list[DiagnosisResult] = Field(default_factory=list)
    fused: list[DiagnosisResult] = Field(default_factory=list)
    fusion_strategy: str = "weighted"
    weights: dict[str, float] = Field(default_factory=dict)


class ExplainabilitySummary(BaseModel):
    overall_summary: str
    top_contributions: list[FeatureContribution] = Field(default_factory=list)
    engine_notes: dict[str, str] = Field(default_factory=dict)


class PipelineMetrics(BaseModel):
    preprocess_ms: float = 0.0
    feature_ms: float = 0.0
    normalization_ms: float = 0.0
    rule_ms: float = 0.0
    ml_ms: float = 0.0
    probabilistic_ms: float = 0.0
    fusion_ms: float = 0.0
    explainability_ms: float = 0.0
    total_ms: float = 0.0
    budget_ms: float = 0.0
    over_budget: bool = False


class ReportRequest(BaseModel):
    signal_id: str
    patient_context: Optional[dict] = None


class ReportResponse(BaseModel):
    analysis_result: AnalysisResult
    patient_context: Optional[dict] = None
    soap_note: SOAPNote
    clinician_summary: str
    patient_summary: str
    generated_at: datetime
    report_id: str


class AnalysisRequest(BaseModel):
    signal_id: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


AnalysisResult.model_rebuild()
