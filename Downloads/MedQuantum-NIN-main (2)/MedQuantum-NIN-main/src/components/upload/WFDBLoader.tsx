import { useState } from 'react'
import { motion } from 'framer-motion'
import { Database, ChevronDown, ChevronUp } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'

const PHYSIONET_RECORDS = [
  { id: 'mitdb/100', label: 'MIT-BIH 100 — Normal sinus rhythm' },
  { id: 'mitdb/200', label: 'MIT-BIH 200 — Ventricular ectopy' },
  { id: 'afdb/04015', label: 'AF Database 04015 — Atrial fibrillation' },
  { id: 'nsrdb/16265', label: 'Normal Sinus Rhythm DB 16265' },
  { id: 'ptbdb/patient001/s0010_re', label: 'PTB Diagnostic — Myocardial infarction' },
]

interface WFDBLoaderProps {
  onLoad?: (recordId: string) => void
  isLoading?: boolean
}

export function WFDBLoader({ onLoad, isLoading = false }: WFDBLoaderProps) {
  const [expanded, setExpanded] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)

  const handleSelect = (id: string) => {
    setSelected(id)
    onLoad?.(id)
    setExpanded(false)
  }

  return (
    <GlassCard padding="sm" animate={false}>
      <button
        onClick={() => setExpanded((p) => !p)}
        className="w-full flex items-center justify-between gap-3 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <div className="flex items-center gap-2">
          <Database size={14} className="text-[var(--accent-primary)]" />
          <span className="font-medium">
            {selected
              ? PHYSIONET_RECORDS.find((r) => r.id === selected)?.label ?? selected
              : 'Load PhysioNet Sample Record'}
          </span>
        </div>
        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      <motion.div
        initial={false}
        animate={{ height: expanded ? 'auto' : 0, opacity: expanded ? 1 : 0 }}
        transition={{ duration: 0.25 }}
        className="overflow-hidden"
      >
        <div className="mt-3 space-y-1">
          {PHYSIONET_RECORDS.map((rec) => (
            <button
              key={rec.id}
              onClick={() => handleSelect(rec.id)}
              disabled={isLoading}
              className="w-full text-left px-3 py-2 rounded-md text-xs text-[var(--text-secondary)] hover:text-[var(--accent-primary)] hover:bg-[rgba(0,212,255,0.05)] transition-all"
            >
              <span className="font-mono text-[var(--text-muted)] mr-2">{rec.id}</span>
              {rec.label}
            </button>
          ))}
        </div>
        <p className="mt-2 px-1 text-xs text-[var(--text-muted)]">
          Sample records from PhysioNet. Uses your configured backend service.
        </p>
      </motion.div>
    </GlassCard>
  )
}
