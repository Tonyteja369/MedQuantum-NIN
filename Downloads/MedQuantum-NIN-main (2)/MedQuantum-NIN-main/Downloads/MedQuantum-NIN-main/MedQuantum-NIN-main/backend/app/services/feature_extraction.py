import time

import numpy as np
from loguru import logger

from app.models.schemas import ECGFeatures


class ECGFeatureExtractor:
    def extract_features(self, signal: np.ndarray, sampling_rate: int) -> ECGFeatures:
        t0 = time.time()

        if signal.ndim > 1:
            ecg = signal[:, 0].astype(float)
        else:
            ecg = signal.astype(float)

        r_peaks = self._detect_r_peaks(ecg, sampling_rate)
        logger.debug(f"Detected {len(r_peaks)} R-peaks")

        rr_intervals = self._compute_rr_intervals(r_peaks, sampling_rate)
        rr_mean = float(np.mean(rr_intervals)) if len(rr_intervals) > 0 else 0.0
        rr_std = float(np.std(rr_intervals)) if len(rr_intervals) > 0 else 0.0

        heart_rate = self._compute_heart_rate(rr_intervals)
        hr_variability = self._compute_hrv(rr_intervals)

        pr_interval = None
        qrs_duration = None
        qt_interval = None
        qtc_interval = None

        if len(r_peaks) >= 3:
            try:
                pr_interval = self._compute_pr_interval(ecg, sampling_rate, r_peaks)
            except Exception as e:
                logger.warning(f"PR interval failed: {e}")

            try:
                qrs_duration = self._compute_qrs_duration(ecg, sampling_rate, r_peaks)
            except Exception as e:
                logger.warning(f"QRS duration failed: {e}")

            try:
                qt_interval = self._compute_qt_interval(ecg, sampling_rate, r_peaks)
            except Exception as e:
                logger.warning(f"QT interval failed: {e}")

            if qt_interval is not None and rr_mean > 0:
                qtc_interval = self._compute_qtc(qt_interval, rr_mean)

        t1 = time.time()
        logger.info(
            f"Feature extraction complete in {(t1 - t0) * 1000:.1f}ms: "
            f"HR={heart_rate:.1f} bpm"
        )

        # Compute qt_interval_ms from qt_interval (convert ms)
        qt_interval_ms = qt_interval  # already in ms from _compute_qt_interval

        return ECGFeatures(
            heart_rate=round(heart_rate, 1),
            rr_intervals=[round(r, 1) for r in rr_intervals],
            pr_interval=round(pr_interval, 1) if pr_interval is not None else None,
            qrs_duration=round(qrs_duration, 1) if qrs_duration is not None else None,
            qt_interval=round(qt_interval, 1) if qt_interval is not None else None,
            qt_interval_ms=round(qt_interval_ms, 1) if qt_interval_ms is not None else None,
            qtc_interval=round(qtc_interval, 1) if qtc_interval is not None else None,
            rr_mean=round(rr_mean, 1),
            rr_std=round(rr_std, 1),
            hr_variability=round(hr_variability, 2),
        )

    def _detect_r_peaks(self, ecg: np.ndarray, fs: int) -> np.ndarray:
        import neurokit2 as nk

        try:
            signals, info = nk.ecg_peaks(ecg, sampling_rate=fs, method="neurokit")
            peaks = info["ECG_R_Peaks"]
            min_rr_samples = int(fs * 0.2)
            validated = [peaks[0]] if len(peaks) > 0 else []
            for p in peaks[1:]:
                if p - validated[-1] >= min_rr_samples:
                    validated.append(p)
            return np.array(validated)
        except Exception as e:
            logger.warning(f"neurokit2 peak detection failed: {e}, using fallback")
            return self._fallback_r_peaks(ecg, fs)

    def _fallback_r_peaks(self, ecg: np.ndarray, fs: int) -> np.ndarray:
        """Simple threshold-based R-peak detection."""
        from scipy.signal import find_peaks

        threshold = np.mean(ecg) + 0.5 * np.std(ecg)
        min_dist = int(fs * 0.3)
        peaks, _ = find_peaks(ecg, height=threshold, distance=min_dist)
        return peaks

    def _compute_rr_intervals(self, r_peaks: np.ndarray, fs: int) -> list[float]:
        if len(r_peaks) < 2:
            return []
        rr_samples = np.diff(r_peaks)
        return [float(rr / fs * 1000) for rr in rr_samples]

    def _compute_heart_rate(self, rr_intervals: list[float]) -> float:
        if not rr_intervals:
            return 0.0
        mean_rr = np.mean(rr_intervals)
        if mean_rr <= 0:
            return 0.0
        return 60000.0 / mean_rr

    def _compute_hrv(self, rr_intervals: list[float]) -> float:
        """SDNN as primary HRV metric."""
        if len(rr_intervals) < 2:
            return 0.0
        return float(np.std(rr_intervals))

    def _compute_pr_interval(
        self, ecg: np.ndarray, fs: int, r_peaks: np.ndarray
    ) -> float | None:
        import neurokit2 as nk

        try:
            signals, waves = nk.ecg_delineate(
                ecg, r_peaks, sampling_rate=fs, method="dwt"
            )
            p_onsets = waves.get("ECG_P_Onsets", [])
            p_onsets = [p for p in p_onsets if p is not None and not np.isnan(p)]
            if len(p_onsets) < 2:
                return None
            intervals = []
            for r, p_on in zip(r_peaks[: len(p_onsets)], p_onsets):
                if p_on < r:
                    intervals.append((r - p_on) / fs * 1000)
            return float(np.median(intervals)) if intervals else None
        except Exception:
            return None

    def _compute_qrs_duration(
        self, ecg: np.ndarray, fs: int, r_peaks: np.ndarray
    ) -> float:
        import neurokit2 as nk

        try:
            signals, waves = nk.ecg_delineate(
                ecg, r_peaks, sampling_rate=fs, method="dwt"
            )
            q_onsets = waves.get("ECG_Q_Peaks", [])
            s_offsets = waves.get("ECG_S_Peaks", [])
            q_onsets = [q for q in q_onsets if q is not None and not np.isnan(q)]
            s_offsets = [s for s in s_offsets if s is not None and not np.isnan(s)]
            if not q_onsets or not s_offsets:
                return 80.0
            n = min(len(q_onsets), len(s_offsets))
            durations = [
                (s_offsets[i] - q_onsets[i]) / fs * 1000
                for i in range(n)
                if s_offsets[i] > q_onsets[i]
            ]
            return float(np.median(durations)) if durations else 90.0
        except Exception:
            return 90.0

    def _compute_qt_interval(
        self, ecg: np.ndarray, fs: int, r_peaks: np.ndarray
    ) -> float | None:
        import neurokit2 as nk

        try:
            signals, waves = nk.ecg_delineate(
                ecg, r_peaks, sampling_rate=fs, method="dwt"
            )
            q_onsets = waves.get("ECG_Q_Peaks", [])
            t_offsets = waves.get("ECG_T_Offsets", [])
            q_onsets = [q for q in q_onsets if q is not None and not np.isnan(q)]
            t_offsets = [t for t in t_offsets if t is not None and not np.isnan(t)]
            if not q_onsets or not t_offsets:
                return None
            n = min(len(q_onsets), len(t_offsets))
            intervals = [
                (t_offsets[i] - q_onsets[i]) / fs * 1000
                for i in range(n)
                if t_offsets[i] > q_onsets[i]
            ]
            return float(np.median(intervals)) if intervals else None
        except Exception:
            return None

    def _compute_qtc(self, qt_ms: float, rr_ms: float) -> float:
        """Bazett formula: QTc = QT / sqrt(RR in seconds)."""
        try:
            rr_s = rr_ms / 1000.0
            if rr_s <= 0:
                return qt_ms
            qtc = qt_ms / np.sqrt(rr_s)
            # Always return a valid float value
            return float(qtc) if not np.isnan(qtc) and not np.isinf(qtc) else qt_ms
        except Exception:
            # Return original QT interval if calculation fails
            return float(qt_ms)
