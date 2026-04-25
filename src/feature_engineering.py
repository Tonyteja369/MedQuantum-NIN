import numpy as np

def extract_features(pqrst_info, sampling_rate=500):
    """
    Extracts clinical features from PQRST info.
    Returns: HR, RR interval, PR interval, QRS duration, QT interval
    """
    r_peaks = pqrst_info.get('ECG_R_Peaks', [])
    p_peaks = pqrst_info.get('ECG_P_Peaks', [])
    q_peaks = pqrst_info.get('ECG_Q_Peaks', [])
    s_peaks = pqrst_info.get('ECG_S_Peaks', [])
    t_peaks = pqrst_info.get('ECG_T_Peaks', [])

    if len(r_peaks) < 2:
        raise ValueError("Not enough R peaks detected to extract features.")

    # Convert lists to numpy arrays and handle NaNs
    r_peaks = np.array([x for x in r_peaks if not np.isnan(x)])
    p_peaks = np.array([x for x in p_peaks if not np.isnan(x)])
    q_peaks = np.array([x for x in q_peaks if not np.isnan(x)])
    s_peaks = np.array([x for x in s_peaks if not np.isnan(x)])
    t_peaks = np.array([x for x in t_peaks if not np.isnan(x)])

    # RR Intervals
    rr_intervals = np.diff(r_peaks) / sampling_rate
    mean_rr = np.mean(rr_intervals)
    
    # Heart Rate (BPM)
    heart_rate = 60.0 / mean_rr if mean_rr > 0 else 0

    # PR Interval: average time between P peak and R peak
    pr_intervals = []
    for r in r_peaks:
        # Find nearest P peak before this R peak
        valid_ps = p_peaks[p_peaks < r]
        if len(valid_ps) > 0:
            pr_intervals.append((r - valid_ps[-1]) / sampling_rate)
    mean_pr = np.mean(pr_intervals) if len(pr_intervals) > 0 else 0.16  # default 160ms

    # QRS Duration: average time between Q peak and S peak
    qrs_durations = []
    for r in r_peaks:
        # Q before R, S after R
        valid_qs = q_peaks[q_peaks < r]
        valid_ss = s_peaks[s_peaks > r]
        if len(valid_qs) > 0 and len(valid_ss) > 0:
            # We take the nearest Q and nearest S
            qrs_durations.append((valid_ss[0] - valid_qs[-1]) / sampling_rate)
    mean_qrs = np.mean(qrs_durations) if len(qrs_durations) > 0 else 0.09  # default 90ms

    # QT Interval: average time between Q peak and T peak
    qt_intervals = []
    for r in r_peaks:
        valid_qs = q_peaks[q_peaks < r]
        valid_ts = t_peaks[t_peaks > r]
        if len(valid_qs) > 0 and len(valid_ts) > 0:
            qt_intervals.append((valid_ts[0] - valid_qs[-1]) / sampling_rate)
    mean_qt = np.mean(qt_intervals) if len(qt_intervals) > 0 else 0.40  # default 400ms

    features = {
        "heart_rate": round(heart_rate, 2),
        "rr_interval": round(mean_rr, 3),
        "pr_interval": round(mean_pr, 3),
        "qrs_duration": round(mean_qrs, 3),
        "qt_interval": round(mean_qt, 3)
    }
    return features

def normalize_features(features):
    """
    Normalizes features (Z-score based on synthetic population means)
    for the probabilistic model.
    """
    pop_means = {
        "heart_rate": 75.0,
        "rr_interval": 0.8,
        "pr_interval": 0.16,
        "qrs_duration": 0.09,
        "qt_interval": 0.40
    }
    pop_stds = {
        "heart_rate": 15.0,
        "rr_interval": 0.15,
        "pr_interval": 0.03,
        "qrs_duration": 0.02,
        "qt_interval": 0.04
    }

    normalized = {}
    for k, v in features.items():
        normalized[k] = (v - pop_means[k]) / pop_stds[k]
    
    return normalized
