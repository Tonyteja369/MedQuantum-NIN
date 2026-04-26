from datetime import datetime
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
    qt_interval_ms: Optional[float] = None  # Qt interval in milliseconds
    qtc_interval: Optional[float] = None
    rr_mean: float
    rr_std: float
    hr_variability: float


class ReasoningStep(BaseModel):
    step: int
    description: str
    feature_used: str
    value: Union[float, str]
    threshold: str
    conclusion: str


class DiagnosisResult(BaseModel):
    id: str
    condition: str
    confidence: float = Field(ge=0, le=1)
    severity: Literal["normal", "warning", "critical"]
    supporting_features: list[str] = []
    reasoning: list[ReasoningStep] = []
    recommendations: list[str] = []


class AnalysisResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    ecg_id: str
    features: ECGFeatures
    diagnoses: list[DiagnosisResult]
    overall_risk: Literal["normal", "low-risk", "moderate", "high-risk", "critical"]
    processing_time: float
    timestamp: datetime
    model_version: str


class SOAPNote(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: str


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
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Quantum Engine schemas
class MeanQTInterval(BaseModel):
    """QT interval measurements with mean, min, max, std"""
    mean: float
    min: float
    max: float
    std: float


class QuantumResult(BaseModel):
    """Result from quantum signal processing"""
    fft_magnitude: list[float]
    fft_frequency: list[float]
    dominant_frequencies: list[float]
    mean_qt_interval: Optional[MeanQTInterval] = None
    processing_time_ms: float = 0.0


# NIN Engine schemas  
class ReasoningTrace(BaseModel):
    """Individual reasoning step in diagnosis"""
    step_number: int
    description: str
    feature_name: str
    feature_value: Union[float, str]
    threshold_or_range: str
    passed: bool


class Diagnosis(BaseModel):
    """Single diagnosis with confidence and reasoning"""
    condition: str
    confidence: float = Field(ge=0, le=1)
    severity: Literal["normal", "warning", "critical"] = "normal"
    reasoning_trace: list[ReasoningTrace] = []
    feature_values: dict = {}
    thresholds: dict = {}
    supporting_evidence: list[str] = []


class NINResult(BaseModel):
    """Final result from NIN 3-pass pipeline"""
    diagnoses: list[Diagnosis]
    primary_diagnosis: Optional[Diagnosis] = None
    analysis_time_ms: float = 0.0
    pipeline_stages_completed: list[str] = []
    confidence_distribution: Optional[dict] = None
