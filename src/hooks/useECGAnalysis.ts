import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useECGStore } from '@/store/useECGStore'
import { analyzeECG, generateReport, getAnalysisResult } from '@/api/ecgApi'
import type { AnalysisRequest, PatientInfo } from '@/types/ecg.types'

export function useECGAnalysis() {
  const navigate = useNavigate()
  const setAnalysisResult = useECGStore((s) => s.setAnalysisResult)
  const setReportData = useECGStore((s) => s.setReportData)
  const uploadState = useECGStore((s) => s.uploadState)
  const analysisResult = useECGStore((s) => s.analysisResult)

  const analyzeMutation = useMutation({
    mutationFn: (request: AnalysisRequest) => analyzeECG(request),
    onSuccess: (response) => {
      setAnalysisResult(response.data)
      navigate('/analysis')
    },
  })

  const reportMutation = useMutation({
    mutationFn: (analysisId: string) => generateReport(analysisId),
    onSuccess: (response) => {
      setReportData(response.data)
      navigate('/report')
    },
  })

  const runAnalysis = (fileId: string, patientInfo?: PatientInfo) => {
    const request: AnalysisRequest = {
      fileId,
      leads: uploadState.selectedLeads,
      patientInfo,
      options: {
        quantumEnhanced: true,
        generateReport: false,
        modelVersion: 'v2.1',
      },
    }
    analyzeMutation.mutate(request)
  }

  const generateSOAPReport = () => {
    if (!analysisResult) return
    reportMutation.mutate(analysisResult.id)
  }

  return {
    runAnalysis,
    generateSOAPReport,
    isAnalyzing: analyzeMutation.isPending,
    analysisError: analyzeMutation.error,
    isGeneratingReport: reportMutation.isPending,
    reportError: reportMutation.error,
  }
}

export function useAnalysisResultQuery(analysisId: string | undefined) {
  return useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => getAnalysisResult(analysisId!),
    enabled: !!analysisId,
    staleTime: 60_000,
    select: (r) => r.data,
  })
}
