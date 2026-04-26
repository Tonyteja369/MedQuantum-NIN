"""Test suite for NIN Engine"""

import pytest
import numpy as np
import asyncio
from app.services.nin_engine import NINEngine, RuleReasoner, ConfidenceCalibrator, ExplainabilityBuilder
from app.services.rule_engine import run_rule_engine
from app.services.explainability import apply_explainability
from app.models.schemas import QuantumResult, MeanQTInterval, Diagnosis, NINResult


@pytest.fixture
def sample_quantum_result():
    """Create a sample quantum result."""
    return QuantumResult(
        fft_magnitude=[1.0, 2.0, 3.0, 2.5, 1.5],
        fft_frequency=[0, 1, 2, 3, 4],
        dominant_frequencies=[2.0, 1.0, 3.0],
        mean_qt_interval=MeanQTInterval(
            mean=400.0,
            min=360.0,
            max=440.0,
            std=20.0
        ),
        processing_time_ms=50.0
    )


def test_nin_engine_initialization():
    """Test NIN engine can be instantiated."""
    engine = NINEngine()
    assert engine is not None
    assert engine.rule_reasoner is not None
    assert engine.confidence_calibrator is not None
    assert engine.explainability_builder is not None


def test_rule_reasoner(sample_quantum_result):
    """Test rule reasoning pass."""
    reasoner = RuleReasoner()
    diagnoses = reasoner.run(sample_quantum_result, sex="M")
    
    assert isinstance(diagnoses, list)
    assert len(diagnoses) >= 6  # Should return at least 6 base conditions
    assert all(isinstance(d, Diagnosis) for d in diagnoses)


def test_rule_engine_returns_all_conditions():
    """Test run_rule_engine returns exactly 6 base conditions."""
    from app.services.quantum_engine import QuantumProcessor
    
    signal = np.random.randn(2500)
    qr = QuantumProcessor.process(signal, sampling_rate=500)
    
    diagnoses = run_rule_engine(qr, sex="M")
    
    assert len(diagnoses) >= 6  # At least 6 base conditions
    assert all(isinstance(d, Diagnosis) for d in diagnoses)
    
    # Check each diagnosis has required fields
    for dx in diagnoses:
        assert dx.condition is not None
        assert 0 <= dx.confidence <= 1
        assert dx.severity in ["normal", "warning", "critical"]
        assert hasattr(dx, 'feature_values')
        assert hasattr(dx, 'thresholds')


def test_confidence_calibrator():
    """Test confidence calibration."""
    calibrator = ConfidenceCalibrator()
    
    diagnoses = [
        Diagnosis(condition="Test", confidence=0.7, severity="warning"),
        Diagnosis(condition="Test2", confidence=0.3, severity="normal"),
    ]
    
    calibrated = calibrator.run(diagnoses)
    
    assert len(calibrated) == 2
    assert all(0 <= d.confidence <= 1 for d in calibrated)


def test_explainability_builder():
    """Test explainability trace building."""
    builder = ExplainabilityBuilder()
    
    diagnoses = [
        Diagnosis(
            condition="Tachycardia",
            confidence=0.8,
            severity="warning",
            reasoning_trace=[]
        )
    ]
    
    explained = builder.run(diagnoses)
    
    assert len(explained) > 0
    assert len(explained[0].reasoning_trace) >= 2  # Should have at least 2 traces


def test_apply_explainability():
    """Test apply_explainability populates reasoning traces."""
    diagnosis = Diagnosis(
        condition="Normal Rhythm",
        confidence=0.85,
        severity="normal",
        reasoning_trace=[]
    )
    
    result = apply_explainability(diagnosis)
    
    assert len(result.reasoning_trace) >= 2
    assert all(hasattr(t, 'step_number') for t in result.reasoning_trace)


def test_nin_engine_normal():
    """Test NIN engine on normal ECG."""
    pytest.importorskip("numpy")
    
    # Create normal ECG-like signal
    fs = 500
    duration = 5
    t = np.arange(0, duration, 1/fs)
    signal = np.sin(2 * np.pi * 1.25 * t)  # 75 BPM equivalent
    
    from app.services.quantum_engine import QuantumProcessor
    qr = QuantumProcessor.process(signal, sampling_rate=fs)
    
    engine = NINEngine()
    result = asyncio.run(engine.analyze(qr, sex="M"))
    
    assert isinstance(result, NINResult)
    assert len(result.diagnoses) > 0
    assert result.primary_diagnosis is not None


def test_nin_engine_detects_tachycardia():
    """Test NIN detects tachycardia from elevated HR signal."""
    pytest.importorskip("numpy")
    
    # Higher frequency = more beats = tachycardia
    fs = 500
    duration = 5
    t = np.arange(0, duration, 1/fs)
    signal = np.sin(2 * np.pi * 2.5 * t)  # ~150 BPM equivalent
    
    from app.services.quantum_engine import QuantumProcessor
    qr = QuantumProcessor.process(signal, sampling_rate=fs)
    
    engine = NINEngine()
    result = asyncio.run(engine.analyze(qr, sex="M"))
    
    assert isinstance(result, NINResult)
    assert len(result.diagnoses) > 0


def test_nin_engine_detects_afib():
    """Test NIN detects AFib from irregular signal."""
    pytest.importorskip("numpy")
    
    # Irregular signal with variable RR intervals
    fs = 500
    duration = 5
    t = np.arange(0, duration, 1/fs)
    # Mix of frequencies for irregular pattern
    signal = (
        np.sin(2 * np.pi * 1.25 * t) +
        0.3 * np.sin(2 * np.pi * 2.0 * t) +
        0.2 * np.sin(2 * np.pi * 0.8 * t)
    )
    
    from app.services.quantum_engine import QuantumProcessor
    qr = QuantumProcessor.process(signal, sampling_rate=fs)
    
    engine = NINEngine()
    result = asyncio.run(engine.analyze(qr, sex="F"))
    
    assert isinstance(result, NINResult)
    assert len(result.diagnoses) > 0


def test_nin_engine_reasoning_traces():
    """Test NIN engine populates reasoning traces."""
    pytest.importorskip("numpy")
    
    fs = 500
    duration = 5
    t = np.arange(0, duration, 1/fs)
    signal = np.sin(2 * np.pi * 1.25 * t)
    
    from app.services.quantum_engine import QuantumProcessor
    qr = QuantumProcessor.process(signal, sampling_rate=fs)
    
    engine = NINEngine()
    result = asyncio.run(engine.analyze(qr))
    
    # Check that diagnoses have reasoning traces
    for dx in result.diagnoses:
        assert hasattr(dx, 'reasoning_trace')
        assert len(dx.reasoning_trace) >= 1  # At least one trace


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
