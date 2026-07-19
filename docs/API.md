# API Reference

This reference is generated from `backend/app/routers/*.py` and `backend/app/models/schemas.py`.

Base path for domain routes: `/api`

## Health Endpoints

### GET `/`
Returns service metadata.

### GET `/health`
Returns status, version, environment, and UTC timestamp.

## ECG Endpoints (`/api/ecg`)

### POST `/upload`
Upload ECG file (`.csv`, `.dat`, `.hea`, `.edf`).

- **Request**: `multipart/form-data` with `file`
- **Response**: `ECGSignal`
- **Errors**:
  - `400` unsupported format
  - `413` file too large
  - `422` invalid signal
  - `500` processing failure

### GET `/samples`
List available WFDB sample records.

- **Response**: array of `{ record_name, condition, duration, condition_type }`

### POST `/load-sample`
Load a sample record.

- **Request**: JSON `{ "record_name": "100" }`
- **Response**: `ECGSignal`
- **Errors**: `422`, `500`

### DELETE `/signal/{signal_id}`
Delete temporary signal artifacts.

- **Response**: `{ "deleted": "<signal_id>" }`
- **Errors**: `404`

## Analysis Endpoints (`/api/analysis`)

### POST `/analyze`
Run preprocessing, feature extraction, rule engine, optional ML placeholder, and explainability.

- **Request**: `AnalysisRequest` (`{ "signal_id": "uuid" }`)
- **Response**: `AnalysisResult`
- **Errors**: `404`, `422`, `500`

### GET `/result/{analysis_id}`
Get cached analysis result by analysis ID.

- **Response**: `AnalysisResult`
- **Errors**: `404`

### GET `/features/{signal_id}`
Extract features without full diagnosis.

- **Response**: `ECGFeatures`
- **Errors**: `404`

## Report Endpoints (`/api/report`)

### POST `/generate`
Generate report package from a signal ID.

- **Request**:
  ```json
  {
    "signal_id": "uuid",
    "patient_context": {
      "age": 54,
      "sex": "F",
      "symptoms": "palpitations"
    }
  }
  ```
- **Response**: `ReportResponse`
- **Errors**: `500` and propagated analysis errors

### GET `/export/{report_id}`
Fetch a previously generated report.

- **Response**: `ReportResponse`
- **Errors**: `404`

## Response Models

Key models are defined in `backend/app/models/schemas.py`:

- `ECGSignal`, `LeadData`, `QualityMetrics`
- `ECGFeatures`
- `DiagnosisResult`, `ReasoningStep`
- `AnalysisResult`
- `SOAPNote`, `ReportResponse`

## Notes on Frontend Contract

The frontend API client in `src/api/ecgApi.ts` includes additional client-side wrappers. Backend route truth is defined by this document and the backend router files.
