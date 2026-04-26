"""Test suite for Quantum Engine"""

import pytest
import numpy as np
from app.services.quantum_engine import QuantumProcessor
from app.models.schemas import QuantumResult


@pytest.fixture
def sample_ecg_signal():
    """Generate a sample ECG signal."""
    fs = 500  # 500 Hz sampling rate
    duration = 5  # 5 seconds
    t = np.arange(0, duration, 1/fs)
    
    # Simple ECG-like signal: HR=75 BPM = 1.25 Hz fundamental
    fundamental = 1.25
    signal = (
        np.sin(2 * np.pi * fundamental * t) +
        0.3 * np.sin(2 * np.pi * fundamental * 2 * t) +
        0.1 * np.random.randn(len(t))
    )
    return signal


def test_quantum_processor_initialization():
    """Test that QuantumProcessor can be instantiated."""
    processor = QuantumProcessor()
    assert processor is not None


def test_fft_analysis(sample_ecg_signal):
    """Test FFT analysis functionality."""
    result = QuantumProcessor.fft_analysis(sample_ecg_signal, sampling_rate=500)
    
    assert "magnitude" in result
    assert "frequency" in result
    assert "dominant_frequencies" in result
    assert len(result["dominant_frequencies"]) > 0


def test_compute_qtc():
    """Test QT/QTc interval computation."""
    signal = np.random.randn(2500)  # 5 seconds at 500 Hz
    
    qtc_data = QuantumProcessor.compute_qtc(signal, sampling_rate=500)
    
    # Ensure all required fields are present
    assert hasattr(qtc_data, 'mean')
    assert hasattr(qtc_data, 'min')
    assert hasattr(qtc_data, 'max')
    assert hasattr(qtc_data, 'std')
    
    # Ensure all values are returned (not None)
    assert qtc_data.mean is not None
    assert qtc_data.min is not None
    assert qtc_data.max is not None
    assert qtc_data.std is not None
    
    # Validate ranges
    assert 350 < qtc_data.mean < 500  # Reasonable QTc range
    assert qtc_data.min < qtc_data.mean < qtc_data.max


def test_process_full_pipeline(sample_ecg_signal):
    """Test full quantum processing pipeline."""
    result = QuantumProcessor.process(sample_ecg_signal, sampling_rate=500)
    
    assert isinstance(result, QuantumResult)
    assert result.fft_magnitude is not None
    assert result.fft_frequency is not None
    assert result.dominant_frequencies is not None
    assert result.mean_qt_interval is not None
    assert isinstance(result.fft_magnitude, list)
    assert len(result.fft_magnitude) > 0


def test_quantum_engine_full():
    """Test complete quantum analysis on synthetic data."""
    # Generate test signal
    fs = 500
    duration = 10
    t = np.arange(0, duration, 1/fs)
    signal = np.sin(2 * np.pi * 1.25 * t) + 0.1 * np.random.randn(len(t))
    
    result = QuantumProcessor.process(signal, sampling_rate=fs)
    
    # Verify result structure
    assert result is not None
    assert len(result.fft_magnitude) > 0
    assert len(result.dominant_frequencies) > 0
    assert result.mean_qt_interval.mean > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
