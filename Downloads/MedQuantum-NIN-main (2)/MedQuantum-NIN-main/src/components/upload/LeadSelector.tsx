import { motion } from 'framer-motion'
import { useECGStore } from '@/store/useECGStore'
import { leadColors } from '@/utils/colorTokens'
import type { LeadName } from '@/types/ecg.types'
import { GlassCard } from '@/components/ui/GlassCard'

const ALL_LEADS: LeadName[] = [
  'I', 'II', 'III', 'aVR', 'aVL', 'aVF',
  'V1', 'V2', 'V3', 'V4', 'V5', 'V6',
]

export function LeadSelector() {
  const selectedLeads = useECGStore((s) => s.uploadState.selectedLeads)
  const setSelectedLeads = useECGStore((s) => s.setSelectedLeads)

  const toggle = (lead: LeadName) => {
    if (selectedLeads.includes(lead)) {
      if (selectedLeads.length > 1) {
        setSelectedLeads(selectedLeads.filter((l) => l !== lead))
      }
    } else {
      setSelectedLeads([...selectedLeads, lead])
    }
  }

  const selectAll = () => setSelectedLeads([...ALL_LEADS])
  const selectStandard = () => setSelectedLeads(['I', 'II', 'III', 'aVR', 'aVL', 'aVF'])
  const selectPrecordial = () => setSelectedLeads(['V1', 'V2', 'V3', 'V4', 'V5', 'V6'])

  return (
    <GlassCard padding="md" animate={false}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Lead Selection</h3>
        <div className="flex gap-1.5">
          {[
            { label: 'All', action: selectAll },
            { label: 'Limb', action: selectStandard },
            { label: 'V1–6', action: selectPrecordial },
          ].map((btn) => (
            <button
              key={btn.label}
              onClick={btn.action}
              className="text-xs px-2 py-0.5 rounded glass border border-[var(--border-primary)] text-[var(--text-muted)] hover:text-[var(--accent-primary)] hover:border-[rgba(0,212,255,0.3)] transition-all"
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-6 gap-1.5">
        {ALL_LEADS.map((lead) => {
          const selected = selectedLeads.includes(lead)
          const color = leadColors[lead] ?? '#00d4ff'
          return (
            <motion.button
              key={lead}
              onClick={() => toggle(lead)}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              className="relative aspect-square rounded-md flex items-center justify-center text-xs font-mono font-semibold transition-all duration-200"
              style={{
                background: selected ? `${color}18` : 'rgba(255,255,255,0.03)',
                border: `1px solid ${selected ? `${color}50` : 'rgba(255,255,255,0.08)'}`,
                color: selected ? color : 'var(--text-muted)',
                boxShadow: selected ? `0 0 8px ${color}30` : undefined,
              }}
            >
              {lead}
            </motion.button>
          )
        })}
      </div>

      <p className="text-xs text-[var(--text-muted)] mt-2">
        {selectedLeads.length} of {ALL_LEADS.length} leads selected
      </p>
    </GlassCard>
  )
}
