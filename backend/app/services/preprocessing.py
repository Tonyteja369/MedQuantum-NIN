import time

import numpy as np
from scipy import signal as scipy_signal
from scipy.interpolate import CubicSpline
from loguru import logger

from app.models.schemas import QualityMetrics


class ECGPreprocessor:
    def preprocess(self, raw_signal: np.ndarray, sampling_rate: int) -> tuple[np.ndarray, QualityMetrics]:
        """Full preprocessing pipeline. Returns (preprocessed_signal, quality_metrics)."""
        t0 = time.time()
        sig = raw_signal.copy().astype(np.float64)
        if sig.ndim == 1:
            sig = sig.reshape(-1, 1)

        sig = self.apply_notch_filter(sig, sampling_rate, 50.0)
        sig = self.apply_notch_filter(sig, sampling_rate, 60.0)
        t1 = time.time()
        logger.debug(f"Notch filter: {(t1 - t0) * 1000:.1f}ms")

        sig = self.apply_bandpass_filter(sig, sampling_rate)
        t2 = time.time()
        logger.debug(f"Bandpass filter: {(t2 - t1) * 1000:.1f}ms")

        sig = self.correct_baseline(sig, sampling_rate)
        t3 = time.time()
        logger.debug(f"Baseline correction: {(t3 - t2) * 1000:.1f}ms")

        sig = self.smooth_signal(sig)
        t4 = time.time()
        logger.debug(f"Smoothing: {(t4 - t3) * 1000:.1f}ms")

        quality = self.compute_quality_metrics(sig, sampling_rate)
        logger.info(
            f"Preprocessing complete in {(time.time() - t0) * 1000:.1f}ms, "
            f"quality={quality.overall_score:.1f}"
        )

        return sig, quality

    def apply_notch_filter(self, sig: np.ndarray, fs: int, freq: float) -> np.ndarray:
        b, a = scipy_signal.iirnotch(freq, Q=30, fs=fs)
        sos = scipy_signal.tf2sos(b, a)
        return scipy_signal.sosfiltfilt(sos, sig, axis=0)

    def apply_bandpass_filter(
        self, sig: np.ndarray, fs: int, lowcut: float = 0.5, highcut: float = 40.0
    ) -> np.ndarray:
        nyq = fs / 2
        low = lowcut / nyq
        high = min(highcut / nyq, 0.99)
        sos = scipy_signal.butter(4, [low, high], btype="band", output="sos")
        return scipy_signal.sosfiltfilt(sos, sig, axis=0)

    def correct_baseline(self, sig: np.ndarray, fs: int) -> np.ndarray:
        result = sig.copy()
        for ch in range(sig.shape[1]):
            channel = sig[:, ch]
            window = max(int(fs * 0.2), 1)
            n = len(channel)
            baseline_pts = []
            for i in range(0, n, window):
                segment = channel[i : i + window]
                if len(segment) > 0:
                    baseline_pts.append(np.percentile(segment, 10))
            x_pts = np.linspace(0, n - 1, len(baseline_pts))
            try:
                cs = CubicSpline(x_pts, baseline_pts)
                baseline = cs(np.arange(n))
                result[:, ch] = channel - baseline
            except Exception:
                result[:, ch] = channel - np.mean(channel)
        return result

    def smooth_signal(self, sig: np.ndarray) -> np.ndarray:
        from scipy.signal import savgol_filter

        result = sig.copy()
        for ch in range(sig.shape[1]):
            window = min(11, len(sig) // 2)
            if window % 2 == 0:
                window -= 1
            if window >= 5:
                result[:, ch] = savgol_filter(
                    sig[:, ch], window_length=window, polyorder=3
                )
        return result

    def compute_quality_metrics(self, sig: np.ndarray, fs: int) -> QualityMetrics:
        scores = []
        details = []
        snr_values = []
        clipping_ratios = []
        flatline_ratios = []
        noise_vars = []

        for ch in range(sig.shape[1]):
            channel = sig[:, ch]

            # SNR estimation
            signal_power = np.var(channel)
            noise_proxy = np.var(np.diff(channel)) / 2
            noise_vars.append(float(noise_proxy))
            if noise_proxy > 0 and signal_power > 0:
                snr = 10 * np.log10(signal_power / max(noise_proxy, 1e-10))
                snr_values.append(float(snr))
                snr_score = min(100, max(0, (snr + 10) * 5))
            else:
                snr_score = 50.0
            scores.append(snr_score)

            # Clipping detection
            max_val = np.max(np.abs(channel))
            clip_ratio = (
                np.sum(np.abs(channel) > 0.99 * max_val) / len(channel)
                if max_val > 0
                else 0
            )
            clipping_ratios.append(float(clip_ratio))
            if clip_ratio > 0.01:
                details.append(
                    f"Channel {ch}: possible clipping ({clip_ratio * 100:.1f}%)"
                )
                scores.append(max(0, 100 - clip_ratio * 500))

            # Flat line detection
            flat_ratio = np.sum(np.abs(np.diff(channel)) < 1e-6) / len(channel)
            flatline_ratios.append(float(flat_ratio))
            if flat_ratio > 0.1:
                details.append(
                    f"Channel {ch}: flat line detected ({flat_ratio * 100:.1f}%)"
                )
                scores.append(max(0, 100 - flat_ratio * 200))

        overall = float(np.mean(scores)) if scores else 50.0

        noise_var = float(
            np.mean([np.var(np.diff(sig[:, ch])) for ch in range(sig.shape[1])])
        )
        if noise_var < 0.001:
            noise_level = "low"
        elif noise_var < 0.01:
            noise_level = "medium"
        else:
            noise_level = "high"

        baseline_wander = False
        baseline_wander_power = None
        if len(sig) > 10:
            try:
                sos_lf = scipy_signal.butter(
                    2, 0.5 / (fs / 2), btype="low", output="sos"
                )
                lf = scipy_signal.sosfiltfilt(sos_lf, sig[:, 0])
                lf_power = np.var(lf)
                total_power = np.var(sig[:, 0])
                if total_power > 0 and lf_power / total_power > 0.3:
                    baseline_wander = True
                    details.append("Baseline wander detected")
                if total_power > 0:
                    baseline_wander_power = float(lf_power / total_power)
            except Exception:
                pass

        nan_ratio = float(np.sum(~np.isfinite(sig)) / sig.size)
        signal_loss = nan_ratio > 0.01
        if signal_loss:
            details.append(f"Signal loss: {nan_ratio * 100:.1f}% non-finite samples")

        return QualityMetrics(
            overall_score=round(overall, 1),
            noise_level=noise_level,
            baseline_wander=baseline_wander,
            signal_loss=signal_loss,
            details=details,
            snr_db=float(np.mean(snr_values)) if snr_values else None,
            clipping_ratio=float(np.mean(clipping_ratios))
            if clipping_ratios
            else None,
            flatline_ratio=float(np.mean(flatline_ratios))
            if flatline_ratios
            else None,
            noise_variance=float(np.mean(noise_vars)) if noise_vars else None,
            baseline_wander_power=baseline_wander_power,
            non_finite_ratio=nan_ratio,
        )
