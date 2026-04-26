import { useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts'
import { useECGStore } from '@/store/useECGStore'
import { toChartData, validateECGSignal } from '@/utils/signalUtils'
import { leadColors } from '@/utils/colorTokens'
import { GlassCard } from '@/components/ui/GlassCard'
import { Spinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { AlertCircle, CheckCircle } from 'lucide-react'

export function SignalPreviewChart() {
  const { preview, selectedLeads, isProcessing } = useECGStore((s) => s.uploadState)

  const { chartData, validation, activeLead } = useMemo(() => {
    const lead = preview.find((s) => selectedLeads.includes(s.lead)) ?? preview[0]
    if (!lead) return { chartData: [], validation: null, activeLead: null }
    
    const data = toChartData(lead.data, lead.samplingRate, 600)
    const validation = validateECGSignal(lead.data, lead.samplingRate)
    
    return { chartData: data, validation, activeLead: lead }
  }, [preview, selectedLeads])

  if (isProcessing) {
    return (
      <GlassCard className="h-48 flex items-center justify-center">
        <Spinner label="Loading signal preview…" />
      </GlassCard>
    )
  }

  if (preview.length === 0) {
    return (
      <GlassCard className="h-48 flex items-center justify-center">
        <p className="text-sm text-[var(--text-muted)] text-center">
          Upload an ECG file to preview the signal
        </p>
      </GlassCard>
    )
  }

  const color = leadColors[activeLead?.lead ?? 'II'] ?? '#00d4ff'

  if (validation && !validation.isValid) {
    return (
      <GlassCard padding="sm">
        <div className="flex items-center justify-between mb-3 px-2">
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            Signal Preview — Lead {activeLead?.lead}
          </h3>
          <Badge variant="danger" className="flex items-center gap-1">
            <AlertCircle size={12} />
            Invalid Signal
          </Badge>
        </div>
        <div className="px-2 py-3">
          <div className="text-sm text-[var(--text-secondary)] mb-2">
            Signal quality issues detected:
          </div>
          <ul className="text-xs text-[var(--text-muted)] space-y-1">
            {validation.issues.map((issue, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-[var(--accent-danger)]">•</span>
                {issue}
              </li>
            ))}
          </ul>
        </div>
      </GlassCard>
    )
  }

  return (
    <GlassCard padding="sm">
      <div className="flex items-center justify-between mb-3 px-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            Signal Preview — Lead {activeLead?.lead}
          </h3>
          {validation && (
            <Badge 
              variant={validation.quality === 'good' ? 'success' : validation.quality === 'fair' ? 'warning' : 'danger'}
              className="flex items-center gap-1"
            >
              {validation.quality === 'good' && <CheckCircle size={12} />}
              {validation.quality === 'fair' && <AlertCircle size={12} />}
              {validation.quality === 'poor' && <AlertCircle size={12} />}
              {validation.quality.charAt(0).toUpperCase() + validation.quality.slice(1)} Quality
            </Badge>
          )}
        </div>
        <span className="text-xs text-[var(--text-muted)] font-mono">
          {activeLead?.samplingRate} Hz • {activeLead?.duration?.toFixed(1)}s
        </span>
      </div>

      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: -20 }}>
          <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" />
          <XAxis
            dataKey="time"
            tickFormatter={(v) => `${v}s`}
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            axisLine={false}
            tickLine={false}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(15,20,36,0.95)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 8,
              fontSize: 12,
              color: 'var(--text-primary)',
            }}
            formatter={(v: number) => [`${v.toFixed(3)} mV`, 'Amplitude']}
            labelFormatter={(l) => `Time: ${l}s`}
          />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.08)" strokeDasharray="2 4" />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: color }}
          />
        </LineChart>
      </ResponsiveContainer>
    </GlassCard>
  )
}
