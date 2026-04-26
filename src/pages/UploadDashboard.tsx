import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, AlertCircle } from 'lucide-react'
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
import { useFileUpload } from '@/hooks/useFileUpload'

export default function UploadDashboard() {
  const { file, isProcessing, quality } = useECGStore((s) => s.uploadState)
  const { runAnalysis, isAnalyzing, analysisError } = useECGAnalysis()
  const { fileId } = useFileUpload()
  // wfdbFileId is set when a PhysioNet sample is loaded
  const [wfdbFileId, setWfdbFileId] = useState<string | null>(null)

  // Can analyze if we have a real file uploaded OR a WFDB sample loaded
  const activeFileId = fileId ?? wfdbFileId
  const canAnalyze = activeFileId !== null && !isProcessing

  const handleAnalyze = () => {
    if (activeFileId) runAnalysis(activeFileId)
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
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">Upload ECG</h1>
            <Badge variant="primary" dot>Ready</Badge>
          </div>
          <p className="text-sm text-[var(--text-secondary)]">
            Upload your ECG recording or load a PhysioNet sample to begin AI analysis.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column */}
          <div className="lg:col-span-2 space-y-5">
            <DropZone />
            <WFDBLoader onLoad={(signalId) => setWfdbFileId(signalId)} />
            <SignalPreviewChart />


          </div>

          {/* Right column */}
          <div className="space-y-5">
            <LeadSelector />
            <QualityScoreCard />

            {/* Patient info (simplified) */}
            <GlassCard padding="md" animate={false}>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
                Patient Info (Optional)
              </h3>
              <div className="space-y-2">
                {[
                  { label: 'Patient ID', placeholder: 'e.g. PT-00142' },
                  { label: 'Age', placeholder: 'Years' },
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
            </GlassCard>

            {/* Analyze button */}
            <motion.button
              onClick={handleAnalyze}
              disabled={!canAnalyze || isAnalyzing}
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
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <Play size={18} />
                  {canAnalyze ? 'Analyze ECG' : 'Upload a file first'}
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
