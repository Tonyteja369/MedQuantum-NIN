import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.config import settings
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResult,
    ECGFeatures,
    EngineBreakdown,
    PipelineMetrics,
)
from app.services.explainability import ExplainabilityEngine
from app.services.feature_extraction import ECGFeatureExtractor
from app.services.feature_normalization import FeatureNormalizer
from app.services.fusion_engine import FusionEngine
from app.services.ml_inference import MLInferenceEngine
from app.services.probabilistic_model import ProbabilisticRiskModel
from app.services.preprocessing import ECGPreprocessor
from app.services.rule_engine import ClinicalRuleEngine
from app.utils.signal_io import load_temp_signal

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

preprocessor = ECGPreprocessor()
extractor = ECGFeatureExtractor()
rule_engine = ClinicalRuleEngine()
feature_normalizer = FeatureNormalizer()
ml_model = MLInferenceEngine(settings.ml_model_path, enabled=settings.enable_ml)
prob_model = ProbabilisticRiskModel()
fusion_engine = FusionEngine()
explainer = ExplainabilityEngine()

# In-memory result cache (production would use Redis)
_result_cache: dict[str, AnalysisResult] = {}


async def run_analysis_pipeline(signal_id: str) -> AnalysisResult:
    """Full ECG analysis pipeline."""
    t_start = time.time()
    logger.info(f"Starting analysis for signal_id={signal_id}")
    metrics = PipelineMetrics(budget_ms=float(settings.performance_budget_ms))

    try:
        signal, metadata = load_temp_signal(signal_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Signal {signal_id} not found. Upload first.")

    fs = int(metadata.get("sampling_rate", 500))

    t1 = time.time()
    preprocessed, quality = preprocessor.preprocess(signal, fs)
    metrics.preprocess_ms = round((time.time() - t1) * 1000, 1)
    logger.debug(f"Preprocessing: {metrics.preprocess_ms:.0f}ms")

    t2 = time.time()
    features = extractor.extract_features(preprocessed, fs, quality)
    metrics.feature_ms = round((time.time() - t2) * 1000, 1)
    logger.debug(f"Feature extraction: {metrics.feature_ms:.0f}ms")

    t_norm = time.time()
    normalized = feature_normalizer.normalize(features)
    metrics.normalization_ms = round((time.time() - t_norm) * 1000, 1)

    rule_results: list = []
    rule_risk = "normal"
    if settings.enable_rule_engine:
        t3 = time.time()
        rule_results, rule_risk = rule_engine.evaluate(features)
        metrics.rule_ms = round((time.time() - t3) * 1000, 1)
        logger.debug(
            f"Rule engine: {metrics.rule_ms:.0f}ms, {len(rule_results)} diagnoses"
        )

    t4 = time.time()
    ml_results = ml_model.predict(features, normalized)
    metrics.ml_ms = round((time.time() - t4) * 1000, 1)

    t5 = time.time()
    prob_results: list = []
    prob_risk = "normal"
    prob_scores: dict[str, float] = {}
    if settings.enable_probabilistic:
        prob_results, prob_risk, prob_scores = prob_model.evaluate(features)
    metrics.probabilistic_ms = round((time.time() - t5) * 1000, 1)

    t6 = time.time()
    diagnoses, overall_risk, fusion_details = fusion_engine.fuse(
        rule_results,
        ml_results,
        prob_results,
        settings.fusion_weights,
    )
    metrics.fusion_ms = round((time.time() - t6) * 1000, 1)

    t7 = time.time()
    diagnoses = explainer.generate_trace(features, diagnoses)
    metrics.explainability_ms = round((time.time() - t7) * 1000, 1)

    processing_time = round((time.time() - t_start) * 1000, 1)
    metrics.total_ms = processing_time
    metrics.over_budget = processing_time > settings.performance_budget_ms

    result = AnalysisResult(
        ecg_id=signal_id,
        features=features,
        diagnoses=diagnoses,
        overall_risk=overall_risk,
        processing_time=processing_time,
        timestamp=datetime.now(timezone.utc),
        model_version=settings.model_version,
        normalized_features=normalized,
        engine_breakdown=EngineBreakdown(
            rule_based=rule_results,
            ml_based=ml_results,
            probabilistic=prob_results,
            fused=diagnoses,
            fusion_strategy="weighted",
            weights=settings.fusion_weights,
        ),
        explainability_summary=explainer.build_summary(diagnoses, overall_risk),
        pipeline_metrics=metrics,
    )

    analysis_id = str(uuid.uuid4())
    _result_cache[analysis_id] = result
    _result_cache[signal_id] = result

    logger.info(
        f"Analysis complete: {processing_time}ms, "
        f"risk={overall_risk}, diagnoses={len(diagnoses)}"
    )
    return result


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Run full ECG analysis pipeline",
)
async def analyze_ecg(request: AnalysisRequest):
    """Run full pipeline: preprocessing → feature extraction → rule engine → explainability."""
    try:
        return await run_analysis_pipeline(request.signal_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@router.get(
    "/result/{analysis_id}",
    response_model=AnalysisResult,
    summary="Get cached analysis result",
)
async def get_result(analysis_id: str):
    """Retrieve a cached analysis result by ID."""
    result = _result_cache.get(analysis_id)
    if not result:
        raise HTTPException(404, f"Analysis result {analysis_id} not found")
    return result


@router.get(
    "/features/{signal_id}",
    response_model=ECGFeatures,
    summary="Extract features only",
)
async def get_features(signal_id: str):
    """Extract ECG features without running full diagnosis pipeline."""
    try:
        signal, metadata = load_temp_signal(signal_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Signal {signal_id} not found")

    fs = int(metadata.get("sampling_rate", 500))
    preprocessed, quality = preprocessor.preprocess(signal, fs)
    features = extractor.extract_features(preprocessed, fs, quality)
    return features
