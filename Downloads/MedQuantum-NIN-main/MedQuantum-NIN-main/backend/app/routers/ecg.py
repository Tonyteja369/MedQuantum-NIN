import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
import numpy as np
from fastapi import APIRouter, Body, File, HTTPException, UploadFile
from loguru import logger

from app.core.config import settings
from app.models.schemas import ECGSignal, LeadData, QualityMetrics
from app.services.preprocessing import ECGPreprocessor
from app.utils.signal_io import (
    delete_temp_signal,
    get_available_wfdb_samples,
    load_csv_ecg,
    load_wfdb_record,
    save_temp_signal,
    validate_signal,
)

router = APIRouter(prefix="/api/ecg", tags=["ECG"])
preprocessor = ECGPreprocessor()

ALLOWED_EXTENSIONS = {".csv", ".dat", ".hea", ".edf"}


@router.post("/upload", response_model=ECGSignal, summary="Upload ECG file")
async def upload_ecg(file: UploadFile = File(...)):
    """Upload an ECG file (.csv, .dat, .hea, .edf). Returns ECGSignal with quality metrics."""
    suffix = Path(file.filename or "unknown").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400, f"Unsupported format: {suffix}. Allowed: {ALLOWED_EXTENSIONS}"
        )

    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(413, f"File too large. Max {settings.max_upload_size_mb}MB")

    temp_dir = Path(settings.temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    raw_path = temp_dir / f"upload_{uuid.uuid4()}{suffix}"

    async with aiofiles.open(raw_path, "wb") as f:
        await f.write(content)

    try:
        if suffix == ".csv":
            signal, fs = load_csv_ecg(str(raw_path))
        else:
            record_stem = str(raw_path.with_suffix(""))
            signal, header = load_wfdb_record(record_stem)
            fs = header["fs"]

        validate_signal(signal, fs)
        signal_2d = signal if signal.ndim == 2 else signal.reshape(-1, 1)
        _, quality = preprocessor.preprocess(signal_2d, fs)

        signal_id = save_temp_signal(
            signal_2d, {"filename": file.filename, "sampling_rate": fs}
        )

        lead_names = [
            "I", "II", "III", "aVR", "aVL", "aVF",
            "V1", "V2", "V3", "V4", "V5", "V6",
        ]
        n_leads = signal_2d.shape[1]
        leads = [
            LeadData(
                name=lead_names[i] if i < len(lead_names) else f"Lead {i + 1}",
                signal=signal_2d[:, i].tolist(),
                unit="mV",
            )
            for i in range(n_leads)
        ]

        return ECGSignal(
            id=signal_id,
            filename=file.filename or "unknown",
            sampling_rate=int(fs),
            duration=round(len(signal_2d) / fs, 2),
            leads=leads,
            uploaded_at=datetime.now(timezone.utc),
            quality=quality,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(500, "Signal processing failed")
    finally:
        raw_path.unlink(missing_ok=True)


@router.get("/samples", summary="List available WFDB sample records")
async def list_samples():
    """Returns list of available PhysioNet sample records."""
    return get_available_wfdb_samples()


@router.post("/load-sample", response_model=ECGSignal, summary="Load a WFDB sample record")
async def load_sample(record_name: str = Body(..., embed=True)):
    """Load a PhysioNet WFDB record by name."""
    try:
        signal, header = load_wfdb_record(record_name)
        fs = header["fs"]
        validate_signal(signal, fs)
        signal_2d = signal if signal.ndim == 2 else signal.reshape(-1, 1)

        max_samples = fs * 30
        signal_2d = signal_2d[:max_samples]

        _, quality = preprocessor.preprocess(signal_2d, fs)
        signal_id = save_temp_signal(
            signal_2d, {"filename": record_name, "sampling_rate": fs}
        )

        sig_names = header.get("sig_name", [])
        leads = [
            LeadData(
                name=sig_names[i] if i < len(sig_names) else f"Lead {i + 1}",
                signal=signal_2d[:, i].tolist(),
                unit="mV",
            )
            for i in range(signal_2d.shape[1])
        ]

        return ECGSignal(
            id=signal_id,
            filename=record_name,
            sampling_rate=int(fs),
            duration=round(len(signal_2d) / fs, 2),
            leads=leads,
            uploaded_at=datetime.now(timezone.utc),
            quality=quality,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        logger.error(f"Load sample failed: {e}")
        raise HTTPException(500, f"Failed to load record {record_name}: {str(e)}")


@router.delete("/signal/{signal_id}", summary="Delete a temp signal")
async def delete_signal(signal_id: str):
    """Clean up temp files for a signal."""
    deleted = delete_temp_signal(signal_id)
    if not deleted:
        raise HTTPException(404, f"Signal {signal_id} not found")
    return {"deleted": signal_id}
