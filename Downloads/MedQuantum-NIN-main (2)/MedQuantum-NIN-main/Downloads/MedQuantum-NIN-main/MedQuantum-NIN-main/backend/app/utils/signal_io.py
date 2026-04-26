import uuid
import json
import numpy as np
from pathlib import Path

import wfdb
from loguru import logger

from app.core.config import settings

# Constants for signal processing
MAX_SIGNAL_DURATION_SECONDS = 30
MIN_SIGNAL_DURATION_SECONDS = 2


def apply_signal_segment_slicing(
    signal: np.ndarray, 
    sampling_rate: int
) -> tuple[np.ndarray, bool, bool, str | None]:
    """
    Apply segment slicing to ECG signal data
    Ensures signals are within 2-30 seconds duration
    Returns: (processed_signal, was_sliced, was_padded, message)
    """
    current_duration = signal.shape[0] / sampling_rate
    max_samples = int(MAX_SIGNAL_DURATION_SECONDS * sampling_rate)
    min_samples = int(MIN_SIGNAL_DURATION_SECONDS * sampling_rate)
    
    processed_signal = signal.copy()
    was_sliced = False
    was_padded = False
    message = None

    # Handle long signals - slice to max duration
    if signal.shape[0] > max_samples:
        processed_signal = signal[:max_samples]
        was_sliced = True
        message = f"Long ECG detected — displaying first {MAX_SIGNAL_DURATION_SECONDS} seconds"
    # Handle short signals - pad to min duration
    elif signal.shape[0] < min_samples:
        last_value = signal[-1] if signal.shape[0] > 0 else 0.0
        padding_needed = min_samples - signal.shape[0]
        
        # Pad with last value and small noise to avoid flat lines
        signal_range = np.max(signal) - np.min(signal) if signal.shape[0] > 0 else 1.0
        noise = np.random.normal(0, signal_range * 0.05, padding_needed)  # ±5% noise
        
        if signal.ndim == 1:
            padding = last_value + noise
        else:
            padding = np.tile(last_value, (padding_needed, 1)) + noise.reshape(-1, 1)
        
        processed_signal = np.vstack([signal, padding]) if signal.ndim > 1 else np.concatenate([signal, padding])
        was_padded = True
        message = f"Short ECG detected — padded to {MIN_SIGNAL_DURATION_SECONDS} seconds"

    return processed_signal, was_sliced, was_padded, message


def load_wfdb_record(record_name: str) -> tuple[np.ndarray, dict]:
    """Load a WFDB record. Returns (signal_array shape [samples, leads], header_dict)."""
    sample_path = Path(settings.wfdb_sample_dir) / record_name
    try:
        record = wfdb.rdrecord(str(sample_path))
    except Exception:
        record = wfdb.rdrecord(record_name, pn_dir="mitdb")

    signal = record.p_signal
    if signal is None:
        signal = record.d_signal.astype(float) * record.adc_gain[0]

    # Apply segment slicing BEFORE any processing
    processed_signal, was_sliced, was_padded, message = apply_signal_segment_slicing(signal, record.fs)
    
    if message:
        logger.info(f"WFDB record {record_name}: {message}")

    header = {
        "fs": record.fs,
        "n_leads": record.n_sig,
        "sig_name": record.sig_name,
        "units": record.units,
        "sig_len": processed_signal.shape[0],  # Update length after slicing
        "record_name": record_name,
        "was_sliced": was_sliced,
        "was_padded": was_padded,
        "slicing_message": message,
    }
    return processed_signal, header


def load_csv_ecg(filepath: str) -> tuple[np.ndarray, int]:
    """Load ECG from CSV. Returns (signal_array, sampling_rate)."""
    import pandas as pd

    df = pd.read_csv(filepath)
    sampling_rate = 500

    time_cols = [c for c in df.columns if c.lower() in ("time", "t", "timestamp")]
    if time_cols:
        t = df[time_cols[0]].values
        if len(t) > 1:
            sampling_rate = int(round(1.0 / (t[1] - t[0])))
        signal_cols = [c for c in df.columns if c not in time_cols]
    else:
        signal_cols = list(df.columns)

    # Handle NaN values and ensure clean signal data
    signal = df[signal_cols].values.astype(np.float32)
    
    # Forward fill NaN values, then backward fill any remaining NaN
    if signal.ndim == 1:
        mask = ~np.isnan(signal)
        if mask.any():
            # Use interpolation for NaN values
            valid_indices = np.where(mask)[0]
            if len(valid_indices) > 1:
                signal = np.interp(np.arange(len(signal)), valid_indices, signal[mask])
            else:
                signal = np.nan_to_num(signal, nan=0.0)
        else:
            signal = np.zeros_like(signal)
        signal = signal.reshape(-1, 1)
    else:
        for col in range(signal.shape[1]):
            mask = ~np.isnan(signal[:, col])
            if mask.any():
                # Use interpolation for NaN values
                valid_indices = np.where(mask)[0]
                if len(valid_indices) > 1:
                    signal[:, col] = np.interp(np.arange(len(signal)), valid_indices, signal[mask, col])
                else:
                    signal[:, col] = np.nan_to_num(signal[:, col], nan=0.0)
            else:
                signal[:, col] = 0.0
    
    # Apply segment slicing BEFORE any processing
    processed_signal, was_sliced, was_padded, message = apply_signal_segment_slicing(signal, sampling_rate)
    
    if message:
        logger.info(f"CSV file {filepath}: {message}")
    
    return processed_signal, sampling_rate


