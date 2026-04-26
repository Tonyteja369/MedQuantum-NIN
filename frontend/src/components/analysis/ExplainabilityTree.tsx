import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight, ChevronDown, GitBranch } from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import type { ExplainabilityNode } from '@/types/ecg.types'

interface TreeNodeProps {
  node: ExplainabilityNode
  depth?: number
}

function TreeNode({ node, depth = 0 }: TreeNodeProps) {
  const [open, setOpen] = useState(depth < 1)
  const hasChildren = (node.children?.length ?? 0) > 0
  const isPositive = node.contribution >= 0
  const color = isPositive ? '#10b981' : '#ff4d6d'
  const bgColor = isPositive ? 'rgba(16,185,129,0.08)' : 'rgba(255,77,109,0.08)'
  const borderColor = isPositive ? 'rgba(16,185,129,0.25)' : 'rgba(255,77,109,0.25)'

  return (
    <div className={`${depth > 0 ? 'ml-5 border-l border-[var(--border-secondary)] pl-3' : ''}`}>
      <motion.div
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: depth * 0.05 }}
        className="mb-1.5"
      >
        <div
          className="flex items-center gap-2 p-2.5 rounded-lg cursor-pointer hover:brightness-110 transition-all"
          style={{ background: bgColor, border: `1px solid ${borderColor}` }}
          onClick={() => hasChildren && setOpen((p) => !p)}
        >
          {hasChildren && (
            <span className="flex-shrink-0" style={{ color: 'var(--text-muted)' }}>
              {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </span>
          )}
          {!hasChildren && <span className="w-3 flex-shrink-0" />}

          <div className="flex-1 min-w-0">
            <span className="text-xs font-medium text-[var(--text-primary)] truncate block">
              {node.feature}
            </span>
            {node.description && (
              <span className="text-xs text-[var(--text-muted)] truncate block">
                {node.description}
              </span>
            )}
          </div>

          {/* Contribution bar */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.abs(node.contribution) * 100}%` }}
                transition={{ duration: 0.6, delay: depth * 0.05 }}
              />
            </div>
            <span
              className="text-xs font-mono font-semibold w-10 text-right"
              style={{ color }}
            >
              {isPositive ? '+' : ''}{(node.contribution * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </motion.div>

      <AnimatePresence>
        {open && hasChildren && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {node.children!.map((child) => (
              <TreeNode key={child.id} node={child} depth={depth + 1} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function ExplainabilityTree() {
  const result = useECGStore((s) => s.analysisResult)

  if (!result || result.explainability.length === 0) return null

  return (
    <GlassCard padding="md">
      <div className="flex items-center gap-2 mb-4">
        <GitBranch size={16} className="text-[var(--accent-secondary)]" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Explainability (SHAP)</h3>
      </div>

      <div className="flex items-center gap-4 mb-3 text-xs text-[var(--text-muted)]">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded bg-[rgba(16,185,129,0.3)] border border-[rgba(16,185,129,0.5)]" />
          Supports diagnosis
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded bg-[rgba(255,77,109,0.3)] border border-[rgba(255,77,109,0.5)]" />
          Against diagnosis
        </div>
      </div>

      <div className="space-y-1 max-h-72 overflow-y-auto">
        {result.explainability.map((node) => (
          <TreeNode key={node.id} node={node} depth={0} />
        ))}
      </div>
    </GlassCard>
  )
}
