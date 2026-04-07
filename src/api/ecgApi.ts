import axios from 'axios'
import type {
  ApiResponse,
  AnalysisResult,
  ReportData,
  SignalQuality,
  ECGSignal,
  AnalysisRequest,
} from '@/types/ecg.types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  timeout: 120_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ?? error.message ?? 'An unknown error occurred'
    return Promise.reject(new Error(message))
  }
)

// Upload ECG file and get a file ID back
export async function uploadECGFile(
  file: File,
  onProgress?: (pct: number) => void
): Promise<ApiResponse<{ fileId: string; filename: string }>> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post<ApiResponse<{ fileId: string; filename: string }>>(
    '/ecg/upload',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (e.total) onProgress?.(Math.round((e.loaded * 100) / e.total))
      },
    }
  )
  return data
}

// Preview raw ECG signals from an uploaded file
export async function previewECGSignal(
  fileId: string
): Promise<ApiResponse<{ signals: ECGSignal[]; quality: SignalQuality }>> {
  const { data } = await api.get<
    ApiResponse<{ signals: ECGSignal[]; quality: SignalQuality }>
  >(`/ecg/preview/${fileId}`)
  return data
}

// Run AI analysis
export async function analyzeECG(
  request: AnalysisRequest
): Promise<ApiResponse<AnalysisResult>> {
  const { data } = await api.post<ApiResponse<AnalysisResult>>('/ecg/analyze', request)
  return data
}

// Get analysis result by ID (for polling / retrieval)
export async function getAnalysisResult(
  analysisId: string
): Promise<ApiResponse<AnalysisResult>> {
  const { data } = await api.get<ApiResponse<AnalysisResult>>(
    `/ecg/analysis/${analysisId}`
  )
  return data
}

// Generate SOAP report
export async function generateReport(
  analysisId: string
): Promise<ApiResponse<ReportData>> {
  const { data } = await api.post<ApiResponse<ReportData>>(
    `/ecg/report/${analysisId}`
  )
  return data
}

export default api
