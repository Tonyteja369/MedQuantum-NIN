/**
 * Signal processing utilities for ECG data
 */

/** Normalize signal to [-1, 1] range */
export function normalizeSignal(data: number[]): number[] {
  if (data.length === 0) return []
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min
  if (range === 0) return data.map(() => 0)
  return data.map((v) => ((v - min) / range) * 2 - 1)
}

/** Apply simple moving-average low-pass filter */
export function lowPassFilter(data: number[], windowSize = 5): number[] {
  if (data.length === 0) return []
  const result: number[] = []
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - Math.floor(windowSize / 2))
    const end = Math.min(data.length - 1, i + Math.floor(windowSize / 2))
    const slice = data.slice(start, end + 1)
    result.push(slice.reduce((a, b) => a + b, 0) / slice.length)
  }
  return result
}

/** Remove baseline wander using high-pass filter */
export function removeBaseline(data: number[], samplingRate: number): number[] {
  const cutoff = 0.5 // Hz
  const alpha = 1 - Math.exp((-2 * Math.PI * cutoff) / samplingRate)
  const filtered: number[] = []
  let baseline = data[0] ?? 0
  for (const v of data) {
    baseline = baseline + alpha * (v - baseline)
    filtered.push(v - baseline)
  }
  return filtered
}

/** Detect R-peaks using Pan-Tompkins-like approach */
export function detectRPeaks(
  data: number[],
  samplingRate: number,
  threshold = 0.6
): number[] {
  if (data.length === 0) return []
  const normalized = normalizeSignal(data)
  const minRRSamples = Math.floor(samplingRate * 0.3) // 300ms refractory
  const peaks: number[] = []
  let lastPeak = -minRRSamples

  for (let i = 1; i < normalized.length - 1; i++) {
    if (
      normalized[i] > threshold &&
      normalized[i] > (normalized[i - 1] ?? 0) &&
      normalized[i] > (normalized[i + 1] ?? 0) &&
      i - lastPeak >= minRRSamples
    ) {
      peaks.push(i)
      lastPeak = i
    }
  }
  return peaks
}

/** Compute RR intervals in ms from R-peak indices */
export function computeRRIntervals(peaks: number[], samplingRate: number): number[] {
  if (peaks.length < 2) return []
  const rr: number[] = []
  for (let i = 1; i < peaks.length; i++) {
    rr.push(((peaks[i]! - peaks[i - 1]!) / samplingRate) * 1000)
  }
  return rr
}

/** Compute heart rate from RR intervals */
export function computeHeartRate(rrIntervals: number[]): number {
  if (rrIntervals.length === 0) return 0
  const meanRR = rrIntervals.reduce((a, b) => a + b, 0) / rrIntervals.length
  return Math.round(60_000 / meanRR)
}

/** Compute RMSSD (HRV metric) from RR intervals */
export function computeRMSSD(rrIntervals: number[]): number {
  if (rrIntervals.length < 2) return 0
  let sumSq = 0
  for (let i = 1; i < rrIntervals.length; i++) {
    const diff = (rrIntervals[i]! - rrIntervals[i - 1]!)
    sumSq += diff * diff
  }
  return Math.sqrt(sumSq / (rrIntervals.length - 1))
}

/** Downsample data for chart rendering while preserving signal characteristics */
export function downsampleSignal(data: number[], targetPoints: number): number[] {
  if (data.length <= targetPoints) return data
  
  const factor = data.length / targetPoints
  const result: number[] = []
  
  for (let i = 0; i < targetPoints; i++) {
    const startIdx = Math.floor(i * factor)
    const endIdx = Math.floor((i + 1) * factor)
    const window = data.slice(startIdx, endIdx)
    
    if (window.length === 0) {
      result.push(0)
      continue
    }
    
    // Use median to preserve signal shape and reduce noise
    const sorted = [...window].sort((a, b) => a - b)
    const median = sorted[Math.floor(sorted.length / 2)]
    
    // Handle NaN/undefined values
    result.push(isNaN(median) || median === undefined ? 0 : median)
  }
  
  return result
}

/** Convert sample index to time in seconds */
export function sampleToTime(sampleIdx: number, samplingRate: number): number {
  return sampleIdx / samplingRate
}

/** Compute SNR estimate in dB */
export function computeSNR(signal: number[], noise: number[]): number {
  const signalPower = signal.reduce((a, b) => a + b * b, 0) / signal.length
  const noisePower = noise.reduce((a, b) => a + b * b, 0) / noise.length
  if (noisePower === 0) return 60
  return 10 * Math.log10(signalPower / noisePower)
}

