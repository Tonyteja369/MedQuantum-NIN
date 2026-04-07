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
import { toChartData } from '@/utils/signalUtils'
import { leadColors } from '@/utils/colorTokens'
import { GlassCard } from '@/components/ui/GlassCard'
import { Spinner } from '@/components/ui/Spinner'

export function SignalPreviewChart() {
  const { preview, selectedLeads, isProcessing } = useECGStore((s) => s.uploadState)

  const chartData = useMemo(() => {
    const lead = preview.find((s) => selectedLeads.includes(s.lead)) ?? preview[0]
    if (!lead) return []
    return toChartData(lead.data, lead.samplingRate, 600)
  }, [preview, selectedLeads])

  const activeLead = preview.find((s) => selectedLeads.includes(s.lead)) ?? preview[0]

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

  return (
    <GlassCard padding="sm">
      <div className="flex items-center justify-between mb-3 px-2">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">
          Signal Preview — Lead {activeLead?.lead}
        </h3>
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
