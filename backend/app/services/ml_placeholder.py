"""
ML Model Placeholder Module
============================
This module is a placeholder for future ML-based ECG classification.

Planned Architecture:
- CNN branch: 1D convolutional network for waveform morphology classification
  (P-wave absence detection, ST-segment morphology, QRS shape analysis)
- LSTM branch: Bidirectional LSTM for temporal pattern recognition
  (rhythm irregularities, rate-dependent changes, long-term RR patterns)
- Ensemble fusion: Weighted combination of CNN, LSTM, and rule engine outputs
  using learned calibration weights per diagnosis category
- SHAP explainability: SHAPDeepExplainer for CNN, SHAPKernelExplainer for rules,
  integrated into ExplainabilityEngine outputs

Current status: Rule-based analysis only (100% offline, no GPU required).
"""

import numpy as np
from loguru import logger

from app.models.schemas import DiagnosisResult, ECGFeatures


class MLModelPlaceholder:
    """Placeholder for future ML-based ECG diagnosis."""

    def __init__(self):
        self.model_loaded = False
        logger.info("MLModelPlaceholder initialized — using rule-based analysis only")

    def predict(self, features: ECGFeatures, signal: np.ndarray) -> list[DiagnosisResult]:
        """
        Returns additional diagnoses from ML model.
        Currently returns empty list — ML not yet implemented.
        """
        logger.debug("ML module not yet implemented — using rule-based analysis only")
        return []

    def load_model(self, model_path: str) -> None:
        """Load trained model weights from disk."""
        raise NotImplementedError("ML model not yet implemented")

    def preprocess_for_model(self, signal: np.ndarray, sampling_rate: int) -> np.ndarray:
        """Prepare signal tensor for model input (normalization, windowing, etc.)."""
        raise NotImplementedError("ML model not yet implemented")

    def postprocess_predictions(self, raw_logits: np.ndarray) -> list[dict]:
        """Convert raw model output logits to diagnosis probabilities."""
        raise NotImplementedError("ML model not yet implemented")

    def compute_shap_values(self, signal_tensor: np.ndarray) -> np.ndarray:
        """Compute SHAP feature importance values for model predictions."""
        raise NotImplementedError("ML model not yet implemented")
