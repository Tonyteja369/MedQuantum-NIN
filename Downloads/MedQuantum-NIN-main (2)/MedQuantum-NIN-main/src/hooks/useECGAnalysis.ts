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
    mutationFn: (request: AnalysisRequest) => {
      console.log('[MUTATION PENDING]', analyzeMutation.isPending)
      console.log('[REQUEST START]', request)
      return analyzeECG(request)
    },
    onSuccess: (result) => {
      const uploadState = useECGStore.getState().uploadState
      setAnalysisResult({
        ...result,
        signals: uploadState.preview.length > 0 ? uploadState.preview : result.signals,
        quality: uploadState.quality ?? result.quality,
      })
      navigate('/analysis')
    },
  })

  const reportMutation = useMutation({
    mutationFn: (signalId: string) => generateReport(signalId),
    onSuccess: (report) => {
      setReportData(report)
      navigate('/report')
    },
  })

  const runAnalysis = (fileId: string, patientInfo?: PatientInfo) => {
    if (analyzeMutation.isPending) {
      console.log('[MUTATION PENDING]', true)
      return
    }

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
    analyzeMutation.mutate(request, {
      onError: (error) => {
        console.log('[ERROR STACK]', error)
      },
    })
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
  })
}
