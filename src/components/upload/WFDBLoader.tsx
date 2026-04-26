import { useState } from 'react'
import { motion } from 'framer-motion'
import { Database, ChevronDown, ChevronUp, Loader } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { useECGStore } from '@/store/useECGStore'
import { loadWFDBSample } from '@/api/ecgApi'
import type { LeadName } from '@/types/ecg.types'

const PHYSIONET_RECORDS = [
  { id: '100', label: 'MIT-BIH 100 — Normal sinus rhythm' },
  { id: '101', label: 'MIT-BIH 101 — Bundle branch block' },
  { id: '200', label: 'MIT-BIH 200 — Ventricular ectopy' },
  { id: '202', label: 'MIT-BIH 202 — Multi-form PVCs' },
  { id: '203', label: 'MIT-BIH 203 — Ventricular tachycardia' },
  { id: '205', label: 'MIT-BIH 205 — Ventricular bigeminy' },
  { id: '207', label: 'MIT-BIH 207 — AV block' },
  { id: '210', label: 'MIT-BIH 210 — Right bundle branch block' },
]

interface WFDBLoaderProps {
  onLoad?: (signalId: string) => void
}

export function WFDBLoader({ onLoad }: WFDBLoaderProps) {
  const [expanded, setExpanded] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const setUploadFile = useECGStore((s) => s.setUploadFile)
  const setUploadPreview = useECGStore((s) => s.setUploadPreview)
  const setUploadQuality = useECGStore((s) => s.setUploadQuality)
  const setUploadProcessing = useECGStore((s) => s.setUploadProcessing)

  const handleSelect = async (id: string) => {
    setSelected(id)
    setExpanded(false)
    setLoading(true)
    setError(null)
    setUploadProcessing(true)

    try {
      const result = await loadWFDBSample(id)

      // Create a synthetic File so the rest of the UI shows a filename
      const syntheticFile = new File([], `physionet-${id}.dat`, { type: 'application/octet-stream' })
      setUploadFile(syntheticFile)
      setUploadPreview(result.signals)   // real waveform from PhysioNet
      setUploadQuality(result.quality)
      onLoad?.(result.signalId)          // pass signal_id up so Analyze button works
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load sample'
      console.error('[WFDBLoader] Error:', msg)
      setError(msg)
    } finally {
      setLoading(false)
      setUploadProcessing(false)
    }
  }

  return (
    <GlassCard padding="sm" animate={false}>
      <button
        onClick={() => setExpanded((p) => !p)}
        className="w-full flex items-center justify-between gap-3 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <div className="flex items-center gap-2">
          {loading
            ? <Loader size={14} className="text-[var(--accent-primary)] animate-spin" />
            : <Database size={14} className="text-[var(--accent-primary)]" />
          }
          <span className="font-medium">
            {loading
              ? `Loading ${PHYSIONET_RECORDS.find(r => r.id === selected)?.label ?? selected}…`
              : selected
              ? PHYSIONET_RECORDS.find((r) => r.id === selected)?.label ?? selected
              : 'Load PhysioNet Sample Record'}
          </span>
        </div>
        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {error && (
        <p className="mt-2 text-xs text-red-400">{error}</p>
      )}

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
              disabled={loading}
              className="w-full text-left px-3 py-2 rounded-md text-xs text-[var(--text-secondary)] hover:text-[var(--accent-primary)] hover:bg-[rgba(0,212,255,0.05)] transition-all disabled:opacity-50"
            >
              <span className="font-mono text-[var(--text-muted)] mr-2">{rec.id}</span>
              {rec.label}
            </button>
          ))}
        </div>
        <p className="mt-2 px-1 text-xs text-[var(--text-muted)]">
          Real PhysioNet records streamed via MedQuantum backend API.
        </p>
      </motion.div>
    </GlassCard>
  )
}
