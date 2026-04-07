import uuid
import json
import re
import numpy as np
from pathlib import Path

import wfdb
from loguru import logger

from app.core.config import settings

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _validate_signal_id(signal_id: str) -> None:
    """Raise ValueError if signal_id is not a valid UUID v4 string."""
    if not _UUID_RE.match(signal_id):
        raise ValueError(f"Invalid signal_id format: {signal_id!r}")


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

    header = {
        "fs": record.fs,
        "n_leads": record.n_sig,
        "sig_name": record.sig_name,
        "units": record.units,
        "sig_len": record.sig_len,
        "record_name": record_name,
    }
    return signal, header


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

    signal = df[signal_cols].values.astype(np.float32)
    if signal.ndim == 1:
        signal = signal.reshape(-1, 1)
    return signal, sampling_rate


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
    _validate_signal_id(signal_id)
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
    _validate_signal_id(signal_id)
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
