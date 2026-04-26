import { motion } from 'framer-motion'
import { clsx } from 'clsx'

type StatusType = 'online' | 'offline' | 'warning' | 'error' | 'idle'

interface StatusDotProps {
  status: StatusType
  pulse?: boolean
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

const statusColors: Record<StatusType, string> = {
  online: '#10b981',
  offline: '#4a5568',
  warning: '#fbbf24',
  error: '#ff4d6d',
  idle: '#00d4ff',
}

const statusLabels: Record<StatusType, string> = {
  online: 'Online',
  offline: 'Offline',
  warning: 'Warning',
  error: 'Error',
  idle: 'Idle',
}

export function StatusDot({ status, pulse = true, label, size = 'md' }: StatusDotProps) {
  const color = statusColors[status]
  const sizeMap = { sm: 6, md: 8, lg: 10 }
  const px = sizeMap[size]

  return (
    <div className="flex items-center gap-2">
      <div className="relative" style={{ width: px, height: px }}>
        <div
          className="rounded-full absolute inset-0"
          style={{ backgroundColor: color }}
        />
        {pulse && status !== 'offline' && (
          <motion.div
            className="rounded-full absolute inset-0"
            style={{ backgroundColor: color }}
            animate={{ scale: [1, 2], opacity: [0.6, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut' }}
          />
        )}
      </div>
      {label !== undefined && (
        <span
          className={clsx(
            'font-medium',
            size === 'sm' ? 'text-xs' : 'text-sm'
          )}
          style={{ color }}
        >
          {label || statusLabels[status]}
        </span>
      )}
    </div>
  )
}
