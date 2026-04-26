import { motion } from 'framer-motion'
import { Heart, Activity, Clock, TrendingUp, BarChart2, Zap } from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { AnimatedNumber } from '@/components/ui/AnimatedNumber'
import { Tooltip } from '@/components/ui/Tooltip'
import { formatInterval, formatAxis, formatVoltage } from '@/utils/formatters'

interface MetricCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  unit?: string
  color?: string
  tooltip?: string
  animated?: boolean
  numericValue?: number
}

function MetricCard({ icon, label, value, unit, color = 'var(--accent-primary)', tooltip, animated, numericValue }: MetricCardProps) {
  return (
    <Tooltip content={tooltip ?? label}>
      <GlassCard padding="md" animate hover className="h-full">
        <div className="flex items-start justify-between mb-3">
          <div className="p-2 rounded-lg" style={{ background: `${color}18`, color }}>
            {icon}
          </div>
        </div>
        <div className="space-y-1">
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-bold font-mono" style={{ color }}>
              {animated && numericValue !== undefined ? (
                <AnimatedNumber value={numericValue} duration={1200} decimals={0} />
              ) : (
                value
              )}
            </span>
            {unit && <span className="text-xs text-[var(--text-muted)]">{unit}</span>}
          </div>
          <p className="text-xs text-[var(--text-secondary)]">{label}</p>
        </div>
      </GlassCard>
    </Tooltip>
  )
}

export function MetricsCards() {
  const result = useECGStore((s) => s.analysisResult)
  if (!result) return null

  const { metrics } = result
  const { heartRate, heartRateVariability, intervals, axis } = metrics

  const cards = [
    {
      icon: <Heart size={18} />,
      label: 'Heart Rate',
      value: heartRate,
      unit: 'bpm',
      color: '#ff4d6d',
      tooltip: 'Average heart rate in beats per minute',
      animated: true,
      numericValue: heartRate,
    },
    {
      icon: <Activity size={18} />,
      label: 'HRV (RMSSD)',
      value: `${heartRateVariability.toFixed(1)}`,
      unit: 'ms',
      color: '#10b981',
      tooltip: 'Heart Rate Variability — Root Mean Square of Successive Differences',
      animated: true,
      numericValue: heartRateVariability,
    },
    {
      icon: <Clock size={18} />,
      label: 'QRS Duration',
      value: formatInterval(intervals.qrs),
      color: '#00d4ff',
      tooltip: 'QRS complex duration (normal: 80-120ms)',
    },
    {
      icon: <TrendingUp size={18} />,
      label: 'QTc Interval',
      value: formatInterval(intervals.qtc),
      color: '#7c3aed',
      tooltip: 'Corrected QT interval (normal: <440ms men, <460ms women)',
    },
    {
      icon: <BarChart2 size={18} />,
      label: 'PR Interval',
      value: formatInterval(intervals.pr),
      color: '#fbbf24',
      tooltip: 'PR interval — AV conduction time (normal: 120-200ms)',
    },
    {
      icon: <Zap size={18} />,
      label: 'QRS Axis',
      value: formatAxis(axis),
      color: '#f97316',
      tooltip: 'Mean QRS electrical axis (normal: -30° to +90°)',
    },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((card, i) => (
        <motion.div
          key={card.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06, duration: 0.35 }}
        >
          <MetricCard {...card} />
        </motion.div>
      ))}
    </div>
  )
}
