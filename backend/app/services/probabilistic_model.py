import math
import uuid

from loguru import logger

from app.models.schemas import DiagnosisResult, ECGFeatures, ReasoningStep


class ProbabilisticRiskModel:
    def evaluate(self, features: ECGFeatures) -> tuple[list[DiagnosisResult], str, dict[str, float]]:
        probabilities: dict[str, float] = {}
        diagnoses: list[DiagnosisResult] = []

        tachy_p = self._sigmoid((features.heart_rate - 100) / 15)
        probabilities["Sinus Tachycardia"] = tachy_p
        brady_p = self._sigmoid((60 - features.heart_rate) / 10)
        probabilities["Sinus Bradycardia"] = brady_p

        irregularity = features.ectopy_irregularity or 0.0
        afib_p = self._sigmoid((irregularity - 0.2) / 0.08)
        probabilities["Possible Atrial Fibrillation"] = afib_p

        qt = features.qtc_interval or 0.0
        qt_p = self._sigmoid((qt - 450) / 25)
        probabilities["QT Prolongation"] = qt_p

        qrs = features.qrs_duration or 0.0
        bbb_p = self._sigmoid((qrs - 120) / 20)
        probabilities["Bundle Branch Block (Possible)"] = bbb_p

        pr = features.pr_interval or 0.0
        av_p = self._sigmoid((pr - 200) / 20)
        probabilities["First-Degree AV Block"] = av_p

        for condition, prob in probabilities.items():
            if prob < 0.4:
                continue
            severity = "warning"
            if condition in ("QT Prolongation",) and prob > 0.75:
                severity = "critical"
            diagnoses.append(
                DiagnosisResult(
                    id=str(uuid.uuid4()),
                    condition=condition,
                    confidence=round(prob, 3),
                    probability=round(prob, 3),
                    severity=severity,
                    source="probabilistic",
                    supporting_features=[f"Probability {prob:.2f}"],
                    reasoning=[
                        ReasoningStep(
                            step=1,
                            description="Probabilistic risk score",
                            feature_used="probability",
                            value=round(prob, 3),
                            threshold=">=0.4",
                            conclusion="Probabilistic score exceeded threshold",
                        )
                    ],
                    recommendations=[],
                )
            )

        overall_risk = self._overall_risk(diagnoses)
        logger.info(
            f"Probabilistic model: {len(diagnoses)} diagnoses, risk={overall_risk}"
        )
        return diagnoses, overall_risk, probabilities

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-x))

    def _overall_risk(self, diagnoses: list[DiagnosisResult]) -> str:
        if not diagnoses:
            return "normal"
        severity_map = {"normal": 0, "warning": 1, "critical": 2}
        max_sev = max(severity_map.get(d.severity, 0) for d in diagnoses)
        max_prob = max(d.confidence for d in diagnoses) if diagnoses else 0.0
        if max_sev == 2:
            return "critical" if max_prob > 0.8 else "high-risk"
        if max_sev == 1:
            return "high-risk" if max_prob > 0.7 else "moderate"
        return "low-risk"
