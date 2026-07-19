# ECG Processing

## Input Handling

Implemented in `backend/app/routers/ecg.py` and `backend/app/utils/signal_io.py`.

- Supported upload formats: `.csv`, `.dat`, `.hea`, `.edf`
- Validation includes:
  - file size limit
  - sampling-rate bounds
  - duration bounds
  - finite-value checks

## Signal Quality

`ECGPreprocessor.compute_quality_metrics()` calculates:
- overall score (0-100)
- noise level (`low`, `medium`, `high`)
- baseline wander detection
- signal loss detection
- channel-level quality notes

## Feature Pipeline

`ECGFeatureExtractor` computes:
- `heart_rate`
- `rr_intervals`, `rr_mean`, `rr_std`
- `hr_variability`
- optional intervals: `pr_interval`, `qrs_duration`, `qt_interval`, `qtc_interval`

## Temporary Data Lifecycle

- Upload/load stores signal + metadata in `TEMP_DIR` via UUID identifiers.
- Signal/report caches are currently in-memory dictionaries.
- App shutdown deletes stale temp files older than 1 hour.
