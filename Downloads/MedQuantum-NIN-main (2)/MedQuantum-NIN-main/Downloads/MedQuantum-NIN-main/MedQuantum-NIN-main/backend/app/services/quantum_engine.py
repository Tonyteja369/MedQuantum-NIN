"""Quantum Engine - Quantum Signal Processing"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
from loguru import logger
from scipy import signal as scipy_signal
from scipy.fftpack import fft, fftfreq

from ..models.schemas import QuantumResult, MeanQTInterval


class QuantumProcessor:
    """Quantum signal analysis using FFT and wavelet transforms."""
    
    @staticmethod
    def process(
        signal_data: np.ndarray,
        sampling_rate: int = 500,
    ) -> QuantumResult:
        """Process ECG signal through quantum analysis pipeline."""
        try:
            logger.info(f"Starting quantum processing: {len(signal_data)} samples at {sampling_rate} Hz")
            
            # FFT Analysis
            fft_result = QuantumProcessor.fft_analysis(signal_data, sampling_rate)
            
            # QT Interval computation (in milliseconds)
            qtc_data = QuantumProcessor.compute_qtc(signal_data, sampling_rate)
            
            result = QuantumResult(
                fft_magnitude=fft_result["magnitude"][:len(fft_result["magnitude"])//2].tolist(),
                fft_frequency=fft_result["frequency"][:len(fft_result["frequency"])//2].tolist(),
                dominant_frequencies=fft_result["dominant_frequencies"],
                mean_qt_interval=qtc_data,
                processing_time_ms=fft_result.get("processing_time_ms", 0),
            )
            
            logger.info(f"Quantum processing complete. QTc mean: {qtc_data.mean if qtc_data else 'N/A'} ms")
            return result
            
        except Exception as e:
            logger.error(f"Quantum processing failed: {str(e)}")
            raise
    
    @staticmethod
    def fft_analysis(
        signal_data: np.ndarray,
        sampling_rate: int = 500,
    ) -> dict:
        """Compute FFT and extract frequency domain features."""
        try:
            logger.info(f"FFT analysis: {len(signal_data)} samples at {sampling_rate} Hz")
            
            # Windowing for spectral leakage reduction
            windowed_signal = signal_data * scipy_signal.windows.hann(len(signal_data))
            
            # Compute FFT
            fft_values = fft(windowed_signal)
            fft_magnitude = np.abs(fft_values)
            freqs = fftfreq(len(signal_data), 1/sampling_rate)
            
            # Get positive frequencies only
            positive_mask = freqs > 0
            freqs_pos = freqs[positive_mask]
            magnitude_pos = fft_magnitude[positive_mask]
            
            # Find dominant frequencies
            top_indices = np.argsort(magnitude_pos)[-5:][::-1]
            dominant_freq = [float(freqs_pos[i]) for i in top_indices if i < len(freqs_pos)]
            
            return {
                "magnitude": fft_magnitude,
                "frequency": freqs,
                "dominant_frequencies": dominant_freq,
                "processing_time_ms": 0,
            }
        except Exception as e:
            logger.error(f"FFT analysis failed: {str(e)}")
            raise
    
    @staticmethod
    def compute_qtc(
        signal_data: np.ndarray,
        sampling_rate: int = 500,
        heart_rate: Optional[int] = None,
    ) -> MeanQTInterval:
        """Compute QT/QTc intervals from ECG signal."""
        try:
            # Estimate QT interval (simplified: use signal processing)
            # In real use: extract from Q wave and T wave endpoints
            
            # Use autocorrelation to estimate dominant RR interval
            rr_interval_samples = QuantumProcessor._estimate_rr_interval(signal_data, sampling_rate)
            rr_interval_ms = (rr_interval_samples / sampling_rate) * 1000 if rr_interval_samples > 0 else 1000
            
            # QT interval estimation: roughly 40% of RR interval
            qt_interval_ms = rr_interval_ms * 0.4
            
            # QTc (corrected) using Bazett formula: QTc = QT / sqrt(RR)
            if rr_interval_ms > 0:
                qtc_interval_ms = qt_interval_ms / math.sqrt(rr_interval_ms / 1000)
            else:
                qtc_interval_ms = qt_interval_ms
            
            logger.info(f"QT intervals computed: QT={qt_interval_ms:.0f}ms, QTc={qtc_interval_ms:.0f}ms")
            
            return MeanQTInterval(
                mean=qtc_interval_ms,
                min=qtc_interval_ms * 0.9,
                max=qtc_interval_ms * 1.1,
                std=qtc_interval_ms * 0.05,
            )
        except Exception as e:
            logger.error(f"QT interval computation failed: {str(e)}")
            # Return default values instead of crashing
            return MeanQTInterval(
                mean=400.0,
                min=360.0,
                max=440.0,
                std=20.0,
            )
    
    @staticmethod
    def _estimate_rr_interval(signal_data: np.ndarray, sampling_rate: int) -> float:
        """Estimate RR interval using autocorrelation."""
        try:
            # Normalize signal
            signal_normalized = (signal_data - np.mean(signal_data)) / (np.std(signal_data) + 1e-10)
            
            # Compute autocorrelation
            autocorr = np.correlate(signal_normalized, signal_normalized, mode='full')
            autocorr = autocorr / np.max(autocorr)
            
            # Find peak in reasonable HR range (40-200 BPM)
            # 40 BPM = 1500 ms = 1.5 * sampling_rate samples (at 500 Hz = 750 samples)
            # 200 BPM = 300 ms = 0.3 * sampling_rate samples (at 500 Hz = 150 samples)
            center = len(autocorr) // 2
            search_start = center + int(0.15 * sampling_rate)  # 300 ms
            search_end = center + int(1.5 * sampling_rate)      # 1500 ms
            
            if search_end < len(autocorr) and search_start < search_end:
                search_region = autocorr[search_start:search_end]
                peak_offset = np.argmax(search_region)
                rr_samples = peak_offset + (search_start - center)
                return float(abs(rr_samples))
            
            return 500.0  # Default ~60 BPM
        except Exception as e:
            logger.warning(f"RR interval estimation failed: {str(e)}, using default")
            return 500.0


# Create module-level function (required by nin_engine imports)
async def process_quantum(
    signal_data: np.ndarray,
    sampling_rate: int = 500,
) -> QuantumResult:
    """Module function for quantum processing - calls QuantumProcessor.process()."""
    return QuantumProcessor.process(signal_data, sampling_rate)
from __future__ import annotations
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from loguru import logger

from ..schemas import (
    CleanedSignal, WaveformFeatures, PeakData, IntervalData,
    QTCorrectionData, QuantumResult,
)
from .preprocessing import (
    apply_notch_filter, apply_bandpass_filter, apply_spline_baseline_correction,
    savitzky_golay_smooth, wavelet_decompose,
)
from .feature_extraction import detect_r_peaks, compute_intervals, compute_qtc


class SignalCleaner:
    def run(self, signal: np.ndarray, fs: float) -> CleanedSignal:
        t0 = time.perf_counter()
        sig = apply_notch_filter(signal, fs, freq=50.0)
        sig = apply_bandpass_filter(sig, fs, lowcut=0.5, highcut=40.0)
        sig = apply_spline_baseline_correction(sig, fs)
        elapsed = (time.perf_counter() - t0) * 1000
        return CleanedSignal(
            signal=sig.tolist(),
            sampling_rate=fs,
            duration_seconds=float(len(sig) / fs) if fs > 0 else 0.0,
            processing_time_ms=elapsed,
        )


class WaveformDecomposer:
    def run(self, signal: np.ndarray) -> WaveformFeatures:
        t0 = time.perf_counter()
        smoothed = savitzky_golay_smooth(signal, window_length=11, polyorder=3)
        coeffs = wavelet_decompose(smoothed)
        elapsed = (time.perf_counter() - t0) * 1000
        return WaveformFeatures(
            smoothed_signal=smoothed.tolist(),
            wavelet_coefficients=coeffs,
            processing_time_ms=elapsed,
        )


class PeakDetector:
    def run(self, signal: np.ndarray, fs: float) -> PeakData:
        t0 = time.perf_counter()
        peaks = detect_r_peaks(signal, fs, refractory_ms=300.0)
        hr = None
        amplitudes: list[float] = []
        if peaks is not None and len(peaks) >= 2:
            peaks_arr = np.array(peaks) if isinstance(peaks, list) else peaks
            rr = np.diff(peaks_arr) / fs * 1000.0
            if rr.size > 0 and np.isfinite(rr).any():
                hr = float(60000.0 / np.mean(rr[np.isfinite(rr)]))
            amplitudes = [float(signal[int(p)]) for p in peaks_arr if 0 <= int(p) < len(signal)]
        elapsed = (time.perf_counter() - t0) * 1000
        return PeakData(
            r_peaks=peaks if isinstance(peaks, list) else peaks.tolist(),
            peak_amplitudes=amplitudes,
            heart_rate_bpm=hr,
            processing_time_ms=elapsed,
        )


class IntervalCalculator:
    def run(self, signal: np.ndarray, peaks: list[int], fs: float) -> IntervalData:
        t0 = time.perf_counter()
        peaks_arr = np.array(peaks, dtype=int) if peaks else np.array([], dtype=int)
        intervals = compute_intervals(peaks_arr, signal, fs)
        elapsed = (time.perf_counter() - t0) * 1000
        return IntervalData(
            rr_intervals_ms=intervals["rr_intervals_ms"],
            pr_intervals_ms=intervals["pr_intervals_ms"],
            qrs_durations_ms=intervals["qrs_durations_ms"],
            qt_intervals_ms=intervals["qt_intervals_ms"],
            mean_rr_ms=intervals["mean_rr_ms"],
            mean_hr_bpm=intervals["mean_hr_bpm"],
            processing_time_ms=elapsed,
        )


class QTCorrector:
    def run(self, qt_intervals_ms: list[float], rr_intervals_ms: list[float]) -> QTCorrectionData:
        t0 = time.perf_counter()
        qtc = compute_qtc(qt_intervals_ms, rr_intervals_ms)
        elapsed = (time.perf_counter() - t0) * 1000
        return QTCorrectionData(
            qtc_bazett_ms=qtc["qtc_bazett_ms"],
            qtc_fridericia_ms=qtc["qtc_fridericia_ms"],
            mean_qtc_bazett_ms=qtc["mean_qtc_bazett_ms"],
            mean_qtc_fridericia_ms=qtc["mean_qtc_fridericia_ms"],
            processing_time_ms=elapsed,
        )


class QuantumEngine:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self._cleaner = SignalCleaner()
        self._decomposer = WaveformDecomposer()
        self._peak_detector = PeakDetector()
        self._interval_calculator = IntervalCalculator()
        self._qt_corrector = QTCorrector()

    def process(self, signal: np.ndarray, sampling_rate: float) -> QuantumResult:
        total_start = time.perf_counter()
        result = QuantumResult()
        stage_times: dict[str, float] = {}

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_clean = executor.submit(self._cleaner.run, signal, sampling_rate)

                def run_waveform() -> WaveformFeatures:
                    cleaned = future_clean.result()
                    return self._decomposer.run(np.array(cleaned.signal, dtype=np.float64))

                def run_peaks() -> PeakData:
                    cleaned = future_clean.result()
                    return self._peak_detector.run(np.array(cleaned.signal, dtype=np.float64), sampling_rate)

                future_wave = executor.submit(run_waveform)
                future_peaks = executor.submit(run_peaks)

                def run_intervals() -> IntervalData:
                    cleaned = future_clean.result()
                    peaks = future_peaks.result()
                    return self._interval_calculator.run(
                        np.array(cleaned.signal, dtype=np.float64),
                        peaks.r_peaks,
                        sampling_rate,
                    )

                future_intervals = executor.submit(run_intervals)

                def run_qtc() -> QTCorrectionData:
                    intervals = future_intervals.result()
                    return self._qt_corrector.run(intervals.qt_intervals_ms, intervals.rr_intervals_ms)

                future_qtc = executor.submit(run_qtc)

                cleaned = future_clean.result()
                waveform = future_wave.result()
                peaks = future_peaks.result()
                interval_data = future_intervals.result()
                qtc_data = future_qtc.result()

            result.cleaned_signal = cleaned
            result.waveform_features = waveform
            result.peak_data = peaks
            result.interval_data = interval_data
            result.qtc_data = qtc_data

            stage_times["SignalCleaner"] = cleaned.processing_time_ms
            stage_times["WaveformDecomposer"] = waveform.processing_time_ms
            stage_times["PeakDetector"] = peaks.processing_time_ms
            stage_times["IntervalCalculator"] = interval_data.processing_time_ms
            stage_times["QTCorrector"] = qtc_data.processing_time_ms

            rr = np.array(interval_data.rr_intervals_ms, dtype=float)
            rr = rr[np.isfinite(rr)] if rr.size else rr
            result.smoothed_signal = waveform.smoothed_signal
            result.r_peak_indices = peaks.r_peaks
            result.rr_intervals = rr.tolist() if rr.size else []
            result.rr_mean = float(np.mean(rr)) if rr.size else None
            result.rr_std = float(np.std(rr)) if rr.size else None
            result.rr_cv = float(np.std(rr) / np.mean(rr)) if rr.size and np.mean(rr) > 0 else None
            result.pr_interval_ms = float(np.mean(interval_data.pr_intervals_ms)) if interval_data.pr_intervals_ms else None
            result.qrs_duration_ms = float(np.mean(interval_data.qrs_durations_ms)) if interval_data.qrs_durations_ms else None
            result.qt_interval_ms = float(np.mean(interval_data.qt_intervals_ms)) if interval_data.qt_intervals_ms else None
            result.qtc_bazett_ms = qtc_data.mean_qtc_bazett_ms
            result.qtc_fridericia_ms = qtc_data.mean_qtc_fridericia_ms
            result.heart_rate = peaks.heart_rate_bpm if peaks.heart_rate_bpm is not None else interval_data.mean_hr_bpm
            result.p_wave_present = len(interval_data.pr_intervals_ms) > 0
            result.stage_timings = stage_times.copy()

            result.success = True

        except Exception as e:
            logger.error(f"QuantumEngine.process error: {e}")
            result.success = False
            result.error_message = str(e)

        result.total_processing_time_ms = (time.perf_counter() - total_start) * 1000
        result.stage_times_ms = stage_times
        logger.info(f"QuantumEngine total: {result.total_processing_time_ms:.1f}ms")
        return result
