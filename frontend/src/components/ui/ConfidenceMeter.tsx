import { motion } from 'framer-motion'
import { confidenceColor } from '@/utils/colorTokens'
import { formatConfidence } from '@/utils/formatters'

interface ConfidenceMeterProps {
  value: number   // 0-1
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export function ConfidenceMeter({ value, label, size = 'md', showLabel = true }: ConfidenceMeterProps) {
  const color = confidenceColor(value)
  const pct = Math.round(value * 100)

  const heights = { sm: 'h-1.5', md: 'h-2', lg: 'h-3' }
  const textSizes = { sm: 'text-xs', md: 'text-sm', lg: 'text-base' }

  return (
    <div className="w-full space-y-1.5">
      {showLabel && (
        <div className="flex items-center justify-between">
          <span className={`${textSizes[size]} text-[var(--text-secondary)]`}>
            {label ?? 'Confidence'}
          </span>
          <span
            className={`${textSizes[size]} font-semibold font-mono`}
            style={{ color }}
          >
            {formatConfidence(value)}
          </span>
        </div>
      )}
      <div className={`w-full bg-white/5 rounded-full overflow-hidden ${heights[size]}`}>
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}60` }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
        />
      </div>
    </div>
  )
}
