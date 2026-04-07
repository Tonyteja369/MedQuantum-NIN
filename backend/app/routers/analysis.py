import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.config import settings
from app.models.schemas import AnalysisRequest, AnalysisResult, ECGFeatures
from app.services.explainability import ExplainabilityEngine
from app.services.feature_extraction import ECGFeatureExtractor
from app.services.ml_placeholder import MLModelPlaceholder
from app.services.preprocessing import ECGPreprocessor
from app.services.rule_engine import ClinicalRuleEngine
from app.utils.signal_io import load_temp_signal

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

preprocessor = ECGPreprocessor()
extractor = ECGFeatureExtractor()
rule_engine = ClinicalRuleEngine()
ml_model = MLModelPlaceholder()
explainer = ExplainabilityEngine()

# In-memory result cache (production would use Redis)
_result_cache: dict[str, AnalysisResult] = {}


async def run_analysis_pipeline(signal_id: str) -> AnalysisResult:
    """Full ECG analysis pipeline."""
    t_start = time.time()
    logger.info(f"Starting analysis for signal_id={signal_id}")

    try:
        signal, metadata = load_temp_signal(signal_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Signal {signal_id} not found. Upload first.")

    fs = int(metadata.get("sampling_rate", 500))

    t1 = time.time()
    preprocessed, _ = preprocessor.preprocess(signal, fs)
    logger.debug(f"Preprocessing: {(time.time() - t1) * 1000:.0f}ms")

    t2 = time.time()
    features = extractor.extract_features(preprocessed, fs)
    logger.debug(f"Feature extraction: {(time.time() - t2) * 1000:.0f}ms")

    t3 = time.time()
    diagnoses, overall_risk = rule_engine.evaluate(features)
    logger.debug(
        f"Rule engine: {(time.time() - t3) * 1000:.0f}ms, {len(diagnoses)} diagnoses"
    )

    ml_results = ml_model.predict(features, preprocessed)
    diagnoses.extend(ml_results)

    t4 = time.time()
    diagnoses = explainer.generate_trace(features, diagnoses)
    logger.debug(f"Explainability: {(time.time() - t4) * 1000:.0f}ms")

    processing_time = round((time.time() - t_start) * 1000, 1)

    result = AnalysisResult(
        ecg_id=signal_id,
        features=features,
        diagnoses=diagnoses,
        overall_risk=overall_risk,
        processing_time=processing_time,
        timestamp=datetime.now(timezone.utc),
        model_version=settings.model_version,
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
    preprocessed, _ = preprocessor.preprocess(signal, fs)
    features = extractor.extract_features(preprocessed, fs)
    return features
