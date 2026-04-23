from __future__ import annotations

from typing import Any

from app.models.schemas import ECGFeatures
from app.services.feature_catalog import normalization_range


class FeatureNormalizer:
    def normalize(self, features: ECGFeatures) -> dict[str, float]:
        """Normalize key features to roughly -1..1 range based on clinical ranges."""
        normalized: dict[str, float] = {}
        data = features.model_dump()
        for name, value in data.items():
            if isinstance(value, (int, float)):
                norm_range = normalization_range(name)
                if norm_range is None:
                    continue
                low, high = norm_range
                span = (high - low) / 2
                if span <= 0:
                    continue
                mid = (high + low) / 2
                normalized[name] = float((value - mid) / span)
        return normalized

    def aggregate(self, features: ECGFeatures) -> dict[str, Any]:
        """Compute aggregated descriptors for downstream models."""
        return {
            "rate_category": self._rate_category(features.heart_rate),
            "rr_irregularity": features.ectopy_irregularity,
            "quality_bucket": self._quality_bucket(features.quality_score),
        }

    def _rate_category(self, heart_rate: float) -> str:
        if heart_rate < 60:
            return "bradycardia"
        if heart_rate > 100:
            return "tachycardia"
        return "normal"

    def _quality_bucket(self, quality_score: float | None) -> str:
        if quality_score is None:
            return "unknown"
        if quality_score >= 80:
            return "high"
        if quality_score >= 50:
            return "medium"
        return "low"
