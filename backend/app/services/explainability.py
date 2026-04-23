import numpy as np
from loguru import logger

from app.models.schemas import (
    DiagnosisResult,
    ECGFeatures,
    ExplainabilitySummary,
    FeatureContribution,
    ReasoningStep,
)
from app.services.feature_catalog import get_feature_spec


CALIBRATION_FACTORS = {
    "Sinus Tachycardia": 1.0,
    "Sinus Bradycardia": 1.0,
    "Possible Atrial Fibrillation": 0.85,
    "QT Prolongation": 0.92,
    "Bundle Branch Block (Possible)": 0.88,
    "First-Degree AV Block": 0.90,
    "Normal Sinus Rhythm": 1.0,
}

FEATURE_CLINICAL_NAMES = {
    "heart_rate": "Heart Rate",
    "rr_mean": "Mean RR Interval",
    "rr_std": "RR Interval Variability",
    "pr_interval": "PR Interval",
    "qrs_duration": "QRS Duration",
    "qt_interval": "QT Interval",
    "qtc_interval": "Corrected QT (Bazett)",
    "hr_variability": "Heart Rate Variability (SDNN)",
    "rr_rmssd": "RMSSD",
    "rr_pnn50": "pNN50",
    "freq_lf_hf_ratio": "LF/HF Ratio",
    "st_segment_deviation": "ST Deviation",
    "axis_qrs": "QRS Axis",
    "ectopy_irregularity": "RR Irregularity Index",
    "quality_score": "Signal Quality Score",
}


