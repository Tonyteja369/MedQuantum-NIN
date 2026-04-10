"""Test suite for quantum engine integration"""

import pytest
import numpy as np
from app.services.quantum_engine import QuantumProcessor
from app.models.schemas import QuantumResult


@pytest.fixture
def real_ecg_data():
    """Generate realistic ECG data."""
    fs = 500
    duration = 10
    t = np.arange(0, duration, 1/fs)
    
    # Realistic ECG: 75 BPM base rhythm + harmonics + noise
    hr_hz = 75 / 60  # 75 BPM in Hz
    ecg = (
        np.sin(2 * np.pi * hr_hz * t) + # P-QRS-T complex fundamental
        0.4 * np.sin(2 * np.pi * hr_hz * 2 * t) +  # Harmonic
        0.2 * np.sin(2 * np.pi * hr_hz * 3 * t) +  # Harmonic
        0.05 * np.random.randn(len(t))  # Noise
    )
    return ecg


def test_quantum_engine_full(real_ecg_data):
    """Test complete quantum engine processing."""
    result = QuantumProcessor.process(real_ecg_data, sampling_rate=500)
    
    assert isinstance(result, QuantumResult)
    assert result.fft_magnitude is not None
    assert isinstance(result.fft_magnitude, list)
    assert len(result.fft_magnitude) > 0
    
    # Check FFT structure
    assert result.fft_frequency is not None
    assert len(result.fft_frequency) > 0
    
    # Check dominant frequencies identified
    assert result.dominant_frequencies is not None
    assert isinstance(result.dominant_frequencies, list)
    assert len(result.dominant_frequencies) > 0
    
    # Check QT interval computation returns all required keys
    assert result.mean_qt_interval is not None
    assert hasattr(result.mean_qt_interval, 'mean')
    assert hasattr(result.mean_qt_interval, 'min')
    assert hasattr(result.mean_qt_interval, 'max')
    assert hasattr(result.mean_qt_interval, 'std')
    
    # Verify values are not None
    assert result.mean_qt_interval.mean is not None
    assert result.mean_qt_interval.min is not None
    assert result.mean_qt_interval.max is not None
    assert result.mean_qt_interval.std is not None


def test_qtc_beat_by_beat():
    """Test QTc interval returns beat-by-beat measurements."""
    # 5 second signal at 500 Hz with clear beat pattern
    fs = 500
    duration = 5
    t = np.arange(0, duration, 1/fs)
    
    # Create 5-beat signal (1 beat per second)
    signal = np.sin(2 * np.pi * 1.0 * t)
    
    qtc = QuantumProcessor.compute_qtc(signal, sampling_rate=fs)
    
    # Validate structure
    assert qtc is not None
    assert hasattr(qtc, 'mean')
    assert hasattr(qtc, 'min')
    assert hasattr(qtc, 'max')
    assert hasattr(qtc, 'std')
    
    # All values should be present
    assert qtc.mean > 0
    assert qtc.min > 0
    assert qtc.max > 0
    assert qtc.std >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
