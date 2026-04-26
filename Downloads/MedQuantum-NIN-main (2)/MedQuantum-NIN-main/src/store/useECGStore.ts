import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'
import type {
  Theme,
  AnalysisResult,
  ReportData,
  UploadState,
  LeadName,
  SignalQuality,
  ECGSignal,
} from '@/types/ecg.types'

interface ECGStore {
  // Persisted
  theme: Theme
  sidebarCollapsed: boolean

  // Upload
  uploadState: UploadState

  // Analysis
  analysisResult: AnalysisResult | null

  // Report
  reportData: ReportData | null

  // Actions — theme & layout
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void

  // Actions — upload
  setUploadFile: (file: File | null) => void
  setUploadFileId: (fileId: string | null) => void
  setUploadPreview: (preview: ECGSignal[]) => void
  setUploadQuality: (quality: SignalQuality | null) => void
  setSelectedLeads: (leads: LeadName[]) => void
  setUploadProcessing: (processing: boolean) => void
  setUploadError: (error: string | null) => void
  setUploadSlicingMessages: (messages: string[]) => void
  resetUpload: () => void

  // Actions — analysis
  setAnalysisResult: (result: AnalysisResult | null) => void
  clearAnalysis: () => void

  // Actions — report
  setReportData: (data: ReportData | null) => void
}

const defaultUploadState: UploadState = {
  file: null,
  fileId: null,
  preview: [],
  quality: null,
  selectedLeads: ['I', 'II', 'III', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
  isProcessing: false,
  error: null,
  slicingMessages: [],
}

export const useECGStore = create<ECGStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        theme: 'dark',
        sidebarCollapsed: false,
        uploadState: defaultUploadState,
        analysisResult: null,
        reportData: null,

        // Theme & layout
        setTheme: (theme) => set({ theme }),
        toggleTheme: () =>
          set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        toggleSidebar: () =>
          set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

        // Upload
        setUploadFile: (file) =>
          set((state) => ({
            uploadState: { ...state.uploadState, file, error: null },
          })),
        setUploadFileId: (fileId) =>
          {
            console.log('[STORE FILE SET]', { fileId })
            set((state) => ({
              uploadState: { ...state.uploadState, fileId },
            }))
          },
        setUploadPreview: (preview) =>
          set((state) => ({ uploadState: { ...state.uploadState, preview } })),
        setUploadQuality: (quality) =>
          set((state) => ({ uploadState: { ...state.uploadState, quality } })),
        setSelectedLeads: (leads) =>
          set((state) => ({
            uploadState: { ...state.uploadState, selectedLeads: leads },
          })),
        setUploadProcessing: (isProcessing) =>
          set((state) => ({ uploadState: { ...state.uploadState, isProcessing } })),
        setUploadError: (error) =>
          set((state) => ({ uploadState: { ...state.uploadState, error } })),
        setUploadSlicingMessages: (slicingMessages) =>
          set((state) => ({ uploadState: { ...state.uploadState, slicingMessages } })),
        resetUpload: () => set({ uploadState: defaultUploadState }),

        // Analysis
        setAnalysisResult: (analysisResult) => set({ analysisResult }),
        clearAnalysis: () => set({ analysisResult: null, reportData: null }),

        // Report
        setReportData: (reportData) => set({ reportData }),
      }),
      {
        name: 'medquantum-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
        }),
      }
    ),
    { name: 'MedQuantum-NIN' }
  )
)
