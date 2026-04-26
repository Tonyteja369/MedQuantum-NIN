import { motion } from 'framer-motion'
import { Lightbulb, AlertCircle, Clock, Pill, Heart, Activity, Users } from 'lucide-react'
import { useECGStore } from '@/store/useECGStore'
import { GlassCard } from '@/components/ui/GlassCard'
import { Badge } from '@/components/ui/Badge'
import { priorityColors, categoryColors } from '@/utils/colorTokens'
import type { RecommendationItem } from '@/types/ecg.types'

const CategoryIcons: Record<string, React.ReactNode> = {
  medication: <Pill size={14} />,
  'follow-up': <Clock size={14} />,
  lifestyle: <Heart size={14} />,
  monitoring: <Activity size={14} />,
  referral: <Users size={14} />,
}

const PriorityBadgeVariants: Record<string, 'danger' | 'warning' | 'info' | 'success'> = {
  urgent: 'danger',
  high: 'warning',
  medium: 'info',
  low: 'success',
}

function RecommendationRow({ item, index }: { item: RecommendationItem; index: number }) {
  const priorityColor = priorityColors[item.priority]
  const categoryColor = categoryColors[item.category as keyof typeof categoryColors] ?? '#00d4ff'

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      className="p-3 rounded-lg"
      style={{
        background: `${priorityColor}08`,
        border: `1px solid ${priorityColor}25`,
      }}
    >
      <div className="flex items-start gap-2.5">
        <div
          className="mt-0.5 p-1.5 rounded-md flex-shrink-0"
          style={{ background: `${categoryColor}15`, color: categoryColor }}
        >
          {CategoryIcons[item.category] ?? <AlertCircle size={14} />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <Badge variant={PriorityBadgeVariants[item.priority]} size="sm" dot>
              {item.priority}
            </Badge>
            <span className="text-xs text-[var(--text-muted)] capitalize">{item.category}</span>
          </div>
          <p className="text-sm text-[var(--text-primary)] leading-snug">{item.text}</p>
          {item.rationale && (
            <p className="text-xs text-[var(--text-muted)] mt-1 italic">{item.rationale}</p>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export function RecommendationsCard() {
  const result = useECGStore((s) => s.analysisResult)
  if (!result || result.recommendations.length === 0) return null

  const sorted = [...result.recommendations].sort((a, b) => {
    const order = { urgent: 0, high: 1, medium: 2, low: 3 }
    return order[a.priority] - order[b.priority]
  })

  return (
    <GlassCard padding="md">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb size={16} className="text-[var(--accent-warning)]" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Clinical Recommendations</h3>
        <Badge variant="warning" size="sm">{sorted.length}</Badge>
      </div>

      <div className="space-y-2">
        {sorted.map((item, i) => (
          <RecommendationRow key={i} item={item} index={i} />
        ))}
      </div>
    </GlassCard>
  )
}