class ExplainabilityEngine:
    def generate_trace(
        self,
        features: ECGFeatures,
        diagnoses: list[DiagnosisResult],
        rule_intermediates: dict | None = None,
    ) -> list[DiagnosisResult]:
        """Enhance diagnoses with detailed reasoning, feature importance, and natural language."""
        enhanced = []
        for dx in diagnoses:
            dx_copy = dx.model_copy(deep=True)
            dx_copy.reasoning = self._natural_language_reasoning(dx_copy.reasoning)
            dx_copy.confidence = self._calibrate_confidence(
                dx_copy.condition, dx_copy.confidence
            )
            dx_copy.supporting_features = self._feature_importance_ranking(features, dx_copy)
            if not dx_copy.feature_contributions:
                dx_copy.feature_contributions = self._feature_contributions(
                    features, dx_copy
                )
            enhanced.append(dx_copy)

        logger.debug(f"Explainability trace generated for {len(enhanced)} diagnoses")
        return enhanced

    def _natural_language_reasoning(
        self, steps: list[ReasoningStep]
    ) -> list[ReasoningStep]:
        """Convert technical reasoning steps to clinically coherent sentences."""
        enhanced = []
        for step in steps:
            clinical_name = FEATURE_CLINICAL_NAMES.get(
                step.feature_used,
                step.feature_used.replace("_", " ").title(),
            )
            threshold_text = (
                str(step.threshold)
                .replace(">", "exceeds")
                .replace("<", "is below")
                .replace("=", "equals")
            )
            nl_conclusion = (
                f"The {clinical_name} of {step.value} {threshold_text} the clinical "
                f"reference threshold, {step.conclusion.lower()}."
            )
            enhanced.append(
                ReasoningStep(
                    step=step.step,
                    description=step.description,
                    feature_used=step.feature_used,
                    value=step.value,
                    threshold=step.threshold,
                    conclusion=nl_conclusion,
                )
            )
        return enhanced

    def _calibrate_confidence(self, condition: str, raw_confidence: float) -> float:
        factor = CALIBRATION_FACTORS.get(condition, 0.9)
        calibrated = raw_confidence * factor
        return round(min(0.99, max(0.01, calibrated)), 3)

    def _feature_importance_ranking(
        self, features: ECGFeatures, dx: DiagnosisResult
    ) -> list[str]:
        """Rank features by their contribution to this diagnosis."""
        feature_dict = {
            "heart_rate": features.heart_rate,
            "rr_mean": features.rr_mean,
            "rr_std": features.rr_std,
            "pr_interval": features.pr_interval,
            "qrs_duration": features.qrs_duration,
            "qt_interval": features.qt_interval,
            "qtc_interval": features.qtc_interval,
            "hr_variability": features.hr_variability,
        }
        importance_map = {
            "Sinus Tachycardia": ["heart_rate", "rr_mean", "rr_std"],
            "Sinus Bradycardia": ["heart_rate", "rr_mean", "rr_std"],
            "Possible Atrial Fibrillation": ["rr_std", "hr_variability", "heart_rate"],
            "QT Prolongation": ["qtc_interval", "qt_interval", "rr_mean"],
            "Bundle Branch Block (Possible)": ["qrs_duration", "pr_interval"],
            "First-Degree AV Block": ["pr_interval", "heart_rate"],
            "Normal Sinus Rhythm": [
                "heart_rate",
                "rr_mean",
                "rr_std",
                "pr_interval",
                "qrs_duration",
            ],
        }
        important_keys = importance_map.get(dx.condition, list(feature_dict.keys()))
        result = []
        for key in important_keys:
            val = feature_dict.get(key)
            if val is not None:
                cname = FEATURE_CLINICAL_NAMES.get(key, key)
                result.append(f"{cname}: {val:.1f}")
        return result if result else dx.supporting_features

    def _feature_contributions(
        self, features: ECGFeatures, dx: DiagnosisResult
    ) -> list[FeatureContribution]:
        feature_dict = features.model_dump()
        importance_map = {
            "Sinus Tachycardia": ["heart_rate", "rr_mean", "rr_std"],
            "Sinus Bradycardia": ["heart_rate", "rr_mean", "rr_std"],
            "Possible Atrial Fibrillation": [
                "ectopy_irregularity",
                "rr_std",
                "hr_variability",
            ],
            "QT Prolongation": ["qtc_interval", "qt_interval", "rr_mean"],
            "Bundle Branch Block (Possible)": ["qrs_duration", "pr_interval"],
            "First-Degree AV Block": ["pr_interval", "heart_rate"],
            "Normal Sinus Rhythm": [
                "heart_rate",
                "rr_mean",
                "rr_std",
                "pr_interval",
                "qrs_duration",
            ],
        }
        keys = importance_map.get(dx.condition, [])
        contributions: list[FeatureContribution] = []
        for key in keys:
            val = feature_dict.get(key)
            if not isinstance(val, (int, float)):
                continue
            spec = get_feature_spec(key)
            normal_range = spec.normal_range if spec else None
            direction = "neutral"
            contribution = 0.0
            if normal_range:
                low, high = normal_range
                if val < low:
                    direction = "negative"
                elif val > high:
                    direction = "positive"
                span = (high - low) or 1.0
                contribution = (val - (low + high) / 2) / span
            contributions.append(
                FeatureContribution(
                    feature=key,
                    value=round(val, 2),
                    contribution=round(contribution, 3),
                    direction=direction,
                    source=dx.source,
                )
            )
        return contributions

    def build_summary(
        self, diagnoses: list[DiagnosisResult], overall_risk: str
    ) -> ExplainabilitySummary:
        top_contribs = []
        for dx in diagnoses:
            top_contribs.extend(dx.feature_contributions[:2])
        summary = (
            f"Explainability summary: {len(diagnoses)} diagnoses, "
            f"overall risk {overall_risk}."
        )
        return ExplainabilitySummary(
            overall_summary=summary,
            top_contributions=top_contribs[:5],
            engine_notes={},
        )

    def _counterfactual_explanation(
        self, features: ECGFeatures, dx: DiagnosisResult
    ) -> str:
        """Compute minimum feature change needed to change this diagnosis."""
        if dx.condition == "Sinus Tachycardia":
            delta = features.heart_rate - 100
            return (
                f"Heart rate would need to decrease by {delta:.0f} bpm "
                f"to fall below the tachycardia threshold."
            )
        if dx.condition == "Sinus Bradycardia":
            delta = 60 - features.heart_rate
            return (
                f"Heart rate would need to increase by {delta:.0f} bpm "
                f"to reach normal range."
            )
        if dx.condition == "QT Prolongation" and features.qtc_interval:
            delta = features.qtc_interval - 450
            return f"QTc would need to decrease by {delta:.0f} ms to fall within normal range."
        return "No simple counterfactual available for this diagnosis."
