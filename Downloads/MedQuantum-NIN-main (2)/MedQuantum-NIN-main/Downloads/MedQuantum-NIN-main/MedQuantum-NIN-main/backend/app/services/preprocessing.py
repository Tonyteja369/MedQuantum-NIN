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

        # Handle signal duration constraints
        sig = self.adjust_signal_length(sig, sampling_rate)

        # Check minimum safe length for filtering
        min_samples_for_filtering = max(8, sampling_rate // 10)  # At least 8 samples or 0.1s worth
        can_apply_filters = sig.shape[0] >= min_samples_for_filtering

        if not can_apply_filters:
            logger.warning(f"Short signal detected ({sig.shape[0]} samples) — skipping filtering")

        # Only apply filters if signal is long enough
        if can_apply_filters:
            try:
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
            except Exception as e:
                logger.warning(f"Filtering failed for short signal: {e} — using raw signal")
                # Continue with raw signal if filtering fails

        quality = self.compute_quality_metrics(sig, sampling_rate)
        logger.info(
            f"Preprocessing complete in {(time.time() - t0) * 1000:.1f}ms, "
            f"quality={quality.overall_score:.1f}, filters_applied={can_apply_filters}"
        )

        return sig, quality

    def adjust_signal_length(self, sig: np.ndarray, sampling_rate: int) -> np.ndarray:
        """Adjust signal length to meet duration constraints (2-30 seconds)."""
        n_samples = sig.shape[0]
        current_duration = n_samples / sampling_rate
        
        # Target duration: 10 seconds (within 2-30s range)
        target_duration = 10.0
        target_samples = int(target_duration * sampling_rate)
        
        if current_duration < 2.0:
            # Pad short signals
            logger.info(f"Padding short signal from {current_duration:.1f}s to {target_duration:.1f}s")
            return self.pad_signal(sig, target_samples)
        elif current_duration > 30.0:
            # Trim long signals
            logger.info(f"Trimming long signal from {current_duration:.1f}s to {target_duration:.1f}s")
            return sig[:target_samples]
        elif current_duration < target_duration:
            # Extend signals shorter than target but longer than minimum
            return self.pad_signal(sig, target_samples)
        else:
            # Trim signals longer than target but within limits
            return sig[:target_samples]
    
    def pad_signal(self, sig: np.ndarray, target_samples: int) -> np.ndarray:
        """Pad signal to target length using last value and small noise."""
        n_samples = sig.shape[0]
        if n_samples >= target_samples:
            return sig[:target_samples]
        
        # Create padded signal
        padded = np.zeros((target_samples, sig.shape[1]))
        padded[:n_samples] = sig
        
        # Use last value for padding with small random noise to avoid flat lines
        last_values = sig[-1]
        for i in range(n_samples, target_samples):
            # Add small random noise (±5% of signal range)
            noise_factor = 0.05
            if sig.shape[1] == 1:
                signal_range = np.max(sig) - np.min(sig)
                noise = (np.random.random() - 0.5) * 2 * signal_range * noise_factor
                padded[i] = last_values + noise
            else:
                for ch in range(sig.shape[1]):
                    channel_range = np.max(sig[:, ch]) - np.min(sig[:, ch])
                    noise = (np.random.random() - 0.5) * 2 * channel_range * noise_factor
                    padded[i, ch] = last_values[ch] + noise
        
        return padded

    def apply_notch_filter(self, sig: np.ndarray, fs: int, freq: float) -> np.ndarray:
        # Safety check for very short signals
        if sig.shape[0] < 8:
            logger.warning(f"Signal too short for notch filter ({sig.shape[0]} samples) — skipping")
            return sig
            
        try:
            b, a = scipy_signal.iirnotch(freq, Q=30, fs=fs)
            sos = scipy_signal.tf2sos(b, a)
            return scipy_signal.sosfiltfilt(sos, sig, axis=0)
        except Exception as e:
            logger.warning(f"Notch filter failed: {e} — returning original signal")
            return sig

    def apply_bandpass_filter(
        self, sig: np.ndarray, fs: int, lowcut: float = 0.5, highcut: float = 40.0
    ) -> np.ndarray:
        # Safety check for very short signals
        if sig.shape[0] < 8:
            logger.warning(f"Signal too short for bandpass filter ({sig.shape[0]} samples) — skipping")
            return sig
            
        nyq = fs / 2
        low = lowcut / nyq
        high = min(highcut / nyq, 0.99)
        
        # Additional safety check for filter parameters
        if low >= high:
            logger.warning(f"Invalid filter parameters: low={low} >= high={high} — skipping")
            return sig
            
        try:
            sos = scipy_signal.butter(4, [low, high], btype="band", output="sos")
            return scipy_signal.sosfiltfilt(sos, sig, axis=0)
        except Exception as e:
            logger.warning(f"Bandpass filter failed: {e} — returning original signal")
            return sig

    def correct_baseline(self, sig: np.ndarray, fs: int) -> np.ndarray:
        """Remove baseline wander using scipy detrend with linear filtering."""
        result = sig.copy()
        for ch in range(sig.shape[1]):
            channel = sig[:, ch]
            try:
                # Use scipy detrend with 'linear' type for baseline correction
                # This applies a linear high-pass filter via detrending
                detrended = scipy_signal.detrend(channel, type='linear')
                result[:, ch] = detrended
            except Exception as e:
                logger.warning(f"Detrend failed on channel {ch}: {e}, using mean subtraction")
                result[:, ch] = channel - np.mean(channel)
        return result

    def smooth_signal(self, sig: np.ndarray) -> np.ndarray:
        from scipy.signal import savgol_filter

        # Safety check for very short signals
        if sig.shape[0] < 10:
            logger.warning(f"Signal too short for smoothing ({sig.shape[0]} samples) — skipping")
            return sig

        result = sig.copy()
        for ch in range(sig.shape[1]):
            window = min(11, len(sig) // 2)
            if window % 2 == 0:
                window -= 1
            if window >= 5:
                try:
                    result[:, ch] = savgol_filter(
                        sig[:, ch], window_length=window, polyorder=min(3, window-1)
                    )
                except Exception as e:
                    logger.warning(f"Smoothing failed on channel {ch}: {e} — using original")
                    # Keep original signal if smoothing fails
        return result

    def compute_quality_metrics(self, sig: np.ndarray, fs: int) -> QualityMetrics:
        scores = []
        details = []

        for ch in range(sig.shape[1]):
            channel = sig[:, ch]

            # SNR estimation
            signal_power = np.var(channel)
            noise_proxy = np.var(np.diff(channel)) / 2
            if noise_proxy > 0 and signal_power > 0:
                snr = 10 * np.log10(signal_power / max(noise_proxy, 1e-10))
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
            if clip_ratio > 0.01:
                details.append(
                    f"Channel {ch}: possible clipping ({clip_ratio * 100:.1f}%)"
                )
                scores.append(max(0, 100 - clip_ratio * 500))

            # Flat line detection
            flat_ratio = np.sum(np.abs(np.diff(channel)) < 1e-6) / len(channel)
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
        )
