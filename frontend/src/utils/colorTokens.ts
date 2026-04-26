import type { RiskLevel } from '@/types/ecg.types'

export const riskColors: Record<RiskLevel, string> = {
  normal: '#10b981',
  borderline: '#fbbf24',
  elevated: '#f97316',
  critical: '#ff4d6d',
}

export const riskGlows: Record<RiskLevel, string> = {
  normal: '0 0 20px rgba(16,185,129,0.4)',
  borderline: '0 0 20px rgba(251,191,36,0.4)',
  elevated: '0 0 20px rgba(249,115,22,0.4)',
  critical: '0 0 20px rgba(255,77,109,0.5)',
}

export const riskBg: Record<RiskLevel, string> = {
  normal: 'rgba(16,185,129,0.1)',
  borderline: 'rgba(251,191,36,0.1)',
  elevated: 'rgba(249,115,22,0.1)',
  critical: 'rgba(255,77,109,0.1)',
}

export const riskBorder: Record<RiskLevel, string> = {
  normal: 'rgba(16,185,129,0.3)',
  borderline: 'rgba(251,191,36,0.3)',
  elevated: 'rgba(249,115,22,0.3)',
  critical: 'rgba(255,77,109,0.4)',
}

export const priorityColors = {
  urgent: '#ff4d6d',
  high: '#f97316',
  medium: '#fbbf24',
  low: '#10b981',
} as const

export const categoryColors = {
  medication: '#00d4ff',
  'follow-up': '#7c3aed',
  lifestyle: '#10b981',
  monitoring: '#fbbf24',
  referral: '#ff4d6d',
} as const

export const leadColors: Record<string, string> = {
  I: '#00d4ff',
  II: '#7c3aed',
  III: '#10b981',
  aVR: '#fbbf24',
  aVL: '#f97316',
  aVF: '#ff4d6d',
  V1: '#06b6d4',
  V2: '#8b5cf6',
  V3: '#34d399',
  V4: '#fcd34d',
  V5: '#fb923c',
  V6: '#f87171',
}

export const confidenceColor = (confidence: number): string => {
  if (confidence >= 0.9) return '#10b981'
  if (confidence >= 0.75) return '#fbbf24'
  if (confidence >= 0.5) return '#f97316'
  return '#ff4d6d'
}
