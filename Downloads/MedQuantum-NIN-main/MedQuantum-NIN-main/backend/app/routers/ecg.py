import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile
from loguru import logger

from app.core.config import settings
from app.models.schemas import ECGSignal, LeadData, LoadSampleRequest, QualityMetrics
from app.services.preprocessing import ECGPreprocessor
from app.utils.signal_io import (
    delete_temp_signal,
    get_available_wfdb_samples,
    load_csv_ecg,
    load_wfdb_record,
    load_uploaded_wfdb_record,
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

    raw_path.write_bytes(content)

    try:
        if suffix == ".csv":
            signal, fs = load_csv_ecg(str(raw_path))
        else:
            record_stem = str(raw_path.with_suffix(""))
            signal, header = load_uploaded_wfdb_record(record_stem)
            fs = int(header["fs"])

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
async def load_sample(request_body: LoadSampleRequest, request: Request):
    record_key = request_body.record_name.strip()
    logger.info(f"Loading sample: {record_key}")

    try:
        leads, sampling_rate, metadata = load_wfdb_record(record_key)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    except Exception as e:
        logger.error(f"Unexpected error loading {record_key}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load sample: {str(e)}"
        )

    signal_id = str(uuid.uuid4())
    duration = len(next(iter(leads.values()))) / sampling_rate

    request.app.state.signals[signal_id] = {
        'leads': leads,
        'sampling_rate': sampling_rate,
        'record_key': record_key,
        'metadata': metadata,
    }

    lead_data_list = []
    for lead_name, signal_array in leads.items():
        if len(signal_array) < 100:
            logger.warning(f"Lead {lead_name} too short, skipping")
            continue
        if np.std(signal_array) < 0.0001:
            logger.warning(f"Lead {lead_name} appears flat, skipping")
            continue

        lead_data_list.append(
            LeadData(
                name=lead_name,
                signal=signal_array.tolist(),
                unit='mV',
            )
        )
        logger.info(
            f"Adding lead {lead_name}: {len(signal_array)} samples std={np.std(signal_array):.4f} mV"
        )

    if not lead_data_list:
        raise HTTPException(
            status_code=500,
            detail='All leads contained flat or invalid data'
        )

    logger.info(
        f"Sample loaded: {record_key} id={signal_id} leads={len(lead_data_list)} duration={duration:.1f}s fs={sampling_rate}Hz"
    )

    return ECGSignal(
        id=signal_id,
        filename=record_key,
        sampling_rate=int(sampling_rate),
        duration=duration,
        leads=lead_data_list,
        uploaded_at=datetime.now(timezone.utc),
        quality=QualityMetrics(
            overall_score=88.0,
            noise_level='low',
            baseline_wander=False,
            signal_loss=False,
            details=[f"Loaded from PhysioNet {metadata['pn_dir']}"],
        ),
    )


@router.delete("/signal/{signal_id}", summary="Delete a temp signal")
async def delete_signal(signal_id: str):
    """Clean up temp files for a signal."""
    deleted = delete_temp_signal(signal_id)
    if not deleted:
        raise HTTPException(404, f"Signal {signal_id} not found")
    return {"deleted": signal_id}
