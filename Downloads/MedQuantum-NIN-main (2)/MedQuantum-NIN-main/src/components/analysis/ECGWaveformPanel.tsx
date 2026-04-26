import { useState, useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Brush,
} from 'recharts'
import { useECGStore } from '@/store/useECGStore'
import { toChartData } from '@/utils/signalUtils'
import { leadColors } from '@/utils/colorTokens'
import { GlassCard } from '@/components/ui/GlassCard'
import type { LeadName } from '@/types/ecg.types'
import { motion } from 'framer-motion'

export function ECGWaveformPanel() {
  const result = useECGStore((s) => s.analysisResult)
  const [activeLead, setActiveLead] = useState<LeadName>('II')
  const [zoom, setZoom] = useState(false)

  const signal = useMemo(
    () => result?.signals.find((s) => s.lead === activeLead) ?? result?.signals[0],
    [result, activeLead]
  )

  const chartData = useMemo(() => {
    if (!signal) return []
    return toChartData(signal.data, signal.samplingRate, zoom ? 1200 : 600)
  }, [signal, zoom])

  if (!result) return null

  const availableLeads = result.signals.map((s) => s.lead)
  const color = leadColors[signal?.lead ?? 'II'] ?? '#00d4ff'

  return (
    <GlassCard padding="sm">
      <div className="flex items-center justify-between mb-3 px-2 flex-wrap gap-2">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">ECG Waveform</h3>

        {/* Lead tabs */}
        <div className="flex gap-1 flex-wrap">
          {availableLeads.map((lead) => {
            const lColor = leadColors[lead] ?? '#00d4ff'
            return (
              <motion.button
                key={lead}
                onClick={() => setActiveLead(lead)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-2 py-0.5 rounded text-xs font-mono font-semibold transition-all"
                style={{
                  background: activeLead === lead ? `${lColor}20` : 'transparent',
                  border: `1px solid ${activeLead === lead ? `${lColor}50` : 'rgba(255,255,255,0.06)'}`,
                  color: activeLead === lead ? lColor : 'var(--text-muted)',
                }}
              >
                {lead}
              </motion.button>
            )
          })}
        </div>

        <button
          onClick={() => setZoom((z) => !z)}
          className="text-xs px-2 py-1 rounded glass border border-[var(--border-primary)] text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors"
        >
          {zoom ? '↙ Standard' : '↗ Zoom'}
        </button>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 8, right: 12, bottom: 4, left: -20 }}>
          <CartesianGrid strokeDasharray="2 6" stroke="rgba(255,255,255,0.04)" />
          {/* 200ms grid reference lines */}
          {[0.2, 0.4, 0.6, 0.8, 1.0].map((t) => (
            <ReferenceLine key={t} x={t} stroke="rgba(255,255,255,0.04)" strokeDasharray="2 4" />
          ))}
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.08)" />
          <XAxis
            dataKey="time"
            tickFormatter={(v: number) => `${v.toFixed(1)}s`}
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `${v.toFixed(1)}`}
            label={{ value: 'mV', position: 'insideTopLeft', fontSize: 10, fill: 'var(--text-muted)' }}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(10,14,26,0.95)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 8,
              fontSize: 11,
            }}
            formatter={(v: number) => [`${v.toFixed(3)} mV`, `Lead ${signal?.lead}`]}
            labelFormatter={(l: number) => `t = ${l}s`}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: color }}
            isAnimationActive={false}
          />
          {zoom && (
            <Brush
              dataKey="time"
              height={20}
              stroke="rgba(255,255,255,0.1)"
              fill="rgba(255,255,255,0.03)"
              travellerWidth={6}
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      <div className="flex items-center gap-4 px-2 mt-2 text-xs text-[var(--text-muted)] flex-wrap">
        <span>SR: {signal?.samplingRate} Hz</span>
        <span>Duration: {signal?.duration?.toFixed(1)}s</span>
        <span>Lead: {signal?.lead}</span>
        <span className="ml-auto">{zoom ? '↗ Zoomed' : 'Normal view'}</span>
      </div>
    </GlassCard>
  )
}
