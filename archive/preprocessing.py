import numpy as np
from scipy import signal
import pandas as pd

def load_ecg_file(file_path_or_bytes, is_csv=True):
    """Loads ECG signal from CSV or bytes."""
    if is_csv:
        # Assuming single column or first column is the signal
        try:
            df = pd.read_csv(file_path_or_bytes)
            # Pick the first numeric column
            col = df.select_dtypes(include=[np.number]).columns[0]
            sig = df[col].values
        except Exception:
            # Maybe it's not a standard CSV with header
            file_path_or_bytes.seek(0)
            sig = np.loadtxt(file_path_or_bytes, delimiter=',')
            if sig.ndim > 1:
                sig = sig[:, 0]
        return sig
    else:
        # Try loading as numpy binary
        sig = np.load(file_path_or_bytes)
        return sig

def preprocess_ecg(ecg_signal, sampling_rate=500):
    """
    Applies High-pass, Low-pass, and Notch filters to clean the ECG signal.
    """
    # 1. Notch filter to remove 50/60 Hz powerline noise
    # Let's use 50 Hz as default, quality factor 30
    freq = 50.0
    q = 30.0
    b_notch, a_notch = signal.iirnotch(freq, q, sampling_rate)
    sig_notch = signal.filtfilt(b_notch, a_notch, ecg_signal)

    # 2. High-pass filter to remove baseline wander (e.g., < 0.5 Hz)
    nyq = 0.5 * sampling_rate
    high_cutoff = 0.5 / nyq
    b_high, a_high = signal.butter(1, high_cutoff, btype='high')
    sig_high = signal.filtfilt(b_high, a_high, sig_notch)

    # 3. Low-pass filter to remove high frequency noise (e.g., > 150 Hz)
    low_cutoff = 150.0 / nyq
    b_low, a_low = signal.butter(1, low_cutoff, btype='low')
    sig_clean = signal.filtfilt(b_low, a_low, sig_high)

    return sig_clean
