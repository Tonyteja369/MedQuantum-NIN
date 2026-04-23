import time

import numpy as np
from loguru import logger

from app.models.schemas import ECGFeatures, QualityMetrics


class ECGFeatureExtractor:
    def extract_features(
        self,
        signal: np.ndarray,
        sampling_rate: int,
        quality: QualityMetrics | None = None,
    ) -> ECGFeatures:
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
        rr_min = float(np.min(rr_intervals)) if len(rr_intervals) > 0 else None
        rr_max = float(np.max(rr_intervals)) if len(rr_intervals) > 0 else None
        rr_median = float(np.median(rr_intervals)) if len(rr_intervals) > 0 else None
        rr_iqr = (
            float(np.percentile(rr_intervals, 75) - np.percentile(rr_intervals, 25))
            if len(rr_intervals) > 0
            else None
        )

        heart_rate = self._compute_heart_rate(rr_intervals)
        hr_variability = self._compute_hrv(rr_intervals)
        hr_min, hr_max, hr_std = self._compute_hr_stats(rr_intervals)
        rr_rmssd, rr_sdsd, rr_pnn20, rr_pnn50 = self._compute_rr_variability(
            rr_intervals
        )
        hrv_cvsd = rr_rmssd / rr_mean if rr_rmssd is not None and rr_mean else None
        hrv_cvnn = rr_std / rr_mean if rr_std is not None and rr_mean else None
        hrv_triangular_index, hrv_tinn = self._compute_hrv_geometric(rr_intervals)
        freq_metrics = self._compute_frequency_domain(rr_intervals)

        pr_interval = None
        qrs_duration = None
        qt_interval = None
        qtc_interval = None
        qtc_framingham = None
        qtc_fridericia = None
        p_wave_duration = None
        t_wave_duration = None
        p_wave_amp = None
        q_wave_amp = None
        r_wave_amp = None
        s_wave_amp = None
        t_wave_amp = None
        st_segment_deviation = None
        st_slope = None
        qrs_area = None
        qt_dispersion = None

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
                qtc_framingham = self._compute_qtc_framingham(qt_interval, rr_mean)
                qtc_fridericia = self._compute_qtc_fridericia(qt_interval, rr_mean)

            try:
                morphology = self._compute_morphology_metrics(
                    ecg, sampling_rate, r_peaks
                )
                p_wave_duration = morphology.get("p_wave_duration")
                t_wave_duration = morphology.get("t_wave_duration")
                p_wave_amp = morphology.get("p_wave_amp")
                q_wave_amp = morphology.get("q_wave_amp")
                r_wave_amp = morphology.get("r_wave_amp")
                s_wave_amp = morphology.get("s_wave_amp")
                t_wave_amp = morphology.get("t_wave_amp")
                st_segment_deviation = morphology.get("st_segment_deviation")
                st_slope = morphology.get("st_slope")
                qrs_area = morphology.get("qrs_area")
                qt_dispersion = morphology.get("qt_dispersion")
            except Exception as e:
                logger.warning(f"Morphology extraction failed: {e}")

        axis_p, axis_qrs, axis_t = self._compute_axis(signal)
        lead_stats = self._compute_lead_stats(signal, sampling_rate)
        ectopy_metrics = self._compute_ectopy_metrics(rr_intervals, rr_mean)
        quality_metrics = self._quality_feature_map(quality)

        t1 = time.time()
        logger.info(
            f"Feature extraction complete in {(t1 - t0) * 1000:.1f}ms: "
            f"HR={heart_rate:.1f} bpm"
        )

        return ECGFeatures(
            heart_rate=round(heart_rate, 1),
            rr_intervals=[round(r, 1) for r in rr_intervals],
            pr_interval=round(pr_interval, 1) if pr_interval is not None else None,
            qrs_duration=round(qrs_duration, 1) if qrs_duration is not None else None,
            qt_interval=round(qt_interval, 1) if qt_interval is not None else None,
            qtc_interval=round(qtc_interval, 1) if qtc_interval is not None else None,
            rr_mean=round(rr_mean, 1),
            rr_std=round(rr_std, 1),
            hr_variability=round(hr_variability, 2),
            rr_min=round(rr_min, 1) if rr_min is not None else None,
            rr_max=round(rr_max, 1) if rr_max is not None else None,
            rr_median=round(rr_median, 1) if rr_median is not None else None,
            rr_iqr=round(rr_iqr, 1) if rr_iqr is not None else None,
            rr_rmssd=round(rr_rmssd, 1) if rr_rmssd is not None else None,
            rr_sdsd=round(rr_sdsd, 1) if rr_sdsd is not None else None,
            rr_pnn20=round(rr_pnn20, 1) if rr_pnn20 is not None else None,
            rr_pnn50=round(rr_pnn50, 1) if rr_pnn50 is not None else None,
            heart_rate_min=round(hr_min, 1) if hr_min is not None else None,
            heart_rate_max=round(hr_max, 1) if hr_max is not None else None,
            heart_rate_std=round(hr_std, 1) if hr_std is not None else None,
            hrv_sdnn=round(rr_std, 1) if rr_std is not None else None,
            hrv_rmssd=round(rr_rmssd, 1) if rr_rmssd is not None else None,
            hrv_sdsd=round(rr_sdsd, 1) if rr_sdsd is not None else None,
            hrv_cvsd=round(hrv_cvsd, 3) if hrv_cvsd is not None else None,
            hrv_cvnn=round(hrv_cvnn, 3) if hrv_cvnn is not None else None,
            hrv_triangular_index=round(hrv_triangular_index, 3)
            if hrv_triangular_index is not None
            else None,
            hrv_tinn=round(hrv_tinn, 1) if hrv_tinn is not None else None,
            freq_vlf_power=freq_metrics.get("vlf"),
            freq_lf_power=freq_metrics.get("lf"),
            freq_hf_power=freq_metrics.get("hf"),
            freq_total_power=freq_metrics.get("total"),
            freq_lf_hf_ratio=freq_metrics.get("lf_hf"),
            freq_peak_hz=freq_metrics.get("peak_hz"),
            p_wave_amp=p_wave_amp,
            q_wave_amp=q_wave_amp,
            r_wave_amp=r_wave_amp,
            s_wave_amp=s_wave_amp,
            t_wave_amp=t_wave_amp,
            p_wave_duration=p_wave_duration,
            t_wave_duration=t_wave_duration,
            st_segment_deviation=st_segment_deviation,
            st_slope=st_slope,
            qrs_area=qrs_area,
            qt_dispersion=qt_dispersion,
            qtc_framingham=qtc_framingham,
            qtc_fridericia=qtc_fridericia,
            axis_p=axis_p,
            axis_qrs=axis_qrs,
            axis_t=axis_t,
            r_peak_count=len(r_peaks),
            beat_count=len(r_peaks),
            ectopy_premature_count=ectopy_metrics.get("premature"),
            ectopy_pause_count=ectopy_metrics.get("pause"),
            ectopy_irregularity=ectopy_metrics.get("irregularity"),
            signal_duration=round(len(ecg) / sampling_rate, 2),
            sampling_rate=sampling_rate,
            lead_count=int(signal.shape[1]) if signal.ndim > 1 else 1,
            lead_mean_amp=lead_stats.get("mean_amp"),
            lead_std_amp=lead_stats.get("std_amp"),
            lead_peak_to_peak=lead_stats.get("ptp"),
            lead_rms=lead_stats.get("rms"),
            lead_kurtosis=lead_stats.get("kurtosis"),
            lead_skewness=lead_stats.get("skewness"),
            lead_noise_est=lead_stats.get("noise_est"),
            lead_baseline_wander=lead_stats.get("baseline_wander"),
            lead_signal_loss_ratio=lead_stats.get("signal_loss_ratio"),
            quality_score=quality_metrics.get("quality_score"),
            quality_snr=quality_metrics.get("quality_snr"),
            quality_clipping_ratio=quality_metrics.get("quality_clipping_ratio"),
            quality_flatline_ratio=quality_metrics.get("quality_flatline_ratio"),
            quality_noise_level=quality_metrics.get("quality_noise_level"),
            quality_noise_level_score=quality_metrics.get("quality_noise_level_score"),
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
        rr_s = rr_ms / 1000.0
        if rr_s <= 0:
            return qt_ms
        return qt_ms / np.sqrt(rr_s)

    def _compute_qtc_fridericia(self, qt_ms: float, rr_ms: float) -> float | None:
        rr_s = rr_ms / 1000.0
        if rr_s <= 0:
            return None
        return qt_ms / np.cbrt(rr_s)

    def _compute_qtc_framingham(self, qt_ms: float, rr_ms: float) -> float | None:
        rr_s = rr_ms / 1000.0
        if rr_s <= 0:
            return None
        return qt_ms + 154.0 * (1 - rr_s)

    def _compute_hr_stats(self, rr_intervals: list[float]) -> tuple[float | None, float | None, float | None]:
        if not rr_intervals:
            return None, None, None
        hr_series = 60000.0 / np.array(rr_intervals)
        return float(np.min(hr_series)), float(np.max(hr_series)), float(np.std(hr_series))

    def _compute_rr_variability(
        self, rr_intervals: list[float]
    ) -> tuple[float | None, float | None, float | None, float | None]:
        if len(rr_intervals) < 2:
            return None, None, None, None
        rr = np.array(rr_intervals)
        diff = np.diff(rr)
        rmssd = float(np.sqrt(np.mean(diff**2)))
        sdsd = float(np.std(diff))
        pnn20 = float(np.mean(np.abs(diff) > 20) * 100)
        pnn50 = float(np.mean(np.abs(diff) > 50) * 100)
        return rmssd, sdsd, pnn20, pnn50

    def _compute_hrv_geometric(
        self, rr_intervals: list[float]
    ) -> tuple[float | None, float | None]:
        if len(rr_intervals) < 2:
            return None, None
        rr = np.array(rr_intervals)
        bin_width = 7.8125
        bins = max(1, int((rr.max() - rr.min()) / bin_width))
        hist, _ = np.histogram(rr, bins=bins)
        if hist.max() == 0:
            return None, None
        triangular_index = len(rr) / hist.max()
        tinn = float(rr.max() - rr.min())
        return float(triangular_index), tinn

    def _compute_frequency_domain(self, rr_intervals: list[float]) -> dict:
        if len(rr_intervals) < 4:
            return {}
        try:
            from scipy import signal as scipy_signal

            rr = np.array(rr_intervals) / 1000.0
            times = np.cumsum(rr)
            if times[-1] <= 0:
                return {}
            fs = 4.0
            t_interp = np.arange(times[0], times[-1], 1 / fs)
            rr_interp = np.interp(t_interp, times, rr)
            freqs, psd = scipy_signal.welch(rr_interp, fs=fs, nperseg=min(256, len(rr_interp)))
            vlf_band = (freqs >= 0.0033) & (freqs < 0.04)
            lf_band = (freqs >= 0.04) & (freqs < 0.15)
            hf_band = (freqs >= 0.15) & (freqs < 0.4)
            vlf = float(np.trapz(psd[vlf_band], freqs[vlf_band])) if np.any(vlf_band) else None
            lf = float(np.trapz(psd[lf_band], freqs[lf_band])) if np.any(lf_band) else None
            hf = float(np.trapz(psd[hf_band], freqs[hf_band])) if np.any(hf_band) else None
            total = float(np.trapz(psd, freqs)) if len(freqs) > 0 else None
            lf_hf = float(lf / hf) if lf and hf and hf > 0 else None
            peak_hz = float(freqs[np.argmax(psd)]) if len(psd) else None
            return {
                "vlf": vlf,
                "lf": lf,
                "hf": hf,
                "total": total,
                "lf_hf": lf_hf,
                "peak_hz": peak_hz,
            }
        except Exception:
            return {}

    def _compute_morphology_metrics(
        self, ecg: np.ndarray, fs: int, r_peaks: np.ndarray
    ) -> dict:
        import neurokit2 as nk

        metrics: dict[str, float | None] = {
            "p_wave_duration": None,
            "t_wave_duration": None,
            "p_wave_amp": None,
            "q_wave_amp": None,
            "r_wave_amp": None,
            "s_wave_amp": None,
            "t_wave_amp": None,
            "st_segment_deviation": None,
            "st_slope": None,
            "qrs_area": None,
            "qt_dispersion": None,
        }
        try:
            _, waves = nk.ecg_delineate(ecg, r_peaks, sampling_rate=fs, method="dwt")
            p_peaks = waves.get("ECG_P_Peaks", [])
            q_peaks = waves.get("ECG_Q_Peaks", [])
            r_peaks = waves.get("ECG_R_Peaks", r_peaks)
            s_peaks = waves.get("ECG_S_Peaks", [])
            t_peaks = waves.get("ECG_T_Peaks", [])
            p_onsets = waves.get("ECG_P_Onsets", [])
            p_offsets = waves.get("ECG_P_Offsets", [])
            t_onsets = waves.get("ECG_T_Onsets", [])
            t_offsets = waves.get("ECG_T_Offsets", [])
            q_onsets = waves.get("ECG_Q_Peaks", [])
            t_offsets_for_qt = waves.get("ECG_T_Offsets", [])

            def _amp(peaks):
                vals = [ecg[int(p)] for p in peaks if p is not None and np.isfinite(p)]
                return float(np.mean(vals)) if vals else None

            metrics["p_wave_amp"] = _amp(p_peaks)
            metrics["q_wave_amp"] = _amp(q_peaks)
            metrics["r_wave_amp"] = _amp(r_peaks)
            metrics["s_wave_amp"] = _amp(s_peaks)
            metrics["t_wave_amp"] = _amp(t_peaks)

            def _duration(onsets, offsets):
                durations = []
                for on, off in zip(onsets, offsets):
                    if on is None or off is None or not np.isfinite(on) or not np.isfinite(off):
                        continue
                    if off > on:
                        durations.append((off - on) / fs * 1000)
                return float(np.mean(durations)) if durations else None

            metrics["p_wave_duration"] = _duration(p_onsets, p_offsets)
            metrics["t_wave_duration"] = _duration(t_onsets, t_offsets)

            qt_intervals = []
            for q_on, t_off in zip(q_onsets, t_offsets_for_qt):
                if q_on is None or t_off is None or not np.isfinite(q_on) or not np.isfinite(t_off):
                    continue
                if t_off > q_on:
                    qt_intervals.append((t_off - q_on) / fs * 1000)
            metrics["qt_dispersion"] = float(np.std(qt_intervals)) if qt_intervals else None

            st_vals = []
            st_slopes = []
            qrs_areas = []
            for r in r_peaks:
                if r is None or not np.isfinite(r):
                    continue
                r = int(r)
                st_point = r + int(0.06 * fs)
                st_point2 = r + int(0.08 * fs)
                if st_point2 >= len(ecg):
                    continue
                baseline_start = max(r - int(0.2 * fs), 0)
                baseline = float(np.mean(ecg[baseline_start:r])) if r > baseline_start else 0.0
                st_vals.append(float(ecg[st_point] - baseline))
                st_slopes.append(float(ecg[st_point2] - ecg[st_point]))
                qrs_window_start = max(r - int(0.04 * fs), 0)
                qrs_window_end = min(r + int(0.04 * fs), len(ecg))
                qrs_areas.append(float(np.trapz(np.abs(ecg[qrs_window_start:qrs_window_end]))))
            metrics["st_segment_deviation"] = float(np.mean(st_vals)) if st_vals else None
            metrics["st_slope"] = float(np.mean(st_slopes)) if st_slopes else None
            metrics["qrs_area"] = float(np.mean(qrs_areas)) if qrs_areas else None
        except Exception:
            return metrics
        return metrics

    def _compute_axis(self, signal: np.ndarray) -> tuple[float | None, float | None, float | None]:
        if signal.ndim < 2 or signal.shape[1] < 6:
            return None, None, None
        lead_i = signal[:, 0]
        lead_avf = signal[:, 5]
        try:
            amp_i = float(np.mean(lead_i))
            amp_avf = float(np.mean(lead_avf))
            axis_qrs = float(np.degrees(np.arctan2(amp_avf, amp_i)))
            return axis_qrs, axis_qrs, axis_qrs
        except Exception:
            return None, None, None

    def _compute_lead_stats(self, signal: np.ndarray, fs: int) -> dict:
        if signal.ndim == 1:
            signal = signal.reshape(-1, 1)
        try:
            from scipy import stats
            from scipy import signal as scipy_signal
        except Exception:
            stats = None
            scipy_signal = None
        finite = np.isfinite(signal)
        signal_loss_ratio = float(1 - np.mean(finite)) if signal.size else 0.0
        clean = np.where(finite, signal, 0.0)
        mean_amp = float(np.mean(np.abs(clean)))
        std_amp = float(np.mean(np.std(clean, axis=0)))
        ptp = float(np.mean(np.ptp(clean, axis=0)))
        rms = float(np.mean(np.sqrt(np.mean(clean**2, axis=0))))
        kurtosis = None
        skewness = None
        if stats is not None:
            try:
                kurtosis = float(np.mean(stats.kurtosis(clean, axis=0, fisher=False)))
                skewness = float(np.mean(stats.skew(clean, axis=0)))
            except Exception:
                kurtosis = None
                skewness = None
        noise_est = float(np.mean(np.var(np.diff(clean, axis=0), axis=0))) if len(clean) > 2 else None
        baseline_wander = None
        if scipy_signal is not None and len(clean) > 10:
            try:
                sos_lf = scipy_signal.butter(2, 0.5 / (fs / 2), btype="low", output="sos")
                lf = scipy_signal.sosfiltfilt(sos_lf, clean[:, 0])
                total_power = np.var(clean[:, 0])
                baseline_wander = float(np.var(lf) / total_power) if total_power > 0 else None
            except Exception:
                baseline_wander = None
        return {
            "mean_amp": round(mean_amp, 4),
            "std_amp": round(std_amp, 4),
            "ptp": round(ptp, 4),
            "rms": round(rms, 4),
            "kurtosis": round(kurtosis, 4) if kurtosis is not None else None,
            "skewness": round(skewness, 4) if skewness is not None else None,
            "noise_est": round(noise_est, 6) if noise_est is not None else None,
            "baseline_wander": round(baseline_wander, 4)
            if baseline_wander is not None
            else None,
            "signal_loss_ratio": round(signal_loss_ratio, 4),
        }

    def _compute_ectopy_metrics(self, rr_intervals: list[float], rr_mean: float) -> dict:
        if len(rr_intervals) < 2 or rr_mean <= 0:
            return {"premature": 0, "pause": 0, "irregularity": None}
        rr = np.array(rr_intervals)
        premature = int(np.sum(rr < 0.8 * rr_mean))
        pause = int(np.sum(rr > 1.5 * rr_mean))
        irregularity = float(np.std(rr) / np.mean(rr)) if np.mean(rr) > 0 else None
        return {"premature": premature, "pause": pause, "irregularity": irregularity}

    def _quality_feature_map(self, quality: QualityMetrics | None) -> dict:
        if not quality:
            return {}
        noise_level_score = {"low": 1.0, "medium": 2.0, "high": 3.0}.get(
            quality.noise_level, None
        )
        return {
            "quality_score": quality.overall_score,
            "quality_snr": quality.snr_db,
            "quality_clipping_ratio": quality.clipping_ratio,
            "quality_flatline_ratio": quality.flatline_ratio,
            "quality_noise_level": quality.noise_level,
            "quality_noise_level_score": noise_level_score,
        }
