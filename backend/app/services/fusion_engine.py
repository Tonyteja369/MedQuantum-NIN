import uuid

from loguru import logger

from app.models.schemas import DiagnosisResult


class FusionEngine:
    def fuse(
        self,
        rule_results: list[DiagnosisResult],
        ml_results: list[DiagnosisResult],
        prob_results: list[DiagnosisResult],
        weights: dict[str, float],
    ) -> tuple[list[DiagnosisResult], str, dict[str, dict[str, float]]]:
        grouped: dict[str, list[tuple[str, DiagnosisResult]]] = {}
        for source, results in (
            ("rule", rule_results),
            ("ml", ml_results),
            ("prob", prob_results),
        ):
            for dx in results:
                grouped.setdefault(dx.condition, []).append((source, dx))

        fused_results: list[DiagnosisResult] = []
        fusion_details: dict[str, dict[str, float]] = {}
        for condition, entries in grouped.items():
            total_weight = 0.0
            weighted_conf = 0.0
            severity = "normal"
            supporting = []
            reasoning = []
            recommendations = []
            for source, dx in entries:
                w = weights.get(source, 0.0)
                total_weight += w
                weighted_conf += w * dx.confidence
                supporting.extend(dx.supporting_features)
                reasoning.extend(dx.reasoning)
                recommendations.extend(dx.recommendations)
                if dx.severity == "critical":
                    severity = "critical"
                elif dx.severity == "warning" and severity != "critical":
                    severity = "warning"
            if total_weight > 0:
                confidence = weighted_conf / total_weight
            else:
                confidence = max(dx.confidence for _, dx in entries)
            fusion_details[condition] = {"weight_sum": total_weight, "confidence": confidence}
            fused_results.append(
                DiagnosisResult(
                    id=str(uuid.uuid4()),
                    condition=condition,
                    confidence=round(confidence, 3),
                    severity=severity,
                    source="fusion",
                    supporting_features=list(dict.fromkeys(supporting))[:6],
                    reasoning=reasoning,
                    recommendations=list(dict.fromkeys(recommendations)),
                )
            )

        fused_results.sort(key=lambda d: d.confidence, reverse=True)
        overall_risk = self._overall_risk(fused_results)
        logger.info(
            f"Fusion engine: {len(fused_results)} diagnoses, risk={overall_risk}"
        )
        return fused_results, overall_risk, fusion_details

    def _overall_risk(self, diagnoses: list[DiagnosisResult]) -> str:
        if not diagnoses:
            return "normal"
        severity_map = {"normal": 0, "warning": 1, "critical": 2}
        max_sev = max(severity_map.get(d.severity, 0) for d in diagnoses)
        max_conf = max(d.confidence for d in diagnoses) if diagnoses else 0.0
        if max_sev == 2:
            return "critical" if max_conf > 0.8 else "high-risk"
        if max_sev == 1:
            return "high-risk" if max_conf > 0.7 else "moderate"
        return "normal" if max_conf > 0.8 else "low-risk"
