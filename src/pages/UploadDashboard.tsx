import { useState } from 'react'
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
import { useFileUpload } from '@/hooks/useFileUpload'
import { generateSyntheticECG } from '@/utils/signalUtils'
import type { AnalysisResult, SignalQuality } from '@/types/ecg.types'

export default function UploadDashboard() {
  const { file, isProcessing, quality } = useECGStore((s) => s.uploadState)
  const setAnalysisResult = useECGStore((s) => s.setAnalysisResult)
  const { runAnalysis, isAnalyzing, analysisError } = useECGAnalysis()
  const { fileId } = useFileUpload()
  const [demoMode, setDemoMode] = useState(false)

  const canAnalyze = (file !== null && fileId !== null) || demoMode

  const handleAnalyze = () => {
    if (demoMode) {
      // Inject demo data directly
      const syntheticData = generateSyntheticECG(360, 10, 72)
      const demoResult: AnalysisResult = {
        id: `demo-${Date.now()}`,
        timestamp: new Date().toISOString(),
        processingTimeMs: 1234,
        signals: [
          { lead: 'II', data: syntheticData, samplingRate: 360, duration: 10, units: 'mV' },
          { lead: 'V1', data: generateSyntheticECG(360, 10, 72), samplingRate: 360, duration: 10, units: 'mV' },
          { lead: 'V5', data: generateSyntheticECG(360, 10, 72), samplingRate: 360, duration: 10, units: 'mV' },
        ],
        quality: {
          overall: 92,
          noiseLevel: 28,
          baselineWander: false,
          artifactRatio: 0.03,
          leadQualities: { II: 0.95, V1: 0.88, V5: 0.91 },
        },
        metrics: {
          heartRate: 72,
          heartRateVariability: 45.2,
          intervals: { pr: 156, qrs: 92, qt: 400, qtc: 418, rr: 833 },
          axis: 45,
          qrsAmplitude: 1.2,
          stDeviation: 0.05,
          tWaveAmplitude: 0.4,
        },
        diagnoses: [
          { code: 'I49.9', label: 'Normal Sinus Rhythm', confidence: 0.94, category: 'Normal', icdVersion: '10' },
          { code: 'R00.0', label: 'Tachycardia, unspecified', confidence: 0.12, category: 'Arrhythmia', icdVersion: '10' },
        ],
        primaryDiagnosis: { code: 'I49.9', label: 'Normal Sinus Rhythm', confidence: 0.94, category: 'Normal', icdVersion: '10' },
        riskLevel: 'normal',
        riskScore: 12,
        confidence: 0.94,
        explainability: [
          {
            id: '1', feature: 'QRS Morphology', contribution: 0.72, importance: 0.85,
            description: 'Normal QRS complex shape',
            children: [
              { id: '1a', feature: 'QRS Duration (92ms)', contribution: 0.38, importance: 0.7 },
              { id: '1b', feature: 'R-wave Amplitude', contribution: 0.34, importance: 0.65 },
            ],
          },
          { id: '2', feature: 'P-wave Presence', contribution: 0.55, importance: 0.75, description: 'Regular P waves preceding each QRS' },
          { id: '3', feature: 'RR Regularity', contribution: 0.48, importance: 0.68, description: 'Regular RR intervals' },
          { id: '4', feature: 'ST Segment', contribution: -0.08, importance: 0.4, description: 'Slight baseline deviation' },
        ],
        recommendations: [
          { priority: 'low', category: 'follow-up', text: 'Routine follow-up in 12 months', rationale: 'Normal ECG findings' },
          { priority: 'low', category: 'lifestyle', text: 'Maintain regular aerobic exercise 150min/week', rationale: 'Preventive cardiac health' },
          { priority: 'medium', category: 'monitoring', text: 'Monitor blood pressure at each visit', rationale: 'Standard cardiovascular screening' },
        ],
        modelVersion: 'v2.1-demo',
        quantumEnhanced: true,
      }
      setAnalysisResult(demoResult)
      // Navigate via demo-navigate custom event (handled by DemoNavigationHandler in App.tsx)
      window.dispatchEvent(new CustomEvent('demo-navigate', { detail: '/analysis' }))
      return
    }

    if (fileId) runAnalysis(fileId)
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
            <WFDBLoader onLoad={() => setDemoMode(true)} />
            <SignalPreviewChart />

            {/* Demo mode banner */}
            {!file && (
              <GlassCard padding="sm" animate={false}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5 text-sm">
                    <Cpu size={16} className="text-[var(--accent-secondary)]" />
                    <span className="text-[var(--text-secondary)]">No file? Try a demo analysis</span>
                  </div>
                  <button
                    onClick={() => setDemoMode((d) => !d)}
                    className="text-xs px-3 py-1.5 rounded-md transition-all"
                    style={{
                      background: demoMode ? 'rgba(124,58,237,0.2)' : 'rgba(124,58,237,0.1)',
                      border: '1px solid rgba(124,58,237,0.3)',
                      color: '#7c3aed',
                    }}
                  >
                    {demoMode ? '✓ Demo Mode On' : 'Enable Demo'}
                  </button>
                </div>
              </GlassCard>
            )}
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
                  {demoMode ? 'Run Demo Analysis' : 'Analyze ECG'}
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
