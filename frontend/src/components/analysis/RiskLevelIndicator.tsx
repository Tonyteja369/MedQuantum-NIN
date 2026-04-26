import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle, AlertOctagon, Activity } from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { riskColors, riskGlows, riskBg, riskBorder } from '@/utils/colorTokens'
import { riskLevelLabel } from '@/utils/formatters'
import type { RiskLevel } from '@/types/ecg.types'

const RiskIcons: Record<RiskLevel, React.ReactNode> = {
  normal: <CheckCircle size={28} />,
  borderline: <Activity size={28} />,
  elevated: <AlertTriangle size={28} />,
  critical: <AlertOctagon size={28} />,
}

const RiskDescriptions: Record<RiskLevel, string> = {
  normal: 'ECG findings are within normal limits. Routine follow-up recommended.',
  borderline: 'Minor abnormalities detected. Clinical correlation advised.',
  elevated: 'Significant abnormalities present. Prompt clinical evaluation needed.',
  critical: 'Life-threatening findings detected. Immediate medical attention required.',
}

export function RiskLevelIndicator() {
  const result = useECGStore((s) => s.analysisResult)
  if (!result) return null

  const { riskLevel, riskScore } = result
  const color = riskColors[riskLevel]
  const glow = riskGlows[riskLevel]
  const bg = riskBg[riskLevel]
  const border = riskBorder[riskLevel]

  return (
    <GlassCard
      padding="md"
      style={{ background: bg, border: `1px solid ${border}`, boxShadow: glow }}
      animate={false}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="flex items-start gap-4"
      >
        <motion.div
          animate={riskLevel === 'critical' ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 1, repeat: riskLevel === 'critical' ? Infinity : 0 }}
          style={{ color }}
        >
          {RiskIcons[riskLevel]}
        </motion.div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-base font-bold" style={{ color }}>
              {riskLevelLabel[riskLevel]} Risk
            </h3>
            <span className="text-2xl font-bold font-mono" style={{ color }}>
              {riskScore.toFixed(0)}
              <span className="text-sm font-normal text-[var(--text-muted)]">/100</span>
            </span>
          </div>
          <p className="text-sm text-[var(--text-secondary)]">{RiskDescriptions[riskLevel]}</p>

          {/* Risk bar */}
          <div className="mt-3 w-full h-2 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}60` }}
              initial={{ width: 0 }}
              animate={{ width: `${riskScore}%` }}
              transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
            />
          </div>
        </div>
      </motion.div>
    </GlassCard>
  )
}
