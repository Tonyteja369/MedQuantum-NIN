import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Cpu, AlertCircle } from 'lucide-react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { DropZone } from '@/components/upload/DropZone'
import { WFDBLoader } from '@/components/upload/WFDBLoader'
import { SignalPreviewChart } from '@/components/upload/SignalPreviewChart'
import { QualityScoreCard } from '@/components/upload/QualityScoreCard'
import { LeadSelector } from '@/components/upload/LeadSelector'
import { GlassCard } from '@/components/ui/GlassCard'
import { Badge } from '@/components/ui/Badge'
import { ECGSpinner } from '@/components/ui/Spinner'
import { useECGStore } from '@/store/useECGStore'
import { useECGAnalysis } from '@/hooks/useECGAnalysis'
import { loadWFDBSample } from '@/api/ecgApi'
import { getAllDemoCases, type DemoCase } from '@/utils/demoECGGenerator'
import type { AnalysisResult, SignalQuality } from '@/types/ecg.types'

export default function UploadDashboard() {
  const { file, fileId, isProcessing, quality } = useECGStore((s) => s.uploadState)
  const setUploadFile = useECGStore((s) => s.setUploadFile)
  const setUploadFileId = useECGStore((s) => s.setUploadFileId)
  const setUploadPreview = useECGStore((s) => s.setUploadPreview)
  const setUploadQuality = useECGStore((s) => s.setUploadQuality)
  const setUploadProcessing = useECGStore((s) => s.setUploadProcessing)
  const setUploadError = useECGStore((s) => s.setUploadError)
  const clearAnalysis = useECGStore((s) => s.clearAnalysis)
  const setAnalysisResult = useECGStore((s) => s.setAnalysisResult)
  const { runAnalysis, isAnalyzing, analysisError } = useECGAnalysis()
  const [demoMode, setDemoMode] = useState(true) // Enable demo mode by default
  const [selectedDemoCase, setSelectedDemoCase] = useState<string>('normal-sinus-rhythm')
  const [loadingSample, setLoadingSample] = useState<string | null>(null)

  const hasRealInput = Boolean(fileId)
  const isDemoActive = demoMode && !hasRealInput
  const canAnalyze = hasRealInput || isDemoActive

  // Auto-load first demo case when demo mode is active
  useEffect(() => {
    if (demoMode && !hasRealInput) {
      const demoCases = getAllDemoCases()
      const selectedCase = demoCases.find((c) => c.id === selectedDemoCase) || demoCases[0]
      setUploadPreview(selectedCase.analysis.signals)
      setUploadQuality(selectedCase.quality)
    }
  }, [demoMode, selectedDemoCase, hasRealInput])

  useEffect(() => {
    if (hasRealInput && demoMode) {
      setDemoMode(false)
    }
  }, [hasRealInput, demoMode])

  const handleSampleLoad = async (recordId: string) => {
    setLoadingSample(recordId)
    setDemoMode(false)
    clearAnalysis()
    setUploadError(null)
    setUploadProcessing(true)
    setUploadFile(null)
    setUploadFileId(null)
    setUploadPreview([])
    setUploadQuality(null)

    try {
      const sample = await loadWFDBSample(recordId)
      setUploadFile(null)
      setUploadFileId(sample.fileId)
      setUploadPreview(sample.preview)
      setUploadQuality(sample.quality)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load sample record'
      setUploadError(message)
    } finally {
      setUploadProcessing(false)
      setLoadingSample(null)
    }
  }

  const handleAnalyze = () => {
    console.log('[ANALYZE CLICK]', {
      demoMode: isDemoActive,
      hasFile: Boolean(file),
      fileId,
      isProcessing,
      isAnalyzing,
      fileShape: file ? { name: file.name, size: file.size, type: file.type } : null,
    })

    if (isDemoActive) {
      // Use high-fidelity demo case
      const demoCases = getAllDemoCases()
      const selectedCase = demoCases.find((c) => c.id === selectedDemoCase) || demoCases[0]
      
      // Load the demo case into the store
      setUploadPreview(selectedCase.analysis.signals)
      setUploadQuality(selectedCase.quality)
      setAnalysisResult(selectedCase.analysis)
      
      // Navigate via demo-navigate custom event
      window.dispatchEvent(new CustomEvent('demo-navigate', { detail: '/analysis' }))
      return
    }

    if (!fileId) {
      console.log('[ERROR STACK]', new Error('Analyze blocked because fileId is missing from shared store'))
      return
    }

    runAnalysis(fileId)
  }

  return (
    <PageWrapper>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">
              {demoMode ? 'ECG Demo Analysis' : 'Upload ECG'}
            </h1>
            {demoMode && <Badge variant="primary">Demo Mode</Badge>}
            {!demoMode && <Badge variant="primary" dot>Ready</Badge>}
          </div>
          <p className="text-sm text-[var(--text-secondary)]">
            {demoMode 
              ? 'Select a clinically simulated ECG case to explore AI analysis capabilities.'
              : 'Upload your ECG recording or load a PhysioNet sample to begin AI analysis.'}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column */}
          <div className="lg:col-span-2 space-y-5">
            {/* Demo mode selector - shown when demo mode is active */}
            {demoMode && (
              <GlassCard padding="md" animate={false}>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <Cpu size={18} className="text-[var(--accent-secondary)]" />
                      <h3 className="text-sm font-semibold text-[var(--text-primary)]">Demo Mode – Clinically Simulated ECG</h3>
                    </div>
                    <Badge variant="primary">Demo</Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-xs text-[var(--text-muted)]">Select demo case:</div>
                    <div className="grid grid-cols-2 gap-2">
                      {getAllDemoCases().map((demoCase) => (
                        <button
                          key={demoCase.id}
                          onClick={() => setSelectedDemoCase(demoCase.id)}
                          className={`text-xs px-3 py-2 rounded-md transition-all text-left ${
                            selectedDemoCase === demoCase.id
                              ? 'bg-[rgba(124,58,237,0.2)] border-[rgba(124,58,237,0.4)] text-[#7c3aed]'
                              : 'bg-[rgba(124,58,237,0.05)] border-[rgba(124,58,237,0.2)] text-[var(--text-secondary)] hover:bg-[rgba(124,58,237,0.1)]'
                          } border`}
                        >
                          <div className="font-medium">{demoCase.name}</div>
                          <div className="text-[10px] opacity-70">{demoCase.heartRate} BPM</div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </GlassCard>
            )}

            {/* Hide upload and sample UI when demo mode is active */}
            {!demoMode && (
              <>
                <DropZone />
                <WFDBLoader onLoad={handleSampleLoad} isLoading={Boolean(loadingSample)} />
              </>
            )}
            
            <SignalPreviewChart />
          </div>

          {/* Right column */}
          <div className="space-y-5">
            <LeadSelector />
            <QualityScoreCard />

            {/* Patient info (simplified) */}
            <GlassCard padding="md" animate={false}>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
                Patient Information
              </h3>
              <div className="space-y-3">
                <div className="text-xs text-[var(--text-secondary)] leading-relaxed">
                  Enter patient details for personalized analysis (optional)
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'Enter Patient ID (optional)', placeholder: 'e.g. PT-00142' },
                    { label: 'Enter Patient Age (optional)', placeholder: 'Years' },
                  ].map((field) => (
                    <div key={field.label}>
                      <label className="text-xs text-[var(--text-muted)] block mb-1">{field.label}</label>
                      <input
                        className="w-full bg-white/5 border border-[var(--border-primary)] rounded-md px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[rgba(0,212,255,0.4)] transition-colors"
                        placeholder={field.placeholder}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </GlassCard>

            {/* Analyze button */}
            <motion.button
              onClick={handleAnalyze}
              disabled={!canAnalyze || isAnalyzing || isProcessing || Boolean(loadingSample)}
              whileHover={canAnalyze ? { scale: 1.02 } : {}}
              whileTap={canAnalyze ? { scale: 0.98 } : {}}
              className="w-full py-3.5 rounded-xl font-semibold text-base transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background: canAnalyze
                  ? 'linear-gradient(135deg, #00d4ff, #7c3aed)'
                  : 'rgba(255,255,255,0.05)',
                color: canAnalyze ? '#fff' : 'var(--text-muted)',
                boxShadow: canAnalyze ? '0 0 24px rgba(0,212,255,0.35)' : undefined,
              }}
            >
              {isAnalyzing ? (
                <div className="flex items-center justify-center gap-2">
                  <ECGSpinner />
                  <span className="text-sm">
                    {uploadProgress < 25 ? "Analyzing..." :
                     uploadProgress < 50 ? "Extracting features..." :
                     uploadProgress < 75 ? "Running AI models..." :
                     "Generating results..."}
                  </span>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <Play size={18} />
                  {isDemoActive ? 'Run Demo Analysis' : 'Analyze ECG'}
                </div>
              )}
            </motion.button>

            {analysisError && (
              <div
                className="flex items-center gap-2 p-3 rounded-lg text-sm"
                style={{
                  background: 'rgba(255,77,109,0.1)',
                  border: '1px solid rgba(255,77,109,0.3)',
                  color: '#ff4d6d',
                }}
              >
                <AlertCircle size={14} className="flex-shrink-0" />
                {analysisError.message}
              </div>
            )}
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
