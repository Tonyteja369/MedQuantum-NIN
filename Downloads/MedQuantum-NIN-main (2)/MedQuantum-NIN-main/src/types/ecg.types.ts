// ============================================================
// ECG Types — MedQuantum-NIN
// ============================================================

export type RiskLevel = 'normal' | 'borderline' | 'elevated' | 'critical'
export type Theme = 'dark' | 'light'
export type LeadName =
  | 'I' | 'II' | 'III'
  | 'aVR' | 'aVL' | 'aVF'
  | 'V1' | 'V2' | 'V3' | 'V4' | 'V5' | 'V6'

export interface ECGSignal {
  lead: LeadName
  data: number[]
  samplingRate: number
  duration: number
  units: string
}

export interface ECGUploadPayload {
  file: File
  leads?: LeadName[]
  samplingRate?: number
  patientId?: string
}

export interface SignalQuality {
  overall: number          // 0-100
  noiseLevel: number       // dB
  baselineWander: boolean
  artifactRatio: number    // 0-1
  leadQualities: Partial<Record<LeadName, number>>
}

export interface ECGIntervals {
  pr: number | null        // ms
  qrs: number | null       // ms
  qt: number | null        // ms
  qtc: number | null       // ms (corrected)
  rr: number | null        // ms
}

export interface ECGMetrics {
  heartRate: number                // bpm
  heartRateVariability: number     // ms (RMSSD)
  intervals: ECGIntervals
  axis: number | null              // degrees
  qrsAmplitude: number | null      // mV
  stDeviation: number | null       // mV
  tWaveAmplitude: number | null    // mV
}

export interface DiagnosisLabel {
  code: string             // e.g. "I48.0"
  label: string            // e.g. "Atrial Fibrillation"
  confidence: number       // 0-1
  category: string         // e.g. "Arrhythmia"
  icdVersion: '10' | '11'
}

export interface ExplainabilityNode {
  id: string
  feature: string
  contribution: number     // -1 to 1 (SHAP-like)
  importance: number       // 0-1
  children?: ExplainabilityNode[]
  description?: string
}

export interface RecommendationItem {
  priority: 'urgent' | 'high' | 'medium' | 'low'
  category: 'medication' | 'follow-up' | 'lifestyle' | 'monitoring' | 'referral'
  text: string
  rationale?: string
}

export interface AnalysisResult {
  id: string
  patientId?: string
  timestamp: string
  processingTimeMs: number
  signals: ECGSignal[]
  quality: SignalQuality
  metrics: ECGMetrics
  diagnoses: DiagnosisLabel[]
  primaryDiagnosis: DiagnosisLabel
  riskLevel: RiskLevel
  riskScore: number        // 0-100
  confidence: number       // 0-1
  explainability: ExplainabilityNode[]
  recommendations: RecommendationItem[]
  modelVersion: string
  quantumEnhanced: boolean
}

export interface SOAPNote {
  subjective: string
  objective: string
  assessment: string
  plan: string
}

export interface ReportData {
  analysisId: string
  generatedAt: string
  patientInfo?: PatientInfo
  soap: SOAPNote
  doctorSummary: string
  patientExplanation: string
  metrics: ECGMetrics
  diagnoses: DiagnosisLabel[]
  recommendations: RecommendationItem[]
  riskLevel: RiskLevel
  confidence: number
}

export interface PatientInfo {
  id: string
  age?: number
  sex?: 'M' | 'F' | 'O'
  weight?: number
  height?: number
  chiefComplaint?: string
  medications?: string[]
  allergies?: string[]
}

export interface UploadState {
  file: File | null
  fileId: string | null
  preview: ECGSignal[]
  quality: SignalQuality | null
  selectedLeads: LeadName[]
  isProcessing: boolean
  error: string | null
}

export interface AppState {
  theme: Theme
  sidebarCollapsed: boolean
  uploadState: UploadState
  analysisResult: AnalysisResult | null
  reportData: ReportData | null
}

// API response wrappers
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  errors?: string[]
}

export interface AnalysisRequest {
  fileId: string
  leads: LeadName[]
  patientInfo?: PatientInfo
  options?: {
    quantumEnhanced?: boolean
    generateReport?: boolean
    modelVersion?: string
  }
}
