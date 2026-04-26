import { useEffect, useRef } from 'react'

export function ECGAnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animFrame: number
    let offset = 0

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resize()
    window.addEventListener('resize', resize)

    const drawECGLine = (
      y: number,
      speed: number,
      amplitude: number,
      color: string,
      lineWidth = 1.5
    ) => {
      const W = canvas.offsetWidth
      const H = canvas.offsetHeight
      ctx.beginPath()
      ctx.strokeStyle = color
      ctx.lineWidth = lineWidth
      ctx.shadowColor = color
      ctx.shadowBlur = 8

      let x = 0
      const step = 3
      const beatWidth = 80

      while (x < W + beatWidth) {
        const localX = ((x + offset * speed) % beatWidth)
        let localY = 0

        if (localX < 10) {
          localY = 0
        } else if (localX < 15) {
          localY = -(amplitude * 0.15)
        } else if (localX < 20) {
          localY = amplitude * 0.1
        } else if (localX < 22) {
          localY = -amplitude
        } else if (localX < 24) {
          localY = amplitude * 0.6
        } else if (localX < 26) {
          localY = -(amplitude * 0.2)
        } else if (localX < 34) {
          const t = (localX - 26) / 8
          localY = amplitude * 0.35 * Math.sin(Math.PI * t)
        }

        if (x === 0) {
          ctx.moveTo(x, y + localY)
        } else {
          ctx.lineTo(x, y + localY)
        }
        x += step
      }
      ctx.stroke()
    }

    const animate = () => {
      const W = canvas.offsetWidth
      const H = canvas.offsetHeight
      ctx.clearRect(0, 0, W, H)
      ctx.shadowBlur = 0

      // Grid
      ctx.strokeStyle = 'rgba(255,255,255,0.03)'
      ctx.lineWidth = 1
      for (let x = 0; x < W; x += 40) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, H)
        ctx.stroke()
      }
      for (let y = 0; y < H; y += 40) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(W, y)
        ctx.stroke()
      }

      // ECG lines at different heights
      drawECGLine(H * 0.25, 0.8, 30, 'rgba(0,212,255,0.2)', 1.5)
      drawECGLine(H * 0.5, 1.0, 40, 'rgba(0,212,255,0.12)', 1)
      drawECGLine(H * 0.75, 0.6, 25, 'rgba(124,58,237,0.15)', 1)

      offset += 0.5
      animFrame = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animFrame)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none select-none"
      aria-hidden="true"
    />
  )
}
