import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Share2 } from 'lucide-react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { SOAPReport } from '@/components/report/SOAPReport'
import { DoctorSummary } from '@/components/report/DoctorSummary'
import { PatientExplanation } from '@/components/report/PatientExplanation'
import { PDFExportButton } from '@/components/report/PDFExportButton'
import { Badge } from '@/components/ui/Badge'
import { useECGStore } from '@/store/useECGStore'
import { formatTimestamp } from '@/utils/formatters'
import { riskColors } from '@/utils/colorTokens'
import { riskLevelLabel } from '@/utils/formatters'

export default function ReportPage() {
  const navigate = useNavigate()
  const report = useECGStore((s) => s.reportData)
  const analysis = useECGStore((s) => s.analysisResult)

  useEffect(() => {
    if (!report && !analysis) {
      navigate('/upload', { replace: true })
    } else if (!report && analysis) {
      navigate('/analysis', { replace: true })
    }
  }, [report, analysis, navigate])

  if (!report) return null

  const riskColor = riskColors[report.riskLevel]

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
                onClick={() => navigate('/analysis')}
                className="p-1.5 rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-white/5 transition-colors"
              >
                <ArrowLeft size={16} />
              </button>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">Clinical Report</h1>
              <span
                className="inline-flex items-center gap-1.5 rounded-full border font-medium text-xs px-2.5 py-1"
                style={{
                  background: `${riskColor}18`,
                  color: riskColor,
                  borderColor: `${riskColor}40`,
                }}
              >
                <span className="inline-block w-1.5 h-1.5 rounded-full" style={{ backgroundColor: riskColor }} />
                {riskLevelLabel[report.riskLevel]} Risk
              </span>
            </div>
            <p className="text-xs text-[var(--text-muted)] ml-9 font-mono">
              {formatTimestamp(report.generatedAt)} • ID: {report.analysisId.slice(0, 12)}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium glass border border-[var(--border-primary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: 'ECG Analysis Report',
                    text: `MedQuantum-NIN ECG Report — ${report.diagnoses[0]?.label}`,
                  }).catch(() => {})
                }
              }}
            >
              <Share2 size={14} />
              Share
            </motion.button>
            <PDFExportButton />
          </div>
        </motion.div>

        {/* Main layout: 3/4 + 1/4 */}
        <div id="report-content">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
            {/* Left 3/4 */}
            <div className="lg:col-span-3 space-y-5">
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <SOAPReport />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <DoctorSummary />
              </motion.div>
            </div>

            {/* Right 1/4 */}
            <div className="space-y-5">
              <motion.div
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 }}
              >
                <PatientExplanation />
              </motion.div>

              {/* Report metadata */}
              <motion.div
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }}
              >
                <div className="glass rounded-lg border border-[var(--border-primary)] p-4">
                  <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
                    Report Info
                  </h4>
                  <div className="space-y-2 text-xs">
                    {[
                      { label: 'Analysis ID', value: report.analysisId.slice(0, 12) },
                      { label: 'Generated', value: formatTimestamp(report.generatedAt) },
                      { label: 'Confidence', value: `${Math.round(report.confidence * 100)}%` },
                      { label: 'Primary Dx', value: report.diagnoses[0]?.label ?? '—' },
                    ].map((item) => (
                      <div key={item.label} className="flex flex-col gap-0.5">
                        <span className="text-[var(--text-muted)]">{item.label}</span>
                        <span className="text-[var(--text-secondary)] font-mono truncate">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-[var(--text-muted)]">
            This report was generated by MedQuantum-NIN AI and is intended to support — not replace —
            clinical decision-making. Always consult a qualified cardiologist for medical decisions.
          </p>
        </div>
      </div>
    </PageWrapper>
  )
}
