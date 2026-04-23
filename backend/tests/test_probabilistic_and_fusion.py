import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.models.schemas import ECGFeatures
from app.services.fusion_engine import FusionEngine
from app.services.ml_inference import MLInferenceEngine
from app.services.probabilistic_model import ProbabilisticRiskModel
from app.services.rule_engine import ClinicalRuleEngine


def make_features(**kwargs) -> ECGFeatures:
    defaults = dict(
        heart_rate=110.0,
        rr_intervals=[550.0] * 20,
        pr_interval=160.0,
        qrs_duration=90.0,
        qt_interval=380.0,
        qtc_interval=420.0,
        rr_mean=550.0,
        rr_std=25.0,
        hr_variability=25.0,
    )
    defaults.update(kwargs)
    return ECGFeatures(**defaults)


def test_probabilistic_model_outputs():
    model = ProbabilisticRiskModel()
    features = make_features(heart_rate=130.0, qtc_interval=480.0)
    diagnoses, risk, scores = model.evaluate(features)
    assert isinstance(scores, dict)
    assert risk in ("normal", "low-risk", "moderate", "high-risk", "critical")
    assert any(d.condition for d in diagnoses)


def test_ml_inference_engine_loads_weights():
    model_path = Path(settings.ml_model_path)
    ml_engine = MLInferenceEngine(str(model_path), enabled=True)
    features = make_features(heart_rate=130.0, qtc_interval=500.0)
    results = ml_engine.predict(features, {"heart_rate": 1.0})
    assert isinstance(results, list)


def test_fusion_engine_combines_sources():
    engine = ClinicalRuleEngine()
    fusion = FusionEngine()
    features = make_features(heart_rate=130.0)
    rule_results, _ = engine.evaluate(features)
    prob_results, _, _ = ProbabilisticRiskModel().evaluate(features)
    fused, risk, details = fusion.fuse(
        rule_results,
        [],
        prob_results,
        settings.fusion_weights,
    )
    assert fused
    assert risk in ("normal", "low-risk", "moderate", "high-risk", "critical")
    assert isinstance(details, dict)
