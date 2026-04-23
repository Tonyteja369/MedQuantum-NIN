import uuid

import numpy as np
from loguru import logger

from app.models.schemas import DiagnosisResult, ECGFeatures, ReasoningStep


class ClinicalRuleEngine:
    def evaluate(self, features: ECGFeatures) -> tuple[list[DiagnosisResult], str]:
        """Evaluate all clinical rules. Returns (diagnoses, overall_risk)."""
        results = []

        for rule_fn in [
            self._rule_tachycardia,
            self._rule_bradycardia,
            self._rule_atrial_fibrillation,
            self._rule_qt_prolongation,
            self._rule_bundle_branch_block,
            self._rule_first_degree_av_block,
        ]:
            try:
                dx = rule_fn(features)
                if dx is not None:
                    results.append(dx)
            except Exception as e:
                logger.warning(f"Rule {rule_fn.__name__} failed: {e}")

        if not results:
            results.append(self._rule_normal_sinus_rhythm(features))

        results.sort(key=lambda d: d.confidence, reverse=True)
        overall_risk = self._compute_overall_risk(results)
        logger.info(f"Rule engine: {len(results)} diagnoses, risk={overall_risk}")
        return results, overall_risk

    def _rule_tachycardia(self, f: ECGFeatures) -> DiagnosisResult | None:
        if f.heart_rate <= 100:
            return None
        excess = f.heart_rate - 100
        confidence = min(0.99, excess / 50 + 0.7)
        severity = "critical" if f.heart_rate >= 150 else "warning"
        recs = [
            "12-lead ECG recommended",
            "Check for underlying cause (fever, anxiety, dehydration, hyperthyroidism)",
        ]
        if severity == "critical":
            recs.insert(0, "Urgent cardiology evaluation required")
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="Sinus Tachycardia",
            confidence=round(confidence, 3),
            severity=severity,
            source="rule",
            supporting_features=[
                f"Heart rate: {f.heart_rate:.1f} bpm (>100 bpm threshold)"
            ],
            reasoning=[
                ReasoningStep(
                    step=1,
                    description="Heart rate exceeds normal upper limit",
                    feature_used="heart_rate",
                    value=round(f.heart_rate, 1),
                    threshold=">100 bpm",
                    conclusion=f"Tachycardia confirmed at {f.heart_rate:.1f} bpm",
                )
            ],
            recommendations=recs,
        )

    def _rule_bradycardia(self, f: ECGFeatures) -> DiagnosisResult | None:
        if f.heart_rate >= 60:
            return None
        deficit = 60 - f.heart_rate
        confidence = min(0.99, deficit / 30 + 0.6)
        severity = "critical" if f.heart_rate < 40 else "warning"
        recs = [
            "12-lead ECG recommended",
            "Review medications (beta-blockers, calcium channel blockers)",
        ]
        if severity == "critical":
            recs.insert(0, "Urgent evaluation — consider pacemaker assessment")
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="Sinus Bradycardia",
            confidence=round(confidence, 3),
            severity=severity,
            source="rule",
            supporting_features=[
                f"Heart rate: {f.heart_rate:.1f} bpm (<60 bpm threshold)"
            ],
            reasoning=[
                ReasoningStep(
                    step=1,
                    description="Heart rate below normal lower limit",
                    feature_used="heart_rate",
                    value=round(f.heart_rate, 1),
                    threshold="<60 bpm",
                    conclusion=f"Bradycardia at {f.heart_rate:.1f} bpm",
                )
            ],
            recommendations=recs,
        )

    def _rule_atrial_fibrillation(self, f: ECGFeatures) -> DiagnosisResult | None:
        if len(f.rr_intervals) < 5:
            return None
        rr = np.array(f.rr_intervals)
        cv = float(np.std(rr) / np.mean(rr)) if np.mean(rr) > 0 else 0
        if cv <= 0.2:
            return None
        confidence = min(0.95, (cv - 0.2) / 0.3 + 0.5)
        severity = "critical" if cv > 0.4 else "warning"
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="Possible Atrial Fibrillation",
            confidence=round(confidence, 3),
            severity=severity,
            source="rule",
            supporting_features=[
                f"RR interval CV: {cv:.3f} (>0.2 threshold)",
                f"Mean HR: {f.heart_rate:.1f} bpm",
            ],
            reasoning=[
                ReasoningStep(
                    step=1,
                    description="RR interval irregularity assessment",
                    feature_used="rr_cv",
                    value=round(cv, 3),
                    threshold=">0.2",
                    conclusion=f"Irregular RR intervals detected (CV={cv:.3f})",
                ),
                ReasoningStep(
                    step=2,
                    description="Heart rate in AFib range",
                    feature_used="heart_rate",
                    value=round(f.heart_rate, 1),
                    threshold=">60 bpm",
                    conclusion="Heart rate consistent with AFib",
                ),
            ],
            recommendations=[
                "Urgent cardiology referral",
                "Holter monitor recommended",
                "Anticoagulation assessment",
                "Rule out thyroid dysfunction",
            ],
        )

    def _rule_qt_prolongation(self, f: ECGFeatures) -> DiagnosisResult | None:
        if f.qtc_interval is None:
            return None
        threshold = 450.0
        if f.qtc_interval <= threshold:
            return None
        excess = f.qtc_interval - threshold
        confidence = min(0.97, excess / 100 + 0.6)
        severity = "critical" if f.qtc_interval > 500 else "warning"
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="QT Prolongation",
            confidence=round(confidence, 3),
            severity=severity,
            source="rule",
            supporting_features=[
                f"QTc: {f.qtc_interval:.1f} ms (threshold {threshold:.0f} ms, Bazett formula)"
            ],
            reasoning=[
                ReasoningStep(
                    step=1,
                    description="QTc exceeds sex-specific threshold",
                    feature_used="qtc_interval",
                    value=round(f.qtc_interval, 1),
                    threshold=f">{threshold:.0f} ms (male)",
                    conclusion=f"QT prolongation: QTc={f.qtc_interval:.1f} ms",
                )
            ],
            recommendations=[
                "Medication review for QT-prolonging drugs",
                "Electrolyte panel (K+, Mg2+, Ca2+)",
                "Cardiology consultation",
                "Avoid QT-prolonging medications",
            ],
        )

    def _rule_bundle_branch_block(self, f: ECGFeatures) -> DiagnosisResult | None:
        if f.qrs_duration is None or f.qrs_duration <= 120:
            return None
        excess = f.qrs_duration - 120
        confidence = min(0.9, excess / 40 + 0.6)
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="Bundle Branch Block (Possible)",
            confidence=round(confidence, 3),
            severity="warning",
            source="rule",
            supporting_features=[
                f"QRS duration: {f.qrs_duration:.1f} ms (>120 ms threshold)"
            ],
            reasoning=[
                ReasoningStep(
                    step=1,
                    description="QRS duration exceeds normal limit",
                    feature_used="qrs_duration",
                    value=round(f.qrs_duration, 1),
                    threshold=">120 ms",
                    conclusion=f"Wide QRS complex: {f.qrs_duration:.1f} ms",
                )
            ],
            recommendations=[
                "12-lead ECG for RBBB vs LBBB differentiation",
                "Cardiology evaluation",
                "Echocardiogram if new finding",
            ],
        )

    def _rule_first_degree_av_block(self, f: ECGFeatures) -> DiagnosisResult | None:
        if f.pr_interval is None or f.pr_interval <= 200:
            return None
        excess = f.pr_interval - 200
        confidence = min(0.92, excess / 100 + 0.55)
        severity = "warning" if f.pr_interval < 300 else "critical"
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="First-Degree AV Block",
            confidence=round(confidence, 3),
            severity=severity,
            source="rule",
            supporting_features=[
                f"PR interval: {f.pr_interval:.1f} ms (>200 ms threshold)"
            ],
            reasoning=[
                ReasoningStep(
                    step=1,
                    description="PR interval exceeds normal upper limit",
                    feature_used="pr_interval",
                    value=round(f.pr_interval, 1),
                    threshold=">200 ms",
                    conclusion=f"Prolonged AV conduction: PR={f.pr_interval:.1f} ms",
                )
            ],
            recommendations=[
                "Serial ECGs to monitor progression",
                "Review AV-nodal blocking medications",
                "Electrolyte panel",
            ],
        )

    def _rule_normal_sinus_rhythm(self, f: ECGFeatures) -> DiagnosisResult:
        steps = [
            ReasoningStep(
                step=1,
                description="Heart rate within normal range",
                feature_used="heart_rate",
                value=round(f.heart_rate, 1),
                threshold="60-100 bpm",
                conclusion="Normal heart rate",
            )
        ]
        if f.pr_interval:
            steps.append(
                ReasoningStep(
                    step=2,
                    description="PR interval within normal range",
                    feature_used="pr_interval",
                    value=round(f.pr_interval, 1),
                    threshold="120-200 ms",
                    conclusion="Normal AV conduction",
                )
            )
        if f.qrs_duration:
            steps.append(
                ReasoningStep(
                    step=3,
                    description="QRS duration within normal range",
                    feature_used="qrs_duration",
                    value=round(f.qrs_duration, 1),
                    threshold="<120 ms",
                    conclusion="Normal ventricular conduction",
                )
            )
        return DiagnosisResult(
            id=str(uuid.uuid4()),
            condition="Normal Sinus Rhythm",
            confidence=0.92,
            severity="normal",
            source="rule",
            supporting_features=[
                "HR within normal range",
                "Regular rhythm",
                "No significant intervals abnormalities",
            ],
            reasoning=steps,
            recommendations=[
                "Continue routine cardiovascular health maintenance",
                "Annual checkup recommended",
            ],
        )

    def _compute_overall_risk(self, diagnoses: list[DiagnosisResult]) -> str:
        if not diagnoses:
            return "normal"
        severity_map = {"normal": 0, "warning": 1, "critical": 2}
        max_sev = max(severity_map.get(d.severity, 0) for d in diagnoses)
        high_conf_warning = any(
            d.severity == "warning" and d.confidence > 0.8 for d in diagnoses
        )
        if max_sev == 2:
            max_conf = max(d.confidence for d in diagnoses if d.severity == "critical")
            return "critical" if max_conf > 0.85 else "high-risk"
        if max_sev == 1:
            return "high-risk" if high_conf_warning else "moderate"
        return (
            "low-risk"
            if any(d.severity == "normal" and d.confidence < 0.95 for d in diagnoses)
            else "normal"
        )