/** Validate ECG signal quality and characteristics */
export function validateECGSignal(data: number[], samplingRate: number): {
  isValid: boolean
  issues: string[]
  quality: 'good' | 'fair' | 'poor'
} {
  const issues: string[] = []
  
  if (!data || data.length === 0) {
    issues.push('Empty signal data')
    return { isValid: false, issues, quality: 'poor' }
  }
  
  // Check sampling rate
  if (samplingRate < 100 || samplingRate > 1000) {
    issues.push(`Invalid sampling rate: ${samplingRate}Hz (expected 100-1000Hz)`)
  }
  
  // Check signal duration
  const duration = data.length / samplingRate
  if (duration < 2) {
    issues.push(`Signal too short: ${duration.toFixed(1)}s (minimum 2s required)`)
  }
  if (duration > 300) {
    issues.push(`Signal too long: ${duration.toFixed(1)}s (maximum 5 minutes)`)
  }
  
  // Check for flat line (no signal variation)
  const signalRange = Math.max(...data) - Math.min(...data)
  if (signalRange < 0.001) {
    issues.push('Signal appears to be flat line (no variation detected)')
  }
  
  // Check for excessive noise
  const noiseLevel = computeNoiseLevel(data)
  if (noiseLevel > 0.5) {
    issues.push('High noise level detected')
  }
  
  // Check for too many NaN/invalid values
  const validRatio = data.filter(v => isFinite(v)).length / data.length
  if (validRatio < 0.9) {
    issues.push(`Too many invalid values: ${((1 - validRatio) * 100).toFixed(1)}%`)
  }
  
  // Determine quality
  let quality: 'good' | 'fair' | 'poor' = 'good'
  if (issues.length > 3) quality = 'poor'
  else if (issues.length > 0) quality = 'fair'
  
  return {
    isValid: issues.length === 0,
    issues,
    quality
  }
}

/** Compute noise level in signal */
function computeNoiseLevel(data: number[]): number {
  if (data.length < 2) return 1
  
  // Use high-frequency component as noise proxy
  const diffs = data.slice(1).map((v, i) => Math.abs(v - data[i]))
  return diffs.reduce((a, b) => a + b, 0) / diffs.length
}

/** Generate synthetic ECG waveform for demo/preview purposes */
export function generateSyntheticECG(
  samplingRate: number,
  durationSeconds: number,
  heartRate = 72
): number[] {
  const totalSamples = samplingRate * durationSeconds
  const rrSamples = Math.floor((60 / heartRate) * samplingRate)
  const data: number[] = new Array(totalSamples).fill(0)

  for (let beat = 0; beat * rrSamples < totalSamples; beat++) {
    const offset = beat * rrSamples

    // P wave
    for (let i = 0; i < Math.floor(rrSamples * 0.1); i++) {
      const t = i / (rrSamples * 0.1)
      const idx = offset + i
      if (idx < totalSamples) data[idx] = (data[idx] ?? 0) + 0.15 * Math.sin(Math.PI * t)
    }

    // QRS complex
    const qrsStart = Math.floor(rrSamples * 0.16)
    const qrsWidth = Math.floor(rrSamples * 0.08)
    for (let i = 0; i < qrsWidth; i++) {
      const t = i / qrsWidth
      const idx = offset + qrsStart + i
      if (idx < totalSamples) {
        const qrs = t < 0.2 ? -0.2 * (t / 0.2) : t < 0.5 ? (t - 0.2) / 0.3 : 1 - (t - 0.5) / 0.5
        data[idx] = (data[idx] ?? 0) + qrs
      }
    }

    // T wave
    const tStart = Math.floor(rrSamples * 0.3)
    const tWidth = Math.floor(rrSamples * 0.2)
    for (let i = 0; i < tWidth; i++) {
      const t = i / tWidth
      const idx = offset + tStart + i
      if (idx < totalSamples) data[idx] = (data[idx] ?? 0) + 0.35 * Math.sin(Math.PI * t)
    }
  }

  // Add small noise
  return data.map((v) => v + (Math.random() - 0.5) * 0.02)
}

/** Format ECG data into recharts-compatible point array */
export function toChartData(
  data: number[],
  samplingRate: number,
  maxPoints = 500
): Array<{ time: number; value: number }> {
  if (!data || data.length === 0) return []
  
  // Filter out NaN and invalid values before processing
  const cleanData = data.filter(v => v !== null && v !== undefined && !isNaN(v) && isFinite(v))
  if (cleanData.length === 0) return []
  
  const downsampled = downsampleSignal(cleanData, maxPoints)
  const factor = cleanData.length / downsampled.length
  
  return downsampled.map((value, i) => {
    const time = sampleToTime(Math.floor(i * factor), samplingRate)
    return {
      time: parseFloat(time.toFixed(3)),
      value: parseFloat(parseFloat(value.toString()).toFixed(4)),
    }
  })
}
