import neurokit2 as nk

def detect_pqrst(ecg_cleaned, sampling_rate=500):
    """
    Detects PQRST complexes using neurokit2.
    Returns the signals dataframe and info dictionary.
    """
    try:
        # Extract R-peaks
        _, rpeaks = nk.ecg_peaks(ecg_cleaned, sampling_rate=sampling_rate)
        
        # Delineate the ECG signal to get P, Q, S, T peaks and boundaries
        _, waves_peak = nk.ecg_delineate(ecg_cleaned, rpeaks['ECG_R_Peaks'], sampling_rate=sampling_rate, method="peak")
        
        info = {**rpeaks, **waves_peak}
        return info
    except Exception as e:
        raise RuntimeError(f"PQRST detection failed: {str(e)}")
