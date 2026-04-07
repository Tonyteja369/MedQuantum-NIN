import { useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { confidenceColor } from '@/utils/colorTokens'
import { formatConfidence } from '@/utils/formatters'

export function ConfidenceGauge() {
  const result = useECGStore((s) => s.analysisResult)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const confidence = result?.confidence ?? 0
  const color = confidenceColor(confidence)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const W = canvas.width
    const H = canvas.height
    const cx = W / 2
    const cy = H * 0.7
    const r = Math.min(W, H) * 0.38

    ctx.clearRect(0, 0, W, H)

    // Background arc
    ctx.beginPath()
    ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI)
    ctx.strokeStyle = 'rgba(255,255,255,0.06)'
    ctx.lineWidth = 16
    ctx.lineCap = 'round'
    ctx.stroke()

    // Progress arc
    const angle = Math.PI + confidence * Math.PI
    ctx.beginPath()
    ctx.arc(cx, cy, r, Math.PI, angle)
    ctx.strokeStyle = color
    ctx.lineWidth = 16
    ctx.lineCap = 'round'
    ctx.shadowColor = color
    ctx.shadowBlur = 16
    ctx.stroke()
    ctx.shadowBlur = 0

    // Tick marks
    for (let i = 0; i <= 10; i++) {
      const tickAngle = Math.PI + (i / 10) * Math.PI
      const innerR = r - 22
      const outerR = r - 12
      const sx = cx + innerR * Math.cos(tickAngle)
      const sy = cy + innerR * Math.sin(tickAngle)
      const ex = cx + outerR * Math.cos(tickAngle)
      const ey = cy + outerR * Math.sin(tickAngle)
      ctx.beginPath()
      ctx.moveTo(sx, sy)
      ctx.lineTo(ex, ey)
      ctx.strokeStyle = 'rgba(255,255,255,0.2)'
      ctx.lineWidth = i % 5 === 0 ? 2 : 1
      ctx.stroke()
    }

    // Needle
    const needleAngle = Math.PI + confidence * Math.PI
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + (r - 30) * Math.cos(needleAngle), cy + (r - 30) * Math.sin(needleAngle))
    ctx.strokeStyle = color
    ctx.lineWidth = 2.5
    ctx.lineCap = 'round'
    ctx.stroke()

    // Center dot
    ctx.beginPath()
    ctx.arc(cx, cy, 5, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
  }, [confidence, color])

  if (!result) return null

  return (
    <GlassCard padding="md" className="flex flex-col items-center">
      <h3 className="text-sm font-semibold text-[var(--text-primary)] self-start mb-2">
        Model Confidence
      </h3>

      <canvas ref={canvasRef} width={200} height={120} className="w-full max-w-[200px]" />

      <div className="text-center -mt-2">
        <motion.p
          key={confidence}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-3xl font-bold font-mono"
          style={{ color }}
        >
          {formatConfidence(confidence)}
        </motion.p>
        <p className="text-xs text-[var(--text-muted)] mt-0.5">
          {confidence >= 0.9 ? 'Very High' : confidence >= 0.75 ? 'High' : confidence >= 0.5 ? 'Moderate' : 'Low'} confidence
        </p>
      </div>

      <div className="w-full mt-3 text-xs text-[var(--text-muted)] flex justify-between">
        <span>0%</span>
        <span className="font-mono" style={{ color }}>v{result.modelVersion}</span>
        <span>100%</span>
      </div>
    </GlassCard>
  )
}
