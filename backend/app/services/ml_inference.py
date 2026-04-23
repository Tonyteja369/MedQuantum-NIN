import json
from pathlib import Path

import numpy as np
from loguru import logger

from app.models.schemas import DiagnosisResult, ECGFeatures, ReasoningStep


class MLInferenceEngine:
    def __init__(self, model_path: str, enabled: bool = True):
        self.model_path = model_path
        self.enabled = enabled
        self.weights = self._load_weights() if enabled else {}

    def _load_weights(self) -> dict:
        path = Path(self.model_path)
        if not path.exists():
            logger.warning(f"ML model weights not found at {path}")
            return {}
        try:
            return json.loads(path.read_text())
        except Exception as exc:
            logger.error(f"Failed to load ML weights: {exc}")
            return {}

    def predict(
        self, features: ECGFeatures, normalized: dict[str, float] | None = None
    ) -> list[DiagnosisResult]:
        if not self.enabled or not self.weights:
            return []
        normalized = normalized or {}
        feature_values = features.model_dump()
        results: list[DiagnosisResult] = []
        for condition, spec in self.weights.get("conditions", {}).items():
            score = float(spec.get("intercept", 0.0))
            weights = spec.get("weights", {})
            for feat, w in weights.items():
                value = normalized.get(feat)
                if value is None:
                    raw = feature_values.get(feat)
                    if isinstance(raw, (int, float)):
                        value = float(raw)
                if value is not None:
                    score += float(w) * float(value)
            prob = float(1.0 / (1.0 + np.exp(-score)))
            threshold = float(spec.get("threshold", 0.6))
            if prob < threshold:
                continue
            severity = spec.get("severity", "warning")
            supporting = [
                f"{feat}: {feature_values.get(feat)}"
                for feat in list(weights.keys())[:2]
                if feat in feature_values
            ]
            results.append(
                DiagnosisResult(
                    id=f"ml-{condition.replace(' ', '-').lower()}",
                    condition=condition,
                    confidence=round(prob, 3),
                    probability=round(prob, 3),
                    severity=severity,
                    source="ml",
                    supporting_features=supporting,
                    reasoning=[
                        ReasoningStep(
                            step=1,
                            description="ML inference score",
                            feature_used="ml_score",
                            value=round(prob, 3),
                            threshold=f">={threshold:.2f}",
                            conclusion=f"ML probability {prob:.2f} exceeds threshold",
                        )
                    ],
                    recommendations=spec.get("recommendations", []),
                )
            )
        return results
