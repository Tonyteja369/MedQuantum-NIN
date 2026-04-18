import json
import re
import shutil
import time
import uuid
from pathlib import Path

import numpy as np
import wfdb
from loguru import logger

from app.core.config import settings

WFDB_CACHE_DIR = Path('/tmp/wfdb_cache')

SAMPLE_REGISTRY = {
    'mitdb/100': {
        'pn_dir': 'mitdb',
        'record': '100',
        'description': 'Normal Sinus Rhythm',
        'expected_hr': 72,
    },
    'mitdb/200': {
        'pn_dir': 'mitdb',
        'record': '200',
        'description': 'Ventricular Ectopy',
        'expected_hr': 83,
    },
    'afdb/04015': {
        'pn_dir': 'afdb',
        'record': '04015',
        'description': 'Atrial Fibrillation',
        'expected_hr': 88,
    },
    'nsrdb/16265': {
        'pn_dir': 'nsrdb',
        'record': '16265',
        'description': 'Normal Sinus Rhythm DB',
        'expected_hr': 68,
    },
    'ptbdb/patient001/s0010_re': {
        'pn_dir': 'ptbdb/patient001',
        'record': 's0010_re',
        'description': 'Myocardial Infarction',
        'expected_hr': 65,
    },
}

MAX_DOWNLOAD_ATTEMPTS = 3
DOWNLOAD_RETRY_DELAY_SEC = 2

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _validate_signal_id(signal_id: str) -> None:
    """Raise ValueError if signal_id is not a valid UUID v4 string."""
    if not _UUID_RE.match(signal_id):
        raise ValueError(f"Invalid signal_id format: {signal_id!r}")


def _record_to_physical_signal(record: wfdb.io.Record, record_key: str) -> np.ndarray:
    if record.p_signal is not None:
        p_signal = record.p_signal.copy().astype(np.float64)
        logger.info(
            f"Using p_signal directly shape={p_signal.shape} "
            f"range=[{p_signal.min():.3f}, {p_signal.max():.3f}]"
        )
        return p_signal

    if record.d_signal is None:
        raise RuntimeError(f"No signal data in record {record_key}")

    logger.info("Converting d_signal to physical units")
    p_signal = np.zeros((record.sig_len, record.n_sig), dtype=np.float64)
    for i in range(record.n_sig):
        gain = record.adc_gain[i] if record.adc_gain else 200.0
        baseline = record.baseline[i] if record.baseline else 0
        p_signal[:, i] = (record.d_signal[:, i].astype(np.float64) - baseline) / gain

    logger.info(
        f"Converted: range=[{p_signal.min():.3f}, {p_signal.max():.3f}] mV"
    )
    return p_signal


def _record_to_metadata(record: wfdb.io.Record, record_name: str, extra: dict | None = None) -> dict:
    metadata = {
        'record_name': record_name,
        'fs': float(record.fs),
        'n_leads': record.n_sig,
        'sig_name': list(record.sig_name or []),
        'units': list(record.units or ['mV'] * record.n_sig),
        'sig_len': record.sig_len,
        'comments': list(record.comments or []),
    }
    if extra:
        metadata.update(extra)
    return metadata


def _download_sample_record(pn_dir: str, record_name: str, record_key: str) -> wfdb.io.Record:
    last_error: Exception | None = None
    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        try:
            logger.info(
                f"Downloading {record_key} (attempt {attempt}/{MAX_DOWNLOAD_ATTEMPTS})"
            )
            return wfdb.rdrecord(record_name, pn_dir=pn_dir, sampto=10800)
        except Exception as error:  # pragma: no cover - network path
            last_error = error
            if attempt == MAX_DOWNLOAD_ATTEMPTS:
                break
            logger.warning(
                f"Download attempt {attempt} failed for {record_key}: {error}. Retrying..."
            )
            time.sleep(DOWNLOAD_RETRY_DELAY_SEC)

    raise RuntimeError(
        f"Failed to download {record_key}: {str(last_error)}"
    )


def _cache_sample_record(pn_dir: str, record_name: str, cache_dir: Path, record_key: str) -> None:
    last_error: Exception | None = None
    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        try:
            wfdb.dl_database(
                pn_dir,
                dl_dir=str(cache_dir),
                records=[record_name],
                annotators=None,
            )
            return
        except Exception as error:  # pragma: no cover - network path
            last_error = error
            if attempt == MAX_DOWNLOAD_ATTEMPTS:
                break
            logger.warning(
                f"Cache attempt {attempt} failed for {record_key}: {error}. Retrying..."
            )
            time.sleep(DOWNLOAD_RETRY_DELAY_SEC)

    raise RuntimeError(
        f"Failed to cache {record_key}: {str(last_error)}"
    )


def load_uploaded_wfdb_record(record_path: str) -> tuple[np.ndarray, dict]:
    """Load a WFDB record uploaded from disk. Returns (signal_array, header_dict)."""
    record = wfdb.rdrecord(record_path)
    signal = _record_to_physical_signal(record, record_path)
    header = _record_to_metadata(record, record_path)
    return signal, header


