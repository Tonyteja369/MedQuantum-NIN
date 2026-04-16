import axios from 'axios'
import type {
  AnalysisRequest,
  AnalysisResult,
  DiagnosisLabel,
  ECGMetrics,
  ECGSignal,
  ExplainabilityNode,
  PatientInfo,
  RecommendationItem,
  ReportData,
  RiskLevel,
  SignalQuality,
} from '@/types/ecg.types'

interface BackendQualityMetrics {
  overall_score: number
  noise_level: 'low' | 'medium' | 'high'
  baseline_wander: boolean
  signal_loss: boolean
  details: string[]
}

interface BackendLeadData {
  name: string
  signal: number[]
  unit: string
}

interface BackendECGSignal {
  id: string
  filename: string
  sampling_rate: number
  duration: number
  leads: BackendLeadData[]
  uploaded_at: string
  quality: BackendQualityMetrics
}

interface BackendECGFeatures {
  heart_rate: number
  rr_intervals: number[]
  pr_interval: number | null
  qrs_duration: number | null
  qt_interval: number | null
  qtc_interval: number | null
  rr_mean: number
  rr_std: number
  hr_variability: number
}

interface BackendReasoningStep {
  step: number
  description: string
  feature_used: string
  value: number | string
  threshold: string
  conclusion: string
}

interface BackendDiagnosisResult {
  id: string
  condition: string
  confidence: number
  severity: 'normal' | 'warning' | 'critical'
  supporting_features: string[]
  reasoning: BackendReasoningStep[]
  recommendations: string[]
}

interface BackendAnalysisResult {
  ecg_id: string
  features: BackendECGFeatures
  diagnoses: BackendDiagnosisResult[]
  overall_risk: 'normal' | 'low-risk' | 'moderate' | 'high-risk' | 'critical'
  processing_time: number
  timestamp: string
  model_version: string
}

interface BackendSOAPNote {
  subjective: string
  objective: string
  assessment: string
  plan: string
}

interface BackendReportResponse {
  analysis_result: BackendAnalysisResult
  patient_context?: Record<string, unknown> | null
  soap_note: BackendSOAPNote
  clinician_summary: string
  patient_summary: string
  generated_at: string
  report_id: string
}

export interface UploadResult {
  fileId: string
  filename: string
  preview: ECGSignal[]
  quality: SignalQuality
}

const api = axios.create({
  baseURL: resolveApiBaseUrl(import.meta.env.VITE_API_URL),
  timeout: 60_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function resolveApiBaseUrl(rawUrl: string | undefined): string {
  const value = (rawUrl ?? '').trim()

  if (!value) {
    if (import.meta.env.DEV) {
      return '/api'
    }

    throw new Error(
      'VITE_API_URL is required in production. Configure it in Vercel Project Settings.'
    )
  }

  if (/^https?:\/\/[^/]+$/i.test(value)) {
    return `${value}/api`
  }

  return value.replace(/\/$/, '')
}

api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.response?.data?.error ??
      error.message ??
      'An unknown error occurred'

    if (axios.isAxiosError(error)) {
      error.message = message
      return Promise.reject(error)
    }

    return Promise.reject(new Error(message))
  }
)

export async function uploadECGFile(
  file: File,
  onProgress?: (pct: number) => void
): Promise<UploadResult> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post<BackendECGSignal>('/ecg/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total))
    },
  })

  return adaptUploadResult(data)
}

const ANALYSIS_MAX_ATTEMPTS = 3
const ANALYSIS_BASE_DELAY_MS = 1000

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function shouldRetryAnalysis(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false

  if (error.code === 'ECONNABORTED') return true
  if (!error.response) return true

  const status = error.response.status
  return status === 408 || status === 429 || status >= 500
}

