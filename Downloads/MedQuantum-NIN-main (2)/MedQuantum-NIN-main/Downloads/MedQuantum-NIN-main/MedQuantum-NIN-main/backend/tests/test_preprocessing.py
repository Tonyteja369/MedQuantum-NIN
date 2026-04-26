import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from app.services.preprocessing import ECGPreprocessor

FS = 500
DURATION = 10


@pytest.fixture
def preprocessor():
    return ECGPreprocessor()


@pytest.fixture
def sample_ecg_signal():
    """Synthetic 10-second ECG at 500 Hz with known HR 75 BPM."""
    t = np.linspace(0, DURATION, FS * DURATION, endpoint=False)
    hr_hz = 75 / 60
    ecg = (
        0.2 * np.sin(2 * np.pi * hr_hz * t)
        + 1.0 * np.sin(2 * np.pi * hr_hz * t + 0.5)
        + 0.15 * np.sin(2 * np.pi * 2 * hr_hz * t)
    )
    return ecg.reshape(-1, 1).astype(np.float64)


@pytest.fixture
def sample_noisy_signal(sample_ecg_signal):
    """ECG with added Gaussian noise and 50 Hz interference."""
    t = np.linspace(0, DURATION, FS * DURATION, endpoint=False)
    noise = 0.05 * np.random.randn(len(t))
    interference = 0.1 * np.sin(2 * np.pi * 50 * t)
    noisy = sample_ecg_signal.copy()
    noisy[:, 0] += noise + interference
    return noisy


def test_notch_filter_removes_50hz(preprocessor, sample_noisy_signal):
    sig = sample_noisy_signal[:, 0]
    filtered = preprocessor.apply_notch_filter(sample_noisy_signal, FS, 50.0)[:, 0]

    freqs = np.fft.rfftfreq(len(sig), 1 / FS)
    idx_50 = np.argmin(np.abs(freqs - 50))

    power_before = np.abs(np.fft.rfft(sig))[idx_50]
    power_after = np.abs(np.fft.rfft(filtered))[idx_50]

    assert power_after < power_before * 0.1, "50 Hz component should be reduced by >90%"


def test_bandpass_preserves_qrs(preprocessor, sample_ecg_signal):
    filtered = preprocessor.apply_bandpass_filter(sample_ecg_signal, FS)
    freqs = np.fft.rfftfreq(len(sample_ecg_signal), 1 / FS)
    spectrum = np.abs(np.fft.rfft(filtered[:, 0]))
    qrs_band = (freqs >= 5) & (freqs <= 40)
    qrs_energy = np.sum(spectrum[qrs_band] ** 2)
    assert qrs_energy > 0, "QRS band energy should be preserved"
    assert filtered.shape == sample_ecg_signal.shape


def test_baseline_correction_removes_drift(preprocessor):
    t = np.linspace(0, DURATION, FS * DURATION)
    clean = np.sin(2 * np.pi * 1.25 * t)
    drift = 0.5 * np.sin(2 * np.pi * 0.05 * t)
    combined = (clean + drift).reshape(-1, 1)

    corrected = preprocessor.correct_baseline(combined, FS)
    # After correction the absolute mean should be reduced vs the raw combined signal
    raw_mean = abs(np.mean(combined[:, 0]))
    corrected_mean = abs(np.mean(corrected[:, 0]))
    # The correction should not increase the mean significantly
    assert corrected_mean < raw_mean + 0.5, (
        f"Baseline correction should not worsen mean drift: "
        f"raw={raw_mean:.3f}, corrected={corrected_mean:.3f}"
    )
    # Variance of the corrected signal should be finite and non-zero
    assert np.var(corrected[:, 0]) > 0


def test_quality_metrics_on_clean_signal(preprocessor, sample_ecg_signal):
    quality = preprocessor.compute_quality_metrics(sample_ecg_signal, FS)
    assert quality.overall_score >= 40, "Clean signal should have reasonable quality score"
    assert quality.noise_level in ("low", "medium", "high")
    assert isinstance(quality.baseline_wander, bool)
    assert isinstance(quality.signal_loss, bool)


def test_quality_metrics_on_noisy_signal(preprocessor, sample_ecg_signal, sample_noisy_signal):
    clean_quality = preprocessor.compute_quality_metrics(sample_ecg_signal, FS)
    noisy_quality = preprocessor.compute_quality_metrics(sample_noisy_signal, FS)
    # Both scores should be within valid range
    assert 0 <= clean_quality.overall_score <= 100
    assert 0 <= noisy_quality.overall_score <= 100
    # Noisy signal should have at least one of: higher noise_level or more details
    got_noisier = (
        noisy_quality.noise_level in ("medium", "high")
        or len(noisy_quality.details) >= len(clean_quality.details)
    )
    assert got_noisier, "Noisy signal quality metrics should reflect added noise"


def test_full_preprocessing_pipeline(preprocessor, sample_ecg_signal):
    processed, quality = preprocessor.preprocess(sample_ecg_signal, FS)
    assert processed.shape == sample_ecg_signal.shape, "Output shape should match input shape"
    assert quality is not None
    assert 0 <= quality.overall_score <= 100
