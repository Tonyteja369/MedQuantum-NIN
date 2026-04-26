from typing import List, Optional
from pydantic import BaseModel


class Diagnosis(BaseModel):
    condition: str
    confidence: float
    severity: Optional[str] = None
    reasoning_trace: Optional[List[str]] = None


class MeanQTInterval(BaseModel):
    mean: float
    min: float
    max: float
    std: float


class QuantumResult(BaseModel):
    heart_rate: float
    rr_intervals: List[float]
    qtc: MeanQTInterval
    signal_quality: dict
    features: dict


class NINResult(BaseModel):
    diagnoses: List[Diagnosis]
    confidence: float
    risk_level: str
    features: dict
    primary_diagnosis: Optional[Diagnosis] = None


class AnalysisResult(BaseModel):
    heart_rate: float
    rr_intervals: List[float]
    diagnoses: List[Diagnosis]
    signal_quality: dict
