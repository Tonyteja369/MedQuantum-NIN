import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, FileText, Cpu, Clock } from 'lucide-react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { ECGWaveformPanel } from '@/components/analysis/ECGWaveformPanel'
import { MetricsCards } from '@/components/analysis/MetricsCards'
import { DiagnosisPanel } from '@/components/analysis/DiagnosisPanel'
import { ConfidenceGauge } from '@/components/analysis/ConfidenceGauge'
import { ExplainabilityTree } from '@/components/analysis/ExplainabilityTree'
import { RiskLevelIndicator } from '@/components/analysis/RiskLevelIndicator'
import { RecommendationsCard } from '@/components/analysis/RecommendationsCard'
import { Badge } from '@/components/ui/Badge'
import { useECGStore } from '@/store/useECGStore'
import { useECGAnalysis } from '@/hooks/useECGAnalysis'
import { formatProcessingTime, formatRelativeTime } from '@/utils/formatters'

export default function AnalysisDashboard() {
  const navigate = useNavigate()
  const result = useECGStore((s) => s.analysisResult)
  const { generateSOAPReport, isGeneratingReport } = useECGAnalysis()

  // Redirect if no result
  useEffect(() => {
    if (!result) {
      navigate('/upload', { replace: true })
    }
  }, [result, navigate])

  if (!result) return null

  return (
    <PageWrapper>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start justify-between mb-6 flex-wrap gap-4"
        >
          <div>
            <div className="flex items-center gap-3 mb-1">
              <button
                onClick={() => navigate('/upload')}
                className="p-1.5 rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-white/5 transition-colors"
              >
                <ArrowLeft size={16} />
              </button>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">ECG Analysis</h1>
              <Badge variant={result.quantumEnhanced ? 'secondary' : 'default'} dot>
                {result.quantumEnhanced ? 'Quantum Enhanced' : 'Standard'}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-xs text-[var(--text-muted)] ml-9">
              <span className="flex items-center gap-1">
                <Clock size={12} /> {formatRelativeTime(result.timestamp)}
              </span>
              <span className="flex items-center gap-1">
                <Cpu size={12} /> {formatProcessingTime(result.processingTimeMs)}
              </span>
              <span className="font-mono">#{result.id.slice(0, 8)}</span>
            </div>
          </div>

          <motion.button
            onClick={generateSOAPReport}
            disabled={isGeneratingReport}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all"
            style={{
              background: 'linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15))',
              border: '1px solid rgba(0,212,255,0.3)',
              color: 'var(--accent-primary)',
            }}
          >
            <FileText size={16} />
            {isGeneratingReport ? 'Generating…' : 'Generate Report'}
          </motion.button>
        </motion.div>

        {/* Risk indicator — full width */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-5"
        >
          <RiskLevelIndicator />
        </motion.div>

        {/* Metrics row */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mb-5"
        >
          <MetricsCards />
        </motion.div>

        {/* Main 2-col layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Left: waveform + explainability */}
          <div className="lg:col-span-2 space-y-5">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <ECGWaveformPanel />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <ExplainabilityTree />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <RecommendationsCard />
            </motion.div>
          </div>

          {/* Right: diagnosis + confidence */}
          <div className="space-y-5">
            <motion.div
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <ConfidenceGauge />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.25 }}
            >
              <DiagnosisPanel />
            </motion.div>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
