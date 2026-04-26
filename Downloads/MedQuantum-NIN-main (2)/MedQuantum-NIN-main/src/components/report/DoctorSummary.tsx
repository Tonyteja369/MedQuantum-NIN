import { GlassCard } from '@/components/ui/GlassCard'
import { useECGStore } from '@/store/useECGStore'
import { Stethoscope } from 'lucide-react'

export function DoctorSummary() {
  const report = useECGStore((s) => s.reportData)
  if (!report) return null

  return (
    <GlassCard padding="md">
      <div className="flex items-center gap-2 mb-4">
        <Stethoscope size={16} className="text-[var(--accent-secondary)]" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Clinical Summary</h3>
        <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-[rgba(124,58,237,0.1)] text-[#7c3aed] border border-[rgba(124,58,237,0.3)]">
          For Clinician
        </span>
      </div>

      <div
        className="rounded-lg p-4 text-sm leading-relaxed text-[var(--text-secondary)]"
        style={{ background: 'rgba(124,58,237,0.06)', border: '1px solid rgba(124,58,237,0.15)' }}
      >
        <p className="whitespace-pre-wrap">{report.doctorSummary}</p>
      </div>

      {/* Recommendations summary */}
      {report.recommendations.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
            Clinical Actions
          </p>
          <ul className="space-y-1.5">
            {report.recommendations.slice(0, 5).map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                <span className="mt-1 w-1.5 h-1.5 rounded-full bg-[var(--accent-secondary)] flex-shrink-0" />
                {rec.text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </GlassCard>
  )
}
