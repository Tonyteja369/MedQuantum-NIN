import { motion } from 'framer-motion'
import { CheckCircle, AlertTriangle, XCircle, Activity } from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { ConfidenceMeter } from '@/components/ui/ConfidenceMeter'
import { formatQuality } from '@/utils/formatters'

export function QualityScoreCard() {
  const quality = useECGStore((s) => s.uploadState.quality)

  if (!quality) return null

  const score = quality.overall
  const qualityLabel = formatQuality(score)

  const Icon = score >= 80 ? CheckCircle : score >= 50 ? AlertTriangle : XCircle
  const iconColor = score >= 80 ? '#10b981' : score >= 50 ? '#fbbf24' : '#ff4d6d'

  const metrics = [
    { label: 'Baseline Wander', value: quality.baselineWander ? 'Detected' : 'None', ok: !quality.baselineWander },
    { label: 'Artifact Ratio', value: `${(quality.artifactRatio * 100).toFixed(1)}%`, ok: quality.artifactRatio < 0.1 },
    { label: 'Noise Level', value: `${quality.noiseLevel.toFixed(1)} dB`, ok: quality.noiseLevel > 20 },
  ]

  return (
    <GlassCard padding="md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity size={16} className="text-[var(--accent-primary)]" />
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">Signal Quality</h3>
        </div>
        <div className="flex items-center gap-2">
          <Icon size={16} style={{ color: iconColor }} />
          <span className="text-sm font-semibold" style={{ color: iconColor }}>
            {qualityLabel}
          </span>
        </div>
      </div>

      <ConfidenceMeter value={score / 100} label="Overall Quality" />

      <div className="mt-4 space-y-2">
        {metrics.map((m) => (
          <div key={m.label} className="flex items-center justify-between text-xs">
            <span className="text-[var(--text-muted)]">{m.label}</span>
            <span
              className="font-mono font-medium"
              style={{ color: m.ok ? '#10b981' : '#fbbf24' }}
            >
              {m.value}
            </span>
          </div>
        ))}
      </div>

      {/* Per-lead quality */}
      {Object.keys(quality.leadQualities).length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-[var(--text-muted)] mb-2">Per-Lead Quality</p>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(quality.leadQualities).map(([lead, q]) => (
              <motion.div
                key={lead}
                whileHover={{ scale: 1.05 }}
                className="px-2 py-1 rounded text-xs font-mono font-medium"
                style={{
                  background: `rgba(${q! >= 0.8 ? '16,185,129' : q! >= 0.5 ? '251,191,36' : '255,77,109'},0.1)`,
                  color: q! >= 0.8 ? '#10b981' : q! >= 0.5 ? '#fbbf24' : '#ff4d6d',
                  border: `1px solid rgba(${q! >= 0.8 ? '16,185,129' : q! >= 0.5 ? '251,191,36' : '255,77,109'},0.3)`,
                }}
              >
                {lead}: {Math.round((q ?? 0) * 100)}%
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </GlassCard>
  )
}