export async function analyzeECG(request: AnalysisRequest): Promise<AnalysisResult> {
  let lastError: unknown

  for (let attempt = 1; attempt <= ANALYSIS_MAX_ATTEMPTS; attempt += 1) {
    try {
      const { data } = await api.post<BackendAnalysisResult>('/analysis/analyze', {
        signal_id: request.fileId,
      })

      return adaptAnalysisResult(data)
    } catch (error) {
      lastError = error

      if (attempt === ANALYSIS_MAX_ATTEMPTS || !shouldRetryAnalysis(error)) {
        throw error
      }

      const backoff = ANALYSIS_BASE_DELAY_MS * 2 ** (attempt - 1)
      await sleep(backoff)
    }
  }

  throw lastError instanceof Error ? lastError : new Error('Analysis request failed')
}

export async function getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
  const { data } = await api.get<BackendAnalysisResult>(`/analysis/result/${analysisId}`)
  return adaptAnalysisResult(data)
}

export async function generateReport(
  signalId: string,
  patientInfo?: PatientInfo
): Promise<ReportData> {
  const { data } = await api.post<BackendReportResponse>('/report/generate', {
    signal_id: signalId,
    patient_context: patientInfo,
  })

  return adaptReportResult(data)
}

function adaptUploadResult(response: BackendECGSignal): UploadResult {
  const preview = response.leads.map((lead) => ({
    lead: lead.name as ECGSignal['lead'],
    data: lead.signal,
    samplingRate: response.sampling_rate,
    duration: response.duration,
    units: lead.unit,
  }))

  return {
    fileId: response.id,
    filename: response.filename,
    preview,
    quality: adaptQuality(response.quality, response.leads),
  }
}

function adaptQuality(
  quality: BackendQualityMetrics,
  leads: BackendLeadData[]
): SignalQuality {
  const leadQualityScore = quality.overall_score / 100
  const leadQualities = Object.fromEntries(
    leads.map((lead, index) => {
      const score = Math.max(0.05, Math.min(0.99, leadQualityScore - index * 0.03))
      return [lead.name, score]
    })
  ) as SignalQuality['leadQualities']

  return {
    overall: quality.overall_score,
    noiseLevel: quality.noise_level === 'low' ? 30 : quality.noise_level === 'medium' ? 20 : 10,
    baselineWander: quality.baseline_wander,
    artifactRatio: quality.signal_loss ? 0.18 : Math.max(0.01, (100 - quality.overall_score) / 100 * 0.12),
    leadQualities,
  }
}

function adaptAnalysisResult(
  response: BackendAnalysisResult,
  uploadContext?: Pick<UploadResult, 'preview' | 'quality'>
): AnalysisResult {
  const diagnoses = response.diagnoses.map((dx, index) => adaptDiagnosis(dx, index))
  const primaryDiagnosis = diagnoses[0] ?? fallbackDiagnosis()
  const riskLevel = adaptRiskLevel(response.overall_risk)

  return {
    id: response.ecg_id,
    patientId: undefined,
    timestamp: response.timestamp,
    processingTimeMs: response.processing_time,
    signals: uploadContext?.preview ?? [],
    quality:
      uploadContext?.quality ??
      adaptQuality(
        {
          overall_score: 85,
          noise_level: 'medium',
          baseline_wander: false,
          signal_loss: false,
          details: [],
        },
        uploadContext?.preview.map((signal) => ({
          name: signal.lead,
          signal: signal.data,
          unit: signal.units,
        })) ?? []
      ),
    metrics: adaptMetrics(response.features),
    diagnoses,
    primaryDiagnosis,
    riskLevel,
    riskScore: adaptRiskScore(riskLevel, primaryDiagnosis.confidence),
    confidence: primaryDiagnosis.confidence,
    explainability: buildExplainability(diagnoses),
    recommendations: collectRecommendations(diagnoses),
    modelVersion: response.model_version,
    quantumEnhanced: false,
  }
}

