from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    group: str
    unit: str
    description: str
    normal_range: Optional[tuple[float, float]] = None


FEATURE_SPECS: list[FeatureSpec] = [
    FeatureSpec("heart_rate", "rate", "bpm", "Average heart rate", (60, 100)),
    FeatureSpec("heart_rate_min", "rate", "bpm", "Minimum heart rate"),
    FeatureSpec("heart_rate_max", "rate", "bpm", "Maximum heart rate"),
    FeatureSpec("heart_rate_std", "rate", "bpm", "Heart rate standard deviation"),
    FeatureSpec("rr_mean", "rate", "ms", "Mean RR interval", (600, 1000)),
    FeatureSpec("rr_std", "rate", "ms", "RR interval standard deviation"),
    FeatureSpec("rr_min", "rate", "ms", "Minimum RR interval"),
    FeatureSpec("rr_max", "rate", "ms", "Maximum RR interval"),
    FeatureSpec("rr_median", "rate", "ms", "Median RR interval"),
    FeatureSpec("rr_iqr", "rate", "ms", "RR interval interquartile range"),
    FeatureSpec("rr_rmssd", "hrv_time", "ms", "RMSSD of RR intervals"),
    FeatureSpec("rr_sdsd", "hrv_time", "ms", "SDSD of RR intervals"),
    FeatureSpec("rr_pnn20", "hrv_time", "%", "Percentage of RR diff > 20 ms"),
    FeatureSpec("rr_pnn50", "hrv_time", "%", "Percentage of RR diff > 50 ms"),
    FeatureSpec("hrv_sdnn", "hrv_time", "ms", "SDNN", (20, 100)),
    FeatureSpec("hrv_rmssd", "hrv_time", "ms", "RMSSD"),
    FeatureSpec("hrv_sdsd", "hrv_time", "ms", "SDSD"),
    FeatureSpec("hrv_cvsd", "hrv_time", "-", "CV of RMSSD"),
    FeatureSpec("hrv_cvnn", "hrv_time", "-", "CV of SDNN"),
    FeatureSpec("hrv_triangular_index", "hrv_time", "-", "Triangular index"),
    FeatureSpec("hrv_tinn", "hrv_time", "ms", "TINN width"),
    FeatureSpec("freq_vlf_power", "hrv_freq", "ms^2", "VLF power"),
    FeatureSpec("freq_lf_power", "hrv_freq", "ms^2", "LF power"),
    FeatureSpec("freq_hf_power", "hrv_freq", "ms^2", "HF power"),
    FeatureSpec("freq_total_power", "hrv_freq", "ms^2", "Total power"),
    FeatureSpec("freq_lf_hf_ratio", "hrv_freq", "-", "LF/HF ratio"),
    FeatureSpec("freq_peak_hz", "hrv_freq", "Hz", "Peak frequency"),
    FeatureSpec("pr_interval", "intervals", "ms", "PR interval", (120, 200)),
    FeatureSpec("qrs_duration", "intervals", "ms", "QRS duration", (80, 120)),
    FeatureSpec("qt_interval", "intervals", "ms", "QT interval", (350, 440)),
    FeatureSpec("qtc_interval", "intervals", "ms", "Bazett QTc", (350, 450)),
    FeatureSpec("qtc_framingham", "intervals", "ms", "Framingham QTc"),
    FeatureSpec("qtc_fridericia", "intervals", "ms", "Fridericia QTc"),
    FeatureSpec("qt_dispersion", "intervals", "ms", "QT dispersion"),
    FeatureSpec("p_wave_amp", "morphology", "mV", "P-wave amplitude"),
    FeatureSpec("q_wave_amp", "morphology", "mV", "Q-wave amplitude"),
    FeatureSpec("r_wave_amp", "morphology", "mV", "R-wave amplitude"),
    FeatureSpec("s_wave_amp", "morphology", "mV", "S-wave amplitude"),
    FeatureSpec("t_wave_amp", "morphology", "mV", "T-wave amplitude"),
    FeatureSpec("p_wave_duration", "morphology", "ms", "P-wave duration"),
    FeatureSpec("t_wave_duration", "morphology", "ms", "T-wave duration"),
    FeatureSpec("st_segment_deviation", "morphology", "mV", "ST segment deviation"),
    FeatureSpec("st_slope", "morphology", "mV", "ST slope"),
    FeatureSpec("qrs_area", "morphology", "mV*ms", "QRS area"),
    FeatureSpec("axis_p", "axis", "deg", "P-wave axis"),
    FeatureSpec("axis_qrs", "axis", "deg", "QRS axis"),
    FeatureSpec("axis_t", "axis", "deg", "T-wave axis"),
    FeatureSpec("ectopy_premature_count", "ectopy", "count", "Premature beats"),
    FeatureSpec("ectopy_pause_count", "ectopy", "count", "Pauses"),
    FeatureSpec("ectopy_irregularity", "ectopy", "-", "RR irregularity index"),
    FeatureSpec("lead_mean_amp", "lead_stats", "mV", "Mean absolute amplitude"),
    FeatureSpec("lead_std_amp", "lead_stats", "mV", "Amplitude std dev"),
    FeatureSpec("lead_peak_to_peak", "lead_stats", "mV", "Peak-to-peak amplitude"),
    FeatureSpec("lead_rms", "lead_stats", "mV", "RMS amplitude"),
    FeatureSpec("lead_kurtosis", "lead_stats", "-", "Signal kurtosis"),
    FeatureSpec("lead_skewness", "lead_stats", "-", "Signal skewness"),
    FeatureSpec("lead_noise_est", "lead_stats", "-", "Noise estimate"),
    FeatureSpec("lead_baseline_wander", "lead_stats", "-", "Baseline wander ratio"),
    FeatureSpec("lead_signal_loss_ratio", "lead_stats", "-", "Signal loss ratio"),
    FeatureSpec("quality_score", "quality", "-", "Overall signal quality score"),
    FeatureSpec("quality_snr", "quality", "dB", "Signal-to-noise ratio"),
    FeatureSpec("quality_clipping_ratio", "quality", "-", "Clipping ratio"),
    FeatureSpec("quality_flatline_ratio", "quality", "-", "Flatline ratio"),
    FeatureSpec("quality_noise_level_score", "quality", "-", "Noise level score"),
    FeatureSpec("signal_duration", "metadata", "s", "Signal duration"),
    FeatureSpec("sampling_rate", "metadata", "Hz", "Sampling rate"),
    FeatureSpec("lead_count", "metadata", "count", "Number of leads"),
    FeatureSpec("r_peak_count", "metadata", "count", "R-peak count"),
    FeatureSpec("beat_count", "metadata", "count", "Beat count"),
]

FEATURE_INDEX = {spec.name: spec for spec in FEATURE_SPECS}


def get_feature_spec(name: str) -> Optional[FeatureSpec]:
    return FEATURE_INDEX.get(name)


def normalization_range(name: str) -> Optional[tuple[float, float]]:
    spec = FEATURE_INDEX.get(name)
    return spec.normal_range if spec else None
