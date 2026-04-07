import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { Badge } from '@/components/ui/Badge'
import { ClipboardList } from 'lucide-react'
import { formatTimestamp, formatHeartRate, formatInterval } from '@/utils/formatters'

export function SOAPReport() {
  const report = useECGStore((s) => s.reportData)
  if (!report) return null

  const sections = [
    {
      key: 'S',
      label: 'Subjective',
      color: '#00d4ff',
      content: report.soap.subjective,
    },
    {
      key: 'O',
      label: 'Objective',
      color: '#10b981',
      content: report.soap.objective,
    },
    {
      key: 'A',
      label: 'Assessment',
      color: '#fbbf24',
      content: report.soap.assessment,
    },
    {
      key: 'P',
      label: 'Plan',
      color: '#7c3aed',
      content: report.soap.plan,
    },
  ]

  return (
    <GlassCard padding="md">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <ClipboardList size={16} className="text-[var(--accent-primary)]" />
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">SOAP Note</h3>
        </div>
        <span className="text-xs text-[var(--text-muted)] font-mono">
          {formatTimestamp(report.generatedAt)}
        </span>
      </div>

      {/* Metrics summary */}
      <div className="flex flex-wrap gap-2 mb-5 pb-4 border-b border-[var(--border-secondary)]">
        <Badge variant="primary" size="sm">
          HR: {formatHeartRate(report.metrics.heartRate)}
        </Badge>
        <Badge variant="success" size="sm">
          QRS: {formatInterval(report.metrics.intervals.qrs)}
        </Badge>
        <Badge variant="warning" size="sm">
          QTc: {formatInterval(report.metrics.intervals.qtc)}
        </Badge>
        <Badge variant="secondary" size="sm">
          PR: {formatInterval(report.metrics.intervals.pr)}
        </Badge>
      </div>

      <div className="space-y-5">
        {sections.map((sec) => (
          <div key={sec.key}>
            <div className="flex items-center gap-2 mb-2">
              <div
                className="w-7 h-7 rounded-md flex items-center justify-center text-sm font-bold font-mono"
                style={{
                  background: `${sec.color}18`,
                  color: sec.color,
                  border: `1px solid ${sec.color}30`,
                }}
              >
                {sec.key}
              </div>
              <h4 className="text-sm font-semibold text-[var(--text-primary)]">{sec.label}</h4>
            </div>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed pl-9 whitespace-pre-wrap">
              {sec.content}
            </p>
          </div>
        ))}
      </div>

      {/* ICD codes */}
      {report.diagnoses.length > 0 && (
        <div className="mt-5 pt-4 border-t border-[var(--border-secondary)]">
          <p className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
            ICD Codes
          </p>
          <div className="flex flex-wrap gap-1.5">
            {report.diagnoses.map((dx) => (
              <Badge key={dx.code} variant="default" size="sm">
                {dx.code} — {dx.label}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </GlassCard>
  )
}
