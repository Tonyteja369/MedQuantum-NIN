import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from app.services.feature_extraction import ECGFeatureExtractor

FS = 500


@pytest.fixture
def extractor():
    return ECGFeatureExtractor()


@pytest.fixture
def synthetic_ecg_75bpm():
    """Synthetic ECG at 75 BPM using neurokit2 simulate."""
    try:
        import neurokit2 as nk

        ecg = nk.ecg_simulate(duration=30, sampling_rate=FS, heart_rate=75, noise=0.05)
        return np.array(ecg).reshape(-1, 1)
    except Exception:
        t = np.linspace(0, 30, FS * 30)
        ecg = np.sin(2 * np.pi * 1.25 * t) + 0.1 * np.random.randn(len(t))
        return ecg.reshape(-1, 1)


@pytest.fixture
def short_signal():
    """Signal too short for reliable feature extraction (1 second)."""
    return np.random.randn(FS * 1, 1) * 0.1


def test_heart_rate_extraction(extractor, synthetic_ecg_75bpm):
    features = extractor.extract_features(synthetic_ecg_75bpm, FS)
    assert features.heart_rate > 0
    assert abs(features.heart_rate - 75) <= 15, (
        f"HR {features.heart_rate:.1f} should be near 75 BPM"
    )


def test_rr_intervals_count(extractor, synthetic_ecg_75bpm):
    features = extractor.extract_features(synthetic_ecg_75bpm, FS)
    assert len(features.rr_intervals) >= 10, (
        "Should detect many RR intervals in 30s signal"
    )


def test_qrs_duration_within_normal_range(extractor, synthetic_ecg_75bpm):
    features = extractor.extract_features(synthetic_ecg_75bpm, FS)
    if features.qrs_duration is not None:
        assert 50 <= features.qrs_duration <= 200, (
            f"QRS {features.qrs_duration:.1f} ms should be in 50-200ms range"
        )


def test_qt_interval_extraction(extractor, synthetic_ecg_75bpm):
    features = extractor.extract_features(synthetic_ecg_75bpm, FS)
    if features.qt_interval is not None:
        assert features.qt_interval > 0


def test_qtc_bazett_formula(extractor):
    """Verify QTc = QT / sqrt(RR_s) directly."""
    qt_ms = 400.0
    rr_ms = 800.0
    expected_qtc = qt_ms / np.sqrt(rr_ms / 1000.0)
    computed = extractor._compute_qtc(qt_ms, rr_ms)
    assert abs(computed - expected_qtc) < 0.01, (
        f"QTc formula error: got {computed:.2f}, expected {expected_qtc:.2f}"
    )


def test_missing_feature_handling(extractor, short_signal):
    """Short signal should return features without raising, with None for unavailable metrics."""
    try:
        features = extractor.extract_features(short_signal, FS)
        assert features is not None
    except Exception as e:
        pytest.fail(f"Feature extraction raised unexpected exception: {e}")
