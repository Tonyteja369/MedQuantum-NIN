import { format, formatDistanceToNow, parseISO } from 'date-fns'
import type { RiskLevel } from '@/types/ecg.types'

/** Format a bpm value */
export function formatHeartRate(bpm: number): string {
  return `${Math.round(bpm)} bpm`
}

/** Format ms interval */
export function formatInterval(ms: number | null | undefined): string {
  if (ms == null) return '—'
  return `${Math.round(ms)} ms`
}

/** Format confidence as percentage string */
export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`
}

/** Format risk score 0-100 */
export function formatRiskScore(score: number): string {
  return score.toFixed(1)
}

/** Risk level label */
export const riskLevelLabel: Record<RiskLevel, string> = {
  normal: 'Normal',
  borderline: 'Borderline',
  elevated: 'Elevated',
  critical: 'Critical',
}

/** Format ISO timestamp to readable */
export function formatTimestamp(iso: string): string {
  try {
    return format(parseISO(iso), 'MMM d, yyyy • HH:mm')
  } catch {
    return iso
  }
}

/** Format relative time */
export function formatRelativeTime(iso: string): string {
  try {
    return formatDistanceToNow(parseISO(iso), { addSuffix: true })
  } catch {
    return iso
  }
}

/** Format file size */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

/** Format duration in seconds */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}

/** Format axis degrees */
export function formatAxis(degrees: number | null | undefined): string {
  if (degrees == null) return '—'
  return `${Math.round(degrees)}°`
}

/** Format voltage in mV */
export function formatVoltage(mv: number | null | undefined): string {
  if (mv == null) return '—'
  return `${mv.toFixed(2)} mV`
}

/** Format quality score */
export function formatQuality(score: number): string {
  if (score >= 80) return 'Excellent'
  if (score >= 60) return 'Good'
  if (score >= 40) return 'Fair'
  return 'Poor'
}

/** Format processing time */
export function formatProcessingTime(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

/** Truncate string */
export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str
  return str.slice(0, maxLen - 3) + '…'
}

/** Capitalize first letter */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}
