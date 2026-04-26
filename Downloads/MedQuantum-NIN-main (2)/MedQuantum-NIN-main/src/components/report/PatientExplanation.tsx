import { GlassCard } from '@/components/ui/GlassCard'
import { useECGStore } from '@/store/useECGStore'
import { User, Heart } from 'lucide-react'
import { riskColors, riskBg } from '@/utils/colorTokens'
import { riskLevelLabel } from '@/utils/formatters'

export function PatientExplanation() {
  const report = useECGStore((s) => s.reportData)
  if (!report) return null

  const riskColor = riskColors[report.riskLevel]
  const riskBgColor = riskBg[report.riskLevel]

  return (
    <GlassCard padding="md">
      <div className="flex items-center gap-2 mb-4">
        <User size={16} className="text-[var(--accent-success)]" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Patient Explanation</h3>
        <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-[rgba(16,185,129,0.1)] text-[#10b981] border border-[rgba(16,185,129,0.3)]">
          Plain Language
        </span>
      </div>

      {/* Risk summary for patient */}
      <div
        className="rounded-lg p-4 mb-4 flex items-center gap-3"
        style={{ background: riskBgColor, border: `1px solid ${riskColor}30` }}
      >
        <Heart size={20} style={{ color: riskColor }} className="flex-shrink-0" />
        <div>
          <p className="text-sm font-semibold" style={{ color: riskColor }}>
            Your heart test shows {riskLevelLabel[report.riskLevel].toLowerCase()} risk
          </p>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">
            {report.riskLevel === 'normal'
              ? 'Your heart rhythm looks healthy!'
              : report.riskLevel === 'borderline'
              ? 'Some small changes detected — please discuss with your doctor.'
              : report.riskLevel === 'elevated'
              ? 'Your doctor should review these results soon.'
              : 'Please seek medical attention promptly.'}
          </p>
        </div>
      </div>

      <div
        className="rounded-lg p-4 text-sm leading-relaxed text-[var(--text-secondary)]"
        style={{ background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.12)' }}
      >
        <p className="whitespace-pre-wrap">{report.patientExplanation}</p>
      </div>

      <p className="text-xs text-[var(--text-muted)] mt-3 italic">
        This explanation is AI-generated and does not replace professional medical advice.
        Always consult your healthcare provider about your results.
      </p>
    </GlassCard>
  )
}
