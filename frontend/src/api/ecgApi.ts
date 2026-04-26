/**
 * ecgApi.ts — MedQuantum-NIN ECG API Client
 *
 * Backend router prefixes (must match exactly):
 *   POST /api/ecg/upload        → upload ECG file, returns ECGSignal (id = signal_id)
 *   POST /api/ecg/load-sample   → load PhysioNet WFDB record by name
 *   GET  /api/ecg/samples       → list available WFDB records
 *   POST /api/analysis/analyze  → run pipeline { signal_id }
 *   GET  /api/analysis/result/:id
 *   POST /api/report/generate   → generate SOAP report { signal_id }
 *
 * In LOCAL DEV: VITE_API_URL is empty — Vite proxy forwards /api/* → localhost:8000
 * In PRODUCTION: VITE_API_URL = https://medquantum-nin.onrender.com
 */

import axios from 'axios'
import type {
  AnalysisResult,
  ReportData,
  SignalQuality,
  ECGSignal,
  LeadName,
  AnalysisRequest,
} from '@/types/ecg.types'

// ─── Axios Instance ──────────────────────────────────────────────────────────

const api = axios.create({
  // Empty string → relative URLs → Vite proxy handles /api/* in dev
  // Production: set VITE_API_URL=https://medquantum-nin.onrender.com in .env.production
  baseURL: import.meta.env.VITE_API_URL ?? '',
  timeout: 120_000,
})

// Request logger — open DevTools → Console → filter "[ECG" to trace data flow
api.interceptors.request.use((config) => {
  console.debug(`[ECG API ▶] ${config.method?.toUpperCase()} ${config.baseURL ?? ''}${config.url}`)
  return config
})

// Error normalizer — always throws a plain Error with a human-readable message
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message ??
      'Unknown error'
    console.error(`[ECG API ✗] ${error.config?.url} →`, detail)
    return Promise.reject(new Error(String(detail)))
  }
)

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Map the backend ECGSignal schema to the frontend ECGSignal[] + SignalQuality shape.
 * Backend returns: { id, filename, sampling_rate, duration, leads[{name,signal,unit}], quality }
 */
function mapBackendECGSignal(raw: {
  id: string
  filename: string
  sampling_rate: number
  duration: number
  leads: Array<{ name: string; signal: number[]; unit: string }>
  quality: {
    overall_score: number
    snr_db: number | null
    baseline_wander: boolean
    clipping_ratio: number | null
  }
}): { signalId: string; filename: string; signals: ECGSignal[]; quality: SignalQuality } {
  const signals: ECGSignal[] = (raw.leads ?? []).map((lead) => ({
    lead: lead.name as LeadName,
    data: lead.signal,          // ← real waveform data from uploaded file
    samplingRate: raw.sampling_rate,
    duration: raw.duration,
    units: lead.unit,
  }))

  const quality: SignalQuality = {
    overall: raw.quality?.overall_score ?? 0,
    noiseLevel: raw.quality?.snr_db ?? 0,
    baselineWander: raw.quality?.baseline_wander ?? false,
    artifactRatio: raw.quality?.clipping_ratio ?? 0,
    leadQualities: {},
  }

  console.debug(
    `[ECG API ✓] signal_id=${raw.id} | leads=${signals.length} | ` +
    `duration=${raw.duration}s | first5=${signals[0]?.data.slice(0, 5).map(v => v.toFixed(3)).join(', ')}`
  )

  return { signalId: raw.id, filename: raw.filename, signals, quality }
}

// ─── API Functions ────────────────────────────────────────────────────────────

/**
 * STEP 1: Upload ECG file → real waveform data + signal_id for analysis.
 * Supports: .csv, .dat, .hea, .edf (max 50 MB)
 */
export async function uploadECGFile(
  file: File,
  onProgress?: (pct: number) => void
): Promise<{ signalId: string; filename: string; signals: ECGSignal[]; quality: SignalQuality }> {
  console.debug(`[ECG Upload] File: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`)

  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post('/api/ecg/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total))
    },
  })

  return mapBackendECGSignal(data)
}

/**
 * Load a PhysioNet WFDB sample record by numeric ID (e.g. "100").
 * This is for demonstration only — uses real PhysioNet data via backend.
 */
export async function loadWFDBSample(
  recordName: string
): Promise<{ signalId: string; filename: string; signals: ECGSignal[]; quality: SignalQuality }> {
  console.debug(`[WFDB Loader] Loading record: ${recordName}`)

  const { data } = await api.post('/api/ecg/load-sample', { record_name: recordName })

  return mapBackendECGSignal(data)
}

/**
 * STEP 2: Run full ECG analysis pipeline.
 * Backend expects: { signal_id: string }
 * Returns: features, diagnoses, overall_risk (NOT waveform — waveform comes from upload)
 */
export async function analyzeECG(
  request: AnalysisRequest
): Promise<{ data: AnalysisResult }> {
  console.debug(`[ECG Analysis] signal_id=${request.fileId}`)

  const { data } = await api.post('/api/analysis/analyze', {
    signal_id: request.fileId,   // fileId in frontend = signal_id in backend
  })

  console.debug(`[ECG Analysis ✓] risk=${data.overall_risk}, diagnoses=${data.diagnoses?.length}`)
  return { data }
}

/**
 * Get a cached analysis result by ID.
 */
export async function getAnalysisResult(
  analysisId: string
): Promise<{ data: AnalysisResult }> {
  const { data } = await api.get(`/api/analysis/result/${analysisId}`)
  return { data }
}

/**
 * STEP 3 (optional): Generate SOAP report.
 * Backend expects: { signal_id: string }
 */
export async function generateReport(
  signalId: string
): Promise<{ data: ReportData }> {
  console.debug(`[ECG Report] signal_id=${signalId}`)
  const { data } = await api.post('/api/report/generate', { signal_id: signalId })
  return { data }
}

/**
 * List available PhysioNet WFDB sample records from the backend.
 */
export async function listWFDBSamples(): Promise<
  Array<{ record_name: string; condition: string; duration: string; condition_type: string }>
> {
  const { data } = await api.get('/api/ecg/samples')
  return data
}

export default api