function adaptReportResult(response: BackendReportResponse): ReportData {
  const analysis = adaptAnalysisResult(response.analysis_result)

  return {
    analysisId: analysis.id,
    generatedAt: response.generated_at,
    patientInfo: response.patient_context as PatientInfo | undefined,
    soap: response.soap_note,
    doctorSummary: response.clinician_summary,
    patientExplanation: response.patient_summary,
    metrics: analysis.metrics,
    diagnoses: analysis.diagnoses,
    recommendations: analysis.recommendations,
    riskLevel: analysis.riskLevel,
    confidence: analysis.confidence,
  }
}

function adaptMetrics(features: BackendECGFeatures): ECGMetrics {
  return {
    heartRate: features.heart_rate,
    heartRateVariability: features.hr_variability,
    intervals: {
      pr: features.pr_interval,
      qrs: features.qrs_duration,
      qt: features.qt_interval,
      qtc: features.qtc_interval,
      rr: features.rr_mean,
    },
    axis: null,
    qrsAmplitude: null,
    stDeviation: null,
    tWaveAmplitude: null,
  }
}

function adaptDiagnosis(dx: BackendDiagnosisResult, index: number): DiagnosisLabel {
  const codeMap: Record<string, string> = {
    'Sinus Tachycardia': 'R00.0',
    'Sinus Bradycardia': 'R00.1',
    'Possible Atrial Fibrillation': 'I48.91',
    'QT Prolongation': 'I45.81',
    'Bundle Branch Block (Possible)': 'I45.4',
    'First-Degree AV Block': 'I44.0',
    'Normal Sinus Rhythm': 'Z13.6',
  }

  return {
    code: codeMap[dx.condition] ?? `ECG-${String(index + 1).padStart(2, '0')}`,
    label: dx.condition,
    confidence: dx.confidence,
    category: dx.severity === 'normal' ? 'Normal' : 'Abnormal',
    icdVersion: '10',
  }
}

function buildExplainability(diagnoses: DiagnosisLabel[]): ExplainabilityNode[] {
  return diagnoses.map((diagnosis, index) => ({
    id: diagnosis.code,
    feature: diagnosis.label,
    contribution: diagnosis.confidence * (index === 0 ? 0.95 : 0.65),
    importance: diagnosis.confidence,
    description: `${diagnosis.category} diagnosis, ICD-${diagnosis.icdVersion}: ${diagnosis.code}`,
    children: [],
  }))
}

function collectRecommendations(diagnoses: DiagnosisLabel[]): RecommendationItem[] {
  const unique = new Map<string, RecommendationItem>()

  for (const diagnosis of diagnoses) {
    const key = diagnosis.label
    if (unique.has(key)) continue

    unique.set(key, {
      priority: diagnosis.confidence > 0.9 ? 'high' : diagnosis.confidence > 0.75 ? 'medium' : 'low',
      category: diagnosis.category === 'Normal' ? 'follow-up' : 'monitoring',
      text: `${diagnosis.label} requires clinical review.`,
      rationale: `Generated from backend diagnosis ${diagnosis.code}.`,
    })
  }

  return Array.from(unique.values())
}

function adaptRiskLevel(level: BackendAnalysisResult['overall_risk']): RiskLevel {
  if (level === 'normal') return 'normal'
  if (level === 'low-risk') return 'borderline'
  if (level === 'moderate') return 'elevated'
  if (level === 'high-risk') return 'elevated'
  return 'critical'
}

function adaptRiskScore(level: RiskLevel, confidence: number): number {
  const base =
    level === 'normal' ? 8 : level === 'borderline' ? 28 : level === 'elevated' ? 62 : 92
  return Math.max(0, Math.min(100, Math.round(base * confidence + (100 - confidence * 100) * 0.1)))
}

function fallbackDiagnosis(): DiagnosisLabel {
  return {
    code: 'Z13.6',
    label: 'Normal Sinus Rhythm',
    confidence: 0.92,
    category: 'Normal',
    icdVersion: '10',
  }
}

export default api
