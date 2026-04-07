import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { ChevronDown, ChevronUp, Stethoscope, Hash } from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { Badge } from '@/components/ui/Badge'
import { ConfidenceMeter } from '@/components/ui/ConfidenceMeter'
import { formatConfidence } from '@/utils/formatters'

export function DiagnosisPanel() {
  const result = useECGStore((s) => s.analysisResult)
  const [expanded, setExpanded] = useState<string | null>(null)

  if (!result) return null

  const { primaryDiagnosis, diagnoses } = result

  return (
    <GlassCard padding="md">
      <div className="flex items-center gap-2 mb-4">
        <Stethoscope size={16} className="text-[var(--accent-primary)]" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Diagnoses</h3>
        <Badge variant="primary" size="sm">{diagnoses.length}</Badge>
      </div>

      {/* Primary */}
      <div
        className="p-4 rounded-lg mb-4"
        style={{
          background: 'rgba(0,212,255,0.06)',
          border: '1px solid rgba(0,212,255,0.2)',
          boxShadow: '0 0 20px rgba(0,212,255,0.08)',
        }}
      >
        <div className="flex items-start justify-between gap-2 mb-2">
          <div>
            <p className="text-xs text-[var(--accent-primary)] font-semibold uppercase tracking-wider mb-1">
              Primary Diagnosis
            </p>
            <h4 className="text-base font-bold text-[var(--text-primary)]">
              {primaryDiagnosis.label}
            </h4>
          </div>
          <Badge variant="primary" size="sm">{primaryDiagnosis.category}</Badge>
        </div>
        <div className="flex items-center gap-2 mb-3">
          <Hash size={12} className="text-[var(--text-muted)]" />
          <span className="text-xs font-mono text-[var(--text-muted)]">
            ICD-{primaryDiagnosis.icdVersion}: {primaryDiagnosis.code}
          </span>
        </div>
        <ConfidenceMeter value={primaryDiagnosis.confidence} label="Confidence" />
      </div>

      {/* Other diagnoses */}
      {diagnoses.filter((d) => d.code !== primaryDiagnosis.code).map((dx) => (
        <motion.div
          key={dx.code}
          className="mb-2 rounded-lg overflow-hidden"
          style={{ border: '1px solid var(--border-primary)' }}
        >
          <button
            onClick={() => setExpanded((p) => (p === dx.code ? null : dx.code))}
            className="w-full flex items-center justify-between p-3 text-left hover:bg-white/3 transition-colors"
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm font-medium text-[var(--text-primary)] truncate">
                {dx.label}
              </span>
              <Badge variant="default" size="sm">{dx.category}</Badge>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="text-xs font-mono text-[var(--accent-primary)]">
                {formatConfidence(dx.confidence)}
              </span>
              {expanded === dx.code ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </div>
          </button>

          <AnimatePresence>
            {expanded === dx.code && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-3 pb-3 space-y-2">
                  <ConfidenceMeter value={dx.confidence} showLabel={false} size="sm" />
                  <p className="text-xs text-[var(--text-muted)] font-mono">
                    ICD-{dx.icdVersion}: {dx.code}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      ))}
    </GlassCard>
  )
}
