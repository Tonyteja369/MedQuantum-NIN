import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from app.models.schemas import ECGFeatures
from app.services.rule_engine import ClinicalRuleEngine


def make_features(**kwargs) -> ECGFeatures:
    defaults = dict(
        heart_rate=75.0,
        rr_intervals=[800.0] * 20,
        pr_interval=160.0,
        qrs_duration=90.0,
        qt_interval=380.0,
        qtc_interval=420.0,
        rr_mean=800.0,
        rr_std=20.0,
        hr_variability=25.0,
    )
    defaults.update(kwargs)
    return ECGFeatures(**defaults)


@pytest.fixture
def engine():
    return ClinicalRuleEngine()


def test_tachycardia_detected_above_100(engine):
    features = make_features(heart_rate=120.0, rr_mean=500.0, rr_intervals=[500.0] * 20)
    diagnoses, risk = engine.evaluate(features)
    conditions = [d.condition for d in diagnoses]
    assert any("Tachycardia" in c for c in conditions)


def test_bradycardia_detected_below_60(engine):
    features = make_features(heart_rate=45.0, rr_mean=1333.0, rr_intervals=[1333.0] * 20)
    diagnoses, risk = engine.evaluate(features)
    conditions = [d.condition for d in diagnoses]
    assert any("Bradycardia" in c for c in conditions)


def test_normal_sinus_rhythm_when_all_normal(engine):
    features = make_features()
    diagnoses, risk = engine.evaluate(features)
    conditions = [d.condition for d in diagnoses]
    assert any("Normal" in c for c in conditions)
    assert risk in ("normal", "low-risk")


def test_qt_prolongation_above_450ms_male(engine):
    features = make_features(qtc_interval=480.0)
    diagnoses, risk = engine.evaluate(features)
    conditions = [d.condition for d in diagnoses]
    assert any("QT" in c for c in conditions)


def test_afib_detected_with_irregular_rr(engine):
    np.random.seed(42)
    irregular_rr = list(np.random.uniform(400, 1200, 30))
    mean_rr = float(np.mean(irregular_rr))
    hr = 60000.0 / mean_rr
    features = make_features(
        heart_rate=hr,
        rr_intervals=irregular_rr,
        rr_mean=mean_rr,
        rr_std=float(np.std(irregular_rr)),
    )
    diagnoses, risk = engine.evaluate(features)
    conditions = [d.condition for d in diagnoses]
    rr = np.array(irregular_rr)
    cv = np.std(rr) / np.mean(rr)
    if cv > 0.2:
        assert any(
            "Fibrillation" in c or "AFib" in c or "Atrial" in c for c in conditions
        ), f"AFib should be detected with CV={cv:.3f}, got: {conditions}"


def test_confidence_between_0_and_1(engine):
    for hr in [45, 75, 120]:
        features = make_features(heart_rate=float(hr))
        diagnoses, _ = engine.evaluate(features)
        for dx in diagnoses:
            assert 0 <= dx.confidence <= 1, (
                f"Confidence {dx.confidence} out of range for {dx.condition}"
            )


def test_overall_risk_reflects_worst_diagnosis(engine):
    features = make_features(heart_rate=160.0)
    _, risk = engine.evaluate(features)
    assert risk in ("high-risk", "critical", "moderate"), (
        f"High HR should give elevated risk, got: {risk}"
    )


def test_reasoning_steps_populated(engine):
    features = make_features(heart_rate=110.0)
    diagnoses, _ = engine.evaluate(features)
    for dx in diagnoses:
        assert len(dx.reasoning) > 0, f"Reasoning should be populated for {dx.condition}"
        for step in dx.reasoning:
            assert step.step >= 1
            assert step.description
            assert step.feature_used