def save_temp_signal(signal: np.ndarray, metadata: dict) -> str:
    """Save signal array and metadata to temp dir. Returns signal_id."""
    signal_id = str(uuid.uuid4())
    temp_dir = Path(settings.temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    np.save(str(temp_dir / f"{signal_id}.npy"), signal)
    with open(temp_dir / f"{signal_id}.json", "w") as f:
        json.dump({**metadata, "signal_id": signal_id}, f, default=str)

    logger.debug(f"Saved temp signal {signal_id}, shape={signal.shape}")
    return signal_id


def load_temp_signal(signal_id: str) -> tuple[np.ndarray, dict]:
    """Load a previously saved temp signal."""
    temp_dir = Path(settings.temp_dir)
    npy_path = temp_dir / f"{signal_id}.npy"
    json_path = temp_dir / f"{signal_id}.json"

    if not npy_path.exists():
        raise FileNotFoundError(f"Signal {signal_id} not found")

    signal = np.load(str(npy_path))
    with open(json_path) as f:
        metadata = json.load(f)
    return signal, metadata


def delete_temp_signal(signal_id: str) -> bool:
    """Delete temp signal files. Returns True if deleted."""
    temp_dir = Path(settings.temp_dir)
    deleted = False
    for ext in [".npy", ".json"]:
        p = temp_dir / f"{signal_id}{ext}"
        if p.exists():
            p.unlink()
            deleted = True
    return deleted


def get_available_wfdb_samples() -> list[dict]:
    """Return list of known PhysioNet MITDB sample records with metadata."""
    return [
        {"record_name": "100", "condition": "Normal sinus rhythm", "duration": "30 min", "condition_type": "normal"},
        {"record_name": "101", "condition": "Bundle branch block", "duration": "30 min", "condition_type": "conduction"},
        {"record_name": "200", "condition": "Ventricular ectopy", "duration": "30 min", "condition_type": "ventricular"},
        {"record_name": "202", "condition": "Multi-form PVCs", "duration": "30 min", "condition_type": "ventricular"},
        {"record_name": "203", "condition": "Run of ventricular tachycardia", "duration": "30 min", "condition_type": "ventricular"},
        {"record_name": "205", "condition": "Ventricular bigeminy", "duration": "30 min", "condition_type": "ventricular"},
        {"record_name": "207", "condition": "First degree AV block", "duration": "30 min", "condition_type": "conduction"},
        {"record_name": "210", "condition": "Right bundle branch block", "duration": "30 min", "condition_type": "conduction"},
    ]


def validate_signal(signal: np.ndarray, sampling_rate: int) -> None:
    """Validate signal array, raising ValueError with specific messages if invalid."""
    if signal is None or signal.size == 0:
        raise ValueError("Signal array is empty")
    if sampling_rate < 100 or sampling_rate > 10000:
        raise ValueError(f"Invalid sampling rate {sampling_rate}Hz. Expected 100-10000 Hz")
    if signal.ndim == 1:
        signal = signal.reshape(-1, 1)
    n_samples = signal.shape[0]
    duration = n_samples / sampling_rate
    if duration < 2.0:
        raise ValueError(f"Signal too short: {duration:.1f}s. Minimum 2 seconds required")
    if duration > 3600:
        raise ValueError(f"Signal too long: {duration:.0f}s. Maximum 1 hour")
    if np.all(np.isnan(signal)):
        raise ValueError("Signal contains only NaN values")
    finite_ratio = np.sum(np.isfinite(signal)) / signal.size
    if finite_ratio < 0.5:
        raise ValueError(f"Signal has too many non-finite values ({(1 - finite_ratio) * 100:.0f}%)")