def load_wfdb_record(record_key: str) -> tuple[dict, float, dict]:
    if record_key not in SAMPLE_REGISTRY:
        raise ValueError(
            f"Unknown record: {record_key}. "
            f"Valid records: {list(SAMPLE_REGISTRY.keys())}"
        )

    info = SAMPLE_REGISTRY[record_key]
    pn_dir = info['pn_dir']
    record_name = info['record']

    if pn_dir.startswith('ptbdb/'):
        logger.info(f"PTB fast path: loading {record_key} via rdsamp")
        signal = None
        fields = None
        last_error: Exception | None = None
        for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
            try:
                signal, fields = wfdb.rdsamp(record_name, pn_dir=pn_dir, sampto=10800)
                break
            except Exception as error:  # pragma: no cover - network path
                last_error = error
                if attempt == MAX_DOWNLOAD_ATTEMPTS:
                    break
                logger.warning(
                    f"PTB download attempt {attempt} failed for {record_key}: {error}. Retrying..."
                )
                time.sleep(DOWNLOAD_RETRY_DELAY_SEC)

        if signal is None or fields is None:
            raise RuntimeError(
                f"Failed to download {record_key}: {str(last_error)}"
            )

        p_signal = np.asarray(signal, dtype=np.float64)

        signal_std = np.std(p_signal[:, 0])
        if signal_std < 0.001:
            raise RuntimeError(
                f"Signal appears flat std={signal_std:.6f}. ADC conversion may have failed."
            )

        leads: dict[str, np.ndarray] = {}
        sig_names = list(fields.get('sig_name') or [])
        for i, name in enumerate(sig_names):
            leads[name] = p_signal[:, i].astype(np.float64)
            logger.info(
                f"Lead {name}: {len(leads[name])} samples range=[{leads[name].min():.3f}, {leads[name].max():.3f}] mV"
            )

        metadata = {
            'record_key': record_key,
            'description': info['description'],
            'pn_dir': pn_dir,
            'record_name': record_name,
            'n_sig': int(fields.get('n_sig', p_signal.shape[1])),
            'sig_name': sig_names,
            'units': list(fields.get('units') or ['mV'] * p_signal.shape[1]),
            'comments': list(fields.get('comments') or []),
        }

        return leads, float(fields['fs']), metadata

    cache_dir = WFDB_CACHE_DIR / pn_dir / record_name
    cache_dir.mkdir(parents=True, exist_ok=True)

    dat_files = list(cache_dir.rglob('*.dat'))
    record = None

    if dat_files:
        logger.info(f"Cache hit: {record_key}")
        local_record_path = str(cache_dir / record_name)
        try:
            record = wfdb.rdrecord(local_record_path)
            logger.info(
                f"Loaded from cache: {record.sig_name} fs={record.fs} len={record.sig_len}"
            )
        except Exception as e:
            logger.warning(f"Cache corrupt, re-downloading: {e}")
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            dat_files = []

    if record is None:
        logger.info(f"Cache miss: downloading {record_key}")
        try:
            record = _download_sample_record(pn_dir, record_name, record_key)
            _cache_sample_record(pn_dir, record_name, cache_dir, record_key)
            logger.info(f"Downloaded and cached: {record_key}")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise RuntimeError(
                f"Failed to download {record_key}: {str(e)}"
            )

    p_signal = _record_to_physical_signal(record, record_key)

    signal_std = np.std(p_signal[:, 0])
    if signal_std < 0.001:
        raise RuntimeError(
            f"Signal appears flat std={signal_std:.6f}. ADC conversion may have failed."
        )

    max_samples = int(record.fs * 30)
    if p_signal.shape[0] > max_samples:
        p_signal = p_signal[:max_samples, :]

    leads: dict[str, np.ndarray] = {}
    for i, name in enumerate(record.sig_name):
        leads[name] = p_signal[:, i].astype(np.float64)
        logger.info(
            f"Lead {name}: {len(leads[name])} samples range=[{leads[name].min():.3f}, {leads[name].max():.3f}] mV"
        )

    metadata = {
        'record_key': record_key,
        'description': info['description'],
        'pn_dir': pn_dir,
        'record_name': record_name,
        'n_sig': record.n_sig,
        'sig_name': record.sig_name,
        'units': record.units or ['mV'] * record.n_sig,
        'comments': record.comments or [],
    }

    return leads, float(record.fs), metadata


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
    return [
        {
            'record_key': key,
            'label': {
                'mitdb/100': 'MIT-BIH #100',
                'mitdb/200': 'MIT-BIH #200',
                'afdb/04015': 'AFDB #04015',
                'nsrdb/16265': 'NSR #16265',
                'ptbdb/patient001/s0010_re': 'PTB Diagnostic',
            }[key],
            'description': info['description'],
            'severity': {
                'mitdb/100': 'normal',
                'mitdb/200': 'warning',
                'afdb/04015': 'critical',
                'nsrdb/16265': 'normal',
                'ptbdb/patient001/s0010_re': 'critical',
            }[key],
        }
        for key, info in SAMPLE_REGISTRY.items()
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
